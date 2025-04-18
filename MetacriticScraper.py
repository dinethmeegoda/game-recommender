import time
import re
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)
import json

# Setup headless Chrome with optimizations
options = uc.ChromeOptions()
options.add_argument("--headless=new")  # Headless mode
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--disable-images")  # Disable images to speed up loading
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options)

# URL
base_url = "https://www.metacritic.com/browse/game?page="
base_url_game = "https://www.metacritic.com/game/"
all_titles = []
all_links = []  # To store game page links
page = 1
pageLimit = 568
cookie_accepted = False

def extract_game_info(html):
    soup = BeautifulSoup(html, 'html.parser')

    def safe_get_text(selector, root=soup):
        el = root.select_one(selector)
        return el.get_text(strip=True) if el else None

    def safe_get_all_texts(selector, root=soup):
        return [el.get_text(strip=True) for el in root.select(selector)]

    game_info = {}

    # === TOP SECTION ===
    game_info['title'] = safe_get_text('[data-testid="hero-title"] h1')
    game_info['platform'] = safe_get_text('.c-gamePlatformLogo_icon title')
    game_info['release_date'] = safe_get_text('.g-text-xsmall span.u-text-uppercase')
    game_info['critic_score'] = safe_get_text('[data-testid="critic-score-info"] .c-siteReviewScore span')
    game_info['critic_sentiment'] = safe_get_text('[data-testid="critic-score-info"] .c-productScoreInfo_scoreSentiment')
    game_info['critic_reviews'] = safe_get_text('[data-testid="critic-score-info"] .c-productScoreInfo_reviewsTotal span')
    game_info['user_score'] = safe_get_text('[data-testid="user-score-info"] .c-siteReviewScore span')
    game_info['user_sentiment'] = safe_get_text('[data-testid="user-score-info"] .c-productScoreInfo_scoreSentiment')
    game_info['user_reviews'] = safe_get_text('[data-testid="user-score-info"] .c-productScoreInfo_reviewsTotal span')

    # === DETAILS SECTION ===
    details = soup.select_one('[data-testid="details-game"]')
    if details:
        game_info['summary'] = safe_get_text('.c-productionDetailsGame_description', details)
        game_info['esrb_rating'] = safe_get_text('.c-productionDetailsGame_esrb_title span.u-block', details)
        game_info['esrb_reason'] = safe_get_text('.c-productionDetailsGame_esrb_title span:not(.u-block)', details)
        game_info['platforms'] = safe_get_all_texts('.c-gameDetails_Platforms li', details)
        game_info['initial_release_date'] = safe_get_text('.c-gameDetails_ReleaseDate span.g-color-gray70', details)
        game_info['developer'] = safe_get_text('.c-gameDetails_Developer li', details)
        game_info['publisher'] = safe_get_text('.c-gameDetails_Distributor span.g-color-gray70', details)
        game_info['genres'] = safe_get_all_texts('.c-genreList_item span.c-globalButton_label', details)

    return game_info

try:
    while page <= pageLimit:
        print(f"\n📄 Scraping Page {page}...\n")
        driver.get(base_url + str(page))

        # Wait until the body is loaded, then proceed with scraping
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Accept cookies only once
        if not cookie_accepted:
            try:
                accept_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                accept_btn.click()
                cookie_accepted = True
                print("✅ Accepted cookies")
            except (NoSuchElementException, TimeoutException):
                pass  # Already accepted or not present

        # Get page content
        soup = BeautifulSoup(driver.page_source, "html.parser")
        titles = soup.find_all("h3")

        for title in titles:
            text = title.text.strip()
            if (
                text
                and not text.lower().startswith("cookie")
                and not text.lower().startswith("manage")
                and text not in all_titles
            ):
                # Remove leading index numbers like "7814. ,813." or similar
                clean_text = re.sub(r"^\s*[\d.,]+\s*", "", text).strip()

                # Remove apostrophes
                clean_texter = clean_text.replace("'", "")

                # Slugify
                slug = re.sub(r"[^\w']+", '-', clean_texter.lower()).strip('-') + "/"
                slug = base_url_game + slug
                print(f"{len(all_titles) + 1}. {clean_text}, {slug}")
                all_titles.append(clean_text)
                all_links.append(slug)

        # Scroll to bottom asynchronously to make sure Next is visible
        driver.execute_async_script("""
            window.scrollTo(0, document.body.scrollHeight);
            arguments[0](true);
        """)

        # Try to find and click the "Next" button
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".c-navigationPagination_item--next.enabled"))
            )
            next_button.click()
            page += 1
        except (ElementClickInterceptedException, TimeoutException) as e:
            print("❌ Could not click Next or reached end. Ending scrape.")
            break

finally:
    print("🛑 Closing driver...")


game_data = {}

for i, title, url in enumerate(zip(all_titles, all_links)):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        info = extract_game_info(driver.page_source)
        game_data[title] = info
        print(f"✅ Scraped info for {title} {i}/{len(all_titles)}")
        time.sleep(0.1)  # Be polite to the server
    except Exception as e:
        print(f"❌ Failed to scrape {title}: {e}")

# Save to JSON file
with open("game_data.json", "w", encoding="utf-8") as f:
    json.dump(game_data, f, ensure_ascii=False, indent=2)

print("📁 Game data saved to game_data.json")

print(game_data.get("The Legend of Zelda: Ocarina of Time"))
