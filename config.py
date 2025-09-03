from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Secret key
SECRET_KEY = os.getenv('SECRET_KEY')

# Database configuration
DB_HOST = os.getenv('AZURE_MYSQL_HOST')
DB_USER = os.getenv('AZURE_MYSQL_USER')
DB_PASSWORD = os.getenv('AZURE_MYSQL_PASSWORD')
DB_NAME = os.getenv('AZURE_MYSQL_DB')

# Email config
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'welcome.uobbjj@gmail.com'
MAIL_KEY = os.getenv('MAIL_KEY')