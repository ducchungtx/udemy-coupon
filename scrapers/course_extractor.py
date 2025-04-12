"""
Course extractor module for HacksNation course pages
"""
import logging
import requests
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger(__name__)

def extract_courses_from_url(url):
    """
    Extract the list of Udemy courses with their enrollment links from a specific HacksNation URL

    Args:
        url (str): URL of the HacksNation page containing Udemy courses

    Returns:
        list: List of dictionaries containing course title and enrollment link
    """
    try:
        logger.info(f"Extracting courses from URL: {url}")

        # Send HTTP request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        logger.info(f"Response status: {response.status_code}")

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all course items
        courses = []

        # Look for specific pattern where each course is listed with "Enroll for Free" link
        # This can be li elements containing both course name and enrollment link
        list_items = soup.find_all(['li', 'p'])
        logger.info(f"Found {len(list_items)} potential course containers")

        for item in list_items:
            # Find "Enroll for Free" link
            enroll_link = item.find('a', string='Enroll for Free')

            if enroll_link:
                # Get the href attribute for enrollment
                enrollment_url = enroll_link.get('href')

                # Extract course name: it's the text content of the list item minus the "Enroll for Free" text
                # Remove any trailing dash and spaces that might be present
                full_text = item.get_text(strip=True)
                course_name = full_text.replace('Enroll for Free', '').strip()
                if course_name.endswith('–'):
                    course_name = course_name[:-1].strip()

                courses.append({
                    'title': course_name,
                    'url': enrollment_url
                })
                logger.info(f"Added course: {course_name}")

        # If the above method didn't work, try an alternative approach
        if not courses:
            logger.info("No courses found with the first method, trying alternative method")

            # Look for strong tags that might contain "Enroll for Free" links
            strong_tags = soup.find_all('strong')

            for strong in strong_tags:
                enroll_link = strong.find('a', string='Enroll for Free')

                if enroll_link:
                    enrollment_url = enroll_link.get('href')

                    # Find the parent paragraph that contains the course name
                    parent = strong.find_parent('p') or strong.find_parent('li')

                    if parent:
                        # Extract course name
                        full_text = parent.get_text(strip=True)
                        course_name = full_text.replace('Enroll for Free', '').strip()
                        if course_name.endswith('–'):
                            course_name = course_name[:-1].strip()

                        courses.append({
                            'title': course_name,
                            'url': enrollment_url
                        })
                        logger.info(f"Added course (alt method): {course_name}")

        # If still no courses, try another approach
        if not courses:
            logger.info("No courses found with alternative method, trying direct link extraction")

            # Find all links on the page
            all_links = soup.find_all('a')

            for link in all_links:
                # Check if the link is for Udemy enrollment
                href = link.get('href', '')
                if 'udemy.com/course' in href and 'couponCode=' in href:
                    # Find parent element containing the course name
                    parent = link.find_parent('p') or link.find_parent('li')

                    if parent:
                        course_name = parent.get_text(strip=True).replace('Enroll for Free', '').strip()
                        if course_name.endswith('–'):
                            course_name = course_name[:-1].strip()

                        courses.append({
                            'title': course_name,
                            'url': href
                        })
                        logger.info(f"Added course (direct link method): {course_name}")

        logger.info(f"Total courses extracted: {len(courses)}")
        return courses

    except Exception as e:
        logger.error(f"Error extracting courses from URL: {e}")
        return []