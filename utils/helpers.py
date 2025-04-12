"""
Utility functions for the Udemy coupon finder application
"""

def month_to_num(month_name):
    """Convert month name to numerical value for sorting"""
    months = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    return months.get(month_name, 0)