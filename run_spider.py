
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from logs.error_handler import ErrorHandler
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.conf import init_env

# Initialize environment
init_env()

# Initialize error handler
error_handler = ErrorHandler()

def run_spider(spider_name):
    """Run a Scrapy spider and handle errors if the spider is not found."""
    settings = get_project_settings()
    
    try:
        # Load available spiders
        spider_loader = SpiderLoader(settings)
        
        if spider_name not in spider_loader.list():
            raise KeyError(f"Spider not found: {spider_name}")

        # Start Scrapy process if the spider exists
        process = CrawlerProcess(settings)
        process.crawl(spider_name)
        process.start()

    except KeyError as e:
        print(f"❌ ERROR: {e}")  # Console output
        error_handler.log_error("Crawling Error","SpiderNotFound",1003, str(e), spider_name)
        sys.exit(1)  # Exit with error code

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_spider.py <spider_name>")
        sys.exit(1)

    spider_name = sys.argv[1]
    run_spider(spider_name)
