import click

from sciop_scraping.cli.tasks import chronicling_america


@click.group("sciop-scrape")
def cli() -> None:
    """Distributed scraping with sciop :)"""
    pass


cli.add_command(chronicling_america)
