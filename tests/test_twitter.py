from ad_downloader.twitter_api import get_accounts


def test_get_accounts():
    accounts = get_accounts()
    print(accounts)
