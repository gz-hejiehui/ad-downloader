import platform
import sys
from datetime import datetime, timedelta
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

    def get_campaign_insights(self, account_id: str, start: datetime, end: datetime):
        # 获取该账号下的广告系列ID
        campaigns = self.get_campaigns(account_id)
        campaign_ids = [campaign['id'] for campaign in campaigns]

        # 根据广告系列ID分批获取数据，每次处理20个广告系列
        campaign_insights = []
        url = f'https://ads-api.twitter.com/{self.version}/stats/accounts/{account_id}'
        for i in range(0, len(campaign_ids), 20):

            # 获取api数据
            params = {
                'start_time': start.strftime('%Y-%m-%d'),
                'end_time': (end + timedelta(days=1)).strftime('%Y-%m-%d'),
                'entity': 'CAMPAIGN',
                'entity_ids': ','.join(campaign_ids[i: i + 20]),
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

                    campaign_insights.append({
                        'campaign_id': item['id'],
                        'time': int((start + timedelta(days=n)).timestamp()),
                        'this_date': (start + timedelta(days=n)).strftime('%Y-%m-%d'),
                        'impressions': impressions,
                        'clicks': clicks,
                        'spend': spend,
                    })

        return campaign_insights
