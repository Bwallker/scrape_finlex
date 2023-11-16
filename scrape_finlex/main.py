""""The main module in scrape-finlex."""

from bs4 import BeautifulSoup
from requests import get, Response


def get_page(offset: int) -> Response:
    """Get a page from Finlex."""
    if offset < 0 or offset > 780:
        raise ValueError("Offset must be between 0 and 780.")
    return get(
        f"https://www.finlex.fi/fi/sopimukset/sopsviite/haku/?search%5Btype%5D=luokitus&search%5Btype1%5D=Monenv%C3%A4liset%20sopimukset&_offset={offset}"
    )


def main() -> None:
    """Main function."""
    print("Running main!")
    res = get_page(0)
    soup = BeautifulSoup(res.text, features="html.parser")
    documents = soup.find(class_="docList")
    if documents is None:
        raise ValueError("Could not find documents.")
    for x in documents:
        print("Element in documents:", x)

    with open("output.html", "w") as f:
        f.write(soup.prettify())
