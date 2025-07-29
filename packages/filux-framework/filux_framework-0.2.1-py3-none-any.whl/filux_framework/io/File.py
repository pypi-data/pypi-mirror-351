"""Basic File loading with operations and data."""

import hashlib
import os
import platform
import stat
import zipfile
import datetime
import win32com

from win32com.client import gencache

DEFAULT_METADATA = [
    'Name', 'Size', 'Item type', 'Date modified', 'Date created', 'Date accessed', 'Attributes',
    'Offline status', 'Availability', 'Perceived type', 'Owner', 'Kind', 'Date taken',
    'Contributing artists', 'Album', 'Year', 'Genre', 'Conductors', 'Tags', 'Rating', 'Authors',
    'Title', 'Subject', 'Categories', 'Comments', 'Copyright', '#', 'Length', 'Bit rate',
    'Protected', 'Camera model', 'Dimensions', 'Camera maker', 'Company', 'File description',
    'Masters keywords', 'Masters keywords'
]

class File:
    """A class for file operations and metadata."""

    def __init__(self, path:str):
        """Initialize File object."""
        self._path = path
        self._dirname, self._filename = os.path.split(self._path)
        self._extension = os.path.splitext(self._filename)[1]

    def get_file_metadata(self, metadata=None):
        """Get file metadata."""
        if metadata is None:
            metadata = DEFAULT_METADATA
        if win32com and platform.system() == "Windows":
            try:
                sh = gencache.EnsureDispatch('Shell.Application', 0)
                ns = sh.NameSpace(self._dirname)
                item = ns.ParseName(str(self._filename))
                file_metadata = {}
                for ind, attribute in enumerate(metadata):
                    attr_value = ns.GetDetailsOf(item, ind)
                    if attr_value:
                        file_metadata[attribute] = attr_value
                return file_metadata
            except Exception as e:
                print(f"Error using Windows Shell API: {e}")
        else:
            try:
                stats = os.stat(self._path)
                return {
                    "name": self._filename,
                    "path": os.path.abspath(self._path),
                    "size_bytes": stats.st_size,
                    "created": datetime.datetime.fromtimestamp(stats.st_ctime),
                    "modified": datetime.datetime.fromtimestamp(stats.st_mtime),
                    "accessed": datetime.datetime.fromtimestamp(stats.st_atime),
                    "is_file": os.path.isfile(self._path),
                    "is_dir": os.path.isdir(self._path),
                    "permissions": stat.filemode(stats.st_mode),
                    "extension": self._extension,
                }
            except Exception as e:
                print(f"Failed to get file metadata: {e}")
                return None

    def get_file_hash(self, algorithm:str='sha256'):
        """Compute the hash of a file using the specified algorithm."""
        hash_func = hashlib.new(algorithm)
        try:
            with open(self._path, 'rb') as file:
                while True:
                    chunk = file.read(8192)
                    if not chunk:
                        break
                    hash_func.update(chunk)
        except Exception as e:
            print(e)
        return hash_func.hexdigest()

    def zip(self, compress=zipfile.ZIP_DEFLATED):
        """Zip the file."""
        with zipfile.ZipFile(self._filename + '.zip', 'w', compress) as target:
            target.write(self._path, arcname=self._filename)

    def rename(self, name:str):
        """Rename the file."""
        os.rename(self._path, os.path.join(self._dirname, name + self._extension))

    def move(self, dest_path:str):
        """Move the file to a new destination."""
        os.rename(self._path, dest_path)

    def delete(self):
        """Delete the file."""
        os.remove(self._path)

    @property
    def file_size(self):
        """Get the file size in bytes."""
        return os.path.getsize(self._path)

    @property
    def extension(self):
        """Return the file extension."""
        return self._extension

    @property
    def filename(self):
        """Return the file name."""
        return self._filename

    @property
    def path(self):
        """Return the file path."""
        return self._path

    @property
    def parent(self):
        """Return the parent directory."""
        return self._dirname