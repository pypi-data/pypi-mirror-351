import random
import re
from collections.abc import AsyncIterator, Generator
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import scrapy
from scrapy.http import HtmlResponse, Response, TextResponse
from scrapy.settings import BaseSettings
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.python.failure import Failure

from sciop_scraping.const import USER_AGENTS

BASE_URL = "https://chroniclingamerica.loc.gov/data/batches/"


class ChroniclingAmericaSpider(scrapy.Spider):
    name = "chronicling-america"
    allowed_domains = ["chroniclingamerica.loc.gov", "tile.loc.gov"]

    USER_AGENT_OVERRIDE: str | None = None
    JOBDIR_OVERRIDE: str | None = None

    def __init__(
        self,
        batch: str | None = None,
        output: Path | None = None,
        cf_cookie: str | None = None,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.batch = batch
        if output is None:
            self.output = Path.cwd() / "data" / "chronicling-america"
        else:
            self.output = Path(output).resolve()
        self.output.mkdir(exist_ok=True, parents=True)
        self.cf_cookie = {"cf_clearance": cf_cookie} if cf_cookie else None
        if not self.batch:
            self.crawl_root = BASE_URL
            self.start_urls = [BASE_URL]
        else:
            self.crawl_root = BASE_URL + self.batch + "/"
            self.start_urls = [self.tile_url(self.crawl_root + "manifest-md5.txt")]

    async def start(self) -> AsyncIterator[Any]:

        for url in self.start_urls:
            if url.endswith("manifest-md5.txt"):
                yield scrapy.Request(
                    url,
                    callback=self.parse_manifest,
                    dont_filter=True,
                    cookies=self.cf_cookie,
                    errback=self.errback,
                    cb_kwargs={"batch_url": self.crawl_root},
                )
            else:
                yield scrapy.Request(
                    url, dont_filter=True, cookies=self.cf_cookie, errback=self.errback
                )

    @classmethod
    def update_settings(cls, settings: BaseSettings) -> None:
        super().update_settings(settings)
        if cls.USER_AGENT_OVERRIDE:
            settings.set("USER_AGENT", cls.USER_AGENT_OVERRIDE, priority="spider")
        else:
            settings.set("USER_AGENT", random.choice(USER_AGENTS), priority="spider")
        if cls.JOBDIR_OVERRIDE:
            settings.set("JOBDIR", cls.JOBDIR_OVERRIDE)
        settings.set("ROBOTSTXT_OBEY", False, priority="spider")
        # there doesn't appear to be a rate limit on tile.loc.gov,
        # and since we can jump straight there when we have a batch name,
        # and i'm not sure how to dynamically modify this, leave this off by default.
        # settings.set("DOWNLOAD_DELAY", 0.5, priority="spider")
        settings.set("RETRY_ENABLED", True, priority="spider")
        settings.set("RETRY_TIMES", 5, priority="spider")
        settings.set("RETRY_HTTP_CODES", [500, 502, 503, 504, 522, 524, 408])

    def url_to_path(self, url: str) -> Path:
        """Get the output path for a given URL."""
        out_name = re.sub(BASE_URL, "", url)
        out_path = self.output / out_name
        out_path.parent.mkdir(exist_ok=True, parents=True)
        return out_path

    def tile_url(self, url: str) -> str:
        """Convert a chroniclingamerica.loc.gov url to a tile.loc.gov url"""
        pattern = re.compile(
            r"^https://chroniclingamerica\.loc\.gov/data/batches/(?P<batch>\w+)/(?P<path>.*)"
        )
        match = pattern.match(url)
        if not match:
            raise ValueError(f"Could not convert url to tile url: {url}")
        val = match.groupdict()
        prefix = val["batch"].split("_")[0]
        return f"https://tile.loc.gov/storage-services/service/ndnp/{prefix}/batch_{val['batch']}/{val['path']}"

    def parse(self, response: HtmlResponse) -> Generator[scrapy.Request, None, None]:
        links = response.css("a::attr(href)").getall()

        # if we are on a page that has a `manifest-md5.txt` in it,
        # shortcut and just use that to enumerate the files
        if any([link == "manifest-md5.txt" for link in links]):
            link = urljoin(response.url, "manifest-md5.txt")
            yield response.follow(
                link,
                callback=self.parse_manifest,
                errback=self.errback,
                cookies=self.cf_cookie,
                cb_kwargs={"batch_url": response.url},
            )
        else:
            links = [urljoin(response.url, link) for link in links]
            # filter to only those underneath the crawl root
            links = [link for link in links if self.crawl_root in link]

            for link in links:
                if link.endswith("/"):
                    yield response.follow(
                        link, callback=self.parse, errback=self.errback, cookies=self.cf_cookie
                    )
                else:
                    if not self.url_to_path(link).exists():
                        tile_link = self.tile_url(link)
                        yield response.follow(
                            tile_link,
                            callback=self.parse_file,
                            errback=self.errback,
                            cb_kwargs={"original_url": link},
                            cookies=self.cf_cookie,
                        )
                    else:
                        self.logger.info("Skipping %s, already downloaded", link)

    def parse_manifest(self, response: TextResponse, batch_url: str) -> None:
        lines = response.text.split("\n")
        paths = [re.split("\s+", line)[-1] for line in lines]
        urls = [urljoin(batch_url, path) for path in paths]
        # yeah this is a little inefficient but we only need to do it once
        existing = [url for url in urls if self.url_to_path(url).exists()]
        not_existing = [url for url in urls if not self.url_to_path(url).exists()]
        if existing:
            self.logger.info(f"Skipping {len(existing)} files, already downloaded")
        self.logger.info(f"Downloading {len(not_existing)} files")
        for url in urls:
            tile_url = self.tile_url(url)
            yield response.follow(
                tile_url,
                callback=self.parse_file,
                errback=self.errback,
                cb_kwargs={"original_url": url},
                cookies=self.cf_cookie,
            )

    def parse_file(self, response: Response, original_url: str) -> None:
        """
        Save a file underneath ``self.output``, removing the base url
        """

        out_path = self.url_to_path(original_url)
        self.logger.debug("Saving %s to %s", response.url, out_path)
        with open(out_path, "wb") as f:
            f.write(response.body)

    def errback(self, failure: Failure) -> None:
        self.logger.error(f"A spider error occurred: {failure}")
        if failure.check(HttpError) and failure.value.response.status == 429:
            raise scrapy.exceptions.CloseSpider(
                "429 received - stopping scrape. We can't wait these out. \n"
                "You should \n"
                "- Open one of the recent pages in a browser,\n"
                "- Pass the cloudflare check\n"
                "- Open your developer tools (often right click + inspect element)\n"
                "- Open the networking tab to watch network requests\n"
                "- Reload the page\n"
                "- Click on the request made to the page you're on to see the request headers\n"
                "- Copy your user agent and the part of the cookie after `cf_clearance=` "
                "and pass them to the -u and -c cli options, respectively.\n"
                "If you are crawling *all* data, rather than a single batch, "
                "you will likely need to set DOWNLOAD_DELAY=1 until the manifests are scraped."
            )
