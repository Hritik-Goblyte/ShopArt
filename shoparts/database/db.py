import sqlite3
import datetime

# Register datetime handlers
sqlite3.register_adapter(datetime.datetime, lambda dt: dt.isoformat())
sqlite3.register_converter("timestamp", lambda s: datetime.datetime.fromisoformat(s.decode("utf-8")))

def get_connection():
    return sqlite3.connect("shop.db", detect_types=sqlite3.PARSE_DECLTYPES)