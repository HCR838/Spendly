import sqlite3
import os
from werkzeug.security import generate_password_hash


def get_db():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(BASE_DIR, "spendly.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
    if row[0] > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    expenses = [
        (user_id, 12.50,  "Food",          "2026-05-10", "Lunch at campus canteen"),
        (user_id, 45.00,  "Bills",         "2026-05-09", "Monthly internet bill"),
        (user_id,  8.75,  "Transport",     "2026-05-09", "Bus pass top-up"),
        (user_id, 29.99,  "Shopping",      "2026-05-08", "New notebook and pens"),
        (user_id, 15.00,  "Health",        "2026-05-07", "Pharmacy — vitamins"),
        (user_id, 22.00,  "Entertainment", "2026-05-06", "Movie ticket"),
        (user_id,  6.30,  "Food",          "2026-05-05", "Coffee and snacks"),
        (user_id, 18.00,  "Other",         "2026-05-04", "Miscellaneous supplies"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    conn.commit()
    conn.close()


def get_user_by_email(email: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row


def create_user(name: str, email: str, password: str) -> int:
    conn = get_db()
    password_hash = generate_password_hash(password)
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash),
    )
    conn.commit()
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return user_id
