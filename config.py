import os
# Secret key
SECRET_KEY = os.getenv('SECRET_KEY')

# Database configuration
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_KEY')
DB_NAME = os.getenv('DB_NAME')

# reCAPTCHA keys
CAPTCHA_SITE_KEY = os.getenv('CAPTCHA_SITE_KEY')
CAPTCHA_SECRET_KEY = os.getenv('CAPTCHA_SECRET_KEY')