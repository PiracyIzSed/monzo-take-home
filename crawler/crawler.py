import json
from concurrent.futures import ThreadPoolExecutor
import threading
from time import time
from urllib.parse import ParseResult, urljoin, urlparse
from bs4 import BeautifulSoup
import httpx
import logging

logger = logging.getLogger(__name__)


class Worker:
    q: set = set()
    visited: set = set()
    q_lock: threading.Lock = threading.Lock()
    visited_lock: threading.Lock = threading.Lock()
    _session: httpx.Client = None

    def __init__(self, base_url: str) -> "Worker":
        self.base_url = base_url
        self.q.add(self.base_url)

    @staticmethod
    def write_dest(data: str) -> str:
        logger.info(data)

    def add_visited(self, url: str) -> None:
        with self.visited_lock:
            self.visited.add(url)

    def is_visited(self, url: str) -> None:
        with self.visited_lock:
            visited = url in self.visited
            if url.endswith("/"):
                return visited or url.rstrip("/") in self.visited
            return visited

    @property
    def session(self):
        if not self._session:
            self._session = httpx.Client(
                base_url=self.base_url,
                headers={"Content-Type": "text/html"},
                follow_redirects=True,
            )
        return self._session

    def work(self) -> None:
        total_urls = 0
        with ThreadPoolExecutor() as exec:
            while True:
                total_urls += len(self.q)
                futures = []
                while self.q:
                    with self.q_lock:
                        item = self.q.pop()
                        futures.append(exec.submit(self.process_link, item))
                for future in futures:
                    self.q |= future.result()
                self.q -= self.visited
                if not self.q:
                    logger.info(
                        f"{int(time())} - url: {self.base_url}, total crawled: {len(self.visited)}, concurrency: {exec._max_workers}\n"
                    )
                    logger.debug(f"All Visited: {json.dumps(list(self.visited))}")
                    return

    def _parse_html(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        return soup.find_all("a", href=True)

    def _get_page(self, link: str) -> str:
        page = self.session.get(link)
        return page.text

    def _get_url(self, link: str) -> ParseResult:
        joined_link = urljoin(self.base_url, link)
        joined_link = urlparse(joined_link)._replace(fragment="")
        return joined_link

    def process_link(self, link: str) -> set[str]:
        page = self._get_page(link)
        anchors = self._parse_html(page)

        self.add_visited(link)
        found_links = set()

        for anchor in anchors:
            found_link: ParseResult = self._get_url(anchor["href"])
            new_domain, base_domain = found_link.netloc, urlparse(self.base_url).netloc
            if new_domain == base_domain and not self.is_visited(found_link.geturl()):
                with self.q_lock:
                    found_link = found_link.geturl()
                    if found_link.endswith("/"):
                        found_link = found_link.rstrip("/")
                    found_links.add(found_link)
        self.write_dest(f"Visited: {link}, Found: {list(found_links)}")
        return found_links
