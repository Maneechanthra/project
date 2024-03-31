# -*- coding: utf-8 -*-

from urllib.parse import urljoin, quote
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
from pythainlp import sent_tokenize, word_tokenize
import pymysql


def insert_raw_data(url, raw_data):
    # Clean raw data
    formatted_text = " ".join(raw_data.split())

    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="cis2024_ir_content",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO raw_data_2 (url, raw_text) VALUES (%s, %s)"
            cursor.execute(sql, (url, formatted_text))
            if cursor.rowcount > 0:
                print(f"Data inserted successfully for {url}.")
            else:
                print(f"Failed to insert data for {url}.")
        connection.commit()
    finally:
        connection.close()


def fetch_content(new_links_queue):
    for current_url in new_links_queue:
        try:
            page_source = urlopen(
                Request(current_url, headers={"User-Agent": "Mozilla/5.0"})
            ).read()
        except HTTPError:
            continue

        html_code = soup(page_source, "html.parser")
        content = html_code.get_text()

        insert_raw_data(current_url, content)


def crawler(links_queue):
    new_links_queue = []

    for current_url in links_queue:
        req_agent = Request(current_url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            page_source = urlopen(req_agent).read()
            html_code = soup(page_source, "html.parser")
            links = html_code.findAll("a", href=True)

            for link in links:
                url = link.get("href")
                if "kuse.csc.ku.ac.th" in url or url.startswith("/"):
                    url = quote(url)
                    full_url = urljoin(current_url, url)
                    if full_url not in new_links_queue:
                        new_links_queue.append(full_url)

        except HTTPError:
            continue

    return new_links_queue


seed_url = "https://kuse.csc.ku.ac.th/"
req_agent = Request(seed_url, headers={"User-Agent": "Mozilla/5.0"})

page_source = urlopen(req_agent).read()
html_code = soup(page_source, "html.parser")
content = html_code.get_text()
links = html_code.findAll("a", href=True)
links_queue = []

for link in links:
    url = link.get("href")
    if "kuse.csc.ku.ac.th" in url or url.startswith("/"):
        full_url = urljoin(seed_url, url)
        if full_url not in links_queue:
            links_queue.append(full_url)

new_links_queue = crawler(links_queue)
fetch_content(new_links_queue)
