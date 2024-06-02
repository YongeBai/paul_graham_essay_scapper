import requests
import os

from bs4 import BeautifulSoup
from ebooklib import epub

IGNORE = ["rss.html", "index.html"]
COVER_IMAGE = "Y_Combinator_logo.png"
ESSAY_DIR = "essays"

def fix_title(title: str):
    title = title.replace("/", "and")
    return title


def visit_link(link: str):
    url = f"https://www.paulgraham.com/{link}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    title = soup.title.string
    title = fix_title(title)
    print(f"Visiting {title}")
    essay_body(soup, title)

def essay_body(soup: BeautifulSoup, title: str):
    third_tr = soup.select("table tr td:nth-child(3) table font")[0]
    with open(f"essays/{title}.html", "w") as f:
        f.write("<h1> " + title + " </h1>\n")
        f.write(str(third_tr))


def create_epub():
    book = epub.EpubBook()

    book.set_title("Paul Graham Essays")
    book.add_author("Paul Graham")

    book.set_cover(COVER_IMAGE, open(COVER_IMAGE, 'rb').read())
    cover_html = f'''
    <html>
        <body>
            <img src="{COVER_IMAGE}"/>
        </body>
    </html>
    '''
    cover_item = epub.EpubHtml(title='Cover', file_name='cover.xhtml', content=cover_html)
    book.add_item(cover_item)
    chapters = []
    toc_items = []
    files = os.listdir(ESSAY_DIR)
    files.sort(
        key=lambda file_name: os.path.getmtime(os.path.join(ESSAY_DIR, file_name)), reverse=True
    )

    for filename in files:
        if filename.endswith(".html"):
            filepath = os.path.join(ESSAY_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                html_content = file.read()
                title = filename.replace(".html", "")
                chapter = epub.EpubHtml(
                    title=title, file_name=filename, content=html_content
                )
                chapters.append(chapter)
                book.add_item(chapter)
                toc_items.append(epub.Link(filename, title, filename))

    book.toc = toc_items

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = ["cover", "nav"] + chapters

    epub.write_epub("PG_essays.epub", book)


def main():
    URL = "https://www.paulgraham.com/articles.html"
    os.mkdir(ESSAY_DIR)
    page = requests.get(URL)
    seen = set()

    soup = BeautifulSoup(page.content, "html.parser")
    trs = soup.find_all("tr", valign="top")

    for tr in trs:
        links = tr.find_all("a")
        for link in links[4:]:
            if link.get("href").endswith(".html") and link.get("href") not in IGNORE and link.get("href") not in seen:
                visit_link(link.get("href"))
                seen.add(link.get("href"))
    create_epub()

if __name__ == "__main__":
    main()    
