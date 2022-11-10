from scrapy import cmdline
from datetime import datetime

logger = 'logs/ao3_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.log'
cmdline.execute(['scrapy', 'crawl', 'ArchiveOfOurOwn', '--logfile', logger])
