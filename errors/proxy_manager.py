import os
import requests
from logs.error_handler import ErrorManager

import logging

# Load your keys from the .env file (assuming you're using python-dotenv to load them)
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
SCRAPER_OPS_KEY = os.getenv("SCRAPER_OPS_KEY")

# Function to fetch current usage stats from Scraper API
def get_api_usage(self,spider):
    url = f"http://api.scraperapi.com/account?api_key={SCRAPER_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for errors in the response
        data = response.json()
        
        request_count = data.get("requestCount", 0)
        request_limit = data.get("requestLimit", 0)
        message = (f"API Usage: {request_count}/{request_limit}")
        logging.info(message)
        # self.error_handler.log_signal(message)
        return request_count, request_limit
        
    except Exception as e:
        print(f"Error fetching API usage: {e}")
        return None, None

# Function to decide whether to switch to Scraper Ops
def should_switch():
    request_count, request_limit = get_api_usage()

    if request_count is None or request_limit is None:
        print("Unable to retrieve usage data.")
        return False

    # Check if the request count has reached the limit
    if request_count >= request_limit:
        return True

    return False

# Main proxy operation function
def perform_proxy_operation():
    request_count, request_limit = get_api_usage()
    
    if request_count is None or request_limit is None:
        print("Error fetching usage data, cannot perform proxy operation.")
        return

    # Display the current request count and limit
    print(f"Current API Usage: {request_count} / {request_limit} requests.")
    
    if should_switch():
        print("Scraper API limit reached. Switching to Scraper Ops.")
        # Switch to Scraper Ops or implement any fallback logic here
        # Example: You could switch your proxy manager to use Scraper Ops API key
        # SCRAPER_API_KEY = SCRAPER_OPS_KEY  # Or however you'd implement the switch
    else:
        print("Scraper API is still active.")
        # Proceed with your regular proxy operations here

# Run the operation
perform_proxy_operation()

