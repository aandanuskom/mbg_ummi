import streamlit as st
import pandas as pd

from database.koneksi import get_db

def data_responden():

    conn = get_db()

    query = """
    SELECT 
        nama,
        sekolah,
        kelas,
        username
    FROM responden
    ORDER BY nama ASC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    # =========================
    # NOMOR URUT
    # =========================
    df.index = range(1, len(df) + 1)

    # =========================
    # TITLE
    # =========================
    st.title("👨‍🎓 Data Responden")

    st.write("Daftar seluruh siswa responden")

    st.divider()

    # =========================
    # TABEL
    # =========================
    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )