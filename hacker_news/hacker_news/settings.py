# Scrapy settings for hacker_news project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import sys
import os
from os.path import dirname
path = dirname(dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(path)
from misc.log import *

BOT_NAME = 'hacker_news'

DATABASE = {
    'drivername': 'postgres',
    'host': 'localhost',
    'port': '5432',
    'username': 'sabbidis',
    'password': '',
    'database': 'auctions'
}


SPIDER_MODULES = ['hacker_news.spiders']
NEWSPIDER_MODULE = 'hacker_news.spiders'

HTTP_PROXY = 'http://127.0.0.1:8123'
COOKIES_ENABLED = False

# Crawl responsibly by identifying yourself (and your website) on the
USER_AGENT = "AdsBot-Google ( http://www.google.com/adsbot.html)",

DOWNLOADER_MIDDLEWARES = {
    'hacker_news.middleware.RotateUserAgentMiddleware': 300,
    # 'hacker_news.middleware.ProxyMiddleware': 400,
    # 'misc.middleware.CustomUserAgentMiddleware': 401,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None
}

ITEM_PIPELINES = {
    # 'hacker_news.pipelines.JsonWithEncodingPipeline': 300,
    'hacker_news.pipelines.LocationPipeline': 200,
    'hacker_news.pipelines.AuctionsPipeline': 500,
    # 'hacker_news.pipelines.CalcPipeline': 341,
}
EXTENSIONS = {'hacker_news.latencies.Latencies': 520, }
LATENCIES_INTERVAL = 5

LOG_LEVEL = 'INFO'

DOWNLOAD_DELAY = 2
LOG_FILE = "maincrawler.log"
# DEPTH_PRIORITY = 1
# SCHEDULE_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
# SCHEDULE_MEMORY_QUEUE = 'scrapy.squeue.PickleFifoMemoryQueue'
CONCURRENT_REQUESTS = 10
CONCURRENT_REQUESTS_PER_DOMAIN = 10

AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = True
