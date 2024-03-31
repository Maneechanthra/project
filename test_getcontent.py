from urllib.request import urlopen, Request
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup as soup

seed_url = "https://kuse.csc.ku.ac.th/"
req_agent = Request(seed_url, headers={"User-Agent": "Mozilla/5.0"})

page_source = urlopen(req_agent).read()
html_code = soup(page_source, "html.parser")
content = html_code.get_text()
links = html_code.findAll("a", href=True)
links_queue = []
base_domain = urlparse(seed_url).netloc  # เพิ่มตัวแปร base_domain

for link in links:
    url = link.get("href")
    if url and (url.find("kuse.csc.ku.ac.th") != -1 or url.startswith("/")):
        full_url = urljoin(seed_url, url)
        if full_url not in links_queue:
            links_queue.append(full_url)

# เริ่มต้นการค้นลิงก์เพิ่มเติม
link_count = 0  # เพิ่มตัวแปรเพื่อนับจำนวนลิงก์ที่ค้นพบ

while len(links_queue) > 0:
    current_url = links_queue.pop(0)  # เอาลิงก์ออกจากคิว
    print("Crawling:", current_url)
    try:
        req_agent = Request(current_url, headers={"User-Agent": "Mozilla/5.0"})
        page_source = urlopen(req_agent).read()
        html_code = soup(page_source, "html.parser")
        new_links = html_code.findAll("a", href=True)
        for link in new_links:
            url = link.get("href")
            if url is not None:
                parsed_url = urlparse(urljoin(current_url, url))
                if parsed_url.netloc == base_domain or parsed_url.netloc == "":
                    full_url = parsed_url.geturl()
                    if full_url not in links_queue:
                        links_queue.append(full_url)
                        link_count += 1  # เพิ่มจำนวนลิงก์ที่ค้นพบ
    except Exception as e:
        print("Error:", e)

print("Total links found:", link_count)

# แปลงอักขระพิเศษและตัดช่องว่างออก
clean_text = "".join(e for e in content if e.isalnum() or e.isspace())
# print("Cleaned text:\n", clean_text)
