import bcrypt
from database.koneksi import get_db

def register_siswa(nama, sekolah, kelas, username, password):

    conn = get_db()
    cursor = conn.cursor()

    # =========================
    # CEK DUPLIKAT LENGKAP
    # =========================
    cursor.execute("""
        SELECT * FROM responden
        WHERE LOWER(username)=?
           OR (
                LOWER(nama)=?
                AND LOWER(sekolah)=?
                AND LOWER(kelas)=?
           )
    """, (
        username.lower(),
        nama.lower(),
        sekolah.lower(),
        kelas.lower()
    ))

    user = cursor.fetchone()

    if user:
        return False, "Data sudah terdaftar / username sudah digunakan"

    # =========================
    # HASH PASSWORD
    # =========================
    hashed = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )

    # =========================
    # SIMPAN
    # =========================
    cursor.execute("""
        INSERT INTO responden
        (nama, sekolah, kelas, username, password)
        VALUES (?, ?, ?, ?, ?)
    """, (
        nama,
        sekolah,
        kelas,
        username,
        hashed
    ))

    conn.commit()
    conn.close()

    return True, "Registrasi berhasil! Silakan login."