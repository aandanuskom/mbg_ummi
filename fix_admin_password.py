import sqlite3
import bcrypt
import os

# cek lokasi file database
db_path = "database/survey_sentimen.db"

print("Database ditemukan:", os.path.exists(db_path))

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# lihat tabel
cursor.execute("""
SELECT name FROM sqlite_master WHERE type='table'
""")

print(cursor.fetchall())

# password baru
password_baru = "admin123"

hashed_password = bcrypt.hashpw(
    password_baru.encode('utf-8'),
    bcrypt.gensalt()
)

# update admin
cursor.execute("""
UPDATE admin
SET password = ?
WHERE username = ?
""", (
    hashed_password,
    "admin"
))

conn.commit()

print("Password berhasil diperbaiki!")

conn.close()