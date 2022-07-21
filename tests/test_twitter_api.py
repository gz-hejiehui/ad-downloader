from datetime import datetime
from functools import cached_property
from typing import List, Dict, Any

import pytest
import responses

from ad_downloader import TwitterApi
from tests import get_mocked_data


class TestTwitterApi:

    @cached_property
    def api(self):
        return TwitterApi({
            'version': '11.0.0',
            'consumer_key': 'pass...',
            'consumer_secret': 'pass...',
            'access_token': 'pass...',
            'access_token_secret': 'pass...',
        })

    @staticmethod
    @pytest.fixture
    def mocked_responses():
        with responses.RequestsMock() as rsps:
            yield rsps

    def test_get_accounts(self, mocked_responses):
        mocked_responses.get(
            f'https://ads-api.twitter.com/{self.api.version}/accounts',
            body=get_mocked_data('twitter_get_accounts_data.json'),
            status=200,
            content_type="application/json",
        )
        actual = self.api.get_accounts()

        # 检查返回结果数量
        assert len(actual) == 6

        # 检查字段是否齐全
        expect_keys = ['id', 'name', 'business_id', 'business_name', 'timezone', 'timezone_switch_at', 'country_code']
        for item in actual:
            assert list(item.keys()) == expect_keys
            assert isinstance(item['timezone_switch_at'], datetime)
