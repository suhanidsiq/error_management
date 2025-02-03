import os
import logging
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ProxyManager:
    """
    This class generates proxy URLs for different proxy providers.
    """

    def __init__(self):
        # Read API keys from environment variables
        self.api_keys = {
            "scraperapi": os.getenv("SCRAPER_API_KEY"),  # API key for ScraperAPI
            "scrapeops": os.getenv("SCRAPEOPS_API_KEY"),  # API key for ScrapeOps
        }

    def get_proxy_url(self, url, proxy_name):
        """
        Generates a proxy URL for a given proxy provider.
        
        :param url: The target website URL
        :param proxy_name: The proxy provider ("scraperapi" or "scrapeops")
        :return: A fully formatted proxy URL
        """

        try:
            # Check if the API key exists
            if proxy_name not in self.api_keys or not self.api_keys[proxy_name]:
                raise ValueError(f"API key for {proxy_name} is not configured.")

            # Strip URL to remove extra spaces
            stripped_url = url.strip()

            # Create a payload (query parameters) for the proxy request
            payload = {
                "url": stripped_url,
                "api_key": self.api_keys[proxy_name],  # Inject API key
                "country_code": "US"  # Target a specific country (optional)
            }

            # Define the base URLs for proxy services
            base_urls = {
                "scraperapi": "http://api.scraperapi.com/",
                "scrapeops": "https://proxy.scrapeops.io/v1/",
            }

            # Ensure the selected proxy provider is valid
            if proxy_name not in base_urls:
                raise ValueError(f"Unsupported proxy provider: {proxy_name}")

            # Construct the final proxy URL
            proxy_url = base_urls[proxy_name] + "?" + urlencode(payload)
            logging.info(f"Generated {proxy_name.capitalize()} Proxy URL: {proxy_url}")
            return proxy_url

        except Exception as e:
            logging.error(f"Error generating proxy URL for {proxy_name}: {e}")
            return None
