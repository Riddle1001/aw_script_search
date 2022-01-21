import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import json


cookies = None
try:
    with open(r'cookies.json', "r") as f:
        cookies = json.load(f)
except FileNotFoundError:
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get("https://aimware.net/forum/user/login")

    input("Press Enter after logging in...")

    cookies = driver.get_cookies()
    driver.close()

    with open(r'cookies.json', 'w') as f:
        json.dump(cookies, f)


session = requests.Session()

for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])


pages = 29

threads = []

def get_thread_info(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    usergroup_text  = soup.select("section.col-lg-12.section-base.section-content > span")[0].text

    usergroup = {
        "Adminitrator": "admin",
        "Super Moderator": "supermod",
        "Beta Tester": "beta",
        "Reseller": "reseller",
        "VIP": "vip",
        "Registered": "registered",
        "Banned": "banned"
    }[usergroup_text] 

    thread_contents = soup.select(".col-lg-12.section-base.section-content")
    date_string = thread_contents.find_all("div")[5].text




    # return {
    #     "usergroup": usergroup,
    #     "date": soup.select("section.col-lg-12.section-base.section-content > span")[1].text
    #     "date_modified": soup.select("section.col-lg-12.section-base.section-content > span")[2].text
    # }
    





for i in range(pages):
    print("Page: " + str(i))
    r = session.get("https://aimware.net/forum/board/97/page/" + str(i))
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.select(".row .forum-thread-list")
    for row in rows:
        title = row.find("a")
        thread_link = "https://aimware.net" + title.get("href")
        thread_title = title.get_text().replace("\n", "")

        author = row.select(".forum-thread-author")[0]
        thread_author = author.get_text()
        thread_author_link = "https://aimware.net" + author.find("a").get("href")
        thread_author_group = get_usergroup(thread_author_link)

        thread_replies = row.select(".d-none")[1].get_text()
        thread_views = row.select(".d-none")[2].get_text()

        threads.append({
            "link": thread_link,
            "title": thread_title,
            "author": thread_author,
            "author_link": thread_author_link,
            "author_group": thread_author_group,
            "replies": thread_replies.replace(",", ""),
            "views": thread_views.replace(",", ""),
            "thread_count": 1
        })


thread_count = {}

for thread in threads:
    if thread["author"] not in thread_count:
        thread_count[thread["author"]] = 1
    else:
        thread_count[thread["author"]] += 1

# Add thread count to every thread that is connected to the author.
for thread in threads:
    if thread["author"] in thread_count:
        thread["thread_count"] = thread_count[thread["author"]]

with open(r'threads.json', 'w') as f:
    json.dump(threads, f, indent=4)