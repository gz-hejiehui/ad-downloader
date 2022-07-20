from enum import Enum
from pathlib import Path

from ad_downloader.twitter_api import TwitterApi

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# Version of the realpython-reader package
__version__ = '0.0.1'


class Media(Enum):
    Twitter = 1


class ADDownloader:
    def __init__(self, config_path: str):
        self.__cfg = tomllib.loads(Path(config_path).read_text(encoding='utf-8'))
        self.__api = None

    def media(self, media: Media):
        if media == Media.Twitter:
            self.__api = TwitterApi(self.__cfg['twitter'])
        return self

    def accounts(self):
        return self.__api.get_accounts()
