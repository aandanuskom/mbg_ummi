import streamlit as st
import pandas as pd

from database.koneksi import get_db

def hasil_sentimen():

    conn = get_db()

    query = """
    SELECT 
        r.nama,
        r.sekolah,
        r.kelas,
        k.isi_komentar,
        h.hasil,
        k.tanggal

    FROM hasil_sentimen h

    JOIN komentar k
        ON h.id_komentar = k.id_komentar

    JOIN responden r
        ON k.id_responden = r.id_responden

    ORDER BY h.id_hasil ASC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    # =========================
    # NOMOR URUT
    # =========================
    df.index = range(1, len(df) + 1)

    # =========================
    # GANTI NAMA KOLOM
    # =========================
    df.columns = [
        "Nama",
        "Sekolah",
        "Kelas",
        "Komentar",
        "Hasil Sentimen",
        # "Confidence",
        "Tanggal"
    ]

    # =========================
    # TITLE
    # =========================
    st.title("📈 Hasil Sentimen")

    st.write("Hasil klasifikasi sentimen metode SVM")

    st.divider()

    # =========================
    # TABEL
    # =========================
    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )