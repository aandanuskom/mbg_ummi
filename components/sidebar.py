import streamlit as st

# ====================================
# SIDEBAR ADMIN
# ====================================
def sidebar_admin():

    st.sidebar.markdown("""
    # 🛠️ Admin Panel
    """)

    menu = st.sidebar.radio(
        "Menu Admin",
        [
            "📊 Dashboard",
            # "👨‍🎓 Data Responden",
            "💬 Data Komentar",
            "📂 Proses Upload File Komentar",
            "📈 Hasil Sentimen",
            "📄 Laporan",
            "⚙️ Manajemen Admin",
            "🚪 Logout"
        ],
        label_visibility="collapsed"
    )

    return menu


# ====================================
# SIDEBAR SISWA
# ====================================
def sidebar_siswa():

    st.sidebar.markdown("""
    # 👨‍🎓 Menu Siswa
    """)

    menu = st.sidebar.radio(
        "Menu Siswa",
        [
            "🏠 Dashboard",
            "📝 Isi Survey",
            "📜 Riwayat Komentar",
            "🚪 Logout"
        ],
        label_visibility="collapsed"
    )

    return menu