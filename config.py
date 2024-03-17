from os import environ
from os import path

DATABASE_FOLDER = environ.get('DB_LOCATION', path.abspath('./shared/db.sqlite3'))