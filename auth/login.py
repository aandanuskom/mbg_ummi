import bcrypt
from database.koneksi import get_db

def login_user(username, password):

    conn = get_db()
    cursor = conn.cursor()

    # ======================
    # CEK ADMIN
    # ======================
    cursor.execute(
        "SELECT * FROM admin WHERE username=?",
        (username,)
    )

    admin = cursor.fetchone()

    if admin:
        if bcrypt.checkpw(
            password.encode('utf-8'),
            admin["password"]
        ):
            return "admin", admin

    # ======================
    # CEK SISWA
    # ======================
    cursor.execute(
        "SELECT * FROM responden WHERE username=?",
        (username,)
    )

    siswa = cursor.fetchone()

    if siswa:
        if bcrypt.checkpw(
            password.encode('utf-8'),
            siswa["password"]
        ):
            return "siswa", siswa

    return None, None