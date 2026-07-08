import base64
import os
import streamlit as st
from auth.login import login_user
from auth.register import register_siswa
from pages.admin.data_responden import data_responden
from pages.admin.data_komentar import data_komentar
from pages.admin.upload_komentar import upload_komentar
from pages.admin.hasil_sentimen import hasil_sentimen
from pages.admin.laporan import laporan
from pages.admin.manajemen_admin import manajemen_admin
from pages.siswa.survey import survey_siswa
from pages.siswa.riwayat_komentar import riwayat_komentar

from components.sidebar import (
    sidebar_admin,
    sidebar_siswa
)

from pages.admin.dashboard_admin import dashboard_admin
from pages.siswa.dashboard_siswa import dashboard_siswa

# ====================================
# KONFIGURASI HALAMAN
# ====================================
st.set_page_config(
    page_title="Survey Sentimen",
    page_icon="📊",
    layout="centered"
)

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #ff7b00,
        #ff9500,
        #ffb347
    );
}

</style>
""", unsafe_allow_html=True)

# LOAD CSS
with open("assets/style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# ====================================
# SESSION DEFAULT
# ====================================
if "login" not in st.session_state:
    st.session_state["login"] = False

if "role" not in st.session_state:
    st.session_state["role"] = None

if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "login"

# if st.session_state.get("register_msg") == "success":
#     st.success(st.session_state["register_text"])

#     # clear setelah tampil
#     st.session_state["register_msg"] = None
#     st.session_state["register_text"] = ""

# elif st.session_state.get("register_msg") == "error":
#     st.error(st.session_state["register_text"])

#     st.session_state["register_msg"] = None
#     st.session_state["register_text"] = ""

# ====================================
# SUDAH LOGIN
# ====================================
if st.session_state["login"]:

    # =================================
    # ADMIN
    # =================================
    if st.session_state["role"] == "admin":

        st.markdown("""
        <style>

        .stApp {
            background: #f5f7fb;
        }
                    
        section[data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #1e293b,
                #0f172a
            );
        }

        </style>
        """, unsafe_allow_html=True)

        menu = sidebar_admin()

        if menu == "📊 Dashboard":
            dashboard_admin()

        # elif menu == "👨‍🎓 Data Responden":
        #     data_responden()

        elif menu == "💬 Data Komentar":
            data_komentar()

        elif menu == "📂 Proses Upload File Komentar":
            upload_komentar()

        elif menu == "📈 Hasil Sentimen":
            hasil_sentimen()

        elif menu == "📄 Laporan":
            laporan()

        elif menu == "⚙️ Manajemen Admin":
            manajemen_admin()

        elif menu == "🚪 Logout":

            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    # =================================
    # SISWA
    # =================================
    elif st.session_state["role"] == "siswa":

        st.markdown("""
        <style>

        .stApp {
            background: #eef7ff;
        }
                    
        section[data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #2563eb,
                #1d4ed8
            );
        }

        </style>
        """, unsafe_allow_html=True)

        menu = sidebar_siswa()

        if menu == "🏠 Dashboard":
            dashboard_siswa()

        elif menu == "📝 Isi Survey":
            survey_siswa(st.session_state["id_responden"])

        elif menu == "📜 Riwayat Komentar":
            riwayat_komentar(st.session_state["id_responden"])

        elif menu == "🚪 Logout":

            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ====================================
# BELUM LOGIN
# ====================================
else:

    # ====================================
    # HEADER
    # ====================================
    st.markdown("""
    <div class="title">📊 Survey Sentimen</div>
    <div class="subtitle">
    Sistem Analisis Sentimen Modern & Elegan
    </div>
    """, unsafe_allow_html=True)

    # ====================================
    # CEK LOGO
    # ====================================
    logo_path = os.path.join("assets", "logo.png")

    if os.path.exists(logo_path):

        # ubah gambar jadi base64 supaya bisa full control center
        with open(logo_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()

        st.markdown(f"""
            <div style="display:flex; justify-content:center; margin-top:5px; margin-bottom:40px;">
                <img src="data:image/png;base64,{encoded}" width="180">
            </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown("""
            <div style="display:flex; justify-content:center; margin-top:20px;">
                <div style="
                    width:170px;
                    height:170px;
                    border-radius:50%;
                    background:rgba(255,255,255,0.1);
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:60px;
                    border:2px dashed white;
                ">
                    📷
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.warning("Logo belum tersedia")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Registrasi Siswa"])

    # ====================================
    # LOGIN
    # ====================================
    with tab1:

        st.subheader("Selamat Datang 👋")

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("🚀 Login Sekarang"):

            role, user = login_user(username, password)

            if role == "admin":

                if not st.session_state.get("login"):
                    st.session_state["login"] = True
                    st.session_state["role"] = "admin"
                    st.rerun()

            elif role == "siswa":

                if not st.session_state.get("login"):
                    st.session_state["login"] = True
                    st.session_state["role"] = "siswa"
                    st.session_state["id_responden"] = user["id_responden"]
                    st.rerun()

            else:
                st.error("❌ Username atau password salah")

    # ====================================
    # REGISTER
    # ====================================
    with tab2:

        st.subheader("Buat Akun Baru Siswa ✨")

        with st.form("form_register", clear_on_submit=True):

            nama = st.text_input("Nama Lengkap")
            sekolah = st.text_input("Sekolah")
            kelas = st.text_input("Kelas")

            reg_username = st.text_input("Username")
            reg_password = st.text_input("Password", type="password")

            submit = st.form_submit_button("🎉 Daftar Sekarang")

        if submit:

            sukses, pesan = register_siswa(
                nama,
                sekolah,
                kelas,
                reg_username,
                reg_password
            )

            if sukses:
                st.success("✅ Registrasi berhasil! Silakan login.")
            else:
                st.error(pesan)

    st.markdown("</div>", unsafe_allow_html=True)