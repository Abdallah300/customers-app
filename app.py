import sqlite3

# إنشاء قاعدة البيانات
conn = sqlite3.connect("app.db")
c = conn.cursor()

# جداول
c.execute("""CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT,
    company_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id)
)""")

c.execute("""CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    lat REAL,
    lon REAL,
    notes TEXT,
    category TEXT,
    last_visit DATE,
    company_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id)
)""")

conn.commit()
