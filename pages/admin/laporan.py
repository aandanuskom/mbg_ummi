import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from database.koneksi import get_db

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import enums
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle


def laporan():

    st.title("📄 Laporan Sentimen")
    st.write("Filter laporan berdasarkan tanggal")
    st.divider()

    # =========================
    # FILTER TANGGAL
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        tanggal_awal = st.date_input("Tanggal Awal")

    with col2:
        tanggal_akhir = st.date_input("Tanggal Akhir")

    # =========================
    # AMBIL DATA
    # =========================
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

    WHERE DATE(k.tanggal) BETWEEN DATE(?) AND DATE(?)

    ORDER BY k.tanggal ASC
    """

    df = pd.read_sql(
        query,
        conn,
        params=[
            str(tanggal_awal),
            str(tanggal_akhir)
        ]
    )

    conn.close()

    # =========================
    # HANDLE DATA KOSONG (INI YANG WAJIB FIX)
    # =========================
    if df is None or df.empty:

        st.warning("📭 Tidak ada data pada rentang tanggal ini")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("😊 PUAS", 0)
        with c2:
            st.metric("😐 NETRAL", 0)
        with c3:
            st.metric("😡 TIDAK PUAS", 0)

        return

    # =========================
    # NOMOR URUT
    # =========================
    df.index = range(1, len(df) + 1)

    # =========================
    # RENAME KOLOM
    # =========================
    df.columns = [
        "Nama",
        "Sekolah",
        "Kelas",
        "Komentar",
        "Hasil Sentimen",
        "Tanggal"
    ]

    st.divider()

    # =========================
    # RINGKASAN
    # =========================
    df["Hasil Sentimen"] = df["Hasil Sentimen"].astype(str).str.upper().str.strip()

    puas = len(df[df["Hasil Sentimen"] == "PUAS"])
    netral = len(df[df["Hasil Sentimen"] == "NETRAL"])
    tidak_puas = len(df[df["Hasil Sentimen"] == "TIDAK PUAS"])

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("😊 PUAS", puas)

    with c2:
        st.metric("😐 NETRAL", netral)

    with c3:
        st.metric("😡 TIDAK PUAS", tidak_puas)

    st.divider()

    # =========================
    # EXPORT EXCEL
    # =========================
    excel_buffer = BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=True, sheet_name="Laporan Sentimen")

    excel_buffer.seek(0)

    # =========================
    # EXPORT PDF (VERSI BAGUS)
    # =========================

    pdf_buffer = BytesIO()

    doc = SimpleDocTemplate(pdf_buffer)

    styles = getSampleStyleSheet()

    elements = []

    # =========================
    # JUDUL
    # =========================

    judul = Paragraph(
        "LAPORAN HASIL ANALISIS SENTIMEN",
        styles["Title"]
    )

    elements.append(judul)

    elements.append(
        Paragraph(
            f"Periode : {tanggal_awal} s/d {tanggal_akhir}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 15))

    # =========================
    # RINGKASAN
    # =========================

    elements.append(
        Paragraph(
            "<b>Ringkasan Sentimen</b>",
            styles["Heading2"]
        )
    )

    summary_data = [
        ["Kategori", "Jumlah"],
        ["PUAS", str(puas)],
        ["NETRAL", str(netral)],
        ["TIDAK PUAS", str(tidak_puas)],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[200, 100]
    )

    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))

    elements.append(summary_table)

    elements.append(Spacer(1, 20))

    # =========================
    # DATA TABEL
    # =========================

    elements.append(
        Paragraph(
            "<b>Data Hasil Sentimen</b>",
            styles["Heading2"]
        )
    )

    data = [[
        "No",
        "Nama",
        "Sekolah",
        "Kelas",
        "Sentimen",
        "Tanggal"
    ]]

    for i, row in df.iterrows():

        data.append([
            str(i),
            str(row["Nama"]),
            str(row["Sekolah"]),
            str(row["Kelas"]),
            str(row["Hasil Sentimen"]),
            str(row["Tanggal"])[:10]
        ])

    table = Table(
        data,
        colWidths=[
            30,
            80,
            100,
            60,
            70,
            80
        ]
    )

    table.setStyle(TableStyle([

        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1F4E78")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('ALIGN', (0,0), (-1,-1), 'CENTER'),

        ('GRID', (0,0), (-1,-1), 1, colors.black),

        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),

        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 20))

    # =========================
    # TOTAL DATA
    # =========================

    elements.append(
        Paragraph(
            f"<b>Total Responden :</b> {len(df)}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 30))

    right_style = ParagraphStyle(
        'RightAlign',
        parent=styles['Normal'],
        alignment=TA_RIGHT
    )

    elements.append(
        Paragraph(
            "Kisaran, " + str(tanggal_akhir),
            right_style
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            "Administrator",
            right_style
        )
    )

    elements.append(Spacer(1, 50))

    elements.append(
        Paragraph(
            "<b>_____________</b>",
            right_style
        )
    )

    # =========================
    # BUILD PDF
    # =========================

    doc.build(elements)

    pdf_buffer.seek(0)

    # =========================
    # BUTTON EXPORT
    # =========================
    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "📥 Export Excel",
            excel_buffer,
            file_name="laporan_sentimen.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with c2:
        st.download_button(
            "📄 Export PDF",
            pdf_buffer,
            file_name="laporan_sentimen.pdf",
            mime="application/pdf"
        )

    st.divider()

    # =========================
    # TABLE
    # =========================
    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )