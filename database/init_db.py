import bcrypt
from koneksi import get_db

conn = get_db()
cursor = conn.cursor()

# =========================
# TABEL ADMIN
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id_admin INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    nama_admin TEXT
)
""")

# =========================
# TABEL RESPONDEN
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS responden (
    id_responden INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    sekolah TEXT,
    kelas TEXT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# =========================
# TABEL KOMENTAR
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS komentar (
    id_komentar INTEGER PRIMARY KEY AUTOINCREMENT,
    id_responden INTEGER,
    isi_komentar TEXT,
    tanggal DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(id_responden)
    REFERENCES responden(id_responden)
)
""")

# =========================
# TABEL HASIL SENTIMEN
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS hasil_sentimen (
    id_hasil INTEGER PRIMARY KEY AUTOINCREMENT,
    id_komentar INTEGER,
    hasil TEXT,
    confidence REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(id_komentar)
    REFERENCES komentar(id_komentar)
)
""")

# =========================
# CEK ADMIN DEFAULT
# =========================
cursor.execute(
    "SELECT * FROM admin WHERE username=?",
    ("admin",)
)

cek_admin = cursor.fetchone()

if not cek_admin:

    password_admin = bcrypt.hashpw(
        "admin123".encode('utf-8'),
        bcrypt.gensalt()
    )

    cursor.execute("""
    INSERT INTO admin
    (username, password, nama_admin)

    VALUES (?, ?, ?)
    """, (
        "admin",
        password_admin,
        "Administrator"
    ))

    print("Admin default berhasil dibuat")

conn.commit()
conn.close()

print("Database berhasil dibuat")