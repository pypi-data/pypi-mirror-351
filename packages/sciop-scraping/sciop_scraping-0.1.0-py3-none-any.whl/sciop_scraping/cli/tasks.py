from pathlib import Path

import click
from scrapy.crawler import CrawlerProcess

from sciop_scraping.spiders import ChroniclingAmericaSpider


@click.command("chronicling-america")
@click.option("-b", "--batch", help="Which batch to crawl. If None, crawl everything", default=None)
@click.option(
    "-o",
    "--output",
    help="Output directory to save files in. "
    "If None, $PWD/data/chronicling-america. "
    "Data will be saved in a chronicling-america subdirectory, "
    "and the crawl state will be saved in crawl_state.",
    default=None,
    type=click.Path(),
)
@click.option(
    "-c",
    "--cloudflare-cookie",
    help="When you get rate limited, you need to go solve a cloudflare challenge, "
    "grab the cookie with the key 'cf_clearance' and pass it here",
    default=None,
)
@click.option(
    "-u",
    "--user-agent",
    help="When you get rate limited, the cookie is tied to a specific user agent, "
    "copy paste that and pass it here",
    default=None,
)
def chronicling_america(
    batch: str | None,
    output: Path | None = None,
    cloudflare_cookie: str | None = None,
    user_agent: str | None = None,
) -> None:
    """
    Scrape the Chronicling America dataset from the Library of Congress in batches

    https://chroniclingamerica.loc.gov/data/batches/

    If you get a 429 redirect, you will need to manually bypass the cloudflare ratelimit check.

    - Open https://chroniclingamerica.loc.gov/data/batches/ in a browser,
    - Pass the cloudflare check
    - Open your developer tools (often right click + inspect element)
    - Open the networking tab to watch network requests
    - Reload the page
    - Click on the request made to the page you're on to see the request headers
    - Copy your user agent and the part of the cookie after `cf_clearance=`
      and pass them to the -u and -c cli options, respectively.
    """
    if output is None:
        output = Path.cwd() / "data" / "chronicling-america"
    else:
        output = Path(output).resolve() / "chronicling-america"

    job_dir = output.parent / "crawl_state"
    job_dir.mkdir(exist_ok=True, parents=True)

    # not sure how to pass args to the settings construction classmethod..
    ChroniclingAmericaSpider.USER_AGENT_OVERRIDE = user_agent
    ChroniclingAmericaSpider.JOBDIR_OVERRIDE = str(job_dir)

    process = CrawlerProcess()
    process.crawl(ChroniclingAmericaSpider, batch=batch, output=output, cf_cookie=cloudflare_cookie)
    process.start()
