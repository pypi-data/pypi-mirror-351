"""TextFile class for handling text files."""

from filux_framework.io.File import File

class TextFile(File):
    """A class for text file operations and data"""

    def __init__(self, path:str):
        super().__init__(path)

    def write_content(self, content:str):
        """Override the content of the file."""
        try:
            with open(self._path, "w", encoding="utf-8") as file:
                file.write(content)
        except Exception as e:
            print(e)

    @property
    def content(self):
        """Read the file and get its content."""
        try:
            with open(self._path, encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            print(e)
            return None