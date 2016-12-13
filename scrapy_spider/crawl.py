# -*- coding:utf-8 -*-
import os
import shutil
from copy import deepcopy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

cache = '/home/erliang/Dev/Project/scrapy-nest/hfut_system/.scrapy'
if os.path.exists(cache):
    shutil.rmtree(cache)

settins = get_project_settings()

settins = deepcopy(settins)
settins.update(
    {
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_ITEMS': 300
    }
)
process = CrawlerProcess(settins)
process.crawl('hfut_system_spider', account=2013217413, password='123456789012', campus='XC')
process.start()  # the script will block here until the crawling is finished
