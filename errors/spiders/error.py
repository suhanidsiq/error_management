import scrapy
from scrapy.exceptions import CloseSpider
from errors.items import ErrorsItem
from logs.error_handler import ErrorHandler  # Correct import for ErrorHandler

class ErrorSpider(scrapy.Spider):
    name = "error"

    def __init__(self, *args, **kwargs):
        super(ErrorSpider, self).__init__(*args, **kwargs)
        self.error_handler = ErrorHandler()

    def start_requests(self):
        """Starts requests and assigns errback for error handling."""
        urls = [
            'https://www.amazon.com/b?node=14253971',
            'https://httpbin.org/status/501',
            'https://httpbin.org/status/502',
            'https://httpbin.org/status/503',
            'https://httpbin.org/status/504',
            'https://httpbin.org/status/505',
            'https://httpbin.org/status/506',
            'https://httpbin.org/status/507',
            'https://httpbin.org/status/508',
            'https://httpbin.org/status/509'
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=lambda failure: self.error_handler.handle_error(failure, self.name)
            )

    def parse(self, response):
        """Parses the response and extracts product details."""
        if response.status != 200:
            error_category = "Crawling Error"
            error_subcategory = f"{response.status} Response"
            error_code = 1002
            error_message = f"{response.status} response received from {response.url} with status {response.status}"
            self.error_handler.log_error(error_category, error_subcategory, error_code, error_message, self.name, url=response.url)
            raise CloseSpider(f'{response.status} Response')

        try:
            self.logger.info(f"Crawling: {response.url}")

            items_found = False  # Flag to track if any items were found

            for error in response.css(".puis-card-border"):
                items = ErrorsItem()
                name = error.css(".a-color-base.a-text-normal>span::text").get(default=None)
                price = error.css(".a-price-whole::text").get(default=None)
                stars = error.css(".a-icon-star-small .a-icon-alt::text").get(default=None)

                # Check for missing required data
                if not name or not price or not stars:
                    # Log error for missing required data with error code 2001
                    error_category = "Parsing Error"
                    error_subcategory = "Missing Required Data"
                    error_code = 2001
                    error_message = f"Missing required item data for URL: {response.url}"
                    self.error_handler.log_error(error_category, error_subcategory, error_code, error_message, self.name, url=response.url)
                    continue  # Skip this item and continue with others

                items['name'] = name
                items['price'] = price
                items['stars'] = stars
                items_found = True

                yield items

            if not items_found:
                # Log error for no items found if necessary, using error code 2002 (as an example)
                error_category = "Parsing Error"
                error_subcategory = "No Items Found"
                error_code = 2002
                error_message = f"No items found on page: {response.url}"
                self.error_handler.log_error(error_category, error_subcategory, error_code, error_message, self.name, url=response.url)

        except Exception as e:
            error_category = "Parsing Error"
            error_subcategory = "Unexpected Parsing Error"
            error_code = 2003  # You could also use a different code for unexpected errors if you like.
            error_message = f"Error occurred while parsing: {str(e)}"
            self.logger.info(f"Response body snippet: {response.body[:200]}")
            self.error_handler.log_error(error_category, error_subcategory, error_code, error_message, self.name, url=response.url)

        # Handling pagination
        next_page = response.css(".s-pagination-next::attr(href)").get()

        if next_page:
            try:
                next_page_url = response.urljoin(next_page)
                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse,
                    errback=lambda failure: self.error_handler.handle_error(failure, self.name, pagination=True),
                    
                )
            except Exception as e:
                # This block may rarely trigger because urljoin is forgiving.
                error_category = "Parsing Error"
                error_subcategory = "Pagination Error"
                error_code = 2003
                error_message = f"Failed to extract next page: {str(e)}"
                self.error_handler.log_error(error_category, error_subcategory, error_code, error_message, self.name, url=response.url)

        else:
            # If next_page is None, log it as a missing pagination error (2003)
            error_category = "Parsing Error"
            error_subcategory = "Missing Required Data - Pagination"
            error_code = 2003
            error_message = "Pagination element '.s-pagination-next' is missing but expected."
            self.error_handler.log_error(error_category, error_subcategory, error_code, error_message, self.name, url=response.url)