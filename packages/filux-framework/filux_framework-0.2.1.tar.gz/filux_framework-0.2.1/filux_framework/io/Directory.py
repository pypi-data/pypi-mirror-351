"""Directory operations."""

import os

class Directory:
    """A class for directory operations."""

    def __init__(self, path:str):
        """Initialize Directory object."""
        self._path = path
        self._dirname, self._filename = os.path.split(self._path)

    def clear(self):
        """Remove all files in the directory."""
        for file in os.listdir(self._path):
            file_path = os.path.join(self._path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def get_content(self, extensions=None):
        """Get files in the directory, optionally filtered by extension(s)."""
        files = []
        for file in os.listdir(self._path):
            if extensions is None:
                files.append(file)
            elif isinstance(extensions, (list, tuple)):
                if os.path.splitext(file)[1] in extensions:
                    files.append(file)
            elif os.path.splitext(file)[1] == extensions:
                files.append(file)
        return files

    @property
    def path(self):
        """Return the directory path."""
        return self._path

    @property
    def parent(self):
        """Return the parent directory."""
        return self._dirname