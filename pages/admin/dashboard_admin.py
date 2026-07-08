import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database.koneksi import get_db

# ====================================
# CSS
# ====================================
st.markdown("""
<style>

/* Background */
.stApp{
    background: #f4f7fb;
}

/* Card metric */
div[data-testid="metric-container"] {

    background: linear-gradient(
        135deg,
        #ffffff,
        #f8fbff
    );

    border: none;

    padding: 25px;

    border-radius: 22px;

    box-shadow:
        0 10px 25px rgba(0,0,0,0.08);

    transition: 0.3s;

    border-left: 6px solid #3b82f6;
}

/* Hover */
div[data-testid="metric-container"]:hover {

    transform: translateY(-5px);

    box-shadow:
        0 15px 35px rgba(0,0,0,0.12);
}

/* Label metric */
div[data-testid="metric-container"] label {

    color: #64748b !important;

    font-weight: 600 !important;

    font-size: 15px !important;
}

/* Angka metric */
div[data-testid="metric-container"] [data-testid="stMetricValue"] {

    color: #0f172a;

    font-size: 34px;

    font-weight: bold;
}

/* Judul */
h1 {

    color: #0f172a;

    font-weight: 800;
}

/* Text */
p {
    color: #475569;
}

</style>
""", unsafe_allow_html=True)

# ====================================
# DASHBOARD ADMIN
# ====================================
def dashboard_admin():

    conn = get_db()
    cursor = conn.cursor()

    # =========================
    # DATA
    # =========================
    cursor.execute("SELECT COUNT(*) as total FROM responden")
    total_responden = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM komentar")
    total_komentar = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM hasil_sentimen")
    total_hasil = cursor.fetchone()["total"]

    query = """
    SELECT hasil, COUNT(*) as jumlah
    FROM (
        SELECT h.hasil
        FROM hasil_sentimen h
        JOIN komentar k ON h.id_komentar = k.id_komentar
        ORDER BY k.tanggal ASC
    )
    GROUP BY hasil
    """

    df_sentimen = pd.read_sql(query, conn)
    conn.close()

    # =========================
    # STYLE MODERN
    # =========================
    st.markdown("""
    <style>

    .title-admin {
        font-size: 34px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 5px;
    }

    .subtitle-admin {
        color: #64748b;
        margin-bottom: 20px;
    }

    .card {
        background: linear-gradient(135deg, #ffffff, #f8fbff);
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border-left: 6px solid #3b82f6;
        transition: 0.3s;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.12);
    }

    .big-number {
        font-size: 34px;
        font-weight: 800;
        color: #0f172a;
    }

    .label {
        color: #64748b;
        font-weight: 600;
    }

    </style>
    """, unsafe_allow_html=True)

    # =========================
    # HEADER
    # =========================
    st.markdown('<div class="title-admin">📊 Dashboard Admin</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-admin">Monitoring sistem survey MBG secara realtime</div>', unsafe_allow_html=True)

    st.divider()

    # =========================
    # KPI CARDS
    # =========================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="label">👨‍🎓 Total Responden</div>
            <div class="big-number">{total_responden}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="label">💬 Total Komentar</div>
            <div class="big-number">{total_komentar}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card">
            <div class="label">📈 Total Hasil Analisis</div>
            <div class="big-number">{total_hasil}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # =========================
    # GRAFIK
    # =========================
    st.subheader("📊 Analisis Sentimen Hari Ini")

    col1, col2 = st.columns(2)

    if df_sentimen.empty:
        st.warning("Belum ada data hari ini")
        return

    # PIE
    with col1:
        fig1, ax1 = plt.subplots()
        ax1.pie(df_sentimen["jumlah"], labels=df_sentimen["hasil"], autopct="%1.1f%%")
        ax1.axis("equal")
        st.pyplot(fig1)

    # BAR
    with col2:
        fig2, ax2 = plt.subplots()
        ax2.bar(df_sentimen["hasil"], df_sentimen["jumlah"])
        ax2.set_ylabel("Jumlah")
        st.pyplot(fig2)

    st.divider()

    # =========================
    # TABLE MODERN
    # =========================
    st.subheader("📋 Detail Sentimen")

    st.dataframe(
        df_sentimen,
        width="stretch",
        hide_index=True
    )