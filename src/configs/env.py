import os
from dotenv import load_dotenv



load_dotenv()


DB_URI = str(os.getenv("DB_URI"))

JWT_ACCESS_EXPIRY = int(os.getenv('JWT_ACCESS_EXPIRY'))
JWT_REFRESH_EXPIRY = int(os.getenv('JWT_REFRESH_EXPIRY'))
JWT_ACCESS_SECRET = str(os.getenv('JWT_ACCESS_SECRET'))
JWT_ALGORITHM = str(os.getenv('JWT_ALGORITHM'))
ENCRYPTION_KEY = str(os.getenv('ENCRYPTION_KEY'))

ADMIN_EMAIL = str(os.getenv("ADMIN_EMAIL"))
ADMIN_FIRSTNAME = str(os.getenv("ADMIN_FIRSTNAME"))
ADMIN_LASTNAME = str(os.getenv("ADMIN_LASTNAME"))
ADMIN_PASSWORD = str(os.getenv("ADMIN_PASSWORD"))
ADMIN_PHONENUMBER = str(os.getenv("ADMIN_PHONENUMBER"))