import bcrypt
import streamlit as st
import pandas as pd
from database.koneksi import get_db

def manajemen_admin():

    conn = get_db()

    st.title("⚙️ Manajemen Admin")

    # =========================
    # AMBIL DATA ADMIN
    # =========================
    df = pd.read_sql("""
        SELECT id_admin, nama_admin, username, password
        FROM admin
        ORDER BY id_admin DESC
    """, conn)

    df.index = range(1, len(df) + 1)

    st.subheader("📋 Data Admin")
    st.dataframe(
        df[["id_admin", "nama_admin", "username"]],
        width="stretch"
    )

    st.divider()

    # =========================
    # EDIT ADMIN
    # =========================
    st.subheader("✏️ Edit Admin")

    list_admin = df["id_admin"].tolist()

    id_admin = st.selectbox("Pilih Admin", list_admin)

    # ambil data terpilih
    admin_data = df[df["id_admin"] == id_admin].iloc[0]

    nama_admin = st.text_input("Nama Admin", admin_data["nama_admin"])
    username = st.text_input("Username", admin_data["username"])

    # kosongkan password
    password = st.text_input("Password Baru", type="password")

    if st.button("💾 Update Admin"):

        # =========================
        # PASSWORD TIDAK DIUBAH
        # =========================
        if password.strip() == "":

            conn.execute("""
                UPDATE admin
                SET nama_admin = ?,
                    username = ?
                WHERE id_admin = ?
            """, (nama_admin, username, id_admin))

        else:

            # =========================
            # HASH PASSWORD BARU
            # =========================
            hashed_password = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            )

            conn.execute("""
                UPDATE admin
                SET nama_admin = ?,
                    username = ?,
                    password = ?
                WHERE id_admin = ?
            """, (
                nama_admin,
                username,
                hashed_password,
                id_admin
            ))

        conn.commit()

        st.success("Admin berhasil diupdate")
        st.rerun()

    conn.close()