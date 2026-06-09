from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time as t


HEADERS = {"User-Agent": "Mozilla/5.0"}


async def get_relax_by_films() -> list[dict]:
    """
    Аналог get_afisha_me_films, но для relax.by.
    """

    url = "https://afisha.relax.by/kino/minsk/"

    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    t.sleep(3)

    # Скроллим до конца страницы
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        t.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    film_links = []
    seen_urls = set()

    # Ищем ссылки вида /kino/<число>-<slug>/minsk/
    for a in soup.select('a[href*="/kino/"]'):
        href = a.get("href") or ""
        if "/kino/" in href:
            part = href.split("/kino/")[1]
            if part and part[0].isdigit():  # фильм имеет числовой ID
                # Берём ТОЛЬКО alt у изображения внутри ссылки/карточки
                title = ""
                img = a.select_one("img") or a.find_previous("img") or a.find("img")
                if img:
                    alt = img.get("alt") or ""
                    if alt.strip():
                        title = alt.strip()

                # Пропускаем карточки без img@alt
                if not title:
                    continue

                if href not in seen_urls:
                    film_links.append({
                        "event_type": "film",
                        "title": title,
                        "url": href
                    })
                    seen_urls.add(href)


    print(film_links[:10])
    return film_links
