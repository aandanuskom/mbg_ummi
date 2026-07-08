import streamlit as st
import pandas as pd

from database.koneksi import get_db


def data_komentar():

    # =========================
    # AMBIL DATA
    # =========================
    conn = get_db()

    query = """
    SELECT
        k.id_komentar,
        r.nama,
        r.sekolah,
        r.kelas,
        k.isi_komentar,
        k.tanggal
    FROM komentar k
    JOIN responden r
        ON k.id_responden = r.id_responden
    ORDER BY k.id_komentar ASC
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # =========================
    # TITLE
    # =========================
    st.title("💬 Data Komentar")
    st.write("Daftar komentar siswa")
    st.divider()

    st.markdown(
        "<h5 style='color:black;'>🔍 Cari Data</h5>",
        unsafe_allow_html=True
    )

    search = st.text_input(
        "",
        placeholder="Cari Nama / Sekolah / Komentar",
        label_visibility="collapsed"
    )

    if search:
        df = df[
            df["nama"].str.contains(search, case=False, na=False)
            |
            df["sekolah"].str.contains(search, case=False, na=False)
            |
            df["isi_komentar"].str.contains(search, case=False, na=False)
        ]

        if search:
            st.session_state.page_komentar = 1

    # =========================
    # PAGINATION
    # =========================

    PAGE_SIZE = 10

    if "page_komentar" not in st.session_state:
        st.session_state.page_komentar = 1

    total_data = len(df)

    total_page = (
        total_data + PAGE_SIZE - 1
    ) // PAGE_SIZE

    start = (
        st.session_state.page_komentar - 1
    ) * PAGE_SIZE

    end = start + PAGE_SIZE

    df_page = df.iloc[start:end]

    # =========================
    # HEADER TABEL
    # =========================
    col1, col2, col3, col4, col5, col6, col7 = st.columns(
        [1, 2, 2, 1, 5, 2, 1]
    )

    col1.markdown("**No**")
    col2.markdown("**Nama**")
    col3.markdown("**Sekolah**")
    col4.markdown("**Kelas**")
    col5.markdown("**Komentar**")
    col6.markdown("**Tanggal**")
    col7.markdown("**Aksi**")

    st.divider()

    # =========================
    # TAMPIL DATA
    # =========================
    for no, row in enumerate(
        df_page.itertuples(),
        start=start + 1
    ):

        col1, col2, col3, col4, col5, col6, col7 = st.columns(
            [1, 2, 2, 1, 5, 2, 1]
        )

        col1.write(no)
        col2.write(row.nama)
        col3.write(row.sekolah)
        col4.write(row.kelas)
        col5.write(row.isi_komentar)
        col6.write(str(row.tanggal))

        if col7.button(
            "✏️",
            key=f"edit_{row.id_komentar}"
        ):
            st.session_state.edit_id = row.id_komentar
            st.session_state.edit_komentar = row.isi_komentar

        st.divider()


    # =========================
    # PAGINATION
    # =========================

    if total_page > 0:

        col1, col2, col3 = st.columns([1,2,1])

        with col1:

            if st.button(
                "⬅ Previous",
                key="prev_page",
                disabled=st.session_state.page_komentar == 1
            ):
                st.session_state.page_komentar -= 1
                st.rerun()

        with col2:

            st.markdown(
                f"""
                <div style='text-align:center'>
                    Halaman {st.session_state.page_komentar}
                    dari {total_page}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:

            if st.button(
                "Next ➡",
                key="next_page",
                disabled=st.session_state.page_komentar >= total_page
            ):
                st.session_state.page_komentar += 1
                st.rerun()

    # =========================
    # POPUP EDIT
    # =========================
    if "edit_id" in st.session_state:

        @st.dialog("✏️ Edit Komentar")
        def edit_dialog():

            komentar_baru = st.text_area(
                "Komentar",
                value=st.session_state.edit_komentar,
                height=200
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "💾 Simpan Perubahan",
                    key="simpan_edit",
                    use_container_width=True
                ):

                    conn = get_db()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        UPDATE komentar
                        SET isi_komentar = ?
                        WHERE id_komentar = ?
                        """,
                        (
                            komentar_baru,
                            st.session_state.edit_id
                        )
                    )

                    conn.commit()
                    conn.close()

                    del st.session_state.edit_id
                    del st.session_state.edit_komentar

                    st.success(
                        "Komentar berhasil diperbarui"
                    )

                    st.rerun()

            with col2:

                if st.button(
                    "❌ Batal",
                    key="batal_edit",
                    use_container_width=True
                ):

                    del st.session_state.edit_id
                    del st.session_state.edit_komentar

                    st.rerun()

        edit_dialog()