from crawler.main import main, cli_parser
import logging


def test_can_accept_list_of_domains():
    parser = cli_parser()
    domains = parser.parse_args(["monzo.com", "lul.com"])
    assert domains


def test_main_app(capfd):
    main(["https://example.com"])
    captured = capfd.readouterr()
    assert "total crawled" in captured.out
