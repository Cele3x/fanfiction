# Scrapy settings for fanfiction project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
from os.path import join, dirname
from dotenv import load_dotenv
import urllib.parse

# load environment variables
dotenv_path = join(dirname(dirname(__file__)), '.env')
load_dotenv(dotenv_path)

# environment variables for archiving
ARCHIVE_PATH_STORIES = os.environ.get('ARCHIVE_PATH_STORIES')
ARCHIVE_PATH_USERS = os.environ.get('ARCHIVE_PATH_USERS')
ARCHIVE_PATH_REVIEWS = os.environ.get('ARCHIVE_PATH_REVIEWS')

# environment variables for extracted html files
EXTRACTED_STORIES_PATH = os.environ.get('EXTRACTED_STORIES_PATH')
EXTRACTED_USERS_PATH = os.environ.get('EXTRACTED_USERS_PATH')
EXTRACTED_REVIEWS_PATH = os.environ.get('EXTRACTED_REVIEWS_PATH')

# environment variables for csv files
CSV_STORIES_PATH = os.environ.get('CSV_STORIES_PATH')
CSV_USERS_PATH = os.environ.get('CSV_USERS_PATH')
CSV_REVIEWS_PATH = os.environ.get('CSV_REVIEWS_PATH')

# environment variables for mongo db with quoting where necessary
MONGO_USER = urllib.parse.quote_plus(str(os.environ.get('MONGO_USER')))
MONGO_PW = urllib.parse.quote_plus(str(os.environ.get('MONGO_PW')))
MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_PORT = os.environ.get('MONGO_PORT')
MONGO_DB = os.environ.get('MONGO_DB')

# MongoDB's connection string
MONGO_URI = 'mongodb://%s:%s@%s:%s' % (MONGO_USER, MONGO_PW, MONGO_HOST, MONGO_PORT)

BOT_NAME = 'fanfiction'

SPIDER_MODULES = ['fanfiction.spiders']
NEWSPIDER_MODULE = 'fanfiction.spiders'

# Directory for storing job information for pausing crawls
# JOBDIR = 'crawls'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'fanfiction (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False
COOKIES_DEBUG = True

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'fanfiction.middlewares.FanfictionSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'fanfiction.middlewares.FanfictionDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
   'scrapy.extensions.spiderstate.SpiderState': 500,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'fanfiction.pipelines.FanfictionPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 2
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
RETRY_HTTP_CODES = [429]

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
    # 'rotating_free_proxies.middlewares.RotatingProxyMiddleware': 610,
    # 'rotating_free_proxies.middlewares.BanDetectionMiddleware': 620,
    # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    # 'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'fanfiction.middlewares.TooManyRequestsRetryMiddleware': 543,
}

# ROTATING_PROXY_LIST = [
#     '88.198.24.108:1080',
#     '88.198.50.103:1080',
#     '194.163.128.225:3128',
# ]
# ROTATING_PROXY_LIST_PATH = 'proxies.txt'  # Path that this library uses to store list of proxies
# NUMBER_OF_PROXIES_TO_FETCH = 6  # Controls how many proxies to use

# Set fake UserAgent providers and default one
FAKEUSERAGENT_PROVIDERS = [
    'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
    'scrapy_fake_useragent.providers.FakerProvider',  # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
    'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
]
USER_AGENT = 'Mozilla/5.0 (Android; Mobile; rv:40.0)'

