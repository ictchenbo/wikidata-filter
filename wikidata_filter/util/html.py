
try:
    from bs4 import BeautifulSoup
except:
    raise ImportError("bs4 not installed")


def text_from_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text(separator=' ', strip=True)
