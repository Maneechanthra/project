from urllib.parse import urljoin, urlparse, quote
from urllib.error import URLError
import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
from pythainlp import sent_tokenize, word_tokenize
import pymysql


def insert_links(link, raw_text):
    try:
        condb = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="cis2024_ir_content",
            charset="utf8mb4",
        )
        with condb.cursor() as cursor:
            cursor.execute(
                "INSERT INTO raw_data_2 (url, raw_text) VALUES (%s, %s)",
                (link, raw_text),
            )
            condb.commit()
            print(f"Data inserted successfully: {link}")
    except Exception as e:
        print(f"Error inserting data for {link}: {e}")
        condb.rollback()
    finally:
        condb.close()


def fetch_rawtext(link):
    try:
        req_agent = Request(link, headers={"User-Agent": "Mozilla/5.0"})
        page_source = urlopen(req_agent).read()
        html_code = soup(page_source, "html.parser")
        raw_text = html_code.get_text()
        raw_text = " ".join(raw_text.split())
        insert_links(link, raw_text)
    except Exception as e:
        print(f"Error fetching raw text for {link}: {e}")

#เก็บลิงก์ไว้ในตัวแปร seed_url
seed_url = "https://kuse.csc.ku.ac.th"
req_agent = Request(seed_url, headers={"User-Agent": "Mozilla/5.0"})
page_source = urlopen(req_agent).read()
html_code = soup(page_source, "html.parser")
links = html_code.find_all("a", href=True)
links_queue = []
all_links = []

for link in links:
    url = link.get("href")
    if url and ("kuse.csc.ku.ac.th" in url or url.startswith("/")):
        full_url = urljoin(seed_url, url)
        if full_url not in links_queue:
            links_queue.append(full_url)

for current_url in links_queue:
    try:
        req_agent = Request(current_url, headers={"User-Agent": "Mozilla/5.0"})
        page_source_current = urlopen(req_agent).read()
        html_code_current = soup(page_source_current, "html.parser")
        current_links = html_code_current.find_all("a", href=True)
        for link in current_links:
            url = link.get("href")
            if url and ("kuse.csc.ku.ac.th" in url or url.startswith("/")):
                url = quote(url)
                full_url = urljoin(current_url, url)
                if full_url not in all_links:
                    all_links.append(full_url)
    except URLError:
        continue

for link in all_links:
    fetch_rawtext(link)

print(all_links)
print(len(all_links))
