# Data Acquisition

This directory contains the source code for the data acquisition. The web scrapers for acquiring fan fiction data is written in Python and uses the [Scrapy](https://scrapy.org) framework.
There are multiple Spiders for the archives [FanFiktion.de](https://www.fanfiktion.de/) and [ArchiveOfOurOwn](https://archiveofourown.org).

### [Spiders](spiders)

- [FanFiktion.py](data-acquisition/spiders/FanFiktion.py): Spider for the archive FanFiktion.de.
- [ArchiveOfOurOwn.py](data-acquisition/spiders/ArchiveOfOurOwn.py): Spider for the archive ArchiveOfOurOwn.
- [FanFiktionHtml.py](data-acquisition/spiders/FanFiktionHtml.py): Spider for the archive FanFiktion.de, which uses the HTML files previously downloaded.
- [FanFiktionMissing.py](data-acquisition/spiders/FanFiktionMissing.py): Spider for the archive FanFiktion.de, scraping missing data.
- [ArchiveOfOurOwnMissing.py](data-acquisition/spiders/ArchiveOfOurOwnMissing.py): Spider for the archive ArchiveOfOurOwn, scraping missing data.

### [Scripts](scripts)
- [extract_archives.py](data-acquisition/scripts/extract_archives.py): Extracts archives from an HTML downloader Spider links their filepath inside the database.
- [generate_csv.py](data-acquisition/scripts/generate_csv.py): Extracts filenames from archives files and derives urls from them. The gathered information are being stored in csv-files for stories, users and reviews
  accordingly.
- [rearchive.py](data-acquisition/scripts/rearchive.py): Extracts archives for storing them in a new archive consisting of 1,000 files.
- [match_fandoms.py](data-acquisition/scripts/match_fandoms.py): Compares FF.de and AO3 fandoms and tries to match those storing them in a CSV file.
- [rename_fandoms.py](data-acquisition/scripts/rename_fandoms.py): Uses the CSV file generated in match_fandoms.py to rename AO3 fandoms matching the FF.de names.
- [simple_scraper.py](data-acquisition/scripts/simple_scraper.py): Simple scraper using BeautifulSoup for filling smaller data gaps in previously crawled data.