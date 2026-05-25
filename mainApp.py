# =========================================================
# IMPORT
# =========================================================
import streamlit as st
import pandas as pd
import numpy as np
import itertools
import plotly.express as px
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="SPK Pemilihan Rumah",
    layout="wide"
)

pd.set_option(
    'display.float_format',
    '{:.10f}'.format
)

# =========================================================
# SESSION STATE
# =========================================================
if 'main_page' not in st.session_state:
    st.session_state.main_page = "profil"

if 'spk_step' not in st.session_state:
    st.session_state.spk_step = 1

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():

    df = pd.read_csv("RealEstate_California_Clean.csv")

    df = df[df['homeType'].isin([
        'SINGLE_FAMILY',
        'CONDO',
        'TOWNHOUSE'
    ])]

    df = df.dropna(subset=[
        'price',
        'livingArea',
        'bedrooms',
        'bathrooms',
        'yearBuilt'
    ])

    df['house_age'] = (
        datetime.now().year - df['yearBuilt']
    )

    return df

df_rumah = load_data()

# =========================================================
# KRITERIA
# =========================================================
kriteria = [
    "Harga Rumah",
    "Luas Bangunan",
    "Jumlah Kamar Tidur",
    "Jumlah Kamar Mandi",
    "Umur Rumah"
]

# =========================================================
# SKALA AHP
# =========================================================
skala_ahp = {
    1: "1 - Sama penting",
    2: "2 - Sedikit lebih penting",
    3: "3 - Cukup lebih penting",
    4: "4 - Lebih penting",
    5: "5 - Sangat lebih penting",
    6: "6 - Jauh lebih penting",
    7: "7 - Sangat dominan",
    8: "8 - Hampir mutlak",
    9: "9 - Mutlak lebih penting"
}

# =========================================================
# PRESET TEMPLATE
# =========================================================
PRESETS = {

    "Pencari Rumah Murah": [
        5, 5, 5, 5,
        1, 1, 1,
        1, 1,
        1
    ],

    "Keluarga Besar": [
        1, 1, 1, 3,
        3, 3, 5,
        3, 5,
        3
    ],

    "Pasangan Muda": [
        2, 3, 3, 3,
        2, 2, 2,
        1, 1,
        1
    ],

    "Investor Properti": [
        3, 3, 3, 1,
        1, 1, 1,
        1, 1,
        1
    ],

    "Rumah Mewah": [
        1, 1, 1, 3,
        5, 5, 5,
        3, 3,
        1
    ],

    "Rumah Baru": [
        1, 1, 1, 1,
        1, 1, 1,
        1, 1,
        5
    ],

    "Mahasiswa / Single": [
        5, 5, 5, 3,
        1, 1, 1,
        1, 1,
        1
    ]
}

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.title("SPK Rumah")
    st.write("---")

    if st.button("Profil Kelompok", use_container_width=True):
        st.session_state.main_page = "profil"

    if st.button("Dataset", use_container_width=True):
        st.session_state.main_page = "dataset"

    if st.button("Perhitungan AHP", use_container_width=True):
        st.session_state.main_page = "spk"
        st.session_state.spk_step = 1

# =========================================================
# HEADER
# =========================================================
st.title("SPK Pemilihan Rumah")
st.caption("Metode AHP dan Weighted Sum")
st.divider()

# =========================================================
# HALAMAN PROFIL
# =========================================================
if st.session_state.main_page == "profil":

    st.header("Profil Aplikasi")

    st.write("""
    Sistem Pendukung Keputusan (SPK) Pemilihan Rumah
    menggunakan metode Analytical Hierarchy Process (AHP)
    dan Weighted Sum untuk membantu pengguna menentukan
    rumah terbaik berdasarkan berbagai kriteria.
    """)

    col1, col2, col3 = st.columns(3)

    col1.metric("Jumlah Data", len(df_rumah))
    col2.metric("Jumlah Kriteria", 5)
    col3.metric("Wilayah", "California")

    st.divider()

    st.header("Profil Kelompok")

    c1, c2 = st.columns(2)

    with c1:
        st.info("""
        Kevin Ridoi Parhusip
        
        NIM: 123240084
        """)

    with c2:
        st.info("""
        Oktavian Prasetya Adi
        
        NIM: 123240135
        """)

# =========================================================
# HALAMAN DATASET
# =========================================================
elif st.session_state.main_page == "dataset":

    st.header("Dataset Rumah")

    st.dataframe(
        df_rumah,
        use_container_width=True
    )

# =========================================================
# HALAMAN SPK
# =========================================================
elif st.session_state.main_page == "spk":

    st.write(f"Langkah {st.session_state.spk_step} dari 4")
    st.progress(st.session_state.spk_step / 4)

    # =====================================================
    # STEP 1
    # =====================================================
    if st.session_state.spk_step == 1:

        st.header("Langkah 1 : Pilih Template")

        metode = st.selectbox(
            "Template Pengguna",
            [
                "Manual",
                "Pencari Rumah Murah",
                "Keluarga Besar",
                "Pasangan Muda",
                "Investor Properti",
                "Rumah Mewah",
                "Rumah Baru",
                "Mahasiswa / Single"
            ]
        )

        st.write("Deskripsi Template")

        st.write("- Pencari Rumah Murah : fokus harga murah")
        st.write("- Keluarga Besar : fokus luas dan kamar")
        st.write("- Investor Properti : fokus investasi")
        st.write("- Rumah Baru : fokus umur rumah")

        if st.button("Lanjut"):

            pasangan = [
                "c12", "c13", "c14", "c15",
                "c23", "c24", "c25",
                "c34", "c35",
                "c45"
            ]

            preset = PRESETS.get(metode, [1] * 10)

            for i, k in enumerate(pasangan):
                st.session_state[f"select_{k}"] = preset[i]

            st.session_state.spk_step = 2
            st.rerun()

    # =====================================================
    # STEP 2
    # =====================================================
    elif st.session_state.spk_step == 2:

        st.header("Langkah 2 : Pairwise Comparison")

        pairwise_list = list(
            itertools.combinations(
                range(len(kriteria)),
                2
            )
        )

        for i, j in pairwise_list:

            key = f"c{i+1}{j+1}"

            st.write(
                f"{kriteria[i]} vs {kriteria[j]}"
            )

            current_val = st.session_state.get(
                f"select_{key}",
                1
            )

            options = list(skala_ahp.keys())

            st.selectbox(
                "Pilih Nilai",
                options=options,
                index=options.index(current_val),
                format_func=lambda x: skala_ahp[x],
                key=f"select_{key}"
            )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Kembali"):
                st.session_state.spk_step = 1
                st.rerun()

        with col2:
            if st.button("Hitung AHP"):
                st.session_state.spk_step = 3
                st.rerun()

    # =====================================================
    # STEP 3
    # =====================================================
    elif st.session_state.spk_step == 3:

        st.header("Langkah 3 : Hasil AHP")

        matriks = np.ones((5, 5))

        pairs = [
            (0,1,"c12"),
            (0,2,"c13"),
            (0,3,"c14"),
            (0,4,"c15"),
            (1,2,"c23"),
            (1,3,"c24"),
            (1,4,"c25"),
            (2,3,"c34"),
            (2,4,"c35"),
            (3,4,"c45")
        ]

        for r, c, k in pairs:

            v = st.session_state.get(
                f"select_{k}",
                1
            )

            matriks[r, c] = v
            matriks[c, r] = 1 / v

        st.subheader("Matriks Pairwise")

        st.dataframe(
            pd.DataFrame(
                matriks,
                columns=kriteria,
                index=kriteria
            ),
            use_container_width=True
        )

        # NORMALISASI
        kolom_sum = matriks.sum(axis=0)
        normalisasi = matriks / kolom_sum

        st.subheader("Matriks Normalisasi")

        st.dataframe(
            pd.DataFrame(
                normalisasi,
                columns=kriteria,
                index=kriteria
            ).round(10),
            use_container_width=True
        )

        # BOBOT
        bobot = normalisasi.mean(axis=1)

        bobot_df = pd.DataFrame({
            "Kriteria": kriteria,
            "Bobot": bobot,
            "Bobot (%)": bobot * 100
        })

        st.subheader("Bobot Prioritas")

        st.dataframe(
            bobot_df.round(10),
            use_container_width=True
        )

        # GRAFIK
        fig = px.bar(
            bobot_df,
            x='Kriteria',
            y='Bobot (%)',
            text='Bobot (%)',
            color='Bobot (%)',
            title='Bobot Prioritas Kriteria'
        )

        fig.update_traces(
            texttemplate='%{text:.2f}%',
            textposition='outside'
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =================================================
        # UJI KONSISTENSI
        # =================================================
        RI = 1.12

        weighted_sum = np.dot(
            matriks,
            bobot
        )

        consistency_vector = weighted_sum / bobot

        lambda_max = np.mean(consistency_vector)

        CI = (lambda_max - 5) / 4

        CR = CI / RI

        st.subheader("Uji Konsistensi")

        c1, c2, c3 = st.columns(3)

        c1.metric("Lambda Max", round(lambda_max, 10))
        c2.metric("CI", round(CI, 10))
        c3.metric("CR", round(CR, 10))

        if CR < 0.1:
            st.success(
                f"Matriks Konsisten (CR = {CR:.10f})"
            )
        else:
            st.error(
                f"Matriks Tidak Konsisten (CR = {CR:.10f})"
            )

        col_back, col_next = st.columns(2)

        with col_back:
            if st.button("Kembali"):
                st.session_state.spk_step = 2
                st.rerun()

        with col_next:
            if st.button("Lihat Ranking"):
                st.session_state.bobot_akhir = bobot
                st.session_state.spk_step = 4
                st.rerun()

    # =====================================================
    # STEP 4
    # =====================================================
    elif st.session_state.spk_step == 4:

        st.header("Langkah 4 : Ranking Rumah")

        alternatif = df_rumah.head(5000).copy()

        st.subheader("Filter Preferensi Rumah")

        col1, col2, col3 = st.columns(3)

        with col1:
            max_harga = st.slider(
                "Maksimal Harga",
                int(alternatif['price'].min()),
                int(alternatif['price'].max()),
                int(alternatif['price'].quantile(0.75))
            )

        with col2:
            min_kamar = st.number_input(
                "Minimal Kamar Tidur",
                min_value=1,
                max_value=10,
                value=3
            )

        with col3:
            tipe_rumah = st.selectbox(
                "Tipe Rumah",
                alternatif['homeType'].dropna().unique()
            )

        # FILTER
        alternatif = alternatif[
            (alternatif['price'] <= max_harga) &
            (alternatif['bedrooms'] >= min_kamar) &
            (alternatif['homeType'] == tipe_rumah)
        ]

        if len(alternatif) == 0:

            st.warning(
                "Tidak ada rumah sesuai filter."
            )

        else:

            # =================================================
            # NORMALISASI ALTERNATIF
            # =================================================

            # COST
            min_price = max(df_rumah['price'].min(), 1)
            max_area  = df_rumah['livingArea'].max()
            max_bed   = df_rumah['bedrooms'].max()
            max_bath  = df_rumah['bathrooms'].max()

            alternatif['house_age'] = alternatif['house_age'].replace(0, 1)  # lindungi dulu
            min_age = max(alternatif['house_age'].min(), 1)
            alternatif['norm_age'] = min_age / alternatif['house_age']

            alternatif['norm_price'] = (
                min_price
                / alternatif['price']
            )

            alternatif['norm_age'] = (
                min_age
                / alternatif['house_age']
            )

            # BENEFIT
            alternatif['norm_area'] = (
                alternatif['livingArea']
                / alternatif['livingArea'].max()
            )

            alternatif['norm_bed'] = (
                alternatif['bedrooms']
                / alternatif['bedrooms'].max()
            )

            alternatif['norm_bath'] = (
                alternatif['bathrooms']
                / alternatif['bathrooms'].max()
            )

            st.subheader("Data Normalisasi")

            normalisasi_tampil = alternatif[
                [
                    'norm_price',
                    'norm_area',
                    'norm_bed',
                    'norm_bath',
                    'norm_age'
                ]
            ].head(10)

            st.dataframe(
                normalisasi_tampil.style.format({
                    'norm_price': '{:.10f}',
                    'norm_area': '{:.10f}',
                    'norm_bed': '{:.10f}',
                    'norm_bath': '{:.10f}',
                    'norm_age': '{:.10f}'
                }),
                use_container_width=True
            )

            # =================================================
            # HITUNG SCORE
            # =================================================
            bobot = st.session_state.bobot_akhir

            alternatif['score'] = (
                bobot[0] * alternatif['norm_price'] +
                bobot[1] * alternatif['norm_area'] +
                bobot[2] * alternatif['norm_bed'] +
                bobot[3] * alternatif['norm_bath'] +
                bobot[4] * alternatif['norm_age']
            )

            hasil = alternatif.sort_values(
                by='score',
                ascending=False
            ).head(10)

            hasil = hasil.reset_index(drop=True)

            hasil.index = hasil.index + 1

            hasil_tampil = hasil[
                [
                    'streetAddress',
                    'city',
                    'price',
                    'livingArea',
                    'bedrooms',
                    'bathrooms',
                    'score'
                ]
            ].rename(columns={
                'streetAddress': 'Alamat',
                'city': 'Kota',
                'price': 'Harga ($)',
                'livingArea': 'Luas',
                'bedrooms': 'K. Tidur',
                'bathrooms': 'K. Mandi',
                'score': 'Skor AHP'
            })

            hasil_tampil.index.name = "Ranking"

            st.subheader("Top 10 Ranking Rumah")

            st.dataframe(
                hasil_tampil.round(10),
                use_container_width=True
            )

            # =================================================
            # GRAFIK RANKING
            # =================================================
            fig_rank = px.bar(
                hasil_tampil.reset_index(),
                x='Ranking',
                y='Skor AHP',
                text='Skor AHP',
                title='Top 10 Ranking Rumah',
                color='Skor AHP'
            )

            fig_rank.update_traces(
                texttemplate='%{text:.10f}',
                textposition='outside'
            )

            st.plotly_chart(
                fig_rank,
                use_container_width=True
            )

            # =================================================
            # MAP
            # =================================================
            st.subheader("Peta Lokasi")

            peta_data = hasil[
                ['latitude', 'longitude']
            ].dropna()

            if len(peta_data) > 0:
                st.map(peta_data)
            else:
                st.info("Koordinat tidak tersedia.")

            # =================================================
            # RESET
            # =================================================
            if st.button("Mulai Ulang"):
                st.session_state.spk_step = 1
                st.rerun()
