import platform
import sys
from datetime import datetime, timedelta
from functools import cached_property
from typing import Dict, Any, List

from requests_oauthlib import OAuth1Session

from ad_downloader.exception import DateRangeLimitError


class TwitterApi:
    def __init__(self, config: Dict[str, Any]):
        self.__cfg = config

    @cached_property
    def __session(self):
        return OAuth1Session(
            self.__cfg['consumer_key'],
            client_secret=self.__cfg['consumer_secret'],
            resource_owner_key=self.__cfg['access_token'],
            resource_owner_secret=self.__cfg['access_token_secret'],
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

    def get_accounts(self) -> List[Dict[str, Any]]:
        """获取账号列表"""
        url = f'https://ads-api.twitter.com/{self.version}/accounts'
        resp = self.__session.get(url, headers=self.__headers)
        resp.raise_for_status()

        accounts = []
        data = resp.json()['data']
        for item in data:
            accounts.append({
                'id': item['id'],
                'name': item['name'],
                'business_id': item['business_id'],
                'business_name': item['business_name'],
                'timezone': item['timezone'],
                'timezone_switch_at': datetime.strptime(item['timezone_switch_at'], '%Y-%m-%dT%H:%M:%SZ'),
                'country_code': item['country_code'],
            })
        return accounts

    def get_campaigns(self, account_id: str) -> List[Dict[str, Any]]:
        """获取广告系列列表"""
        url = f'https://ads-api.twitter.com/{self.version}/accounts/{account_id}/campaigns'
        resp = self.__session.get(url, headers=self.__headers)
        resp.raise_for_status()

        campaigns = []
        data = resp.json()['data']
        for item in data:
            campaigns.append({
                'id': item['id'],
                'name': str(item['name']).strip(),
                'status': item['entity_status'],
                'currency': item['currency'],
                'created_at': datetime.strptime(item['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
                'updated_at': datetime.strptime(item['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
            })

        return campaigns

    def get_campaign_insights(self, account_id: str, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """
        获取广告系列成效数据
        :param account_id: 账号ID
        :param start: 开始日期
        :param end: 结束日期
        :return:
        """
        # 检查日期范围
        if (end - start).days + 1 > 7:
            raise DateRangeLimitError('A maximum date range (end - start) of 7 days is allowed.')

        # 获取该账号下的广告系列
        campaigns = self.get_campaigns(account_id)

        # 根据广告系列ID分批获取数据，每次处理20个广告系列
        campaign_insights = []
        url = f'https://ads-api.twitter.com/{self.version}/stats/accounts/{account_id}'
        for i in range(0, len(campaigns), 20):
            _campaigns = {campaign['id']: campaign for campaign in campaigns[i: i + 20]}

            # 获取api数据
            params = {
                'start_time': start.strftime('%Y-%m-%d'),
                'end_time': (end + timedelta(days=1)).strftime('%Y-%m-%d'),
                'entity': 'CAMPAIGN',
                'entity_ids': ','.join(_campaigns.keys()),
                'granularity': 'DAY',
                'metric_groups': 'BILLING,ENGAGEMENT',
                'placement': 'ALL_ON_TWITTER',
            }
            resp = self.__session.get(url, headers=self.__headers, params=params)
            resp.raise_for_status()

            # 整理结果集
            data = resp.json()['data']
            for item in data:
                metrics = item['id_data'][0]['metrics']

                # 排除空数据
                if metrics['impressions'] is None:
                    continue

                for n in range((end - start).days + 1):
                    impressions = metrics['impressions'][n] or 0
                    clicks = metrics['clicks'][n] or 0
                    spend = (metrics['billed_charge_local_micro'][n] or 0) / 1000000

                    # 排除各个指标都为 0 的数据
                    if sum([impressions, clicks, spend]) == 0:
                        continue

                    campaign_id = item['id']
                    campaign_insights.append({
                        'time': int((start + timedelta(days=n)).timestamp()),
                        'account_id': account_id,
                        'campaign_id': campaign_id,
                        'campaign_name': _campaigns[campaign_id]['name'],
                        'impressions': impressions,
                        'clicks': clicks,
                        'spend': spend,
                        'currency': _campaigns[campaign_id]['currency'],
                    })

        return campaign_insights
