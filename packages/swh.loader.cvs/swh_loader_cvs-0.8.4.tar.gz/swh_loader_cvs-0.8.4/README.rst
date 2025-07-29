Software Heritage - CVS loader
==============================

The Software Heritage CVS Loader imports the history of CVS repositories
into the SWH dataset.

The main entry points is:

-  ``swh.loader.cvs.loader.CvsLoader`` for the main cvs loader
   which ingests content out of a local cvs repository


Features
--------

The CVS loader can access CVS repositories via rsync or via the CVS
pserver protocol, with optional support for tunnelling pserver via SSH.

The CVS loader does *not* require the cvs program to be installed.
However, the loader's test suite does require cvs to be installed.

Access via rsync requires the rsync program to be installed. The CVS
loader will then invoke rsync to obtain a temporary local copy of the
entire CVS repository. It will then walk the local copy the CVS
repository and parse history of each RCS file with a built-in RCS
parser. This will usually be the fastest method for importing a given
CVS repository. However, most CVS servers do not offer repository access
via rsync, and CVS repositories which see active commits may see
conversion problems because the CVS repository format was not designed
for lock-less read access.

Access via the plaintext CVS pserver protocol requires no external
dependencies to be installed, and is compatible with regular CVS
servers. This method will use read-locks on the server side and should
therefore be safe to use with active CVS repositories. The CVS loader
will use a built-in minimal CVS client written in Python to fetch the
output of the cvs rlog command executed on the CVS server. This output
will be processed to obtain repository history information. All versions
of all files will then be fetched from the server and injected into the
SWH archive.

Access via pserver over SSH requires OpenSSH to be installed. Apart from
using SSH as a transport layer the conversion process is the same as in
the plaintext pserver case. The SSH client will be instructed to trust
SSH host key fingeprints upon first use. If a CVS server changes its SSH
fingerprint then manual intervention may be required in order for future
visits to be successful.

Regardless of access protocol, the CVS loader uses heuristics to convert
the per-file history stored in CVS into changesets. These changesets
correspond to snapshots in the SWH database model. A given CVS
repository should always yield a consistent series of changesets across
multiple visits.

The following URL protocol schemes are recognized by the loader:

-  rsync://
-  pserver://
-  ssh://

After the protocol scheme, the CVS server hostname must be specified,
with an optional user:password field delimited from the hostname with
the ‘@’ character::

   pserver://anonymous:password@cvs.example.com/

After the hostname, the server-side CVS root path must be specified. The
path will usually contain a CVSROOT directory on the server, though this
directory may be hidden from clients::

   pserver://anonymous:password@cvs.example.com/var/cvs/

The final component of the URL identifies the name of the CVS module
which should be ingested into the SWH archive::

   pserver://anonymous:password@cvs.example.com/var/cvs/project1

As a concrete example, this URL points to the historical CVS repository
of the a2ps project. In this case, the cvsroot path is /sources/a2ps and
the CVS module of the project is called a2ps::

   pserver://anonymous:anonymous@cvs.savannah.gnu.org/sources/a2ps/a2ps

In order to obtain the history of this repository the CVS loader will
perform the CVS pserver protocol exchange which is also performed by::

   cvs -d :pserver:anonymous@cvs.savannah.gnu.org/sources/a2ps rlog a2ps

Known Limitations
-----------------

CVS repositories which see active commits should be converted with care.
It is possible to end up with a partial conversion of the latest commit
if repository data is fetched via rsync while a commit is in progress.
The pserver protocol is the safer option in such cases.

Only history of main CVS branch is converted. CVS vendor branch imports
and merges which modify the main branch are modeled as two distinct
commits to the main branch. Other branches will not be represented in
the conversion result at all.

CVS labels are not converted into corresponding SWH tags/releases yet.

The converter does not yet support incremental fetching of CVS history.
The entire history will be fetched and processed during every visit. By
design, CVS does not fully support a concept of changesets that span
multiple files and, as such, importing an evolving CVS history
incrementally is a not a trivial problem. Regardless, some improvements
could be made relatively easily, as noted below.

CVS repositories copied with rsync could be cached locally, such that
rsync will only download RCS files which have changed since the last
visit. At present the local copy of the repository is fetched to a
temporary directory and is deleted once the conversion process is done.

It might help to store persistent meta-data about blobs imported from
CVS. If such meta-data could be searched via a given CVS repository
name, a path, and an RCS revision number then redundant downloads of
file versions over the pserver protocol could be detected and skipped.

The minimal CVS client does not yet support the optional gzip extension
offered by the CVS pserver protocol. If this was supported then files
downloaded from a CVS server could be compressed while in transit.

The built-in minimal CVS client has not been tested against many
versions of CVS. It should work fine against CVS 1.11 and 1.12 servers.
More work may be needed to improve compatibility with older versions of
CVS.

Acknowledgements
----------------

This software contains code derived from *cvs2gitdump* written by
YASUOKA Masahiko, and from the *rcsparse* library written by Simon
Schubert.

This software contains code derived from ViewVC: https://www.viewvc.org/

Licensing information
---------------------

Parts of the software written by SWH developers are licensed under
GPLv3. See the file LICENSE

cvs2gitdump by YASUOKA Masahiko is licensed under ISC. See the top of
the file swh/loader/cvs/cvs2gitdump/cvs2gitdump.py

rcsparse by Simon Schubert is licensed under AGPLv3. See the file
swh/loader/cvs/rcsparse/COPYRIGHT

ViewVC is licensed under the 2-clause BSD licence. See the file
swh/loader/cvs/rlog.py

Running Tests
=============

The loader's test suite requires cvs to be installed.

Because the rcsparse library is implemented in C and accessed via Python
bindings, the CVS loader must be compiled and installed before tests can
be run and the *build* directory must be passed as an argument to
pytest::

   $ ./setup.py build install
   $ pytest ./build

The test suite uses internal protocol schemes which cannot be reached
from "Save Code Now". These are:

 - fake://
 - file://

The fake:// scheme corresponds to pserver:// and ssh://. The test suite
will spawn a 'cvs server' process locally and the loader will connect
to this server via a pipe and communicate using the pserver protocol.
Real ssh:// access lacks test coverage at present and would require
sshd to become part of the test setup.

The file:// scheme corresponds to rsync:// and behaves as if the rsync
program had already created a local copy of the repository. Real rsync://
access lacks test coverage at present and would require an rsyncd server
to become part of the test setup.

CLI run
=======

With the configuration:

/tmp/loader_cvs.yml::

   storage:
     cls: remote
     args:
       url: http://localhost:5002/

Run::

   swh loader --config-file /tmp/loader_cvs.yml \
       run cvs <cvs-url>
