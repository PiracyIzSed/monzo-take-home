import argparse
from concurrent.futures import ProcessPoolExecutor
import sys
from .crawler import Worker
import logging

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Process domains using seed urls")
    parser.add_argument("domains", nargs="+", action="extend")
    return parser


def crawl(urls: list[str]):
    with ProcessPoolExecutor() as ppe:
        futures = []
        for link in urls:
            futures.append(ppe.submit(bootstrap_process, link))
        for future in futures:
            future.result()


def bootstrap_process(link: str):
    worker = Worker(link)
    logging.info(f"Created Process for {link}")
    worker.work()


def main(argv=None):
    cli = cli_parser()
    seeds = cli.parse_args(argv)
    crawl(seeds.domains)


if __name__ == "__main__":
    raise SystemExit(main())
