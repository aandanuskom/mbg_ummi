import streamlit as st
import joblib
import re
import nltk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords
from database.koneksi import get_db
from datetime import datetime

# =========================
# SETUP NLP
# =========================
nltk.download("stopwords", quiet=True)

stop_words = set(stopwords.words("indonesian"))
factory = StemmerFactory()
stemmer = factory.create_stemmer()

def preprocess(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    tokens = [w for w in tokens if w not in stop_words]
    tokens = [stemmer.stem(w) for w in tokens]
    return " ".join(tokens)

# =========================
# LOAD MODEL
# =========================
@st.cache_resource
def load_model():
    tfidf = joblib.load("model/tfidf.pkl")
    model = joblib.load("model/model_svm.pkl")
    return tfidf, model

tfidf, model = load_model()

# =========================
# PREDIKSI FIX (TANPA predict_proba)
# =========================
def predict_sentimen(text):
    clean = preprocess(text)
    vec = tfidf.transform([clean])

    # =========================
    # PAKAI SVM SCORE
    # =========================
    scores = model.decision_function(vec)

    # multiclass
    if len(scores.shape) > 1:
        label_index = np.argmax(scores)
        confidence = float(np.max(scores))
    else:
        # binary SVM
        label_index = 1 if scores[0] > 0 else 0
        confidence = float(abs(scores[0]))

    label = model.classes_[label_index]

    return label, confidence

# =========================
# AMBIL DATA GRAFIK
# =========================
def get_data():
    conn = get_db()
    df = pd.read_sql("SELECT hasil FROM hasil_sentimen", conn)
    conn.close()
    return df

# =========================
# PAGE SISWA
# =========================
def survey_siswa(id_responden):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM komentar 
        WHERE id_responden = ?
    """, (id_responden,))

    sudah_isi = cursor.fetchone()["total"] > 0
    conn.close()

    st.title("📝 Isi Survey MBG")
    st.write("Silakan isi komentar Anda terkait MBG")
    st.divider()

    show_form = not sudah_isi

    if sudah_isi:
        st.warning("⚠️ Kamu sudah mengisi survey. Terima kasih 🙏")

    if show_form:

        komentar = st.text_area(
            "Tulis Komentar Anda",
            placeholder="Contoh: Makanan MBG sangat enak dan bergizi..."
        )

        if st.button("🚀 Kirim Survey"):

            if komentar.strip() == "":
                st.warning("Komentar tidak boleh kosong")

            else:
                conn = get_db()
                cursor = conn.cursor()

                # =========================
                # PREDIKSI
                # =========================
                hasil, confidence = predict_sentimen(komentar)

                # =========================
                # SIMPAN KOMENTAR
                # =========================
                cursor.execute("""
                    INSERT INTO komentar (id_responden, isi_komentar, tanggal)
                    VALUES (?, ?, ?)
                """, (
                    id_responden,
                    komentar,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

                id_komentar = cursor.lastrowid

                # =========================
                # SIMPAN HASIL
                # =========================
                cursor.execute("""
                    INSERT INTO hasil_sentimen (id_komentar, hasil, confidence)
                    VALUES (?, ?, ?)
                """, (
                    id_komentar,
                    hasil,
                    confidence
                ))

                conn.commit()
                conn.close()

                st.rerun()

        # =========================
        # TAMPIL HASIL
        # =========================

        conn = get_db()

        query = """
        SELECT hs.hasil
        FROM hasil_sentimen hs
        JOIN komentar k ON hs.id_komentar = k.id_komentar
        WHERE k.id_responden = ?
        ORDER BY hs.id_hasil DESC
        LIMIT 1
        """

        df_hasil = pd.read_sql(query, conn, params=(id_responden,))
        conn.close()

        if not df_hasil.empty:

            hasil = df_hasil.iloc[0]["hasil"].strip().upper()

            if hasil == "PUAS":
                st.success(f"😊 Hasil Sentimen: {hasil}")
            elif hasil == "NETRAL":
                st.info(f"😐 Hasil Sentimen: {hasil}")
            elif hasil == "TIDAK PUAS":
                st.error(f"😡 Hasil Sentimen: {hasil}")

    # =========================
    # GRAFIK
    # =========================
    st.divider()
    st.subheader("📊 Hasil Grafik Sentimen SVM")

    df = get_data()

    if df is None or df.empty:
        st.warning("📭 Belum ada data untuk ditampilkan")

    else:

        count = df["hasil"].value_counts()

        col1, col2 = st.columns(2)

        # =========================
        # PIE CHART
        # =========================
        with col1:
            st.markdown("### 🥧 Pie Chart")

            fig1, ax1 = plt.subplots()
            ax1.pie(count.values, labels=count.index, autopct="%1.1f%%")
            ax1.axis("equal")

            st.pyplot(fig1)

        # =========================
        # BAR CHART
        # =========================
        with col2:
            st.markdown("### 📊 Bar Chart")

            fig2, ax2 = plt.subplots()
            ax2.bar(count.index, count.values)
            ax2.set_ylabel("Jumlah")
            ax2.set_title("Distribusi Sentimen")

            st.pyplot(fig2)

            # =========================
            # KETERANGAN GRAFIK
            # =========================
            st.divider()
            st.subheader("📌 Keterangan Hasil Sentimen")

            total_data = count.sum()

            for label, jumlah in count.items():

                persentase = (jumlah / total_data) * 100

                # icon otomatis
                if str(label).upper() == "PUAS":
                    icon = "😊"
                elif str(label).upper() == "NETRAL":
                    icon = "😐"
                else:
                    icon = "😡"

                st.write(
                    f"{icon} Sentimen **{label}** sebanyak "
                    f"**{jumlah} data** atau sekitar "
                    f"**{persentase:.1f}%** dari total survey."
                )

            # =========================
            # KESIMPULAN OTOMATIS
            # =========================
            dominan = count.idxmax()
            persen_dominan = (count.max() / total_data) * 100

            st.success(
                f"📊 Mayoritas responden memberikan sentimen "
                f"**{dominan}** sebesar **{persen_dominan:.1f}%**."
            )
