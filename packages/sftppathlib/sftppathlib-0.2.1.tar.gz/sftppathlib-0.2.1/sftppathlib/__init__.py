import logging
import posixpath
from paramiko import sftp, sftp_attr
from pathlib import PurePath, Path
from pathlib_abc import PathBase
from stat import S_ISDIR, S_ISREG

__version__ = "0.2.1"
logger = logging.getLogger(__name__)


_CACHED_CLIENT = None


def _load_client():
    global _CACHED_CLIENT

    if _CACHED_CLIENT is None:
        import configparser
        import paramiko

        def get_app_directory():
            # https://stackoverflow.com/questions/19078969/python-getting-appdata-folder-in-a-cross-platform-way
            import sys

            home = Path.home()

            if sys.platform == "win32":
                return home / "AppData/Roaming"
            elif sys.platform == "linux":
                return home / ".local/share"
            elif sys.platform == "darwin":
                return home / "Library/Application Support"
            else:
                raise OSError(f"Unsupported system '{sys.platform}'.")

        def load_config(config_path):
            # Ugly way to read simple yaml files using the standard library
            reader = configparser.ConfigParser()
            content = Path(config_path).expanduser().read_text(encoding="UTF-8")
            if not content.startswith("["):
                content = "\n".join(("[config]", content))
            reader.read_string(content)

            return dict(reader["config"])

        def load_client(config):
            ssh_client = paramiko.SSHClient()
            if "key" not in config:
                # Uses the file ~/.ssh/known_hosts
                ssh_client.load_system_host_keys()
            ssh_client.connect(**config)
            sftp_client = paramiko.sftp_client.SFTPClient.from_transport(
                ssh_client.get_transport())

            # Monkey patch the close() method.
            # This is simpler than making a new SSHSFTPClient class.
            _close = sftp_client.close
            def close(*args, **kwargs):
                sftp_client.close()
                ssh_client.close()
            sftp_client.close = close

            return sftp_client

        config_path = get_app_directory() / "sftppathlib" / "config.yaml"
        config = load_config(config_path)
        _CACHED_CLIENT = load_client(config)

    return _CACHED_CLIENT


class SFTPPath(PathBase):  #(PurePath): fails in older versions due to __new__
    """Partially copies the interface of pathlib.Path"""
    # Preferably we'd like to subclass Path, but we have to make sure not to
    # call Path's methods; we have to re-implement all its methods.
    # Update: pathlib_abc.PathBase resolves this issue

    __slots__ = ("_accessor")
    pathmod = posixpath

    # Everywhere with self.as_posix() should be removed once paramiko supports
    # the Path interface. Then we can pass self.

    def __init__(self, path, *paths, accessor=None):
        # Reference to the sftp handler is necessary; in pathlib this is
        # equivalent to a reference to the os module; but this module is
        # assumed to be a singleton since it's unexpected for the os to
        # change when running a Python script. In comparison an sftppath
        # can refer to different servers.

        # In pathlib _accessor is a union of io and os. open() uses the io
        # module, while mkdir() and touch() uses os.
        # self._path = path
        self._accessor = accessor if accessor is not None else _load_client()
        super().__init__(path, *paths)

    def with_segments(self, *pathsegments):
        # Need to overload this one since it's used to construct new classes
        # and we need to pass down the accessor object.
        return type(self)(*pathsegments, accessor=self._accessor)

    def stat(self, *, follow_symlinks=True) -> sftp_attr.SFTPAttributes:
        logger.warning("Argument 'follow_symlinks' ignored.")
        return self._accessor.stat(self.as_posix())

    def open(self, mode="rb", buffering=-1, encoding=None,
             errors=None, newline=None):
        return FileHandler(
            self._accessor.open(self.as_posix(), mode=mode, bufsize=buffering),
            encoding, errors, newline)

    def iterdir(self):
        for path in self._accessor.listdir(self.as_posix()):
            yield type(self)(self._raw_path, path, accessor=self._accessor)

    def absolute(self):
        path = self.pathmod.normcase(self._raw_path)
        if not self.pathmod.isabs(path):
            # It's not possible to change directory (chdir) with the Path API
            # so getcwd() should always be None, and cwd will be "/".
            cwd = self._accessor.getcwd()
            if cwd is None:
                cwd = "/"
            path = self.pathmod.join(cwd, path)
        return posixpath.normpath(path)

    # Unsupported
    # def expanduser(): pass

    # Unsupported
    # def readlink(): pass

    def symlink_to(self, target, target_is_directory=None):
        logger.warning("Argument 'target_is_directory' ignored.")
        self.symlink_to(target, self.as_posix())

    # Unsupported
    # def hardlink_to(): pass

    def touch(self, mode=0o666, exist_ok=True):
        # Apparently there's no such thing as touch, only open
        # Note that exist_ok is True for touch, but False for mkdir

        flags = sftp.SFTP_FLAG_CREATE | sftp.SFTP_FLAG_WRITE
        if not exist_ok:
            flags |= sftp.SFTP_FLAG_EXCL

        attrblock = sftp_attr.SFTPAttributes()
        t, msg = self._accessor._request(
            sftp.CMD_OPEN, self.as_posix(), flags, attrblock)

        if t != sftp.CMD_HANDLE:
            raise sftp.SFTPError("Expected handle")

        handle = msg.get_binary()

        try:
            self._accessor._request(sftp.CMD_CLOSE, handle)
        except Exception as e:
            pass

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        try:
            self._accessor.mkdir(self.as_posix(), mode)
        except FileNotFoundError:
            if not parents or self.parent == self:
                raise
            self.parent.mkdir(parents=True, exist_ok=True)
            self.mkdir(self.as_posix(), mode, parent=False, exist_ok=exist_ok)
        except OSError:
            if not exist_ok or not self.is_dir():
                raise

    def rename(self, target):
        self._accessor.rename(
            self.as_posix(),
            str(target),
        )

    # Unsupported
    # def replace(): pass

    def chmod(self, mode, *, follow_symlinks=None):
        logger.warning("Argument 'follow_symlinks' ignored.")
        self._accessor.chmod(self.as_posix(), mode)

    def unlink(self):
        self._accessor.remove(self.as_posix())

    def rmdir(self):
        self._accessor.rmdir(self.as_posix())

    # Unsupported
    # def owner(): pass

    # Unsupported
    # def group(): pass

    # Unsupported
    # def from_uri(): pass

    # Unsupported
    # def as_uri(): pass

    def __repr__(self):
        return f"{type(self).__name__}('{self.as_posix()}')"

    # Required for PathLike objects
    def __fspath__(self):
        return str(self)

    # Python 3.14
    # def copy(): pass
    # def copy_into(): pass
    # def move(self): raise NotImplementedError
    # def move_into(self): raise NotImplementedError


PathBase.register(SFTPPath)


# Overload paramiko.sftp_file.SFTPFile?
# That is tricky because the constructor is paramiko.sftp_client.SFTPClient.open
# Instead we put it in a simple wrapper to handle encoding.
class FileHandler:
    def __init__(self, file_handler, encoding, errors, newline):
        self.file_handler = file_handler
        self.encoding = encoding
        self.errors = errors
        self.newline = newline

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.close()

    @property
    def prefetch(self):
        return self.file_handler.prefetch

    @property
    def _is_binary(self):
        return self.file_handler._flags & self.file_handler.FLAG_BINARY

    def close(self):
        self.file_handler.close()

    def read(self, size=None):
        # SFTPFile ignores binary/text flag, so we have to check it ourself
        text = self.file_handler.read(size)

        if not self._is_binary:
            text = text.decode(self.encoding)

        return text

    def write(self, text):
        if not self._is_binary:
            text = text.encode(self.encoding)

        self.file_handler.write(text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
