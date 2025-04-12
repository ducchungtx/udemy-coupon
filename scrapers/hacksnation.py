"""
Scraper module for HacksNation coupon posts
"""
import logging
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.helpers import month_to_num

# Configure logging
logger = logging.getLogger(__name__)

# URL to scrape
HACKSNATION_URL = "https://hacksnation.com/t/free-coupons"

def get_latest_coupon_posts(limit=5, use_selenium=False):
    """
    Scrape the HacksNation free coupons page and extract the latest coupon posts

    Args:
        limit (int): Number of coupon posts to return
        use_selenium (bool): Whether to use Selenium for handling AJAX content

    Returns:
        list: List of dictionaries containing title and url of the latest posts
    """
    if use_selenium:
        return get_latest_coupon_posts_selenium(limit)
    else:
        return get_latest_coupon_posts_bs4(limit)

def get_latest_coupon_posts_bs4(limit=5):
    """Use BeautifulSoup to scrape the static HTML content"""
    try:
        # Send HTTP request to the website
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(HACKSNATION_URL, headers=headers)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        logger.info(f"BS4 Response status: {response.status_code}")

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all link elements that might contain coupon posts
        coupon_posts = []
        links = soup.find_all('a')

        logger.info(f"BS4 Found {len(links)} links on the page")

        # Current date for filtering relevant posts
        current_date = datetime.now()
        current_year = current_date.year

        # Process each link
        for link in links:
            href = link.get('href')
            title = link.get_text(strip=True)

            # Check if it's a Udemy coupon post by title pattern
            if href and ('Udemy Free' in title or 'Udemy Courses' in title or 'udemy' in title.lower()):
                logger.info(f"BS4 Found potential coupon: {title}")

                # Make URL absolute if it's relative
                if not href.startswith(('http://', 'https://')):
                    href = f"https://hacksnation.com{href}"

                # Extract date from title if possible
                date_match = re.search(r'for\s+(\d+)\s+([A-Za-z]+)\s+(\d{4})', title)

                # Add to list with date info if available
                coupon_data = {
                    'title': title,
                    'url': href
                }

                if date_match:
                    day = int(date_match.group(1))
                    month = date_match.group(2)
                    year = int(date_match.group(3))

                    # Only add posts from current year
                    if year == current_year:
                        coupon_data['day'] = day
                        coupon_data['month'] = month
                        coupon_data['year'] = year
                        coupon_posts.append(coupon_data)
                        logger.info(f"BS4 Added coupon with date: {title}")
                else:
                    # If no date in title, still add it
                    coupon_posts.append(coupon_data)
                    logger.info(f"BS4 Added coupon without date: {title}")

        logger.info(f"BS4 Total coupons found: {len(coupon_posts)}")

        # Sort by most recent (assuming higher day value is more recent within same month)
        coupon_posts.sort(key=lambda x: (x.get('year', 0), month_to_num(x.get('month', '')), x.get('day', 0)), reverse=True)

        # Return the specified number of latest posts
        result = coupon_posts[:limit] if limit else coupon_posts
        logger.info(f"BS4 Returning {len(result)} coupons")
        return result

    except Exception as e:
        logger.error(f"Error scraping HacksNation with BS4: {e}")
        return []

def get_latest_coupon_posts_selenium(limit=5):
    """Use Selenium to scrape dynamically loaded content"""
    try:
        logger.info("Starting Selenium scraping...")

        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize Chrome driver
        logger.info("Initializing Chrome driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Navigate to the URL
        logger.info(f"Navigating to {HACKSNATION_URL}...")
        driver.get(HACKSNATION_URL)

        # Wait for the page to load (adjust timeout as needed)
        logger.info("Waiting for page to load...")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))

        # Allow time for AJAX content to load
        logger.info("Waiting for AJAX content...")
        time.sleep(3)

        # Get the page source after JavaScript execution
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all links
        links = soup.find_all('a')
        logger.info(f"Selenium Found {len(links)} links on the page")

        coupon_posts = []

        # Current date for filtering relevant posts
        current_date = datetime.now()
        current_year = current_date.year

        # Add a more specific selector for discussion items if we can identify them
        discussion_links = soup.select('a.PostItem-title')
        if discussion_links:
            logger.info(f"Selenium Found {len(discussion_links)} discussion links")
            links = discussion_links

        # Process each link
        for link in links:
            href = link.get('href')
            title = link.get_text(strip=True)

            # Check if it's a Udemy coupon post by title pattern with more relaxed criteria
            if href and ('udemy' in title.lower() or 'course' in title.lower() or 'coupon' in title.lower()):
                logger.info(f"Selenium Found potential coupon: {title}")

                # Make URL absolute if it's relative
                if not href.startswith(('http://', 'https://')):
                    href = f"https://hacksnation.com{href}"

                # Extract date from title if possible
                date_match = re.search(r'for\s+(\d+)\s+([A-Za-z]+)\s+(\d{4})', title)

                # Add to list with date info if available
                coupon_data = {
                    'title': title,
                    'url': href
                }

                if date_match:
                    day = int(date_match.group(1))
                    month = date_match.group(2)
                    year = int(date_match.group(3))

                    # Only add posts from current year
                    if year == current_year:
                        coupon_data['day'] = day
                        coupon_data['month'] = month
                        coupon_data['year'] = year
                        coupon_posts.append(coupon_data)
                        logger.info(f"Selenium Added coupon with date: {title}")
                else:
                    # If no date in title, still add it
                    coupon_posts.append(coupon_data)
                    logger.info(f"Selenium Added coupon without date: {title}")

        # Close the driver
        driver.quit()

        logger.info(f"Selenium Total coupons found: {len(coupon_posts)}")

        # If no coupons found with Selenium, try a more general approach
        if not coupon_posts:
            logger.info("No coupons found with specific selectors, trying general approach")
            # Try BS4 as fallback
            return get_latest_coupon_posts_bs4(limit)

        # Sort by most recent date
        coupon_posts.sort(key=lambda x: (x.get('year', 0), month_to_num(x.get('month', '')), x.get('day', 0)), reverse=True)

        # Return the specified number of latest posts
        result = coupon_posts[:limit] if limit else coupon_posts
        logger.info(f"Selenium Returning {len(result)} coupons")
        return result

    except Exception as e:
        logger.error(f"Error scraping HacksNation with Selenium: {e}")
        # Fallback to BS4 if Selenium fails
        logger.info("Falling back to BS4 scraping method")
        return get_latest_coupon_posts_bs4(limit)