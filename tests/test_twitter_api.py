from datetime import datetime
from functools import cached_property

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

    def test_get_campaigns(self, mocked_responses):
        mocked_account_id = '18ce55gbmoz'
        mocked_responses.get(
            f'https://ads-api.twitter.com/{self.api.version}/accounts/{mocked_account_id}/campaigns',
            body=get_mocked_data('twitter_get_campaigns_data.json'),
            status=200,
            content_type="application/json",
        )
        actual = self.api.get_campaigns(mocked_account_id)

        # 检查结果集数量
        assert len(actual) == 9

        # 检查字段是否齐全
        expect_keys = ['id', 'name', 'status', 'currency', 'created_at', 'updated_at']
        for item in actual:
            assert list(item.keys()) == expect_keys
            assert isinstance(item['created_at'], datetime)
            assert isinstance(item['updated_at'], datetime)

    def test_get_campaign_insights(self, mocked_responses):
        mocked_account_id = '18ce55gbmoz'
        mocked_responses.get(
            f'https://ads-api.twitter.com/{self.api.version}/accounts/{mocked_account_id}/campaigns',
            body=get_mocked_data('twitter_get_campaigns_data.json'),
            status=200,
            content_type="application/json",
        )
        mocked_responses.get(
            f'https://ads-api.twitter.com/{self.api.version}/stats/accounts/{mocked_account_id}',
            body=get_mocked_data('twitter_get_campaign_insights_data.json'),
            status=200,
            content_type="application/json",
        )
        start = datetime.strptime('2021-12-26', '%Y-%m-%d')
        end = datetime.strptime('2021-12-31', '%Y-%m-%d')
        actual = self.api.get_campaign_insights(mocked_account_id, start, end)

        # 检查结果集数量
        assert len(actual) == 6

        # 检查字段是否齐全
        expect_keys = [
            'time', 'account_id', 'campaign_id', 'campaign_name', 'impressions', 'clicks', 'spend',
            'currency'
        ]
        for item in actual:
            assert list(item.keys()) == expect_keys
