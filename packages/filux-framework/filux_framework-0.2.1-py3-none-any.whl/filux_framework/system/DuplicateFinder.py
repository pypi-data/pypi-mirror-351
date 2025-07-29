"""Module for finding duplicate files in a directory."""

import os
from collections import defaultdict
from filux_framework.io.File import File

class DuplicateFinder:
    """Class to find duplicate files based on size and hash."""

    def __init__(self, path:str):
        """
        Initialize DuplicateFinder.

        Args:
            path (str): Directory path to search for duplicates.
        """
        self.path = path
        self.files_by_size = defaultdict(list)

    def find_duplicates(self):
        """
        Find duplicate files in the directory.

        Returns:
            list: List of lists, each containing paths to duplicate files.
        """
        for root, _, files in os.walk(self.path):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(full_path)
                    self.files_by_size[size].append(full_path)
                except OSError:
                    continue

        duplicates = []
        for size, files in self.files_by_size.items():
            if len(files) < 2:
                continue
            hashes = defaultdict(list)
            for f in files:
                try:
                    h = File(f).get_file_hash()
                    hashes[h].append(f)
                except Exception:  #Todo: Consider replacing with a more specific exception if possible
                    continue
            for dup_list in hashes.values():
                if len(dup_list) > 1:
                    duplicates.append(dup_list)
        return duplicates
