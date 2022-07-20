from functools import cached_property
from typing import Dict, Any

from requests_oauthlib import OAuth1Session


class TwitterApi:
    def __init__(self, config: Dict[str, Any]):
        self.__cfg = config

    @cached_property
    def __session(self):
        return OAuth1Session(
            self.__cfg['consumer_key'],
            client_secret=self.__cfg['consumer_secret'],
            resource_owner_key=self.__cfg['access_token'],
            resource_owner_secret=self.__cfg['accesstoken_secret'],
        )

    @property
    def version(self):
        return self.__cfg['version']

    def get_accounts(self):
        resp = self.__session.get(f'https://ads-api.twitter.com/{self.version}/accounts')
        print(resp.json())
