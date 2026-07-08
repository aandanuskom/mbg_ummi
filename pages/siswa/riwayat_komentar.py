import streamlit as st
import pandas as pd
from database.koneksi import get_db

def riwayat_komentar(id_responden):

    conn = get_db()

    query = """
        SELECT 
            k.isi_komentar,
            hs.hasil,
            k.tanggal
        FROM komentar k
        LEFT JOIN hasil_sentimen hs 
            ON k.id_komentar = hs.id_komentar
        WHERE k.id_responden = ?
        ORDER BY k.tanggal DESC
    """

    df = pd.read_sql(query, conn, params=(id_responden,))
    conn.close()

    st.title("📜 Riwayat Komentar")

    if df.empty:
        st.info("Belum ada komentar")
        return

    # =========================
    # STYLE TABLE
    # =========================
    st.markdown("""
    <style>
    .riwayat-table {
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )