import scrapy
from scrapy_playwright.page import PageMethod
import os


class NaturalDisastersSpider(scrapy.Spider):
    name = "natural_disasters"
    allowed_domains = [
        "news.google.com", "cnn.com", "bbc.com", "nytimes.com", "reuters.com",
        "washingtonpost.com", "foxnews.com", "aljazeera.com", "npr.org", "cbsnews.com",
        "abcnews.go.com", "nbcnews.com", "theguardian.com", "bloomberg.com",
        "apnews.com", "usatoday.com", "forbes.com", "news.yahoo.com", "theatlantic.com"
    ]

    def __init__(self, seed_file=None, num_pages=1000, hops_away=2, output_dir="output_dir", *args, **kwargs):
        super(NaturalDisastersSpider, self).__init__(*args, **kwargs)

        self.num_pages = int(num_pages)
        self.hops_away = int(hops_away)
        self.output_dir = output_dir
        self.visited_urls = set()
        os.makedirs(self.output_dir, exist_ok=True)

        self.start_urls = []
        if seed_file:
            try:
                with open(seed_file, "r", encoding="utf-8") as f:
                    self.start_urls = [line.strip() for line in f.readlines()]
            except FileNotFoundError:
                self.logger.error(f"Seed file '{seed_file}' not found! Using default URLs.")

    def parse(self, response):
        for article in response.xpath("//item"):
            title = article.xpath("title/text()").get()
            url = article.xpath("link/text()").get()

            if url and url not in self.visited_urls:
                self.visited_urls.add(url)
                yield scrapy.Request(
                    url,
                    callback=self.extract_real_url,
                    errback=self.handle_failure,
                    meta={"title": title or "Unknown Title", "depth": 0, "retry": 0},
                    dont_filter=False
                )

    def extract_real_url(self, response):
        final_url = response.url
        title = response.meta["title"]

        canonical_url = response.xpath("//link[@rel='canonical']/@href").get()
        if canonical_url:
            final_url = response.urljoin(canonical_url)

        if not final_url.startswith(("http://", "https://")):
            self.logger.warning(f"Skipping malformed URL: {final_url}")
            return

        if final_url not in self.visited_urls:
            self.visited_urls.add(final_url)
            yield scrapy.Request(
                final_url,
                callback=self.parse_article,
                errback=self.handle_failure,
                meta={
                    "title": title,
                    "url": final_url,
                    "depth": response.meta.get("depth", 0),
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "domcontentloaded"),
                        PageMethod("wait_for_timeout", 5000),
                    ],
                },
                dont_filter=False
            )

    def parse_article(self, response):
        items_scraped = self.crawler.stats.get_value("item_scraped_count", 0)
        if items_scraped >= self.num_pages:
            self.logger.info("Reached crawl limit, stopping...")
            self.crawler.engine.close_spider(self, reason="Crawl limit reached")
            return

        title = response.xpath("//meta[@property='og:title']/@content").get() or \
                response.xpath("//title/text()").get() or response.meta.get("title", "No Title")

        url = response.meta.get("url", "")
        paragraphs = response.xpath("//p//text()").getall()
        if not paragraphs:
            paragraphs = response.xpath("//div[contains(@class, 'article')]//text()").getall()

        content = " ".join(paragraphs).strip()

        metadata = {
            "published_date": response.xpath("//meta[@property='article:published_time']/@content").get() or "Unknown",
            "author": response.xpath("//meta[@name='author']/@content").get() or "Unknown",
            "source": response.xpath("//meta[@property='og:site_name']/@content").get() or "Unknown",
        }

        if not content or len(content) < 50:
            self.logger.info(f"Skipping article (too short): {title} - {url}")
            return

        self.logger.info(f"Scraped {items_scraped + 1}/{self.num_pages} articles")

        yield {
            "title": title.strip(),
            "url": url,
            "content": content,
            "metadata": metadata,
        }

        current_depth = response.meta.get("depth", 0)
        if current_depth < self.hops_away:
            new_links = response.xpath("//a[@href]/@href").getall()
            for link in new_links:
                if link.startswith(("javascript", "mailto", "#")):
                    continue

                full_link = response.urljoin(link)

                if full_link.startswith(("http://", "https://")) and full_link not in self.visited_urls:
                    self.visited_urls.add(full_link)
                    yield scrapy.Request(
                        full_link,
                        callback=self.parse_article,
                        errback=self.handle_failure,
                        meta={"url": full_link, "depth": current_depth + 1},
                        dont_filter=False
                    )

    def handle_failure(self, failure):
        request = failure.request
        retry_count = request.meta.get("retry", 0)

        if retry_count < 3:
            self.logger.warning(f"Retry {retry_count + 1}/3: {request.url} due to {failure.value}")

            return scrapy.Request(
                request.url,
                callback=request.callback,
                errback=self.handle_failure,
                meta={**request.meta, "retry": retry_count + 1},
                dont_filter=True
            )

        self.logger.error(f"Failed after 3 retries: {request.url} - {failure.value}")
        return None
