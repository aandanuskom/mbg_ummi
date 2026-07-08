import streamlit as st
import pandas as pd
import numpy as np
import joblib
import sqlite3
import re
import math
from collections import Counter
from io import BytesIO

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet

from database.koneksi import get_db


# =========================
# MODEL
# =========================
model = joblib.load("model/model_svm.pkl")
vectorizer = joblib.load("model/tfidf.pkl")


# =========================
# DB SQLITE
# =========================
conn = get_db()
cursor = conn.cursor()


# =========================
# NLP SETUP
# =========================
factory = StemmerFactory()
stemmer = factory.create_stemmer()

stop_words = set(["yang", "dan", "di", "ke", "dari"])


# =========================
# PREPROCESS DETAIL (LAMAMU STYLE)
# =========================
def preprocessing_detail(text):

    if pd.isna(text):
        text = ""

    case_folding = str(text).lower()

    cleaned = re.sub(r'[^a-zA-Z ]', '', case_folding)

    tokens = cleaned.split()

    stop_removed = [w for w in tokens if w not in stop_words]

    stemming = [stemmer.stem(w) for w in stop_removed]

    return case_folding, tokens, stop_removed, stemming


# =========================
# CEK DUPLIKAT DB
# =========================
def cek_duplikat(nama, sekolah, kelas, komentar):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT k.id_komentar
        FROM komentar k
        JOIN responden r ON k.id_responden = r.id_responden
        WHERE LOWER(TRIM(r.nama)) = ?
          AND LOWER(TRIM(r.sekolah)) = ?
          AND LOWER(TRIM(r.kelas)) = ?
          AND LOWER(TRIM(k.isi_komentar)) = ?
        LIMIT 1
    """, (
        nama.lower(),
        sekolah.lower(),
        kelas.lower(),
        komentar.lower()
    ))

    return cursor.fetchone() is not None

# =========================
# TF-IDF DETAIL (SCROLL STYLE)
# =========================
def tfidf_detail(docs):

    clean_docs = [" ".join([stemmer.stem(w) for w in str(d).lower().split()]) for d in docs]

    X = vectorizer.transform(clean_docs)
    feature = vectorizer.get_feature_names_out()

    result_all = []

    for i, row in enumerate(X):

        scores = row.toarray()[0]
        top = scores.argsort()[::-1][:10]

        hasil = []

        for idx in top:
            if scores[idx] > 0:
                hasil.append({
                    "Kata": feature[idx],
                    "TF-IDF": round(scores[idx], 4)
                })

        result_all.append(hasil)

    return clean_docs, result_all


# =========================
# EXPORT EXCEL
# =========================
def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Hasil")
    return output.getvalue()


# =========================
# EXPORT PDF
# =========================
def export_pdf(df):

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter)
    )

    elements = []

    # =========================
    # HEADER KOLOM
    # =========================
    header = list(df.columns)

    data = [header]

    # =========================
    # ISI DATA
    # =========================
    for _, row in df.iterrows():
        data.append(list(map(str, row.values)))

    # =========================
    # BIKIN TABLE
    # =========================
    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 7),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))

    elements.append(table)

    pdf.build(elements)

    buffer.seek(0)
    return buffer

def upload_komentar():
    # =========================
    # MAIN APP
    # =========================
    st.title("📂 Upload Komentar Sentimen")

    file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])

    if file:

        df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

        st.subheader("Preview Data")
        st.dataframe(df, use_container_width=True)

        # =========================
        # NORMALISASI KOLOM
        # =========================
        df.columns = df.columns.str.strip().str.lower()

        # =========================
        # DETEKSI KOLOM KOMENTAR
        # =========================
        kolom_komentar = None

        for col in df.columns:
            if "komentar" in col:
                kolom_komentar = col
                break

        if kolom_komentar is None:
            st.error("Kolom komentar tidak ditemukan (harus ada kata 'komentar')")
            st.stop()

        # rename jadi standar
        df.rename(columns={
            kolom_komentar: "komentar"
        }, inplace=True)

        df["nama"] = df.get("nama", "anonim")
        df["sekolah"] = df.get("sekolah", "-")
        df["kelas"] = df.get("kelas", "-")

        # =========================
        # CEK DUPLIKAT + FILTER
        # =========================
        filtered_rows = []

        for _, row in df.iterrows():

            if not cek_duplikat(row["nama"], row["sekolah"], row["kelas"], row["komentar"]):
                filtered_rows.append(row)

        df = pd.DataFrame(filtered_rows).reset_index(drop=True)

        if df.empty:
            st.warning("Semua data sudah ada di database (duplikat)")
            st.stop()

        # =========================
        # PREPROCESS DETAIL (TABEL)
        # =========================
        hasil_pre = df["komentar"].apply(preprocessing_detail)

        df_pre = pd.DataFrame({
            "Original": df["komentar"],
            "Case Folding": [x[0] for x in hasil_pre],
            "Tokenizing": [x[1] for x in hasil_pre],
            "Stopword Removal": [x[2] for x in hasil_pre],
            "Stemming": [x[3] for x in hasil_pre],
        })

        df_pre["Clean Text"] = df_pre["Stemming"].apply(lambda x: " ".join(x))

        st.subheader("1. Preprocessing Detail")
        st.dataframe(df_pre, use_container_width=True)

        # =========================
        # TF-IDF DETAIL (SCROLL)
        # =========================
        st.subheader("2. TF-IDF Detail")

        clean_docs, tfidf_result = tfidf_detail(df["komentar"])

        with st.container(height=500):

            for i in range(len(df)):
                st.write(f"{df['komentar'][i]}")
                st.dataframe(pd.DataFrame(tfidf_result[i]))
                st.markdown("---")

        # =========================
        # PREDIKSI
        # =========================
        X = vectorizer.transform(clean_docs)
        pred = model.predict(X)

        df["hasil"] = pred

        st.subheader("3. Hasil Prediksi")
        st.dataframe(df, use_container_width=True)

        # =========================
        # SIMPAN DATABASE
        # =========================
        sukses = 0

        for _, row in df.iterrows():

            cursor.execute("""
                INSERT INTO responden (nama, sekolah, kelas)
                VALUES (?, ?, ?)
            """, (row["nama"], row["sekolah"], row["kelas"]))

            id_r = cursor.lastrowid

            cursor.execute("""
                INSERT INTO komentar (id_responden, isi_komentar)
                VALUES (?, ?)
            """, (id_r, row["komentar"]))

            id_k = cursor.lastrowid

            cursor.execute("""
                INSERT INTO hasil_sentimen (id_komentar, hasil)
                VALUES (?, ?)
            """, (id_k, row["hasil"]))

            sukses += 1

        conn.commit()

        st.success(f"Berhasil simpan {sukses} data baru")

        # =========================
        # EXPORT
        # =========================
        st.download_button(
            "⬇ Export Excel",
            data=export_excel(df),
            file_name="hasil_sentimen.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.download_button(
            "⬇ Export PDF",
            data=export_pdf(df),
            file_name="hasil_sentimen.pdf",
            mime="application/pdf"
        )