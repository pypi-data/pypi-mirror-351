import os

class Cache:
    def __init__(self, cache_dir:str=".remote_cache"):
        self._cache_dir = cache_dir
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)

    def delete_cache(self):
        """Delete all cached files."""
        for file in os.listdir(self._cache_dir):
            if os.path.isdir(file):
                os.rmdir(file)
            else:
                os.remove(file)

    def delete_cached_file(self, filename:str):
        """Delete a Singel file from the cache"""
        _path = os.path.join(self._cache_dir, filename)
        if os.path.exists(_path):
            os.remove(_path)

    @property
    def cache_path(self):
        """returns the path of the cache"""
        return self._cache_dir