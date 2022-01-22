from scrapy import cmdline

cmdline.execute('scrapy crawl FanFiktion'.split())

# for pausing and resuming crawls
# when pausing this crawl, resume it with the same command
# cmdline.execute('scrapy crawl FanFiktion -s JOBDIR=crawls/FanFiktion-1'.split())
