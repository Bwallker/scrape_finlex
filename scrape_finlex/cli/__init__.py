""""The main module in scrape-finlex."""

from io import BufferedIOBase, BufferedWriter, RawIOBase
from sys import stderr
from typing import Iterable
from bs4 import BeautifulSoup, PageElement, Tag
from requests import get, Response, Session
from dataclasses import dataclass
from itertools import batched
from multiprocessing import Pool
from dotenv import load_dotenv
from os import PathLike, getenv


def get_page(offset: int, link: str) -> Response:
    """Get a page from Finlex."""
    if offset < 0 or offset > 1090:
        raise ValueError("Offset must be between 0 and 1090.")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
    }
    session = Session()
    return session.get(f"{link}&_offset={offset}", headers=headers)


@dataclass
class Config:
    """Configuration class representing configuration read from dotenv file."""

    link: str
    output_file: BufferedIOBase
    print_to_console: bool


def parse_config() -> Config:
    """Parse configuration from dotenv file."""
    load_dotenv()
    link = getenv("LINK")
    if link is None:
        raise ValueError("LINK environment variable must be set.")
    output_file_name = getenv("OUTPUT_FILE_NAME")
    if output_file_name is None:
        print("OUTPUT_FILE_NAME not specified in .env file. Defaulting to output.csv.")
        output_file_name = "output.csv"
    output_file = open(output_file_name, "wb")
    return Config(link, output_file, True)


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


def pass_(offset: int, config: Config) -> list[DocumentEntry]:
    """Run a pass."""
    if config.print_to_console:
        print("Running pass number", offset)
    res = get_page(offset, config.link)
    soup = BeautifulSoup(res.text, features="html.parser")
    entries = list(parse_page(soup))
    if config.print_to_console:
        print("Finished running pass number", offset)
    return entries


def get_num_pages(link: str) -> int:
    """Get the number of pages."""
    res = get_page(0, link)
    soup = BeautifulSoup(res.text, features="html.parser")
    print("Soup:", soup.prettify(), file=stderr)
    super_div = soup.find(class_="result-text")
    if super_div is None:
        raise ValueError("Could not find number of results.")
    p_tag = super_div.find("p")
    if p_tag is None:
        raise ValueError("Could not find p tag.")
    if not isinstance(p_tag, Tag):
        raise TypeError("p_tag must be a Tag.")
    text = p_tag.get_text()
    if not text.startswith("Hakuosumia "):
        raise ValueError('Did not start with "Hakuosumia ".')
    if not text.endswith(" kpl."):
        raise ValueError('Did not end with " kpl.".')
    num_text = text[len("Hakuosumia ") : -len(" kpl.")]
    try:
        return int(num_text)
    except ValueError as e:
        raise ValueError("Could not convert number of results to int.") from e


def calc_upper_limit(num_pages: int) -> int:
    """Calculate the upper limit for the offset."""
    if num_pages % 20 == 0:
        return num_pages
    return num_pages + 20 - num_pages % 20


def do_scrape(config: Config) -> None:
    num_pages = get_num_pages(config.link)

    upper_limit = calc_upper_limit(num_pages)

    result: list[DocumentEntry] = []

    with Pool(upper_limit // 20) as p:
        res = p.starmap(pass_, map(lambda x: (x, config), range(0, upper_limit, 20)))
        result.extend(i for y in res for i in y)

    config.output_file.write(b"name,description,link\n")
    for entry in result:
        config.output_file.write(
            bytes(f'"{entry.name}","{entry.description}","{entry.link}"\n', "utf-8")
        )


def cli_main() -> None:
    """Main function."""
    print("Running main!")

    config = parse_config()
    try:
        do_scrape(config)
    finally:
        config.output_file.close()

    print("Finished running main!")
