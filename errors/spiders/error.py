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
    # Check if the spider has been passed a 'urls' parameter.
    # If so, assume it's a comma-separated string of URLs.
        if hasattr(self, 'urls') and self.urls:
            urls = self.urls.split(',')
        else:
            # Fallback to a default list (currently empty or any hardcoded values)
            urls = [
                'https://httpbin.org/status/300'
            ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,                
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
                    
                    self.error_manager.log_missing_required_data(response, self.name)
                    continue  
                item['name'] = name
                item['price'] = price
                item['stars'] = stars
                items_found = True
                yield item

            if not items_found:
               
                self.error_manager.log_no_items_found(response, self.name)
        except Exception as e:
            self.error_manager.log_parsing_error(
                response,
                 {str(e)},
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
                self.error_manager.log_pagination_error(response,self)
        else:
               
            is_last_page = response.css(".s-pagination-next[aria-disabled='true']")
            if not is_last_page:
                self.error_manager.log_pagination_error_1(response,self)
