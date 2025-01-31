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
        yield scrapy.Request(
            url='https://httpbin.org/status/200',
            callback=self.parse,
            errback=self.handle_error
        )

    def parse(self, response):
        """Parses the response and extracts product details."""
        if response.status != 200:
            import pdb;pdb.set_trace()
            error_type = f"{response.status} Response"
            error_message = f"{response.status} response received from {response.url} with status {response.status}"
            self.error_handler.log_error(error_type, error_message, self.name)
            raise CloseSpider(f'{response.status} Response')

        try:
            self.logger.info(f"Crawling: {response.url}")

            items_found = False  # Flag to track if any items were found

            for error in response.css(".puis-card-border"):
                items = ErrorsItem()
                name = error.css(".a-color-base.a-text-normal>span::text").get(default=None)
                price = error.css(".a-price-whole::text").get(default=None)
                stars = error.css(".a-icon-star-small .a-icon-alt::text").get(default=None)

                if not name or not price or not stars:
                    raise ValueError(f"Missing required item data for URL: {response.url}")

                items['name'] = name
                items['price'] = price
                items['stars'] = stars
                items_found = True

                yield items

            if not items_found:
                raise ValueError(f"No items found on page: {response.url}")

        except Exception as e:
            error_type = "Parsing Error"
            error_message = f"Error occurred while parsing: {str(e)}"
            self.logger.info(f"Response body snippet: {response.body[:200]}")
            self.error_handler.log_error(error_type, error_message, self.name)

        # Handling pagination
        next_page = response.css(".s-pagination-next::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse, errback=self.handle_error)

    def handle_error(self, failure):
        """Handles request failures and logs errors properly."""
        self.logger.error(f"Request failed: {failure}")

        request = failure.request
        response = getattr(failure.value, 'response', None)

        if response:
            # Handling HTTP errors (e.g., 404, 500)
            error_type = f"{response.status} Response Error"
            error_message = f"Non-200 response received from {response.url} with status {response.status}"
        else:
            # Handling network errors, DNS failures, timeouts, etc.
            error_type = "Request Failure"
            error_message = f"Request failed for {request.url}: {failure.getErrorMessage()}"

        self.error_handler.log_error(error_type, error_message, self.name)
