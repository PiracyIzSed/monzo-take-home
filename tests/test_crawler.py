import logging
import pytest
from crawler.crawler import Worker


@pytest.fixture
def worker():
    return Worker("https://example-seed.com")


@pytest.fixture
def url_in_a_traversal():
    return "https://example-seed.com/a/page/in/the/middle/"


def test_can_extract_links_from_html(worker, test_html):
    links = worker._parse_html(test_html)
    assert len(links) == 9


def test_can_get_page(worker):
    response = worker._get_page("https://example.com")
    assert str(response)


@pytest.mark.parametrize(
    "url, expected",
    (
        ("https://example-seed.com/", "https://example-seed.com/"),
        ("//example.com/", "https://example.com/"),
        ("blog/1/", "https://example-seed.com/a/page/in/the/middle/blog/1/"),
        ("mailto:help@example.com", "mailto:help@example.com"),
        ("/default.html", "https://example-seed.com/default.html"),
        ("/default.html#fragment-on-page", "https://example-seed.com/default.html"),
        ("../../blog/2", "https://example-seed.com/a/page/in/blog/2"),
        ("tel:+1233455678", "tel:+1233455678"),
    ),
)
def test_get_url(url, expected, url_in_a_traversal):
    worker = Worker(url_in_a_traversal)
    assert worker._get_url(url).geturl() == expected


def test_process_link(test_html, mocker, caplog):
    caplog.set_level(logging.INFO)
    mocker.patch("crawler.crawler.Worker._get_page", return_value=test_html)
    worker = Worker("https://example.com")
    worker.process_link("https://example.com")
    for record in caplog.records:
        assert "https://example.com" in record.msg
