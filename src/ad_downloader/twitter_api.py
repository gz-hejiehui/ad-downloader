import platform
import sys
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
    def __headers(self):
        python_version = "{}.{}".format(sys.version_info.major, sys.version_info.minor)
        user_agent = 'twitter-ads version: {} platform: Python {} ({}/{})'.format(
            self.__cfg['version'],
            python_version,
            platform.python_implementation(),
            sys.platform
        )

        return {'user-agent': user_agent}

    @property
    def version(self):
        return self.__cfg['version'].split('.')[0]

    def get_accounts(self):
        url = f'https://ads-api.twitter.com/{self.version}/accounts'
        resp = self.__session.get(url, headers=self.__headers)
        resp.raise_for_status()

        data = resp.json()
        return data['data'] or []

    def get_campaigns(self, account_id: str):
        url = f'https://ads-api.twitter.com/{self.version}/accounts/{account_id}/campaigns'
        resp = self.__session.get(url, headers=self.__headers)
        resp.raise_for_status()

        data = resp.json()
        return data['data'] or []
