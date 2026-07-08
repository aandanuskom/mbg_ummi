import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database.koneksi import get_db

def dashboard_siswa():

    conn = get_db()
    cursor = conn.cursor()

    id_siswa = st.session_state.get("id_responden")

    # =========================
    # DATA TOTAL SURVEY SISWA
    # =========================
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM komentar 
        WHERE id_responden = ?
    """, (id_siswa,))

    total_survey = cursor.fetchone()["total"]

    # =========================
    # DATA SENTIMEN
    # =========================
    cursor.execute("""
        SELECT hasil, COUNT(*) as jumlah
        FROM hasil_sentimen
        GROUP BY hasil
    """)

    data_sentimen = cursor.fetchall()

    conn.close()

    # =========================
    # STYLE
    # =========================
    st.markdown("""
    <style>

    .dashboard-card {
        background: linear-gradient(135deg, #ffffff, #f0f7ff);
        padding: 25px;
        border-radius: 18px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border-left: 6px solid #2563eb;
        transition: 0.3s;
    }

    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.12);
    }

    .big-number {
        font-size: 42px;
        font-weight: bold;
        color: #1e3a8a;
    }

    .label {
        font-size: 16px;
        color: #64748b;
        font-weight: 600;
    }

    .welcome {
        font-size: 28px;
        font-weight: 700;
        color: #0f172a;
    }

    </style>
    """, unsafe_allow_html=True)

    # =========================
    # HEADER
    # =========================
    st.markdown('<div class="welcome">🧑‍🎓 Dashboard Siswa</div>', unsafe_allow_html=True)
    st.write("Selamat datang di sistem survey MBG 👋")
    st.divider()

    # =========================
    # CARD
    # =========================
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="label">Total Survey Kamu</div>
            <div class="big-number">{total_survey}</div>
            <div style="color:#64748b; margin-top:10px;">
                Status: {"Sudah mengisi survey" if total_survey > 0 else "Belum mengisi survey"}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <div class="label">Aksi Cepat</div>
            <br>
            👉 Isi survey sekarang<br>
            👉 Lihat hasil analisis<br>
            👉 Pantau riwayat
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # =========================
    # GRAFIK SENTIMEN
    # =========================
    st.subheader("📊 Statistik Kepuasan Survey")

    if data_sentimen:

        df = pd.DataFrame(data_sentimen, columns=["hasil", "jumlah"])

        total = df["jumlah"].sum()

        # Hitung persentase
        df["persentase"] = (df["jumlah"] / total) * 100

        # =========================
        # PIE CHART
        # =========================
        col1, col2, col3 = st.columns([1,2,1])

        with col2:

            fig, ax = plt.subplots(figsize=(3.5,3.5))

            ax.pie(
                df["jumlah"],
                labels=df["hasil"],
                autopct='%1.1f%%',
                startangle=90
            )

            ax.axis('equal')

            st.pyplot(fig)

        # =========================
        # KETERANGAN
        # =========================
        st.markdown("### 📌 Keterangan")

        for index, row in df.iterrows():
            st.write(
                f"- {row['persentase']:.1f}% responden merasa **{row['hasil']}** "
                f"sebanyak {row['jumlah']} data."
            )

    else:
        st.warning("Belum ada data sentimen.")

    st.divider()

    # =========================
    # INFO
    # =========================
    if total_survey == 0:
        st.info("📝 Kamu belum mengisi survey. Silakan isi sekarang untuk memberikan penilaian.")
    else:
        st.success("🎉 Terima kasih sudah mengisi survey!")