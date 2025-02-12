
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from logs.error_handler import ErrorManager
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.conf import init_env

# Initialize environment
init_env()

# Initialize error handler
error_handler = ErrorManager()

def run_spider(spider_name, urls=None):
   
    settings = get_project_settings()
    
    try:
        # Load available spiders
        spider_loader = SpiderLoader(settings)
        if spider_name not in spider_loader.list():
            raise KeyError(f"Spider not found: {spider_name}")

        # Start Scrapy process if the spider exists
        process = CrawlerProcess(settings)
        
        if urls:
            # Pass the URLs as a spider argument.
            # Your spider should be coded to accept and process this argument.
            urls_arg = ','.join(urls)
            print(f"Starting spider '{spider_name}' with URLs: {urls_arg}")
            process.crawl(spider_name, urls=urls_arg)
        else:
            print(f"Starting spider '{spider_name}' with its default start URLs.")
            process.crawl(spider_name)
            
        process.start()

    except KeyError as e:
        print(f"❌ ERROR: {e}")  # Console output
        error_handler.log_error("Crawling Error", "SpiderNotFound", 1003, str(e), spider_name, url="N/A")
        sys.exit(1)  # Exit with error code

if __name__ == "__main__":
    # Expect at least one argument: the spider name.
    if len(sys.argv) < 2:
        print("Usage: python run_spider.py <spider_name> [url1 url2 ...]")
        sys.exit(1)

    spider_name = sys.argv[1]
    # If additional arguments are provided, treat them as URLs.
    urls = sys.argv[2:] if len(sys.argv) > 2 else None

    run_spider(spider_name, urls)
