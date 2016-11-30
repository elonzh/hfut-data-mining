# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem

from .items import MajorItem, TermItem, CourseItem, StudentItem


class DuplicatedCheckPipeline(object):
    # 避免重复生成 Item
    item_cache = {
        TermItem.__name__: {},
        MajorItem.__name__: {},
        CourseItem.__name__: {},
        StudentItem.__name__: {}
    }

    def process_item(self, item, spider):
        cache = self.item_cache.get(item.__class__.__name__)
        if cache is not None:
            code = item['code']
            if cache.get(code):
                raise DropItem()
            else:
                cache[code] = item
        return item
