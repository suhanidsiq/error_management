import os
import json
from datetime import datetime

class ErrorHandler:
    """Handles logging of errors in a structured format."""

    def __init__(self, log_file="logs/errors.json"):
        self.log_file = log_file
        self.ensure_error_log_file()
       

    def ensure_error_log_file(self):
        """Ensure the error log file exists and initialize it properly."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f, indent=4)
        
                 # Initialize with an empty list

    def log_error(self, error_type, error_message, spider_name="unknown", url="unknown"):
        """Log an error and write it to the file."""
        error_entry = {
            "error_type": error_type,
            "error_message": error_message,
            "spider": spider_name,
            "url": url,
            "timestamp": self.get_current_timestamp()
        }

        # Read existing errors and append the new one
        existing_errors = self.read_existing_errors()
        existing_errors.append(error_entry)

        with open(self.log_file, "w") as f:
            json.dump(existing_errors, f, indent=4)

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

