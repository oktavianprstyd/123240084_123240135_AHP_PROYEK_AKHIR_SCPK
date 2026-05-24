import streamlit as st
import pandas as pd
import numpy as np
import itertools
import base64
import plotly.express as px

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="SPK Pemilihan Rumah",
    page_icon="🏡",
    layout="wide"
)

# =========================================================
# BACKGROUND
# =========================================================
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(image_file):
    try:
        bin_str = get_base64(image_file)
        bg = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """
    except Exception:
        bg = """
        <style>
        .stApp {
            background: linear-gradient(
                135deg,
                #1a0a00,
                #3d2000,
                #1a0a00
            );
        }
        </style>
        """
    st.markdown(bg, unsafe_allow_html=True)

set_background("pexels-stephen-leonardi-587681991-34276128.jpg")

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.45);
    z-index: 0;
    pointer-events: none;
}

.block-container {
    position: relative;
    z-index: 1;
    padding-top: 1.5rem;
}

[data-testid="stSidebar"] {
    background: rgba(20,20,20,0.95);
}

.hero-wrap {
    text-align:center;
    padding:2rem;
    border-radius:20px;
    background:rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    margin-bottom:1rem;
}

.hero-title {
    color:white;
    font-size:3rem;
    font-weight:bold;
}

.hero-title span {
    color:#f5c842;
}

.hero-sub {
    color:rgba(255,255,255,0.7);
}

.main-card {
    background: rgba(255,255,255,0.08);
    border-radius:20px;
    padding:2rem;
    margin-bottom:1rem;
    backdrop-filter: blur(12px);
    color:white;
}

.profile-card {
    background: rgba(255,255,255,0.08);
    border-radius:16px;
    padding:1.5rem 2rem;
    margin-bottom:1rem;
    backdrop-filter: blur(12px);
    color:white;
    border: 1px solid rgba(245,200,66,0.3);
}

.profile-card h3 {
    color: #f5c842;
    margin-top: 0;
}

.member-card {
    background: rgba(245,200,66,0.10);
    border-radius:12px;
    padding:1rem 1.5rem;
    margin-bottom:0.75rem;
    border-left: 4px solid #f5c842;
}

.member-name {
    color: white;
    font-size: 1.1rem;
    font-weight: bold;
    margin: 0;
}

.member-nim {
    color: rgba(255,255,255,0.6);
    font-size: 0.9rem;
    margin: 0;
}

.badge {
    display:inline-block;
    background: linear-gradient(135deg, #f5c842, #d4921a);
    color: black;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.85rem;
    font-weight: bold;
    margin: 0.2rem 0.2rem 0.2rem 0;
}

.stButton button {
    background: linear-gradient(
        135deg,
        #f5c842,
        #d4921a
    );
    color:black;
    border:none;
    border-radius:30px;
    padding:0.6rem 1.5rem;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

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
    df = pd.read_csv("RealEstate_California.csv")
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
    df['house_age'] = 2021 - df['yearBuilt']
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

skala_ahp = {
    1: "1 — Sama penting",
    2: "2 — Sedikit lebih penting",
    3: "3 — Cukup lebih penting",
    4: "4 — Lebih penting",
    5: "5 — Sangat lebih penting",
    6: "6 — Jauh lebih penting",
    7: "7 — Sangat dominan",
    8: "8 — Hampir mutlak",
    9: "9 — Mutlak lebih penting"
}

# =========================================================
# HELPER: Hitung CR dari preset
# =========================================================
def hitung_cr_dari_preset(preset):
    """
    preset: list 10 nilai untuk pasangan
    (0,1),(0,2),(0,3),(0,4),(1,2),(1,3),(1,4),(2,3),(2,4),(3,4)
    Return: CR value
    """
    pairs_idx = [
        (0,1),(0,2),(0,3),(0,4),
        (1,2),(1,3),(1,4),
        (2,3),(2,4),
        (3,4)
    ]
    matriks = np.ones((5,5))
    for (r,c), v in zip(pairs_idx, preset):
        matriks[r,c] = v
        matriks[c,r] = 1/v

    kolom_sum = matriks.sum(axis=0)
    normalisasi = matriks / kolom_sum
    bobot = normalisasi.mean(axis=1)

    RI = 1.12
    weighted_sum = np.dot(matriks, bobot)
    consistency_vector = weighted_sum / bobot
    lambda_max = np.mean(consistency_vector)
    CI = (lambda_max - 5) / 4
    CR = CI / RI
    return CR

# =========================================================
# PRESET TEMPLATES — semua dirancang agar CR < 0.1
#
# Urutan 10 pasangan:
# (H,L),(H,KT),(H,KM),(H,U),
# (L,KT),(L,KM),(L,U),
# (KT,KM),(KT,U),(KM,U)
#
# H=Harga, L=Luas, KT=K.Tidur, KM=K.Mandi, U=Umur
# =========================================================
PRESETS = {
    # Harga >> segalanya
    "Pencari Rumah Murah": [
        5, 5, 5, 5,   # H vs L, KT, KM, U
        1, 1, 1,      # L vs KT, KM, U
        1, 1,         # KT vs KM, U
        1             # KM vs U
    ],

    # Luas & Kamar >> Harga & Umur
    "Keluarga Besar": [
        1, 1, 1, 3,   # H vs L=sama, KT=sama, KM=sama, U=H sedikit lebih
        3, 3, 5,      # L vs KT=cukup, KM=cukup, U=sangat
        3, 5,         # KT vs KM=cukup, U=sangat
        3             # KM vs U=cukup
    ],

    # Seimbang, sedikit prioritas Harga & Luas
    "Pasangan Muda": [
        2, 3, 3, 3,   # H vs L, KT, KM, U
        2, 2, 2,      # L vs KT, KM, U
        1, 1,         # KT vs KM, U
        1             # KM vs U
    ],

    # Umur & Harga penting (investasi = murah & baru)
    "Investor Properti": [
        3, 3, 3, 1,   # H vs L, KT, KM, U=sama
        1, 1, 1,      # L vs KT, KM, U
        1, 1,         # KT vs KM, U
        1             # KM vs U (Umur sedikit di atas lewat H vs U)
    ],

    # Luas & Kamar Mandi >> segalanya (premium)
    "Rumah Mewah": [
        1, 1, 1, 3,   # H vs L, KT, KM, U
        5, 5, 5,      # L vs KT, KM, U
        3, 3,         # KT vs KM, U
        1             # KM vs U
    ],

    # Umur Rumah (baru) paling penting
    "Rumah Baru": [
        1, 1, 1, 1,   # H vs L, KT, KM, U=sama (U akan unggul dari bawah)
        1, 1, 1,      # L vs KT, KM, U
        1, 1,         # KT vs KM, U
        5             # KM vs U → U lebih penting dari KM
    ],

    # Harga murah & simpel (kamar sedikit ok)
    "Mahasiswa / Single": [
        5, 5, 5, 3,   # H vs L, KT, KM, U
        1, 1, 1,      # L vs KT, KM, U
        1, 1,         # KT vs KM, U
        1             # KM vs U
    ]
}

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("🏡 SPK Rumah")

    if st.button("Profil Kelompok", use_container_width=True):
        st.session_state.main_page = "profil"

    if st.button("Dataset", use_container_width=True):
        st.session_state.main_page = "dataset"

    if st.button("Perhitungan AHP", use_container_width=True):
        st.session_state.main_page = "spk"
        st.session_state.spk_step = 1

# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero-wrap">
    <h1 class="hero-title">
        SPK <span>Pemilihan Rumah</span>
    </h1>
    <p class="hero-sub">
        Analytical Hierarchy Process (AHP)
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# PROFIL
# =========================================================
if st.session_state.main_page == "profil":

    st.markdown("""
    <div class="profile-card">
        <h3>📋 Profil Aplikasi</h3>
        <p>
            Sistem Pendukung Keputusan (SPK) Pemilihan Rumah ini dirancang
            untuk membantu pengguna dalam menentukan rumah terbaik berdasarkan
            beberapa kriteria penting seperti harga rumah, luas bangunan,
            jumlah kamar tidur, jumlah kamar mandi, dan umur rumah.
        </p>
        <p>
            Aplikasi ini menggunakan metode <strong>Analytical Hierarchy Process (AHP)</strong>
            untuk menghitung tingkat prioritas setiap kriteria melalui proses
            perbandingan berpasangan (pairwise comparison). Hasil akhir berupa
            rekomendasi rumah dengan skor tertinggi sesuai preferensi pengguna.
        </p>
        <p>
            Dataset yang digunakan berasal dari <strong>Real Estate California</strong>
            yang berisi data properti residensial di California, Amerika Serikat.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Jumlah Data", len(df_rumah))
    with col_stat2:
        st.metric("Jumlah Kriteria", 5)
    with col_stat3:
        st.metric("Wilayah", "California")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="profile-card">
        <h3>👥 Profil Kelompok</h3>
    </div>
    """, unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.markdown("""
        <div class="member-card">
            <p class="member-name">🧑‍💻 Kevin Ridoi Parhusip</p>
            <p class="member-nim">NIM: 123240084</p>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown("""
        <div class="member-card">
            <p class="member-name">🧑‍💻 Oktavian Prasetya Adi</p>
            <p class="member-nim">NIM: 123240135</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="profile-card" style="margin-top:1rem;">
        <h3>📚 Informasi Akademik</h3>
        <p>
            <span class="badge">Mata Kuliah</span>
            Sistem Cerdas Pendukung Keputusan
        </p>
        <p>
            <span class="badge">Metode</span>
            Analytical Hierarchy Process (AHP)
        </p>
        <p>
            <span class="badge">Dataset</span>
            Real Estate California
        </p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# DATASET
# =========================================================
elif st.session_state.main_page == "dataset":

    st.markdown("""
    <div class="main-card">
        <h2>Dataset Mentah</h2>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(df_rumah, use_container_width=True)

# =========================================================
# SPK
# =========================================================
elif st.session_state.main_page == "spk":

    # =====================================================
    # STEP 1
    # =====================================================
    if st.session_state.spk_step == 1:

        st.markdown("""
        <div class="main-card">
            <h2>Pilih Template Pengguna</h2>
        </div>
        """, unsafe_allow_html=True)

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

        st.markdown("""
        ### Deskripsi Template

        - **Pencari Rumah Murah** → fokus harga serendah mungkin
        - **Keluarga Besar** → fokus luas & jumlah kamar
        - **Pasangan Muda** → seimbang antara harga dan fasilitas
        - **Investor Properti** → fokus nilai investasi & harga
        - **Rumah Mewah** → fokus luas dan fasilitas premium
        - **Rumah Baru** → fokus umur rumah (bangunan baru)
        - **Mahasiswa / Single** → fokus murah & simpel
        - **Manual** → tentukan sendiri bobot pairwise
        """)

        if st.button("Lanjut Pairwise"):

            pasangan = [
                "c12","c13","c14","c15",
                "c23","c24","c25",
                "c34","c35","c45"
            ]

            preset = PRESETS.get(metode, [1]*10)

            for i, k in enumerate(pasangan):
                st.session_state[f"select_{k}"] = preset[i]

            st.session_state.spk_step = 2
            st.rerun()

    # =====================================================
    # STEP 2
    # =====================================================
    elif st.session_state.spk_step == 2:

        st.markdown("""
        <div class="main-card">
            <h2>Pairwise Comparison</h2>
        </div>
        """, unsafe_allow_html=True)

        pairwise_list = list(
            itertools.combinations(range(len(kriteria)), 2)
        )

        # FIX: gunakan default_index bukan format_func lambda closure bug
        for i, j in pairwise_list:
            key = f"c{i+1}{j+1}"
            st.subheader(f"{kriteria[i]} VS {kriteria[j]}")

            current_val = st.session_state.get(f"select_{key}", 1)
            options = list(skala_ahp.keys())

            # Pastikan current_val valid
            if current_val not in options:
                current_val = 1

            selected = st.selectbox(
                "Tingkat Kepentingan",
                options=options,
                index=options.index(current_val),
                format_func=lambda x, d=skala_ahp: d[x],
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
            v = st.session_state.get(f"select_{k}", 1)
            matriks[r, c] = v
            matriks[c, r] = 1 / v

        st.subheader("Matriks Pairwise")
        st.dataframe(
            pd.DataFrame(matriks, columns=kriteria, index=kriteria),
            use_container_width=True
        )

        kolom_sum = matriks.sum(axis=0)
        normalisasi = matriks / kolom_sum

        st.subheader("Matriks Normalisasi")
        st.dataframe(
            pd.DataFrame(normalisasi, columns=kriteria, index=kriteria).round(4),
            use_container_width=True
        )

        bobot = normalisasi.mean(axis=1)

        bobot_df = pd.DataFrame({
            "Kriteria": kriteria,
            "Bobot": bobot,
            "Bobot (%)": bobot * 100
        })

        st.subheader("Bobot Prioritas")
        st.dataframe(bobot_df.round(4), use_container_width=True)

        # Grafik bobot
        fig_bobot = px.bar(
            bobot_df,
            x='Kriteria',
            y='Bobot (%)',
            text='Bobot (%)',
            title='Bobot Prioritas Kriteria',
            color='Bobot (%)',
            color_continuous_scale='YlOrBr'
        )
        fig_bobot.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        st.plotly_chart(fig_bobot, use_container_width=True)

        # Uji Konsistensi
        RI = 1.12
        weighted_sum = np.dot(matriks, bobot)
        consistency_vector = weighted_sum / bobot
        lambda_max = np.mean(consistency_vector)
        CI = (lambda_max - 5) / 4
        CR = CI / RI

        st.subheader("Uji Konsistensi")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Lambda Max", round(lambda_max, 4))
        with col2:
            st.metric("CI", round(CI, 4))
        with col3:
            st.metric("CR", round(CR, 4))

        if CR < 0.1:
            st.success(f"✅ Matriks Konsisten (CR = {CR:.4f} < 0.1)")
        else:
            st.error(f"❌ Matriks Tidak Konsisten (CR = {CR:.4f} ≥ 0.1). Silakan kembali dan sesuaikan nilai pairwise.")

        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("Kembali ke Pairwise"):
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

        alternatif = df_rumah.head(1000).copy()

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
                alternatif['homeType'].unique()
            )

        alternatif = alternatif[
            (alternatif['price'] <= max_harga) &
            (alternatif['bedrooms'] >= min_kamar) &
            (alternatif['homeType'] == tipe_rumah)
        ]

        if len(alternatif) == 0:
            st.warning("Tidak ada data yang sesuai filter. Coba longgarkan filter.")
            if st.button("Kembali"):
                st.session_state.spk_step = 3
                st.rerun()
        else:
            p_low, p_high = alternatif['price'].quantile([0.33, 0.66])
            l_low, l_high = alternatif['livingArea'].quantile([0.33, 0.66])
            a_low, a_high = alternatif['house_age'].quantile([0.33, 0.66])

            def r_price(x):
                return 0.65 if x <= p_low else (0.25 if x <= p_high else 0.10)

            def r_area(x):
                return 0.60 if x >= l_high else (0.30 if x >= l_low else 0.10)

            def r_bed(x):
                return 0.63 if x >= 4 else (0.26 if x == 3 else 0.11)

            def r_bath(x):
                return 0.63 if x >= 3 else (0.26 if x >= 2 else 0.11)

            def r_age(x):
                return 0.65 if x <= a_low else (0.25 if x <= a_high else 0.10)

            bobot = st.session_state.bobot_akhir

            alternatif = alternatif.copy()
            alternatif['score'] = (
                bobot[0] * alternatif['price'].apply(r_price) +
                bobot[1] * alternatif['livingArea'].apply(r_area) +
                bobot[2] * alternatif['bedrooms'].apply(r_bed) +
                bobot[3] * alternatif['bathrooms'].apply(r_bath) +
                bobot[4] * alternatif['house_age'].apply(r_age)
            )

            hasil = alternatif.sort_values(by='score', ascending=False).head(10)
            hasil = hasil.reset_index(drop=True)
            hasil.index = hasil.index + 1

            hasil_tampil = hasil[[
                'streetAddress', 'city', 'price',
                'livingArea', 'bedrooms', 'bathrooms', 'score'
            ]].rename(columns={
                'streetAddress': 'Alamat',
                'city': 'Kota',
                'price': 'Harga ($)',
                'livingArea': 'Luas (sqft)',
                'bedrooms': 'K. Tidur',
                'bathrooms': 'K. Mandi',
                'score': 'Skor AHP'
            })

            hasil_tampil.index.name = "Ranking"

            st.subheader("Top 10 Ranking Rumah")
            st.dataframe(hasil_tampil, use_container_width=True)

            fig_rank = px.bar(
                hasil_tampil.reset_index(),
                x='Ranking',
                y='Skor AHP',
                text='Skor AHP',
                hover_data=['Alamat'],
                title='Top 10 Ranking Rumah',
                color='Skor AHP',
                color_continuous_scale='YlOrBr'
            )
            fig_rank.update_traces(
                texttemplate='%{text:.4f}',
                textposition='outside'
            )
            st.plotly_chart(fig_rank, use_container_width=True)

            st.subheader("Peta Lokasi")
            peta_data = hasil[['latitude', 'longitude']].dropna()
            if len(peta_data) > 0:
                st.map(peta_data)
            else:
                st.info("Data koordinat tidak tersedia untuk hasil ini.")

            if st.button("Mulai Ulang"):
                st.session_state.spk_step = 1
                st.rerun()