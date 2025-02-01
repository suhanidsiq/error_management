from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.signalmanager import SignalManager
from logs.error_handler import ErrorHandler

class ErrorLoggingExtension:

    def __init__(self, crawler):
        self.crawler = crawler
        self.error_handler = ErrorHandler()
        
        # Connect the signals manually
        self.connect_signals()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # Initialize the extension only if enabled
        if not crawler.settings.getbool('ERROR_LOGGING_ENABLED', False):
            raise NotConfigured
        return cls(crawler)

    def connect_signals(self):
        """Connect Scrapy signals to the corresponding handlers"""
        signal_manager = SignalManager(self.crawler)
        signal_manager.connect(self.spider_opened_handler, signal=signals.spider_opened)
        signal_manager.connect(self.spider_closed_handler, signal=signals.spider_closed)
        signal_manager.connect(self.handle_spider_error, signal=signals.spider_error)
        signal_manager.connect(self.handle_request_failed, signal=signals.request_failed)

    def spider_opened_handler(self, spider):
        
        """Log when a spider is opened."""
        spider.logger.info(f"Spider {spider.name} opened.")

    def spider_closed_handler(self, spider, reason):
        """Log when a spider is closed."""
        spider.logger.info(f"Spider {spider.name} closed. Reason: {reason}")

    def handle_spider_error(self, failure, spider):
        """Handle spider errors and log them into the custom error log."""
        spider.logger.error(f"Spider error: {failure}")
        
        error_message = f"Error occurred in spider: {str(failure)}"
        self.error_handler.log_error("SpiderError", error_message, spider.name)

    def handle_request_failed(self, failure, request, spider):
        """Handle request errors and log them into the custom error log."""
        error_message = f"Request failed for URL: {request.url}, Error: {failure}"
        self.error_handler.log_error("RequestFailed", error_message, spider.name, request.url)
