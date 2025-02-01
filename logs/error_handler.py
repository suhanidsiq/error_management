import os
import json
from datetime import datetime
import pytz
import logging

class ErrorHandler:
    """Handles logging of errors in a structured format."""

    def __init__(self, log_file="logs/errors.json"):
        self.log_file = log_file
        self.ensure_error_log_file()
        # Initialize the logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.ERROR)
        # Set up a file handler if not already attached.
        if not self.logger.handlers:
            file_handler = logging.FileHandler("scrapy_errors.log")
            file_handler.setLevel(logging.ERROR)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def ensure_error_log_file(self):
        """Ensure the error log file exists and initialize it properly."""
        dir_name = os.path.dirname(self.log_file)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f, indent=4)

    def log_error(self, error_category, error_subcategory, error_code, error_message, spider_name="unknown", url="unknown"):
        """Log an error and write it to the file."""
        error_entry = {
            "error_category": error_category,
            "error_subcategory": error_subcategory,
            "error_code": error_code,
            "error_message": error_message,
            "spider": spider_name,
            "url": url,
            "timestamp": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
        }

        # Read existing errors and append the new one
        existing_errors = self.read_existing_errors()
        existing_errors.append(error_entry)

        with open(self.log_file, "w") as f:
            json.dump(existing_errors, f, indent=4)

        # Log to the logger as well
        self.logger.error(json.dumps(error_entry, indent=4))

    def read_existing_errors(self):
        """Read existing errors from the log file safely."""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []  # If the file is corrupted, reset it
        return []

    def get_current_timestamp(self):
        """Get the current timestamp in a readable format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def handle_error(self, failure, spider_name):
        """Handles request failures and logs errors properly with structured error details."""
        self.logger.error(f"Request failed: {failure}")

        request = failure.request
        response = getattr(failure.value, 'response', None)

        if response:
            # Handling HTTP errors (e.g., 404, 500)
            error_category = "Crawling Error"
            error_sub_category = f"{response.status} Response Error"
            error_code = 1002
            error_message = f"{response.status} response received from {response.url} with status {response.status}"
        else:
            # Handling network errors, DNS failures, timeouts, etc.
            error_category = "Crawling Error"
            error_sub_category = "Request Failure"
            error_code = 1001
            error_message = f"Request failed for {request.url}: {failure.getErrorMessage()}"

        self.log_error(error_category, error_sub_category, error_code, error_message, spider_name, url=request.url)
