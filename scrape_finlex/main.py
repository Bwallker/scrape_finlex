""""The main module in scrape-finlex."""

from typing import Any, Iterable
from bs4 import BeautifulSoup, PageElement, Tag
from requests import get, Response
from dataclasses import dataclass
from itertools import batched, chain


def get_page(offset: int) -> Response:
    """Get a page from Finlex."""
    if offset < 0 or offset > 780:
        raise ValueError("Offset must be between 0 and 780.")
    return get(
        f"https://www.finlex.fi/fi/sopimukset/sopsviite/haku/?search%5Btype%5D=luokitus&search%5Btype1%5D=Monenv%C3%A4liset%20sopimukset&_offset={offset}"
    )


@dataclass
class DocumentEntry:
    """Class representing a document entry."""

    description: str
    name: str
    link: str


def process(x: tuple[str | PageElement, ...]) -> DocumentEntry:
    """Process a document entry."""
    if len(x) != 2:
        raise ValueError("x must be a tuple of length 2.")
    doc, desc = x
    if not isinstance(desc, Tag):
        raise TypeError("desc must be a Tag.")
    if not isinstance(doc, Tag):
        raise TypeError("doc must be a Tag.")

    doc_link = doc.find("a")
    desc_link = desc.find("a")

    if not isinstance(doc_link, Tag):
        raise TypeError("doc_link must be a Tag.")
    if not isinstance(desc_link, Tag):
        raise TypeError("desc_link must be a Tag.")

    doc_link_href = doc_link.get("href")
    desc_link_href = desc_link.get("href")

    if doc_link_href != desc_link_href:
        raise ValueError("doc_link_href and desc_link_href must be equal.")

    if not isinstance(doc_link_href, str):
        raise TypeError("doc_link_href must be a string.")
    if not isinstance(desc_link_href, str):
        raise TypeError("desc_link_href must be a string.")

    doc_contents = doc_link.contents
    desc_contents = desc_link.contents

    if len(doc_contents) != 1:
        raise ValueError("doc_contents must be of length 1.")
    if len(desc_contents) != 1:
        raise ValueError("desc_contents must be of length 1.")

    doc_content = doc_contents[0]
    desc_content = desc_contents[0]

    name = doc_content.get_text()
    description = desc_content.get_text()

    link = f"https://www.finlex.fi{doc_link_href}"

    return DocumentEntry(name=name, description=description, link=link)


def parse_page(soup: BeautifulSoup) -> Iterable[DocumentEntry]:
    documents = soup.find(class_="docList")
    if documents is None:
        raise ValueError("Could not find documents.")
    entries = filter(
        None,
        map(process, batched(filter(lambda x: isinstance(x, Tag), documents), 2)),
    )
    return entries


def main() -> None:
    """Main function."""
    print("Running main!")

    result: Iterable[DocumentEntry] = iter([])

    for i in range(0, 800, 20):
        print("Running pass number", i)
        res = get_page(i)
        soup = BeautifulSoup(res.text, features="html.parser")
        entries = parse_page(soup)
        result = chain(result, entries)

        print("Finished running pass number", i)
    with open("output.csv", "wb") as f:
        f.write(b"name,description,link\n")
        for entry in result:
            f.write(
                bytes(f'"{entry.name}","{entry.description}","{entry.link}"\n', "utf-8")
            )
