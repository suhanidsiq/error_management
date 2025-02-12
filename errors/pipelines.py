# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


from itemadapter import ItemAdapter
from logs.error_handler import ErrorHandler
from scrapy.exceptions import DropItem

error_handler = ErrorHandler()

class ErrorsPipeline:
    def process_item(self, item, spider):
        """Process items and simulate errors."""
        if not item.get("url"):
            error_handler.log_error("DropItem", "Missing URL in item!", spider.name)
            raise DropItem("Missing URL in item!")
        
        if item.get("status") != 200:
            error_handler.log_error("Non-200 Status", f"Non-200 status code for URL: {item['url']}", spider.name)
        
        return item

