import pytest


@pytest.fixture
def test_html():
    return """
    <html>
    <head>
    </head>
    <body>
        <a></a>
        <a href="https://www.example.com/">Visit Example</a>
        <a href="//example.com/">Visit Example</a>
        <a href="blog/1/">hreflang attribute 101</a>. 
        <a href="mailto:help@example.com">help@example.com</a>
        <a href="new_page.asp">HTML Images</a>
        <a href="/default.html"></a>
        <a href="/legal/files/premium/some-file.pdf">read this</a>
        <a href="../../blog/2"></a>
        <a href="tel:+1233455678">1233 455 678</a>
    </body>
    </html>
    """
