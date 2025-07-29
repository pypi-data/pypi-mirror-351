import os

from urllib.request import urlopen
from filux_framework.system.Cache import Cache

class Download(Cache):
    def __init__(self, url:str, cache_dir:str=".remote_cache"):
        super().__init__(cache_dir)
        self._url = url
        
    def downlaod(self, filename:str, download_dir=None):
        if download_dir is None:
            download_dir=self._cache_dir

        file = urlopen(self._url)
        with open(os.path.join(download_dir, filename),'wb') as output_file:
          output_file.write(file.read())
