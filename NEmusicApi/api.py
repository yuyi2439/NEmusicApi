import os

import requests
import urllib3

from nemusicapi.type import QualityLevel, EncodeType
from nemusicapi.base_api import BaseApi
from nemusicapi.exception import NoDownloadDirException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Api(BaseApi):
    def __init__(self, *, 
                 cookie='',
                 download_dir=None
                 ):
        super().__init__(cookie=cookie)
        self.download_dir = download_dir
        
        if download_dir:
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)


    def get_song_data(self, raw_song_name: str, *, limit: int = 10) -> dict[int, str] | None:
        res = self.search_music(raw_song_name, limit=limit)
        if res['result']['songCount'] == 0:
            return
        song_data = {}
        for j in res['result']['songs']:
            song_id = j['id']
            song_name = j['name']
            song_data[song_id] = song_name
        return song_data


    def get_song_download_data(self, song_id: int, *,
                               level=QualityLevel.standard,
                               encodeType=EncodeType.flac
                               ) -> tuple[str, EncodeType] | None:
        res = self.get_song_file_data(song_id, level=level, encodeType=encodeType)
        if res['data'][0]['url'] is None:
            return
        song_url = res['data'][0]['url']
        song_type = res['data'][0]['type']
        return song_url, EncodeType(song_type)


    def download_song(self, song_url: str, file_name: str):
        if self.download_dir == None:
            raise NoDownloadDirException
        
        file_path = os.path.join(self.download_dir, file_name)
        
        with open(file_path, 'wb') as f:
            f.write(requests.get(song_url).content)
        return True