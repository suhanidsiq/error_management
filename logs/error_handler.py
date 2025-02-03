import os
import json
import logging
import datetime
import pytz

class ErrorManager:
    """Centralizes error management, including logging and error checking."""
    
    def __init__(self, log_file="logs/errors.json"):
        self.log_file = log_file
        self.ensure_error_log_file()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.ERROR)
        # Attach file handler if none exists
        if not self.logger.handlers:
            file_handler = logging.FileHandler("logs/scrapy_log.json")
            file_handler.setLevel(logging.ERROR)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
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
    
    def log_error(self, category, subcategory, code, message, spider, url):
        """Logs an error to both a JSON file and a log file."""
        error_entry = {
            "error_category": category,
            "error_subcategory": subcategory,
            "error_code": code,
            "error_message": message,
            "spider": spider,
            "url": url,
            "timestamp": datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
        }
        errors = self.read_errors()
        errors.append(error_entry)
        with open(self.log_file, "w") as f:
            json.dump(errors, f, indent=4)
        self.logger.error(json.dumps(error_entry, indent=4))
    
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

