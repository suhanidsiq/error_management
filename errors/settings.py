# Scrapy settings for mopes project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "errors"

SPIDER_MODULES = ["errors.spiders"]
NEWSPIDER_MODULE = "errors.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "mopes (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
# "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
# "accept-encoding":"gzip, deflate, br, zstd",
# "accept-language":"en-US,en;q=0.9",
# "device-memory":"8",
# "downlink":"1.6",
# "dpr":"1",
# "ect":"4g",
# "priority":"u=0, i",
# "rtt":"100",
# "sec-ch-device-memory":"8",
# "sec-ch-dpr":"1",
# "user-agent":"curl/8.5.0",
# "viewport-width":"958"
# }




# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "errors.middlewares.ErrorsSpiderMiddleware": 350,
# }

# # Enable or disable downloader middlewares
# # See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'errors.middlewares.ErrorsSpiderMiddleware': 700,

}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    # If you have custom middlewares, order them appropriately.
}
# DOWNLOADER_MIDDLEWARES = {
#    #  'scrapy_rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
#     'scrapy_rotating_proxies.middlewares.BanDetectionMiddleware': 620,
# }


# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "mopes.pipelines.MopesPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"



# CUSTOM_SETTINGS = { 

#     # "ITEM_PIPELINES": {"errors.pipelines.ErrorHandlingPipeline": 300}, 

#     "RETRY_ENABLED": True, 

#     "RETRY_TIMES": 2,  # Retry failed requests 2 times 

#     "DOWNLOAD_TIMEOUT": 10,  # Set timeout for requests 

#     "LOG_LEVEL": "DEBUG",  # Adjust log level for better debugging 

# } 


# Add the path for logging (if needed for other extensions or settings)
LOG_FILE = 'logs/scrapy_log.json'
LOG_LEVEL = 'DEBUG'

ROTATING_PROXY_LIST_PATH = 'proxy_list.txt'

EXTENSIONS = {
    'errors.extension.ErrorLoggingExtension': 500,  # Ensure correct path
}
ERROR_LOGGING_ENABLED = True