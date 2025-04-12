from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import logging
import re
from datetime import datetime
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
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

def month_to_num(month_name):
    """Convert month name to numerical value for sorting"""
    months = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    return months.get(month_name, 0)

@app.route('/')
def home():
    """Home page route that displays the latest Udemy coupon posts"""
    # Try with Selenium first (AJAX support), fallback to BS4
    logger.info("Processing request for home page")
    coupon_posts = get_latest_coupon_posts(limit=5, use_selenium=True)
    logger.info(f"Found {len(coupon_posts)} coupon posts")

    # Add error checking - ensure we actually have data
    if not coupon_posts:
        # Try direct BS4 method as a last resort
        logger.info("No coupons found with Selenium, trying BS4 directly")
        coupon_posts = get_latest_coupon_posts_bs4(limit=5)
        logger.info(f"BS4 direct method found {len(coupon_posts)} coupon posts")

        # If still no data, add some dummy data for debugging
        if not coupon_posts:
            logger.warning("No data found with any method, adding dummy data for debugging")
            coupon_posts = [
                {
                    'title': 'Debug: Udemy Free Courses for 12 April 2025',
                    'url': 'https://hacksnation.com/t/udemy-free-courses-debug'
                },
                {
                    'title': 'Debug: More Udemy Coupons for Testing',
                    'url': 'https://hacksnation.com/t/more-debug-coupons'
                }
            ]

    logger.info(f"Rendering template with {len(coupon_posts)} coupons")
    return render_template('index.html', coupons=coupon_posts)

@app.route('/api/coupons')
def api_coupons():
    """API endpoint that returns the latest Udemy coupon posts as JSON"""
    coupon_posts = get_latest_coupon_posts(limit=5, use_selenium=True)
    return jsonify(coupon_posts)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # Create a simple template file if it doesn't exist
    template_path = os.path.join('templates', 'index.html')
    if not os.path.exists(template_path):
        with open(template_path, 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Udemy Coupon Finder</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .coupon-box {
            border: 1px solid #ddd;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
        h1 {
            color: #2c3e50;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .loading {
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <h1>Latest Udemy Coupons from HacksNation</h1>

    <div id="coupons-container">
        {% if coupons %}
            {% for coupon in coupons %}
            <div class="coupon-box">
                <h2>{{ coupon.title }}</h2>
                <p><a href="{{ coupon.url }}" target="_blank">Go to post</a></p>
            </div>
            {% endfor %}
        {% else %}
            <p>No coupons found. Please try again later.</p>
        {% endif %}
    </div>

    <p><small>Data scraped from <a href="https://hacksnation.com/t/free-coupons" target="_blank">HacksNation</a></small></p>
</body>
</html>
            ''')

    print("Starting app on http://127.0.0.1:5000")
    app.run(debug=True)