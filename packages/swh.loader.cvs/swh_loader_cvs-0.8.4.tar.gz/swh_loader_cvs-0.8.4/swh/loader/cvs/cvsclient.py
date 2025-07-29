# Copyright (C) 2015-2022  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""Minimal CVS client implementation"""

import os.path
import socket
import subprocess
import tempfile
from typing import IO, Tuple

from tenacity import retry
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_attempt

from swh.loader.exception import NotFound

CVS_PSERVER_PORT = 2401
CVS_PROTOCOL_BUFFER_SIZE = 8192
EXAMPLE_PSERVER_URL = "pserver://user:password@cvs.example.com/cvsroot/repository"
EXAMPLE_SSH_URL = "ssh://user@cvs.example.com/cvsroot/repository"

VALID_RESPONSES = [
    "ok",
    "error",
    "Valid-requests",
    "Checked-in",
    "New-entry",
    "Checksum",
    "Copy-file",
    "Updated",
    "Created",
    "Update-existing",
    "Merged",
    "Patched",
    "Rcs-diff",
    "Mode",
    "Removed",
    "Remove-entry",
    "Template",
    "Notified",
    "Module-expansion",
    "Wrapper-rcsOption",
    "M",
    "Mbinary",
    "E",
    "F",
    "MT",
]

# Trivially encode strings to protect them from innocent eyes (i.e.,
# inadvertent password compromises, like a network administrator
# who's watching packets for legitimate reasons and accidentally sees
# the password protocol go by).
#
# This is NOT secure encryption.


def scramble_password(password):
    s = ["A"]  # scramble scheme version number
    # fmt: off
    scramble_shifts = [
        0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,  # noqa: E241
       16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,  # noqa: E241,E131,B950
      114,120, 53, 79, 96,109, 72,108, 70, 64, 76, 67,116, 74, 68, 87,  # noqa: E241,E131,B950
      111, 52, 75,119, 49, 34, 82, 81, 95, 65,112, 86,118,110,122,105,  # noqa: E241,E131,B950
       41, 57, 83, 43, 46,102, 40, 89, 38,103, 45, 50, 42,123, 91, 35,  # noqa: E241,E131,B950
      125, 55, 54, 66,124,126, 59, 47, 92, 71,115, 78, 88,107,106, 56,  # noqa: E241,E131,B950
       36,121,117,104,101,100, 69, 73, 99, 63, 94, 93, 39, 37, 61, 48,  # noqa: E241,E131,B950
       58,113, 32, 90, 44, 98, 60, 51, 33, 97, 62, 77, 84, 80, 85,223,  # noqa: E241,E131,B950
      225,216,187,166,229,189,222,188,141,249,148,200,184,136,248,190,  # noqa: E241,E131,B950
      199,170,181,204,138,232,218,183,255,234,220,247,213,203,226,193,  # noqa: E241,E131,B950
      174,172,228,252,217,201,131,230,197,211,145,238,161,179,160,212,  # noqa: E241,E131,B950
      207,221,254,173,202,146,224,151,140,196,205,130,135,133,143,246,  # noqa: E241,E131,B950
      192,159,244,239,185,168,215,144,139,165,180,157,147,186,214,176,  # noqa: E241,E131,B950
      227,231,219,169,175,156,206,198,129,164,150,210,154,177,134,127,  # noqa: E241,E131,B950
      182,128,158,208,162,132,167,209,149,241,153,251,237,236,171,195,  # noqa: E241,E131,B950
      243,233,253,240,194,250,191,155,142,137,245,235,163,242,178,152]  # noqa: E241,E131,B950
    # fmt: on
    for c in password:
        s.append("%c" % scramble_shifts[ord(c)])
    return "".join(s)


def decode_path(path: bytes) -> Tuple[str, str]:
    """Attempt to decode a file path based on encodings known to be used
    in CVS repositories that can be found in the wild.

    Args:
        path: raw bytes path

    Returns:
        A tuple (decoded path, encoding)

    """
    path_encodings = ["ascii", "iso-8859-1", "utf-8"]
    for encoding in path_encodings:
        try:
            how = "ignore" if encoding == path_encodings[-1] else "strict"
            path_str = path.decode(encoding, how)
            break
        except UnicodeError:
            pass
    return path_str, encoding


class CVSProtocolError(Exception):
    pass


class CVSClient:
    # connection to an existing pserver might sometimes fail,
    # retrying the operation usually fixes the issue
    @retry(
        retry=retry_if_exception_type(NotFound),
        stop=stop_after_attempt(max_attempt_number=3),
        reraise=True,
    )
    def connect_pserver(self, hostname, port, username, password):
        if port is None:
            port = CVS_PSERVER_PORT
        if username is None:
            raise NotFound(
                "Username is required for "
                "a pserver connection: %s" % EXAMPLE_PSERVER_URL
            )

        try:
            self.socket = socket.create_connection((hostname, port))
        except ConnectionRefusedError:
            raise NotFound("Could not connect to %s:%s", hostname, port)

        # use empty password if it is None
        scrambled_password = scramble_password(password or "")
        request = "BEGIN AUTH REQUEST\n%s\n%s\n%s\nEND AUTH REQUEST\n" % (
            self.cvsroot_path,
            username,
            scrambled_password,
        )
        print("Request: %s\n" % request)
        self.socket.sendall(request.encode("UTF-8"))

        response = self.conn_read_line()
        if response != b"I LOVE YOU\n":
            raise NotFound(
                "pserver authentication failed for %s:%s: %s"
                % (hostname, port, response)
            )

    def connect_ssh(self, hostname, port, username):
        command = ["ssh"]
        if username is not None:
            # Assume 'auth' contains only a user name.
            # We do not support password authentication with SSH since the
            # anoncvs user is usually granted access without a password.
            command += ["-l", "%s" % username]
        if port is not None:
            command += ["-p", "%d" % port]

        # accept new SSH hosts keys upon first use; changed host keys
        # will require intervention
        command += ["-o", "StrictHostKeyChecking=accept-new"]

        # disable interactive prompting
        command += ["-o", "BatchMode=yes"]

        # disable further option processing by adding '--'
        command += ["--"]

        command += ["%s" % hostname, "cvs", "server"]
        # use non-buffered I/O to match behaviour of self.socket
        self.ssh = subprocess.Popen(
            command, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

    def connect_fake(self):
        command = ["cvs", "server"]
        # use non-buffered I/O to match behaviour of self.socket
        self.ssh = subprocess.Popen(
            command, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

    def conn_read_line(self, require_newline=True):
        if len(self.linebuffer) != 0:
            return self.linebuffer.pop(0)
        buf = b""
        idx = -1
        while idx == -1:
            if len(buf) >= CVS_PROTOCOL_BUFFER_SIZE:
                if require_newline:
                    raise CVSProtocolError(
                        "Overlong response from " "CVS server: %s" % buf
                    )
                else:
                    break
            if self.socket:
                buf += self.socket.recv(CVS_PROTOCOL_BUFFER_SIZE)
            elif self.ssh:
                buf += self.ssh.stdout.read(CVS_PROTOCOL_BUFFER_SIZE)
            else:
                raise Exception("No valid connection")
            if not buf:
                return None
            idx = buf.rfind(b"\n")
        if idx != -1:
            self.linebuffer = buf[: idx + 1].splitlines(keepends=True)
        else:
            if require_newline:
                raise CVSProtocolError("Invalid response from CVS server: %s" % buf)
            else:
                self.linebuffer.append(buf)
        if len(self.incomplete_line) > 0:
            self.linebuffer[0] = self.incomplete_line + self.linebuffer[0]
        if idx != -1:
            self.incomplete_line = buf[idx + 1 :]
        else:
            self.incomplete_line = b""
        return self.linebuffer.pop(0)

    def conn_write(self, data):
        if self.socket:
            return self.socket.sendall(data)
        if self.ssh:
            self.ssh.stdin.write(data)
            return self.ssh.stdin.flush()
        raise Exception("No valid connection")

    def conn_write_str(self, s, encoding="utf-8"):
        return self.conn_write(s.encode(encoding))

    def conn_close(self):
        if self.socket:
            self.socket.close()
        if self.ssh:
            self.ssh.kill()
            try:
                self.ssh.wait(timeout=10)
            except subprocess.TimeoutExpired as e:
                raise subprocess.TimeoutExpired(
                    "Could not terminate " "ssh program: %s" % e
                )

    def __init__(self, url):
        """
        Connect to a CVS server at the specified URL and perform the initial
        CVS protocol handshake.
        """
        self.hostname = url.hostname
        self.cvsroot_path = os.path.dirname(url.path)
        self.cvs_module_name = os.path.basename(url.path)
        self.socket = None
        self.ssh = None
        self.linebuffer = list()
        self.incomplete_line = b""
        self.tempfile_cutoff = 100 * 1024 * 1024

        if url.scheme == "pserver":
            self.connect_pserver(url.hostname, url.port, url.username, url.password)
        elif url.scheme == "ssh":
            self.connect_ssh(url.hostname, url.port, url.username)
        elif url.scheme == "fake":
            self.connect_fake()
        else:
            raise NotFound("Invalid CVS origin URL '%s'" % url)

        # we should have a connection now
        assert self.socket or self.ssh

        self.conn_write_str(
            "Root %s\nValid-responses %s\nvalid-requests\n"
            "UseUnchanged\n" % (self.cvsroot_path, " ".join(VALID_RESPONSES))
        )
        response = self.conn_read_line()
        if not response:
            raise CVSProtocolError("No response from CVS server")
        try:
            if response[0:15] != b"Valid-requests ":
                raise CVSProtocolError(
                    "Invalid response from " "CVS server: %s" % response
                )
        except IndexError:
            raise CVSProtocolError("Invalid response from CVS server: %s" % response)
        response = self.conn_read_line()
        if response != b"ok\n":
            raise CVSProtocolError("Invalid response from CVS server: %s" % response)

    def __del__(self):
        self.conn_close()

    def _parse_rlog_response(self, fp: IO[bytes]):
        rlog_output = tempfile.SpooledTemporaryFile(max_size=self.tempfile_cutoff)
        expect_error = False
        for line in fp:
            if expect_error:
                raise CVSProtocolError("CVS server error: %r" % line)
            if line == b"ok\n":
                break
            elif line[0:2] == b"M ":
                rlog_output.write(line[2:])
            elif line[0:8] == b"MT text ":
                rlog_output.write(line[8:-1])
            elif line[0:8] == b"MT date ":
                rlog_output.write(line[8:-1])
            elif line[0:10] == b"MT newline":
                rlog_output.write(line[10:])
            elif line[0:7] == b"error  ":
                expect_error = True
                continue
            else:
                raise CVSProtocolError("Bad CVS protocol response: %r" % line)
        rlog_output.seek(0)
        return rlog_output

    def fetch_rlog(self, path: bytes = b"", state=""):
        if path:
            path_arg, encoding = decode_path(path)
        else:
            path_arg, encoding = self.cvs_module_name, "utf-8"

        if len(state) > 0:
            state_arg = "Argument -s%s\n" % state
        else:
            state_arg = ""
        fp = tempfile.SpooledTemporaryFile(max_size=self.tempfile_cutoff)
        self.conn_write_str(
            "Global_option -q\n"
            f"{state_arg}"
            "Argument --\n"
            f"Argument {path_arg}\n"
            "rlog\n",
            encoding=encoding,
        )
        while True:
            response = self.conn_read_line()
            if response is None:
                raise CVSProtocolError("No response from CVS server")
            if response[0:2] == b"E ":
                if len(path) > 0 and (
                    response.endswith(b" - ignored\n")
                    or b"could not read RCS file" in response
                ):
                    response = self.conn_read_line()
                    if response not in (b"error  \n", b"ok\n"):
                        raise CVSProtocolError(
                            "Invalid response from CVS server: %s" % response
                        )
                    return None  # requested path does not exist (ignore)
                raise CVSProtocolError("Error response from CVS server: %s" % response)
            fp.write(response)
            if response == b"ok\n":
                break
        fp.seek(0)
        return self._parse_rlog_response(fp)

    def checkout(self, path: bytes, rev: str, dest_path: bytes, expand_keywords: bool):
        """
        Download a file revision from the cvs server and store
        the file's contents in a temporary file. If expand_keywords is
        set then ask the server to expand RCS keywords in file content.

        From the server's point of view this function behaves much
        like 'cvs update -r rev path'. The server is unaware that
        we do not actually maintain a CVS working copy. Because of
        this it sends more information than we need. We simply skip
        responses that are of no interest to us.
        """
        skip_line = False
        expect_modeline = False
        expect_bytecount = False
        have_bytecount = False
        bytecount = 0

        path_str, encoding = decode_path(path)

        dirname = os.path.dirname(path_str)
        if dirname:
            self.conn_write_str(
                "Directory %s\n%s\n"
                % (dirname, os.path.join(self.cvsroot_path, dirname))
            )

        if expand_keywords:
            # use server-side per-file default expansion rules
            karg = ""
        else:
            # force binary file mode
            karg = "Argument -kb\n"
        # TODO: cvs <= 1.10 servers expect to be given every Directory along the path.
        self.conn_write_str(
            "Global_option -q\n"
            "Argument -N\n"
            "Argument -P\n"
            f"Argument -r{rev}\n"
            f"{karg}"
            "Argument --\n"
            f"Argument {path_str}\n"
            "Directory .\n"
            f"{os.path.join(self.cvsroot_path, self.cvs_module_name)}\n"
            "co\n",
            encoding=encoding,
        )

        with open(dest_path, "wb") as co_output:
            while True:
                if have_bytecount:
                    if bytecount < 0:
                        raise CVSProtocolError("server sent too much file content data")
                    response = self.conn_read_line(require_newline=False)
                    if response is None:
                        raise CVSProtocolError("Incomplete response from CVS server")
                    if len(response) > bytecount:
                        # When a file lacks a final newline we receive a line which
                        # contains file content as well as CVS protocol response data.
                        # Split last line of file content from CVS protocol data...
                        co_output.write(response[:bytecount])
                        response = response[bytecount:]
                        bytecount = 0
                        # ...and process the CVS protocol response below.
                    else:
                        co_output.write(response)
                        bytecount -= len(response)
                        continue
                else:
                    response = self.conn_read_line()
                if response[0:2] == b"E ":
                    if (
                        b"Skipping `$Log$' keyword due to excessive comment leader"
                        in response
                    ):
                        # non fatal error, continue checkout operation without `$Log$'
                        # keyword expansion
                        continue
                    raise CVSProtocolError("Error from CVS server: %s" % response)
                if response == b"ok\n":
                    if have_bytecount:
                        break
                    else:
                        raise CVSProtocolError("server sent 'ok' but no file contents")
                if skip_line:
                    skip_line = False
                    continue
                elif expect_bytecount:
                    try:
                        bytecount = int(response[0:-1])  # strip trailing \n
                    except ValueError:
                        raise CVSProtocolError(
                            "Bad CVS protocol response: %s" % response
                        )
                    have_bytecount = True
                    continue
                elif response in (b"M \n", b"MT +updated\n", b"MT -updated\n"):
                    continue
                elif response[0:9] == b"MT fname ":
                    continue
                elif response.split(b" ")[0] in (
                    b"Created",
                    b"Checked-in",
                    b"Update-existing",
                    b"Updated",
                    b"Removed",
                ):
                    skip_line = True
                    continue
                elif response[0:1] == b"/":
                    expect_modeline = True
                    continue
                elif expect_modeline and response[0:2] == b"u=":
                    expect_modeline = False
                    expect_bytecount = True
                    continue
                elif response[0:2] == b"M ":
                    continue
                elif response[0:8] == b"MT text ":
                    continue
                elif response[0:10] == b"MT newline":
                    continue
                else:
                    raise CVSProtocolError("Bad CVS protocol response: %s" % response)
