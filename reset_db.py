from database.koneksi import get_db

conn = get_db()
cursor = conn.cursor()

# =========================
# MATIKAN FOREIGN KEY (WAJIB)
# =========================
cursor.execute("PRAGMA foreign_keys = OFF")

# =========================
# HAPUS DATA TRANSAKSI
# =========================
cursor.execute("DELETE FROM hasil_sentimen")
cursor.execute("DELETE FROM komentar")
cursor.execute("DELETE FROM responden")

# =========================
# OPTIONAL: reset auto increment
# =========================
cursor.execute("DELETE FROM sqlite_sequence WHERE name='hasil_sentimen'")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='komentar'")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='responden'")

# =========================
# AKTIFKAN LAGI FOREIGN KEY
# =========================
cursor.execute("PRAGMA foreign_keys = ON")

conn.commit()
conn.close()

print("Database berhasil di-reset (admin aman)")