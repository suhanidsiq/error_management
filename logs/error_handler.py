from http.client import HTTPResponse
import os
import json
import logging
import datetime
from urllib import response
import pytz # type: ignore

class ErrorManager:
    """Centralizes error management, including logging and error checking."""
    
    def __init__(self, log_file="logs/errors.json",signal_log_file="logs/signals.log"):
        self.log_file = log_file
        self.ensure_error_log_file()
        self.signal_log_file = signal_log_file
        
        self.signal_logger = logging.getLogger("signals.log")
        self.signal_logger.setLevel(logging.INFO)
        if not self.signal_logger.handlers:
            signal_handler = logging.FileHandler(self.signal_log_file)
            signal_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            signal_handler.setFormatter(self.get_log_formatter())
            self.signal_logger.addHandler(signal_handler)


    def log_signal(self, message):
        """Logs general Scrapy process signals."""
        self.signal_logger.info(message)       
    
    def ensure_error_log_file(self):
        """Ensure the error log file exists."""
        dir_name = os.path.dirname(self.log_file)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f, indent=4)
    
    def read_errors(self):
        """Read the existing errors from the file."""
        try:
            with open(self.log_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
        
    def get_log_formatter(self):
        """Custom formatter that uses Asia/Kolkata time zone."""
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Override the default time format to use Asia/Kolkata timezone
        def custom_time(*args, **kwargs):
            # Return the time in Asia/Kolkata time zone
            return datetime.datetime.now(pytz.timezone('Asia/Kolkata')).timetuple()

        # Set custom time function to the formatter
        formatter.converter = custom_time
        return formatter    
    
    def log_error(self, category, subcategory, code, message, spider, url):
        """Logs an error to both a JSON file and a log file."""
        error_entry = {
            "error_category": category,
            "error_subcategory": subcategory,
            "error_code": code,
            "error_message": message,
            "spider": spider,
            "url": url if isinstance(response, HTTPResponse) else str(response),
            "timestamp": datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
        }
        errors = self.read_errors()
        errors.append(error_entry)
        with open(self.log_file, "a") as f:
            
            json.dump(error_entry, f, indent=4)
            f.write("\n")  # Add newline for readability
            
        
    
    def check_response_status(self, response, spider):
        """Checks if the response status is 200; if not, logs an error and returns False."""
        if response.status != 200:
            category = "Crawling Error"
            subcategory = f"{response.status} Response"
            code = 1002
            message = f"{response.status} response received from {response.url}"
            self.log_error(category, subcategory, code, message, spider, response.url)
            return False
        return True
    
    def log_parsing_error(self, response, message, spider, code=2003, subcategory="Unexpected Parsing Error"):
        """Logs a parsing error."""
        category = "Parsing Error"
        message = f"Error occurred while parsing: {str(e)}"
        self.log_error(category, subcategory, code, message, spider, response.url)
    
    def handle_request_failure(self, failure, spider):
        """Handles request failures (HTTP errors, network errors) dynamically."""
        request = failure.request
        response = getattr(failure.value, 'response', None)
        if response:
            category = "Crawling Error"
            subcategory = f"{response.status} Response Error"
            code = 1002
            message = f"{response.status} response received from {response.url}"
        else:
            category = "Crawling Error"
            subcategory = "Request Failure"
            code = 1001
            message = f"Request failed for {request.url}: {failure.getErrorMessage()}"
        self.log_error(category, subcategory, code, message, spider, request.url)

    def log_pagination_error(self, response, spider):
        """
        Logs a pagination error using dynamic values from the configuration.
        The spider doesn't need to supply any message or error code.
        """
        category = "Parsing Error"
        subcategory = "Pagination Error"
        code =  2003
        message =  "Failed to extract next page."
        self.log_error(category, subcategory, code, message, spider, response.url)

    def log_pagination_error_1(self, response, spider):
        """
        Logs a pagination error using dynamic values from the configuration.
        The spider doesn't need to supply any message or error code.
        """
        category = "Parsing Error"
        subcategory = "Missing Required Data - Pagination"
        code = 2003
        message = "Pagination element is missing but expected."
        
        self.log_error(category, subcategory, code, message, spider, response)

    def log_missing_required_data(self, response, spider):
        """
        Logs an error for missing required data dynamically.
        """
        category = "Parsing Error"
        subcategory = "Missing Required Data"
        code =  2001 
        message = f"Missing required item data for URL: {response.url}"
        self.log_error(category, subcategory, code, message, spider, response.url)
    
    def log_no_items_found(self, response, spider):
        """
        Logs an error when no items are found on the page.
        """
        category = "Parsing Error"
        subcategory = "No Items Found"
        code =  2002
        message =  f"No items found on page: {response.url}"
        self.log_error(category, subcategory, code, message, spider, response.url)    