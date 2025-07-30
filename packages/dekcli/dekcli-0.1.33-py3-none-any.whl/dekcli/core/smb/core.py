import os
import stat
import smbclient
from smbprotocol.exceptions import SMBOSError


class SmbClient:
    def __init__(self, server, share, username=None, password=None, domain=None):
        self.server = server
        self.domain = domain or server
        self.share = share  # shared root folder name
        self.username = username
        self.password = password

    def connect(self):
        smbclient.register_session(self.server, username=self.username, password=self.password)

    def path(self, path):
        return rf'\\{self.domain}\{self.share}{path}'

    def listdir(self, path=''):
        return smbclient.listdir(self.path(path))

    def stat(self, path):
        try:
            return smbclient.stat(self.path(path))
        except SMBOSError:
            return None

    def is_dir(self, path):
        st = self.stat(path)
        if st:
            return bool(st.st_file_attributes & stat.FILE_ATTRIBUTE_DIRECTORY)
        return False

    def is_file(self, path):
        st = self.stat(path)
        if st:
            return not (st.st_file_attributes & stat.FILE_ATTRIBUTE_DIRECTORY)
        return False

    def file_size(self, path):
        st = self.stat(path)
        return st.st_size

    def download(self, src, dest, size=None, block_size=None, progress_cls=None):
        block_size = block_size or 64 * 2 ** 10
        with smbclient.open_file(self.path(src), mode='rb') as fd:
            size = self.file_size(src) if size is None else size
            if os.path.isfile(dest):
                os.remove(dest)
            with open(dest, 'wb') as f:
                cursor = 0
                progress = progress_cls(src, size) if progress_cls else None
                while cursor < size:
                    read_size = min(size - cursor, block_size)
                    f.write(fd.read(read_size))
                    if progress:
                        progress.update(read_size)
                    cursor += read_size
                if progress:
                    progress.close()

    def download_dir(self, src, dest, block_size=None, progress_cls=None):
        for item in sorted(self.listdir(src)):
            s = f'{src}/{item}'
            d = f'{dest}/{item}'
            if self.is_file(s):
                self.download(s, d, block_size=block_size, progress_cls=progress_cls)
            else:
                if not os.path.isdir(d):
                    os.makedirs(d)
                self.download_dir(s, d, progress_cls)
