import os
# Secret key
SECRET_KEY = os.getenv('SECRET_KEY')

# Database configuration
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_KEY')
DB_NAME = os.getenv('DB_NAME')

# Email config
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'welcome.uobbjj@gmail.com'
MAIL_KEY = os.getenv('MAIL_KEY')