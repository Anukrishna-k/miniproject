#db.py
import mysql.connector
import hashlib

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="evenstdb"
    )

def get_dict_cursor(db):
    """Return a dictionary cursor"""
    return db.cursor(dictionary=True)

def hash_password(password: str) -> str:
    """Hash password with SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()
