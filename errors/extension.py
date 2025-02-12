from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.signalmanager import SignalManager
from logs.error_handler import ErrorManager

class ErrorLoggingExtension:
    """Scrapy extension to log signals and errors dynamically."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.error_handler = ErrorManager()

        # Connect the signals dynamically
        self.connect_signals()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """Initialize the extension only if enabled in settings."""
        if not crawler.settings.getbool('ERROR_LOGGING_ENABLED', False):
            raise NotConfigured
        return cls(crawler)


    def connect_signals(self):
        """Connect Scrapy signals to the corresponding handlers."""
        signal_manager = SignalManager(self.crawler)

        # Spider lifecycle signals
        signal_manager.connect(self.spider_opened_handler, signal=signals.spider_opened)
        signal_manager.connect(self.spider_closed_handler, signal=signals.spider_closed)

        # Error handling signals
        signal_manager.connect(self.handle_spider_error, signal=signals.spider_error)
        signal_manager.connect(self.handle_request_failed, signal=signals.request_dropped)

        # Item processing signals
        signal_manager.connect(self.item_scraped_handler, signal=signals.item_scraped)
        signal_manager.connect(self.item_dropped_handler, signal=signals.item_dropped)

        # Response signals
        signal_manager.connect(self.response_received_handler, signal=signals.response_received)

        # Other optional signals
        signal_manager.connect(self.engine_started_handler, signal=signals.engine_started)
        signal_manager.connect(self.engine_stopped_handler, signal=signals.engine_stopped)


 

    def spider_opened_handler(self, spider):
        """Triggered when the spider starts running."""
        message = f"Spider '{spider.name}' started."
        spider.logger.info(message)
        self.error_handler.log_signal(message)

    def spider_closed_handler(self, spider, reason):
        """Triggered when the spider finishes execution."""
        message = f"Spider '{spider.name}' closed. Reason: {reason}"
        spider.logger.info(message)
        self.error_handler.log_signal(message)



    
    def handle_request_failed(self, failure, request, spider):
        """Handles request failures (e.g., timeouts, connection errors)."""
        message = f"Request failed: {request.url}, Error: {failure}"
        spider.logger.warning(message)
        self.error_handler.log_error("Crawling Error", "RequestFailed - Network Error", 1003, message, spider.name, request.url)

    def handle_spider_error(self, failure, spider):
        """Handles unexpected spider errors."""
        message = f"Spider error in '{spider.name}': {failure}"
        spider.logger.error(message)
        self.error_handler.log_error("System Failure", "SpiderError - Runtime Error", 3002, message, spider.name, url="N/A")    


   
    def item_dropped_handler(self, item, response, exception, spider):
        """Handles dropped items (e.g., missing fields, validation issues)."""
        message = f"Item dropped: {exception}. URL: {response.url}"
        spider.logger.warning(message)
        self.error_handler.log_error("System Failure", "ItemDropped - Validation Error", 3003, message, spider.name, response.url)




    def item_scraped_handler(self, item, response, spider):
        """Logs when an item is successfully scraped."""
        message = f"Item scraped from {response.url}"
        spider.logger.info(message)
        self.error_handler.log_signal(message)


   

    def response_received_handler(self, response, request, spider):
        """Logs when a response is received."""
        message = f"Response received ({response.status}) from {request.url}"
        spider.logger.info(message)
        self.error_handler.log_signal(message)

    def response_received_headers_handler(self, headers, request, spider):
        """Logs when response headers are received."""
        message = f"Headers received from {request.url}: {headers}"
        spider.logger.info(message)
        self.error_handler.log_signal(message)

   
    def engine_started_handler(self):
        """Logs when the Scrapy engine starts."""
        message = "Scrapy engine started."
        self.error_handler.log_signal(message)

    def engine_stopped_handler(self):
        """Logs when the Scrapy engine stops."""
        message = "Scrapy engine stopped."
        self.error_handler.log_signal(message)
