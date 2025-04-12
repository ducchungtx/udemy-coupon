"""
Main application file for the Udemy Coupon Finder
"""
import os
import logging
from flask import Flask, render_template, jsonify, request
from scrapers.hacksnation import get_latest_coupon_posts
from scrapers.course_extractor import extract_courses_from_url

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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
        coupon_posts = get_latest_coupon_posts(limit=5, use_selenium=False)
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

@app.route('/api/extract-courses', methods=['GET'])
def api_extract_courses():
    """API endpoint that extracts Udemy courses from a specific HacksNation URL"""
    url = request.args.get('url')

    if not url:
        return jsonify({'error': 'No URL provided. Please add ?url=https://example.com parameter'}), 400

    courses = extract_courses_from_url(url)
    return jsonify({
        'url': url,
        'count': len(courses),
        'courses': courses
    })

def ensure_template_exists():
    """Ensure that the template directory and index.html file exist"""
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # Create a simple template file if it doesn't exist
    template_path = os.path.join('templates', 'index.html')
    if not os.path.exists(template_path):
        logger.info("Creating default index.html template")
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
        logger.info("Default template created")

if __name__ == '__main__':
    # Ensure template exists
    ensure_template_exists()

    # Start Flask server
    logger.info("Starting app on http://127.0.0.1:5000")
    app.run(debug=True)