from os import environ
from os import path
from dotenv import load_dotenv

load_dotenv()

DB_LOCATION = environ.get('DB_LOCATION', path.abspath('./shared/db.sqlite3'))
TOKEN = environ.get('TOKEN')

packed_parameters = {
    'db_location': DB_LOCATION,
    'token': TOKEN
}
