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
import django
import environ

path = dirname(dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(path)


BOT_NAME = 'hacker_news'

DATABASE = {
    'drivername': 'postgres',
    'host': 'localhost',
    'port': '5432',
    'username': 'postgres',
    'password': 'gt5050gt',
    'database': 'auctions'
}
REDIRECT_ENABLED = True

SPIDER_MODULES = ['hacker_news.spiders']
NEWSPIDER_MODULE = 'hacker_news.spiders'

HTTP_PROXY = 'http://127.0.0.1:8123'
COOKIES_ENABLED = False

# Crawl responsibly by identifying yourself (and your website) on the
#USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
USER_AGENT = "Mozilla/5.0 (Linux; U; Android 4.0.3; de-ch; HTC Sensation Build/IML74K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 1,
    'hacker_news.middleware.RotateUserAgentMiddleware': 100,
    # 'hacker_news.middleware.ProxyMiddleware': 400,
    #    'misc.middleware.CustomUserAgentMiddleware': 401,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None
}

ITEM_PIPELINES = {
    # 'hacker_news.pipelines.JsonWithEncodingPipeline': 200,
    'hacker_news.pipelines.DjangoPipeline': 200,
    # 'hacker_news.pipelines.LocationPipeline': 200,
    # 'hacker_news.pipelines.AuctionsPipeline': 500,
    # 'hacker_news.pipelines.CalcPipeline': 341,
}
EXTENSIONS = {'hacker_news.latencies.Latencies': 520, }
LATENCIES_INTERVAL = 5

LOG_LEVEL = 'DEBUG'

DOWNLOAD_DELAY = 4
LOG_FILE = "Aircrawler.log"
# DEPTH_PRIORITY = 1
# SCHEDULE_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
# SCHEDULE_MEMORY_QUEUE = 'scrapy.squeue.PickleFifoMemoryQueue'
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1

AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = True


sys.path.append(os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), "../.."))
os.environ['DJANGO_SETTINGS_MODULE'] = 'pyauctions.config.settings.scrapy_set'

django.setup()
