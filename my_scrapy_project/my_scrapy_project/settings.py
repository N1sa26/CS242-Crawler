import os

# Scrapy project settings
BOT_NAME = "my_scrapy_project"

SPIDER_MODULES = ["my_scrapy_project.spiders"]
NEWSPIDER_MODULE = "my_scrapy_project.spiders"

# Enable Playwright for JavaScript rendering
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Playwright browser settings - Reduced timeout for efficiency
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,  # Run in headless mode
    "timeout": 7000,  # Reduced timeout to 7s
}

# Reduce Playwright navigation timeout
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 7000  # Set Playwright timeout to 7s

# Spoof User-Agent to prevent blocking
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Increase concurrent requests and reduce download delay
CONCURRENT_REQUESTS = 50
DOWNLOAD_DELAY = 0.1  # Reduce delay to speed up crawling

# Enable AutoThrottle to prevent getting blocked
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.1
AUTOTHROTTLE_MAX_DELAY = 2
AUTOTHROTTLE_TARGET_CONCURRENCY = 6  # Adjust based on performance

# Enable retry mechanism to handle request failures
RETRY_ENABLED = True
RETRY_TIMES = 3  # Retry failed requests up to 3 times
RETRY_HTTP_CODES = [500, 502, 503, 504, 403, 408]

# Ignore robots.txt rules to maximize coverage
ROBOTSTXT_OBEY = False

# Enable HTTP cache to reduce duplicate requests
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # Cache for 1 hour
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 403, 408]

# Data output settings
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output_dir")
FEEDS = {
    os.path.join(OUTPUT_DIR, "disaster_news.jsonl"): {
        "format": "jsonlines",
        "encoding": "utf8",
        "overwrite": True  # Ensure only one output file is used
    }
}

# Logging level
LOG_LEVEL = "INFO"

# Twisted Reactor settings for better async handling
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Read the dynamic item limit from environment variable
NUM_PAGES = int(os.getenv("NUM_PAGES", 1000))  # Default to 1000 if not set

# Apply dynamic CLOSESPIDER_ITEMCOUNT
CLOSESPIDER_ITEMCOUNT = NUM_PAGES
