# for easy logging, to convert log requests to text containing system status and logs
class Logger:
    def __init__(self):
        ...
import sqlite3
connection = sqlite3.connect('./shared/db.sqlite3')