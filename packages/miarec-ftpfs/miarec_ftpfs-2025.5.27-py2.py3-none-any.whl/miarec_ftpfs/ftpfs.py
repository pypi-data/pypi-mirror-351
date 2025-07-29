"""Manage filesystems on remote FTP servers.
"""

from __future__ import print_function, unicode_literals

import typing

import array
import calendar
import datetime
import io
import itertools
import socket
import ssl
from collections import OrderedDict
from contextlib import contextmanager
from ftplib import FTP

from .ftp_tls import ImplicitFTP_TLS, ExplicitFTP_TLS
from typing import cast

from ftplib import error_perm, error_temp, error_proto, error_reply
import ftplib
from six import PY2, raise_from, text_type

from . import _ftp_parse as ftp_parse
from fs import errors
from fs.base import FS
from fs.constants import DEFAULT_CHUNK_SIZE
from fs.enums import ResourceType, Seek
from fs.info import Info
from fs.iotools import line_iterator
from fs.mode import Mode
from fs.path import abspath, basename, dirname, normpath, split
from fs.time import epoch_to_datetime

if typing.TYPE_CHECKING:
    from typing import (
        Any,
        BinaryIO,
        ByteString,
        Container,
        Dict,
        Iterable,
        Iterator,
        List,
        Optional,
        SupportsInt,
        Text,
        Tuple,
        Union,
    )

    import ftplib
    import mmap

    from fs.base import _OpendirFactory
    from fs.info import RawInfo
    from fs.permissions import Permissions
    from fs.subfs import SubFS


import logging
log = logging.getLogger(__name__)


_F = typing.TypeVar("_F", bound="FTPFS")


__all__ = ["FTPFS"]

@contextmanager
def ignore_network_errors(op):
    """Ignore Socket and SSL errors"""
    try:
        yield
    except (ssl.SSLError, socket.error, ftplib.Error) as error:
        log.info(f"[{op}] Unexpected network error (ignoring): {error}")
        pass   # do nothing


@contextmanager
def convert_ftp_errors(fs, path=None, op=None, connection_error=errors.RemoteConnectionError):
    """Convert Socket and FTP protocol errors into the appropriate FSError types"""

    try:
        yield

    except ssl.SSLError as error:
        log.info('FTP SSL Socket error: %s' % error)
        raise connection_error(
            f"ftp connection SSL error (host={fs.host}:{fs.port} op={op}): {error}"
        )

    except socket.timeout as error:
        log.info('FTP Socket timeout error: %s' % error)
        raise connection_error(
            f"ftp operation timed out (host={fs.host}:{fs.port} op={op} path={path}): {error}"
        )

    except socket.error as error:
        log.info('FTP Socket error: %s' % error)
        raise connection_error(
            f"ftp connection error (host={fs.host}:{fs.port} op={op}): {error}"
        )

    except EOFError as error:     # FTP.getresp() may throw EOFError (c) MiaRec
        log.info('FTP Unexpected EOF: %s' % error)
        raise connection_error(
            f"ftp lost connection to {fs.host}:{fs.port} op={op} path={path}: {error}"
        )

    except (error_reply, error_proto) as error:   # Added by MiaRec
        log.info('FTP error: %s' % error)
        if isinstance(fs, FTPFS):
            fs._ftp = None    # clear the connection, so, it can be re-opened on next operation (c) MiaRec
        if path is not None:
            raise errors.ResourceError(
                path, msg=f"ftp error on resource '{path}' (op={op}): {error}"
            )
        else:
            raise errors.OperationFailed(msg=f"ftp error (op={op}): {error}")

    except error_temp as error:
        log.info('FTP temporary error: %s' % error)
        if path is not None:
            raise errors.ResourceError(
                path, msg=f"ftp error on resource '{path}' (op={op}): {error}"
            )
        else:
            raise errors.OperationFailed(msg=f"ftp error (op={op}): {error}")

    except error_perm as error:
        log.info('FTP permission error: %s' % error)
        code, message = _parse_ftp_error(error)
        if code == "552":
            raise errors.InsufficientStorage(path=path, msg=message)
        elif code in ("501", "550"):
            raise errors.ResourceNotFound(
                # path, msg=f"ftp resource '{path}' not found or permission error (op={op}): {error}"
                path=cast(str, path)
            )
        else:
            raise errors.PermissionDenied(path=path, msg=message)


@contextmanager
def get_ftp_connection(fs, path=None, op=None):
    # type: (FTPFS, Optional[Text], Optional[Text]) -> Iterator[FTP]
    """
    Handle FTP errors accordingly.

    In case of RemoteConnectioError, the internal network connection will be discarded,
    and on the next operation, a new connection to remote server will be attempted.
    """
    ftp = None
    try:
        with convert_ftp_errors(fs, path, op):
            with fs._lock:
                if fs._ftp is None:
                    fs._ftp = fs._open_ftp()   # this method can throw exception
                ftp = fs._ftp
            yield ftp
    except errors.RemoteConnectionError:
        with fs._lock:
            if ftp:
                with ignore_network_errors(op):
                    ftp.close()    # RemoteConnectionError could be caused by socket.timeout. Close FTP connection to avoid memory leakage
            if ftp == fs._ftp:
                fs._ftp = None   # Discard the network connection. It will be reopened  on the next operation
        raise


def _parse_ftp_error(error):
    # type: (ftplib.Error) -> Tuple[Text, Text]
    """Extract code and message from ftp error."""
    text = text_type(error)
    code = text[:3]
    if text[3:4] == '-':
        # If the error message is multiline, we take the first line
        message = text.splitlines()[0][4:]
    else:
        message = text[4:]
    return code, message


class FTPFile(io.RawIOBase):
    def __init__(self, ftpfs, path, mode):
        # type: (FTPFS, Text, Text) -> None
        super(FTPFile, self).__init__()
        self.fs = ftpfs
        self.path = path
        self.mode = Mode(mode)
        self.pos = 0
        self.ftp = self._open_ftp()
        self._read_conn = None  # type: Optional[socket.socket]
        self._write_conn = None  # type: Optional[socket.socket]
        self._closed = False

    def __del__(self):
        # Close this file and release FTP connection when the object is destroyed by garbage collector
        # Otherwise, we may have a connection leakage
        self.close()

    def _open_ftp(self, connection_error=errors.RemoteConnectionError):
        # type: () -> FTP
        """Open an ftp object for the file."""
        ftp = self.fs._open_ftp(connection_error=connection_error)
        with convert_ftp_errors(self.fs, op='open_file', path=self.path, connection_error=connection_error):
            ftp.voidcmd(str("TYPE I"))
        return ftp


    @property
    def read_conn(self):
        # type: () -> socket.socket
        if self._read_conn is None:
            with convert_ftp_errors(self.fs, op='open_read_conn', path=self.path, connection_error=IOError):
                self._read_conn = self.ftp.transfercmd(
                    "RETR " + self.path, self.pos
                )
        return self._read_conn

    @property
    def write_conn(self):
        # type: () -> socket.socket
        if self._write_conn is None:
            with convert_ftp_errors(self.fs, op='open_write_conn', path=self.path, connection_error=IOError):
                if self.mode.appending:
                    self._write_conn = self.ftp.transfercmd(
                        "APPE " + self.path
                    )
                else:
                    self._write_conn = self.ftp.transfercmd(
                        "STOR " + self.path, self.pos
                    )
        return self._write_conn

    def __repr__(self):
        # type: () -> str
        _repr = "<ftpfile {!r} {!r} {!r}>"
        return _repr.format(self.fs.ftp_url, self.path, self.mode)

    def close(self):
        # type: () -> None
        if not self.closed:
            try:
                if self._write_conn is not None:
                    # Here we silently ignore any errors during closing of the file (c) MiaRec
                    # A network connection could be already dead and any FTP commands will throw error
                    with ignore_network_errors("Unwrapping SSL write connection"):  # (c) MiaRec
                        if isinstance(self._write_conn, ssl.SSLSocket):
                            self._write_conn = self._write_conn.unwrap()

                    with ignore_network_errors("Closing write connection"):  # (c) MiaRec
                        self._write_conn.close()

                    self._write_conn = None

                    with ignore_network_errors("FTP voidresp"):  # (c) MiaRec
                        self.ftp.voidresp()  # Ensure last operation is completed

                if self._read_conn is not None:
                    with ignore_network_errors("Unwrapping SSL read connection"):  # (c) MiaRec
                        # Due to buffering in read operations, some data may be read into buffer,
                        # but not consumed by the application.
                        # Unwrap operation will throw ssl.SSLError(APPLICATION_DATA_AFTER_CLOSE_NOTIFY)
                        # if there is still some data in the reading buffer.
                        # It is safe to ignore such error
                        if isinstance(self._read_conn, ssl.SSLSocket):
                            self._read_conn = self._read_conn.unwrap()

                    with ignore_network_errors("Closing read connection"):  # (c) MiaRec
                        self._read_conn.close()
                        self._read_conn = None

                with ignore_network_errors("Closing FTP file connection"):  # (c) MiaRec
                    self.ftp.quit()

            finally:
                super(FTPFile, self).close()

    def tell(self):
        # type: () -> int
        return self.pos

    def readable(self):
        # type: () -> bool
        return self.mode.reading

    def read(self, size=-1):
        # type: (int) -> bytes
        if not self.mode.reading:
            raise IOError("File not open for reading")

        chunks = []
        remaining = size

        conn = self.read_conn
        with convert_ftp_errors(self.fs, op='read', path=self.path, connection_error=IOError):
            while remaining:
                if remaining < 0:
                    read_size = DEFAULT_CHUNK_SIZE
                else:
                    read_size = min(DEFAULT_CHUNK_SIZE, remaining)
                chunk = conn.recv(read_size)
                if not chunk:
                    break
                chunks.append(chunk)
                self.pos += len(chunk)
                remaining -= len(chunk)
        return b"".join(chunks)

    def readinto(self, buffer):
        # type: (Union[bytearray, memoryview, array.array[Any], mmap.mmap]) -> int
        data = self.read(len(buffer))
        bytes_read = len(data)
        if isinstance(buffer, array.array):
            buffer[:bytes_read] = array.array(buffer.typecode, data)
        else:
            buffer[:bytes_read] = data  # type: ignore
        return bytes_read

    def readline(self, size=None):
        # type: (Optional[int]) -> bytes
        return next(line_iterator(self, size))  # type: ignore

    def readlines(self, hint=-1):
        # type: (int) -> List[bytes]
        lines = []
        size = 0
        for line in line_iterator(self):  # type: ignore
            lines.append(line)
            size += len(line)
            if hint != -1 and size > hint:
                break
        return lines

    def writable(self):
        # type: () -> bool
        return self.mode.writing

    def write(self, data):
        # type: (Union[bytes, memoryview, array.array[Any], mmap.mmap]) -> int
        if not self.mode.writing:
            raise IOError("File not open for writing")

        if isinstance(data, array.array):
            data = data.tobytes()

        with convert_ftp_errors(self.fs, op='write', path=self.path, connection_error=IOError):
            conn = self.write_conn
            data_pos = 0
            remaining_data = len(data)

            while remaining_data:
                chunk_size = min(remaining_data, DEFAULT_CHUNK_SIZE)
                sent_size = conn.send(data[data_pos : data_pos + chunk_size])
                data_pos += sent_size
                remaining_data -= sent_size
                self.pos += sent_size

        return data_pos

    def writelines(self, lines):
        # type: (Iterable[Union[bytes, memoryview, array.array[Any], mmap.mmap]]) -> None  # noqa: E501
        if not self.mode.writing:
            raise IOError("File not open for writing")
        data = bytearray()
        for line in lines:
            if isinstance(line, array.array):
                data.extend(line.tobytes())
            else:
                data.extend(line)  # type: ignore
        self.write(data)

    def truncate(self, size=None):
        # type: (Optional[int]) -> int
        # Inefficient, but I don't know if truncate is possible with ftp
        # TODO: this strange implementation of "truncate" must be clearly documented 
        # as we are reading the original file into memory and then pushing it back.
        # If file is huge, we can hit Out-of-memory issue
        # (c) MiaRec
        if size is None:
            size = self.tell()
        with self.fs.openbin(self.path) as f:
            data = f.read(size)
        with self.fs.openbin(self.path, "w") as f:
            f.write(data)
            if len(data) < size:
                f.write(b"\0" * (size - len(data)))
        return size

    def seekable(self):
        # type: () -> bool
        return True

    def seek(self, pos, whence=Seek.set):
        # type: (int, SupportsInt) -> int
        _whence = int(whence)
        if _whence not in (Seek.set, Seek.current, Seek.end):
            raise ValueError("invalid value for whence")
        if _whence == Seek.set:
            new_pos = pos
        elif _whence == Seek.current:
            new_pos = self.pos + pos
        elif _whence == Seek.end:
            file_size = self.fs.getsize(self.path)
            new_pos = file_size + pos

        new_pos = max(0, new_pos)
        if new_pos == self.pos:
            return self.pos   # no changes in position, do nothing

        # We need to re-open write_conn/read_conn to move the file seek position.
        # When they are re-opened, RESTART (REST) FTP command is sent with a file position
        self.pos = new_pos

        # Make sure we flush all pending write data before closing the connection (c) MiaRec
        if self._write_conn is not None:
            with ignore_network_errors("Unwrapping SSL write connection"):  # (c) MiaRec
                if isinstance(self._write_conn, ssl.SSLSocket):
                    self._write_conn = self._write_conn.unwrap()
            with ignore_network_errors("Closing write connection"):  # (c) MiaRec
                self._write_conn.close()
            self._write_conn = None

            with ignore_network_errors("FTP voidresp"):  # (c) MiaRec
                self.ftp.voidresp()  # Ensure last write completed

        if self._read_conn is not None:
            with ignore_network_errors("Unwrapping SSL read connection"):  # (c) MiaRec
                if isinstance(self._read_conn, ssl.SSLSocket):
                    self._read_conn = self._read_conn.unwrap()
            with ignore_network_errors("Closing read connection"):  # (c) MiaRec
                self._read_conn.close()
            self._read_conn = None

        with ignore_network_errors("Closing FTP file connection"):  # (c) MiaRec
            self.ftp.quit()
        self.ftp = self._open_ftp()

        return self.tell()


class FTPFS(FS):
    """A FTP (File Transport Protocol) Filesystem.

    Optionally, the connection can be made securely via TLS. This is known as
    FTPS, or FTP Secure. TLS will be enabled when using the ftps:// protocol,
    or when setting the `tls` argument to True in the constructor.

    Examples:
        Create with the constructor::

            >>> from fs.ftpfs import FTPFS
            >>> ftp_fs = FTPFS("demo.wftpserver.com")

        Or via an FS URL::

            >>> ftp_fs = fs.open_fs('mftp://test.rebex.net')

        Or via an FS URL, using TLS::

            >>> ftp_fs = fs.open_fs('mftps://demo.wftpserver.com')

        You can also use a non-anonymous username, and optionally a
        password, even within a FS URL::

            >>> ftp_fs = FTPFS("test.rebex.net", user="demo", passwd="password")
            >>> ftp_fs = fs.open_fs('mftp://demo:password@test.rebex.net')

        Connecting via a proxy is supported. If using a FS URL, the proxy
        URL will need to be added as a URL parameter::

            >>> ftp_fs = FTPFS("ftp.ebi.ac.uk", proxy="test.rebex.net")
            >>> ftp_fs = fs.open_fs('mftp://ftp.ebi.ac.uk/?proxy=test.rebex.net')

    """

    _meta = {
        "invalid_path_chars": "\0",
        "network": True,
        "read_only": False,
        "thread_safe": True,
        "unicode_paths": True,
        "virtual": False,
    }

    def __init__(
        self,
        host,  # type: Text
        user="anonymous",  # type: Text
        passwd="",  # type: Text
        acct="",  # type: Text
        timeout=10,  # type: int
        port=21,  # type: int
        proxy=None,  # type: Optional[Text]
        tls=False,  # type: bool
        implicit_tls=False, # type: bool
        reuse_ssl_session=True,  # type: bool
    ):
        # type: (...) -> None
        """Create a new `FTPFS` instance.

        Arguments:
            host (str): A FTP host, e.g. ``'ftp.mirror.nl'``.
            user (str): A username (default is ``'anonymous'``).
            passwd (str): Password for the server, or `None` for anon.
            acct (str): FTP account.
            timeout (int): Timeout for contacting server (in seconds,
                defaults to 10).
            port (int): FTP port number (default 21).
            proxy (str, optional): An FTP proxy, or ``None`` (default)
                for no proxy.
            tls (bool): Attempt to use FTP over TLS (FTPS) (default: False)
            implicit_tls (bool): Use Implicit TLS (default: False)
            reuse_ssl_session (bool): Reuse SSL session between control and data channels (default: True)

        """
        super(FTPFS, self).__init__()
        self._host = host
        self._user = user
        self.passwd = passwd
        self.acct = acct
        self.timeout = timeout
        self.port = port
        self.proxy = proxy
        self.tls = tls
        self.implicit_tls = implicit_tls

        # Support TLS session resumpion
        # See https://stackoverflow.com/questions/14659154/ftpes-session-reuse-required
        self.reuse_ssl_session = reuse_ssl_session

        self.encoding = "latin-1"
        self._ftp = None  # type: Optional[FTP]
        self._welcome = None  # type: Optional[Text]
        self._features = {}  # type: Dict[Text, Text]

    def __repr__(self):
        # type: (...) -> Text
        return "FTPFS({!r}, port={!r})".format(self.host, self.port)

    def __str__(self):
        # type: (...) -> Text
        _fmt = "<ftpfs '{host}'>" if self.port == 21 else "<ftpfs '{host}:{port}'>"
        return _fmt.format(host=self.host, port=self.port)

    @property
    def user(self):
        # type: () -> Text
        return (
            self._user if self.proxy is None else "{}@{}".format(self._user, self._host)
        )

    @property
    def host(self):
        # type: () -> Text
        return self._host if self.proxy is None else self.proxy

    @classmethod
    def _parse_features(cls, feat_response):
        # type: (Text) -> Dict[Text, Text]
        """Parse a dict of features from FTP feat response."""
        features = {}
        if feat_response.split("-")[0] == "211":
            for line in feat_response.splitlines():
                if line.startswith(" "):
                    key, _, value = line[1:].partition(" ")
                    features[key] = value
        return features

    def _open_ftp(self, connection_error=errors.RemoteConnectionError):
        # type: () -> FTP
        """Open a new ftp object."""
        if self.tls or self.implicit_tls:
            _ftp = (
                ImplicitFTP_TLS(reuse_ssl_session=self.reuse_ssl_session) 
                if self.implicit_tls else 
                ExplicitFTP_TLS(reuse_ssl_session=self.reuse_ssl_session)
            )
        else:
            _ftp = FTP()

        _ftp.set_debuglevel(0)
        with convert_ftp_errors(self, op="open_ftp", connection_error=connection_error):
            _ftp.connect(self.host, self.port, self.timeout)
            _ftp.login(self.user, self.passwd, self.acct)
            try:
                _ftp.prot_p()  # type: ignore
            except AttributeError:
                pass
            self._features = {}
            try:
                feat_response = _ftp.sendcmd("FEAT")
            except error_perm:  # pragma: no cover
                self.encoding = "latin-1"
            else:
                self._features = self._parse_features(feat_response)
                self.encoding = "utf-8" if "UTF8" in self._features else "latin-1"
                if not PY2:
                    _ftp.file = _ftp.sock.makefile(  # type: ignore
                        "r", encoding=self.encoding
                    )
        _ftp.encoding = self.encoding
        self._welcome = _ftp.welcome
        return _ftp

    def _close_ftp(self):
        if self._ftp is not None:
            self._ftp.quit()
            self._ftp = None

    @property
    def ftp_url(self):
        # type: () -> Text
        """Get the FTP url this filesystem will open."""
        if self.port == 21:
            _host_part = self.host
        else:
            _host_part = "{}:{}".format(self.host, self.port)

        if self.user == "anonymous" or self.user is None:
            _user_part = ""
        else:
            _user_part = "{}:{}@".format(self.user, self.passwd)

        scheme = "mftps" if self.tls else "mftp"
        url = "{}://{}{}".format(scheme, _user_part, _host_part)
        return url

    def geturl(self, path, purpose="download"):
        # type: (str, str) -> Text
        """Get FTP url for resource."""
        _path = self.validatepath(path)
        if purpose != "download":
            raise errors.NoURL(_path, purpose)
        url_params = '?implicit_tls=True' if self.implicit_tls else ''
        return "{}{}{}".format(self.ftp_url, _path, url_params)

    @property
    def features(self):  # noqa: D401
        # type: () -> Dict[Text, Text]
        """`dict`: Features of the remote FTP server."""
        with get_ftp_connection(self, op='get_features'):
            return self._features

    def _read_dir(self, path):
        # type: (Text) -> Dict[Text, Info]
        _path = abspath(normpath(path))
        lines = []  # type: List[Union[ByteString, Text]]
        with get_ftp_connection(self, path=path, op='LIST') as ftp:
            ftp.retrlines(
                "LIST " + _path, lines.append
            )
        lines = [
            line.decode("utf-8") if isinstance(line, bytes) else line for line in lines
        ]
        _list = [Info(raw_info) for raw_info in ftp_parse.parse(lines)]
        dir_listing = OrderedDict({info.name: info for info in _list})
        return dir_listing

    @property
    def supports_mlst(self):
        # type: () -> bool
        """bool: whether the server supports MLST feature."""
        return "MLST" in self.features

    @property
    def supports_mdtm(self):
        # type: () -> bool
        """bool: whether the server supports the MDTM feature."""
        return "MDTM" in self.features

    def create(self, path, wipe=False):
        # type: (Text, bool) -> bool
        _path = self.validatepath(path)
        with get_ftp_connection(self, path, op='STOR') as ftp:
            if wipe or not self.isfile(path):
                empty_file = io.BytesIO()
                ftp.storbinary(
                    "STOR " + _path, empty_file
                )
                return True
        return False

    @classmethod
    def _parse_ftp_time(cls, time_text):
        # type: (Text) -> Optional[int]
        """Parse a time from an ftp directory listing."""
        try:
            tm_year = int(time_text[0:4])
            tm_month = int(time_text[4:6])
            tm_day = int(time_text[6:8])
            tm_hour = int(time_text[8:10])
            tm_min = int(time_text[10:12])
            tm_sec = int(time_text[12:14])
        except ValueError:
            return None
        epoch_time = calendar.timegm(
            (tm_year, tm_month, tm_day, tm_hour, tm_min, tm_sec)
        )
        return epoch_time

    @classmethod
    def _parse_facts(cls, line):
        # type: (Text) -> Tuple[Optional[Text], Dict[Text, Text]]
        name = None
        facts = {}
        for fact in line.split(";"):
            key, sep, value = fact.partition("=")
            if sep:
                key = key.strip().lower()
                value = value.strip()
                facts[key] = value
            else:
                name = basename(fact.rstrip("/").strip())
        return name if name not in (".", "..") else None, facts

    @classmethod
    def _parse_mlsx(cls, lines):
        # type: (Iterable[Text]) -> Iterator[RawInfo]
        for line in lines:
            name, facts = cls._parse_facts(line.strip())
            if name is None:
                continue
            _type = facts.get("type", "file")
            if _type not in {"dir", "file"}:
                continue
            is_dir = _type == "dir"
            raw_info = {}  # type: Dict[Text, Dict[Text, object]]

            raw_info["basic"] = {"name": name, "is_dir": is_dir}
            raw_info["ftp"] = facts  # type: ignore
            raw_info["details"] = {
                "type": (int(ResourceType.directory if is_dir else ResourceType.file))
            }

            details = raw_info["details"]
            size_str = facts.get("size", facts.get("sizd", "0"))
            size = 0
            if size_str.isdigit():
                size = int(size_str)
            details["size"] = size
            if "modify" in facts:
                details["modified"] = cls._parse_ftp_time(facts["modify"])
            if "create" in facts:
                details["created"] = cls._parse_ftp_time(facts["create"])
            yield raw_info

    if typing.TYPE_CHECKING:

        def opendir(self, path, factory=None):
            # type: (_F, Text, Optional[_OpendirFactory]) -> SubFS[_F]
            pass

    def getinfo(self, path, namespaces=None):
        # type: (Text, Optional[Container[Text]]) -> Info
        _path = self.validatepath(path)
        namespaces = namespaces or ()

        if _path == "/":
            return Info(
                {
                    "basic": {"name": "", "is_dir": True},
                    "details": {"type": int(ResourceType.directory)},
                }
            )

        if self.supports_mlst:
            with get_ftp_connection(self, path=path, op="MLST") as ftp:
                response = ftp.sendcmd(
                    "MLST " + _path
                )
            lines = response.splitlines()[1:-1]
            for raw_info in self._parse_mlsx(lines):
                return Info(raw_info)

        dir_name, file_name = split(_path)
        directory = self._read_dir(dir_name)
        if file_name not in directory:
            raise errors.ResourceNotFound(path)
        info = directory[file_name]
        return info

    def getmeta(self, namespace="standard"):
        # type: (Text) -> Dict[Text, object]
        _meta = {}  # type: Dict[Text, object]
        with get_ftp_connection(self, op='getmeta') as ftp:
            if namespace == "standard":
                _meta = self._meta.copy()
                _meta["unicode_paths"] = "UTF8" in self.features
                _meta["supports_mtime"] = "MDTM" in self.features
        return _meta

    def getmodified(self, path):
        # type: (Text) -> Optional[datetime.datetime]
        if self.supports_mdtm:
            _path = self.validatepath(path)
            with get_ftp_connection(self, path=path, op="MDTM") as ftp:
                cmd = "MDTM " + _path
                response = ftp.sendcmd(cmd)
                mtime = self._parse_ftp_time(response.split()[1])
                return epoch_to_datetime(mtime)
        return super(FTPFS, self).getmodified(path)

    def listdir(self, path):
        # type: (Text) -> List[Text]
        _path = self.validatepath(path)
        with self._lock:
            dir_list = [info.name for info in self.scandir(_path)]
        return dir_list

    def makedir(
        self,  # type: _F
        path,  # type: Text
        permissions=None,  # type: Optional[Permissions]
        recreate=False,  # type: bool
    ):
        # type: (...) -> SubFS[_F]
        _path = self.validatepath(path)

        with get_ftp_connection(self, path=path, op="MKD") as ftp:
            if _path == "/":
                if recreate:
                    return self.opendir(path)
                else:
                    raise errors.DirectoryExists(path)

            if not (recreate and self.isdir(path)):
                try:
                    ftp.mkd(_path)
                except error_perm as error:
                    code, _ = _parse_ftp_error(error)
                    if code == "550":
                        if self.isdir(path):
                            raise errors.DirectoryExists(path)
                        else:
                            if self.exists(path):
                                raise errors.DirectoryExists(path)
                    raise errors.ResourceNotFound(path)
        return self.opendir(path)

    def openbin(self, path, mode="r", buffering=-1, **options):
        # type: (Text, Text, int, **Any) -> BinaryIO
        _mode = Mode(mode)
        _mode.validate_bin()
        _path = self.validatepath(path)

        with self._lock:
            try:
                info = self.getinfo(_path)
            except errors.ResourceNotFound:
                if _mode.reading:
                    raise errors.ResourceNotFound(path)
                if _mode.writing and not self.isdir(dirname(_path)):
                    raise errors.ResourceNotFound(path)
            else:
                if info.is_dir:
                    raise errors.FileExpected(path)
                if _mode.exclusive:
                    raise errors.FileExists(path)
            ftp_file = FTPFile(self, _path, _mode.to_platform_bin())
        return ftp_file  # type: ignore

    def remove(self, path):
        # type: (Text) -> None
        self.check()
        _path = self.validatepath(path)
        with self._lock:
            if self.isdir(path):
                raise errors.FileExpected(path=path)
            with get_ftp_connection(self, path, op="DELE") as ftp:
                ftp.delete(_path)

    def removedir(self, path):
        # type: (Text) -> None
        _path = self.validatepath(path)
        if _path == "/":
            raise errors.RemoveRootError()

        with get_ftp_connection(self, path, op="RMD") as ftp:
            try:
                ftp.rmd(_path)
            except error_perm as error:
                code, _ = _parse_ftp_error(error)
                if code == "550":
                    if self.isfile(path):
                        raise errors.DirectoryExpected(path)
                    if not self.isempty(path):
                        raise errors.DirectoryNotEmpty(path)
                raise  # pragma: no cover

    def _scandir(self, path, namespaces=None):
        # type: (Text, Optional[Container[Text]]) -> Iterator[Info]
        _path = self.validatepath(path)
        with self._lock:
            if self.supports_mlst:
                lines = []
                with get_ftp_connection(self, path=path, op="MLSD") as ftp:
                    try:
                        ftp.retrlines(
                            "MLSD " + _path,
                            lambda l: lines.append(l),
                        )
                    except error_perm:
                        if not self.getinfo(path).is_dir:
                            raise errors.DirectoryExpected(path)
                        raise  # pragma: no cover
                if lines:
                    for raw_info in self._parse_mlsx(lines):
                        yield Info(raw_info)
                    return
            for info in self._read_dir(_path).values():
                yield info

    def scandir(
        self,
        path,  # type: Text
        namespaces=None,  # type: Optional[Container[Text]]
        page=None,  # type: Optional[Tuple[int, int]]
    ):
        # type: (...) -> Iterator[Info]
        if not self.supports_mlst and not self.getinfo(path).is_dir:
            raise errors.DirectoryExpected(path)
        iter_info = self._scandir(path, namespaces=namespaces)
        if page is not None:
            start, end = page
            iter_info = itertools.islice(iter_info, start, end)
        return iter_info

    def upload(self, path, file, chunk_size=None, **options):
        # type: (Text, BinaryIO, Optional[int], **Any) -> None
        _path = self.validatepath(path)
        with get_ftp_connection(self, path, op="STOR") as ftp:
            ftp.storbinary(
                "STOR " + _path, file
            )

    def writebytes(self, path, contents):
        # type: (Text, ByteString) -> None
        if not isinstance(contents, bytes):
            raise TypeError("contents must be bytes")
        self.upload(path, io.BytesIO(contents))

    def setinfo(self, path, info):
        # type: (Text, RawInfo) -> None
        use_mfmt = False
        if "MFMT" in self.features:
            info_details = None
            if "modified" in info:
                info_details = info["modified"]
            elif "details" in info:
                info_details = info["details"]
            if info_details and "modified" in info_details:
                use_mfmt = True
                mtime = cast(float, info_details["modified"])

        if use_mfmt:
            with get_ftp_connection(self, path, "MFMT") as ftp:
                cmd = (
                    "MFMT "
                    + datetime.datetime.utcfromtimestamp(mtime).strftime("%Y%m%d%H%M%S")
                    + " "
                    + path
                )
                try:
                    ftp.sendcmd(cmd)
                except error_perm:
                    pass
        else:
            if not self.exists(path):
                raise errors.ResourceNotFound(path)

    def readbytes(self, path):
        # type: (Text) -> bytes
        _path = self.validatepath(path)
        data = io.BytesIO()
        with get_ftp_connection(self, path, op="RETR") as ftp:
            try:
                ftp.retrbinary(
                    "RETR " + _path, data.write
                )
            except error_perm as error:
                code, _ = _parse_ftp_error(error)
                if code == "550":
                    if self.isdir(path):
                        raise errors.FileExpected(path)
                raise

        data_bytes = data.getvalue()
        return data_bytes

    def move(self, src_path, dst_path, overwrite=False, preserve_time=False):
        """Move a file from ``src_path`` to ``dst_path``.

        Arguments:
            src_path (str): A path on the filesystem to move.
            dst_path (str): A path on the filesystem where the source
                file will be written to.
            overwrite (bool): If `True`, destination path will be
                overwritten if it exists.

        Raises:
            fs.errors.FileExpected: If ``src_path`` maps to a
                directory instead of a file.
            fs.errors.DestinationExists: If ``dst_path`` exists,
                and ``overwrite`` is `False`.
            fs.errors.ResourceNotFound: If a parent directory of
                ``dst_path`` does not exist.

        """
        if not overwrite and self.exists(dst_path):
            raise errors.DestinationExists(dst_path)
        if self.getinfo(src_path).is_dir:
            raise errors.FileExpected(src_path)

        with get_ftp_connection(self, src_path, op='rename {} -> {}'.format(src_path, dst_path)) as ftp:
            try:
                ftp.rename(src_path, dst_path)
            except error_perm:
                if overwrite or not self.exists(dst_path):
                    # Fallback to copy/delete
                    with self.openbin(src_path) as read_file:
                        self.upload(dst_path, read_file)
                    self.remove(src_path)
                else:
                    raise

    def close(self):
        # type: () -> None
        if not self.isclosed():
            try:
                self._close_ftp()
            except Exception:  # pragma: no cover
                pass
        super(FTPFS, self).close()
