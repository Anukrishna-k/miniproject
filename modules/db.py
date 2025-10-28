import psycopg2
import psycopg2.extras
import hashlib

def connect_db():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        host="localhost",
        user="postgres",
        password="root",
        database="eventsdb" 
    )

def get_dict_cursor(db):
    """Return a dictionary cursor"""
    return db.cursor(cursor_factory=psycopg2.extras.DictCursor)

def hash_password(password: str) -> str:
    """Hash password with SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()