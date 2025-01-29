import scrapy
import json
import os
from errors.items import ErrorsItem

class ErrorSpider(scrapy.Spider):
    name = "error"
    allowed_domains = ["www.amazon.com"]
    start_urls = ["https://www.amazon.com/b?node=14253971"]
    
    error_log_dir = "logs"  # ✅ New logs directory
    error_log_file = os.path.join(error_log_dir, "errors.json")  # ✅ Full path

    def __init__(self, *args, **kwargs):
        super(ErrorSpider, self).__init__(*args, **kwargs)
        self.errors = []
        self.ensure_error_log_file()  # ✅ Ensure file exists at startup!

    def ensure_error_log_file(self):
        """Create the error log directory and file if they do not exist."""
        os.makedirs(self.error_log_dir, exist_ok=True)  # ✅ Create 'logs/' if missing

        if not os.path.exists(self.error_log_file):
            with open(self.error_log_file, 'w') as f:  # ✅ 'w' mode creates the file
                json.dump([], f)  # ✅ Initialize with an empty JSON list
            self.logger.info(f"Created error log file: {self.error_log_file}")

    def log_error(self, error_type, error_message, url):
        """Log an error and write it to the file."""
        error_entry = {
            "error_type": error_type,
            "error_message": error_message,
            "url": url
        }
        self.errors.append(error_entry)
        self.write_errors_to_file()

    def write_errors_to_file(self):
        """Write the errors to the log file (ensuring the file exists)."""
        self.ensure_error_log_file()  # ✅ Ensure the file exists before writing
        with open(self.error_log_file, 'w') as f:
            json.dump(self.errors, f, indent=4)

    def parse(self, response):
        self.logger.info(f"Crawling: {response.url}")

        for error in response.css(".puis-card-border"):
            items = ErrorsItem()

            try:
                items['name'] = error.css(".a-color-base.a-text-normal>span::text").get()
                items['price'] = error.css(".a-price-whole::text").get()
                items['stars'] = error.css(".a-icon-star-small .a-icon-alt::text").get()

                if not items['name']:
                    self.log_error("Attribute Error", "Missing 'name' attribute", response.url)
                if not items['price']:
                    self.log_error("Attribute Error", "Missing 'price' attribute", response.url)
                if not items['stars']:
                    self.log_error("Attribute Error", "Missing 'stars' attribute", response.url)

                yield items

            except Exception as e:
                self.log_error("Exception", str(e), response.url)

        # Fix incorrect `next_page` extraction
        next_page = response.css(".s-pagination-next::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse, errback=self.handle_error)

    def handle_error(self, failure):
        self.log_error("Request Error", str(failure), failure.request.url)
