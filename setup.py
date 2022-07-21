from setuptools import setup

setup(
    name='ad-downloader',
    version='0.0.1',
    install_requires=[
        'twitter-ads',
    ],
    extras_require={
        'dev': [
            'build',
            'coverage',
            'pytest',
            'responses',
        ]
    },
)
