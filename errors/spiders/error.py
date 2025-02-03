import scrapy
from scrapy.exceptions import CloseSpider
from errors.items import ErrorsItem
from logs.error_handler import ErrorManager 





class ErrorSpider(scrapy.Spider):
    name = "error"

    def __init__(self, *args, **kwargs):
        super(ErrorSpider, self).__init__(*args, **kwargs)
        self.error_manager = ErrorManager()

    def start_requests(self):
        
        urls = [
            'https://www.amazon.com/b?node=14253971'
        ]

        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                # meta={"proxy": "http://scraperapi:37c95f2cdd5d0f402065e4cf09825ef3@proxy-server.scraperapi.com:8001"},
                errback=lambda failure: self.error_manager.handle_request_failure(failure, self.name)

            )

    def parse(self, response):
        """Parses the response and extracts product details."""
        self.logger.info('IP address: %s' % response.text)
        if not self.error_manager.check_response_status(response, self.name):
            raise CloseSpider(f"{response.status} Response")
        
        try:
            self.logger.info(f"Crawling: {response.url}")
            items_found = False
            for sel in response.css(".puis-card-border"):
                item = ErrorsItem()
                name = sel.css(".a-color-base.a-text-normal>span::text").get()
                price = sel.css(".a-price-whole::text").get()
                stars = sel.css(".a-icon-star-small .a-icon-alt::text").get()
                if not name or not price or not stars:
                    
                    self.error_manager.log_error(
                        "Parsing Error", "Missing Required Data", 2001,
                        f"Missing required item data for URL: {response.url}",
                        self.name, response.url
                    )
                    continue  
                item['name'] = name
                item['price'] = price
                item['stars'] = stars
                items_found = True
                yield item

            if not items_found:
               
                self.error_manager.log_error(
                    "Parsing Error", "No Items Found", 2002,
                    f"No items found on page: {response.url}",
                    self.name, response.url
                )
        except Exception as e:
            self.error_manager.log_parsing_error(
                response,
                f"Error occurred while parsing: {str(e)}",
                self.name
            )

        # Pagination Handling
        next_page = response.css(".s-pagination-next::attr(href)").get()
        if next_page:
            try:
                next_page_url = response.urljoin(next_page)
                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse,
                    errback=lambda failure: self.error_manager.handle_request_failure(failure, self.name),
                    meta={'pagination': True}  # Mark this as a pagination request
                )
            except Exception as e:
                self.error_manager.log_error(
                    "Parsing Error", "Pagination Error", 2003,
                    f"Failed to extract next page: {str(e)}",
                    self.name, response.url
                )
        else:
            # If pagination element is missing (but it's expected)
            is_last_page = response.css(".s-pagination-next[aria-disabled='true']")
            if not is_last_page:
                self.error_manager.log_error(
                    "Parsing Error", "Missing Required Data - Pagination", 2003,
                    "Pagination element '.s-pagination-next' is missing but expected.",
                    self.name, response.url
                )
