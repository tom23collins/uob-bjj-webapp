from dotenv import load_dotenv
import os

# Load environment variables from .env file in the project root
load_dotenv()

# Secret key
SECRET_KEY = os.getenv('SECRET_KEY', 'local-demo-secret-key')

# This account is kept as the club's permanent administrator. Override only
# if the deployment is being reused for a different club.
PERMANENT_ADMIN_EMAIL = os.getenv('PERMANENT_ADMIN_EMAIL', 'txc282@student.bham.ac.uk').strip().lower()

# Use SQLite locally when PostgreSQL is not configured.
DATABASE_URL = os.getenv('DATABASE_URL')
PG_HOST = os.getenv('AZURE_POSTGRES_HOST', os.getenv('PGHOST'))
PG_PORT = os.getenv('AZURE_POSTGRES_PORT', os.getenv('PGPORT', '5432'))
PG_USER = os.getenv('AZURE_POSTGRES_USER', os.getenv('PGUSER'))
PG_PASSWORD = os.getenv('AZURE_POSTGRES_PASSWORD', os.getenv('PGPASSWORD'))
PG_DATABASE = os.getenv('AZURE_POSTGRES_DB', os.getenv('PGDATABASE'))
PG_SSLMODE = os.getenv('PGSSLMODE', 'require')
POSTGRES_MODE = bool(DATABASE_URL or PG_HOST)
DEMO_MODE = os.getenv('DEMO_MODE', '0') == '1' or not POSTGRES_MODE
SQLITE_PATH = os.getenv('SQLITE_PATH', os.path.join(os.path.dirname(__file__), 'instance', 'demo.sqlite3'))

# Email config (MAIL_KEY must be set in .env)
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'welcome.uobbjj@gmail.com'
MAIL_KEY = os.getenv('MAIL_KEY')

# Public links used by the Linktree-style landing page.
INSTAGRAM_URL = os.getenv('INSTAGRAM_URL', 'https://instagram.com/uob_bjj')
WHATSAPP_URL = os.getenv('WHATSAPP_URL', 'https://linktr.ee/uobbjj')
MEMBERSHIP_URL = os.getenv('MEMBERSHIP_URL', 'https://www.usbonline.bham.ac.uk/JoinAtHome/')
