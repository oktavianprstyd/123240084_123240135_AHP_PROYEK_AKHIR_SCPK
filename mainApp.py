import streamlit as st
import pandas as pd
import numpy as np
import base64
import plotly.express as px

# =========================================================
# 1. PENGATURAN KONFIGURASI HALAMAN UTAMA & BACKEND MEMORI
# =========================================================
st.set_page_config(page_title="SPK Pemilihan Rumah - 7 Kriteria AHP", layout="centered")

if 'hasil_terakhir' not in st.session_state:
    st.session_state.hasil_terakhir = None

# =========================================================
# 2. IMPLEMENTASI BACKGROUND & PRESET CSS CUSTOMIZATION CONTRAST
# =========================================================
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_bg_from_local(gambar_file):
    try:
        bin_str = get_base64_of_bin_file(gambar_file)
        bg_css = f'background-image: url("data:image/png;base64,{bin_str}");'
    except Exception:
        bg_css = 'background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);'

    page_bg_img = f'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=500;700;800&display=swap');

    .stApp {{
        {bg_css}
        background-attachment: fixed;
        background-size: cover;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        text-align: center;
    }}
    
    .stMarkdown p, .stMarkdown li {{
        text-align: center !important;
    }}
    
    .stMarkdown, .stSlider, .stSelectbox, .stTextInput, .stTable, div[data-testid="stAlert"], .stRadio, div.row-widget.stRadio > div {{
        background-color: rgba(15, 32, 39, 0.85); 
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        color: #ffffff !important; 
        font-weight: 700 !important;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.4); 
        border: 2px solid #00f0ff !important; 
    }}
    
    div[data-testid="stAlert"] {{
        border: 2px solid #00f0ff !important; 
        background-color: rgba(15, 32, 39, 0.9) !important;
    }}
    
    .stApp label, .stApp p, .stApp small {{
        color: #ffffff !important; 
        font-weight: 700 !important;
        justify-content: center; 
    }}

    /* CSS DROPDOWN KONTRAS FIX */
    .stApp div:not([data-baseweb="select"]):not([data-baseweb="popover"]):not([role="option"]):not([data-baseweb="menu"]),
    .stApp span:not([data-baseweb="select"]):not([data-baseweb="popover"]):not([role="option"]):not([data-baseweb="menu"]) {{
        color: #ffffff;
    }}
    
    h1, h2, h3, h4 {{
        background-color: rgba(15, 32, 39, 0.9);
        padding: 15px;
        border-radius: 12px;
        color: #ffffff !important; 
        font-weight: 800 !important;
        text-align: center !important;
        border: 2px solid #00f0ff !important;
        border-bottom: 6px solid #00f0ff !important; 
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
    }}
    
    hr {{
        border: 0;
        height: 3px;
        background: linear-gradient(to right, transparent, #00f0ff, transparent);
        margin: 25px 0;
    }}

    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] {{
        background-color: #ffffff !important;
        border: 2px solid #00f0ff !important; 
        border-radius: 8px !important;
    }}

    div[data-baseweb="select"] div, 
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] [aria-selected="true"] {{
        color: #000000 !important;
        font-weight: 700 !important;
        -webkit-text-fill-color: #000000 !important;
    }}
    
    div[data-testid="stTextInput"] input {{
        color: #000000 !important;
        font-weight: 700 !important;
        -webkit-text-fill-color: #000000 !important;
    }}
    
    div[data-baseweb="popover"] ul, 
    div[data-baseweb="popover"] li, 
    div[data-baseweb="popover"] div,
    div[data-baseweb="menu"] div,
    div[role="option"],
    div[role="option"] span,
    div[role="option"] div {{
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: 700 !important;
        -webkit-text-fill-color: #000000 !important;
    }}

    div[data-testid="stSlider"] div[role="slider"] {{
        background-color: #00f0ff !important; 
        border: 2px solid #ffffff !important;
        box-shadow: 0px 0px 8px #00f0ff;
    }}
    div[data-testid="stSlider"] div[aria-hidden="true"] > div {{
        background-color: #00f0ff !important; 
    }}
    div[data-testid="stSlider"] div[aria-hidden="true"] > div:first-child {{
        background-color: rgba(255, 255, 255, 0.2) !important; 
    }}

    div[data-testid="stTable"] table, div[data-testid="stDataFrame"] div {{
        border: 2px solid #00f0ff !important; 
        color: #ffffff !important;
    }}
    
    div.stButton > button:first-child {{
        background-color: #00f0ff !important; 
        color: #000000 !important; 
        font-weight: 800 !important; 
        border: 2px solid #000000 !important; 
        border-radius: 8px !important;
        padding: 0.6rem 2.5rem !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0px 4px 12px rgba(0, 240, 255, 0.4);
        width: 100%; 
    }}

    div.stButton > button:first-child:hover {{
        background-color: #00e5ff !important; 
        box-shadow: 0px 8px 20px rgba(0, 240, 255, 0.7);
        transform: translateY(-3px); 
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_bg_from_local('pexels-stephen-leonardi-587681991-34276128.jpg')

# =========================================================
# 3. ENGINE MEMUAT DATASET UTAMA (7 KRITERIA DASAR)
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_csv('RealEstate_California.csv')
    df_clean = df[df['homeType'].isin(['SINGLE_FAMILY', 'CONDO', 'TOWNHOUSE'])].copy()
    
    if 'garageSpaces' in df_clean.columns:
        df_clean['garageSpaces'] = df_clean['garageSpaces'].fillna(0)
    else:
        df_clean['garageSpaces'] = 0
        
    df_clean = df_clean.dropna(subset=['price', 'livingArea', 'bedrooms', 'bathrooms', 'yearBuilt'])
    
    df_clean = df_clean[(df_clean['price'] > 0) & 
                        (df_clean['livingArea'] > 0) & 
                        (df_clean['bedrooms'] > 0) & 
                        (df_clean['bathrooms'] > 0) & 
                        (df_clean['yearBuilt'] > 0)]
    
    df_clean['house_age'] = 2026 - df_clean['yearBuilt']
    df_clean['house_age'] = df_clean['house_age'].replace(0, 1)
    
    return df_clean

try:
    df_rumah = load_data()
except Exception as e:
    st.error(f"Gagal memuat file RealEstate_California.csv. Error: {e}")
    st.stop()

# Skema Bobot Standar Intensitas Penilaian Absolut (Skor Lokal Alternatif)
bobot_rating = {
    'price': {'Murah': 0.65, 'Sedang': 0.25, 'Mahal': 0.10},
    'livingArea': {'Luas': 0.60, 'Cukup': 0.30, 'Sempit': 0.10},
    'bedrooms': {'Banyak': 0.63, 'Standar': 0.26, 'Sedikit': 0.11},
    'bathrooms': {'Banyak': 0.63, 'Standar': 0.26, 'Sedikit': 0.11},
    'house_age': {'Baru': 0.65, 'Sedang': 0.25, 'Tua': 0.10},
    'homeType': {'SINGLE_FAMILY': 0.60, 'TOWNHOUSE': 0.30, 'CONDO': 0.10},
    'garageSpaces': {'Ada Garasi Luas': 0.65, 'Ada Garasi Standar': 0.25, 'Tidak Ada Garasi': 0.10}
}

kriteria_label = [
    'Harga Rumah (C1)', 'Luas Bangunan (C2)', 'Jumlah Kamar Tidur (C3)', 
    'Jumlah Kamar Mandi (C4)', 'Umur Fisik Rumah (C5)', 'Jenis Rumah (C6)', 'Fasilitas Garasi (C7)'
]

# =========================================================
# 4. SISTEM MENU NAVIGASI (SIDEBAR)
# =========================================================
st.sidebar.title("Navigasi Aplikasi")
menu_halaman = st.sidebar.radio(
    "Pilih Halaman:",
    ["Halaman Profil Kelompok", "Halaman Data", "Halaman Hitung SPK", "Halaman Visualisasi Peta"]
)

# ---------------------------------------------------------
# HALAMAN 1: PROFIL KELOMPOK
# ---------------------------------------------------------
if menu_halaman == "Halaman Profil Kelompok":
    st.title("Halaman Profil Kelompok")
    st.write("Sistem Pendukung Keputusan Pemilihan Properti Rumah Ideal Menggunakan Metode AHP.")
    
    st.info("""
    Anggota Kelompok / Pengembang:
    1. Kevin Ridoi Parhusip (NIM. 123240084) - Informatika H
    2. Oktavian Prasetya Adi (NIM. 123240135) - Informatika H
    """)
    st.write("Silakan gunakan menu navigasi di Sidebar sebelah kiri untuk berpindah halaman.")

# ---------------------------------------------------------
# HALAMAN 2: DATA EXPLORATION
# ---------------------------------------------------------
elif menu_halaman == "Halaman Data":
    st.title("Eksplorasi Dataset Mentah")
    st.write("Menampilkan data komprehensif real estate wilayah California hasil unduhan online.")
    
    st.success(f"Syarat Jumlah Baris Terpenuhi: Dataset memiliki {df_rumah.shape[0]} baris data (Minimal syarat: 250 baris).")
    st.success("Syarat Jumlah Kriteria Terpenuhi: Memiliki 7 Kriteria Utama (Harga, Luas, Kamar Tidur, Kamar Mandi, Umur Rumah, Jenis Rumah, Garasi).")
    
    st.subheader("Tabel Interaktif Dataset Mentah (st.dataframe)")
    st.dataframe(df_rumah[['streetAddress', 'city', 'price', 'livingArea', 'bedrooms', 'bathrooms', 'house_age', 'homeType', 'garageSpaces']], use_container_width=True)

# ---------------------------------------------------------
# HALAMAN 3: PROSES KOMPUTASI & HITUNG SPK (10 PERSONAL BUYER)
# ---------------------------------------------------------
elif menu_halaman == "Halaman Hitung SPK":
    st.title("Perhitungan SPK (Metode AHP - 7 Kriteria)")
    st.write("Sesuaikan tingkat prioritas komparasi berpasangan antar kriteria.")
    
    st.subheader("Input Bobot & Filter Dinamis")
    kota_pilihan = st.selectbox("Saring Kota Penempatan Properti:", ['Semua Kota'] + sorted(df_rumah['city'].unique().tolist()))
    
    # INDIKATOR INPUT PAIRWISE DENGAN 10 TEMPLATE BUYER PERSONA
    st.write("Prosedur Pengisian Matriks Perbandingan Berpasangan:")
    metode_input = st.radio(
        "Pilih Metode Pengisian Preferensi:", 
        ["Gunakan Template Buyer Properti (10 Persona)", "Isi Manual via Slider"]
    )
    
    matriks_ahp = np.ones((7, 7))
    
    if metode_input == "Gunakan Template Buyer Properti (10 Persona)":
        tipe_buyer = st.selectbox(
            "Pilih Profil Calon Pembeli (Buyer Persona):",
            [
                "1. Keluarga Besar (Prioritas Kamar Banyak & Luas Bangunan)",
                "2. Pasangan Suami Istri Baru (Prioritas Finansial & Harga Ekonomis)",
                "3. Pekerja Lajang / Eksekutif (Prioritas Garasi & Rumah Minimalis)",
                "4. Investor Real Estate (Prioritas Harga Murah & Umur Rumah Baru)",
                "5. Keluarga Muda Beranak Satu (Prioritas Keseimbangan Harga & Kamar)",
                "6. Lansia / Pensiunan (Prioritas Rumah Tua/Klasik & Luas Halaman)",
                "7. Kolektor Mobil / Otomotif (Prioritas Utama Garasi Sangat Luas)",
                "8. Pengusaha Home Industry (Prioritas Luas Bangunan Maksimal)",
                "9. Pemburu Rumah Baru / Gress (Prioritas Umur Fisik Rumah Terkecil)",
                "10. Kaum Urban / Praktis (Prioritas Kondominium/Townhouse Modern)"
            ]
        )
        
        # LOGIKA MATRIKS BERDASARKAN 10 BUYER PERSONA (PASTI KONSISTEN < 0.1)
        if "1. Keluarga Besar" in tipe_buyer:
            st.info("Template Aktif: Mengutamakan kapasitas ruangan (Kamar Tidur/Mandi) dan kelonggaran Luas Bangunan.")
            c12, c13, c14, c15, c16, c17 = 1, 0.33, 0.33, 2, 1, 2
            c23, c24, c25, c26, c27 = 1, 1, 4, 3, 3
            c34, c35, c36, c37 = 2, 5, 4, 4
            c45, c46, c47 = 4, 3, 3
            c56, c57 = 0.5, 0.5
            c67 = 1
            
        elif "2. Pasangan Suami Istri Baru" in tipe_buyer:
            st.info("Template Aktif: Fokus menekan budget pengeluaran awal (Harga Rumah C1 sangat dominan).")
            c12, c13, c14, c15, c16, c17 = 4, 6, 6, 5, 4, 5
            c23, c24, c25, c26, c27 = 2, 2, 3, 1, 2
            c34, c35, c36, c37 = 1, 1, 0.5, 1
            c45, c46, c47 = 1, 0.5, 1
            c56, c57 = 0.5, 1
            c67 = 2
            
        elif "3. Pekerja Lajang" in tipe_buyer:
            st.info("Template Aktif: Mengutamakan ketersediaan Fasilitas Garasi (C7) dan fleksibilitas kendaraan.")
            c12, c13, c14, c15, c16, c17 = 1, 3, 3, 1, 0.33, 0.25
            c23, c24, c25, c26, c27 = 2, 2, 1, 0.5, 0.33
            c34, c35, c36, c37 = 1, 0.5, 0.33, 0.2
            c45, c46, c47 = 1, 0.33, 0.2
            c56, c57 = 0.5, 0.33
            c67 = 0.5
            
        elif "4. Investor Real Estate" in tipe_buyer:
            st.info("Template Aktif: Fokus memaksimalkan margin keuntungan lewat Harga Beli Rendah (C1) dan bangunan awet.")
            c12, c13, c14, c15, c16, c17 = 5, 5, 5, 1, 4, 4
            c23, c24, c25, c26, c27 = 1, 1, 0.25, 2, 1
            c34, c35, c36, c37 = 1, 0.2, 1, 1
            c45, c46, c47 = 0.2, 1, 1
            c56, c57 = 4, 3
            c67 = 1

        elif "5. Keluarga Muda Beranak Satu" in tipe_buyer:
            st.info("Template Aktif: Keseimbangan proporsional antara Harga Terjangkau dan Kamar Tidur Standar.")
            c12, c13, c14, c15, c16, c17 = 2, 2, 3, 2, 2, 3
            c23, c24, c25, c26, c27 = 1, 2, 1, 1, 2
            c34, c35, c36, c37 = 2, 1, 1, 2
            c45, c46, c47 = 0.5, 0.5, 1
            c56, c57 = 1, 2
            c67 = 1

        elif "6. Lansia / Pensiunan" in tipe_buyer:
            st.info("Template Aktif: Mengabaikan tren modernitas, menyukai rumah mapan/umur matang yang tenang.")
            c12, c13, c14, c15, c16, c17 = 1, 2, 2, 0.25, 2, 1
            c23, c24, c25, c26, c27 = 2, 2, 0.2, 1, 1
            c34, c35, c36, c37 = 1, 0.2, 0.5, 0.5
            c45, c46, c47 = 0.2, 0.5, 0.5
            c56, c57 = 4, 3
            c67 = 1

        elif "7. Kolektor Mobil / Otomotif" in tipe_buyer:
            st.info("Template Aktif: Menempatkan Fasilitas Garasi (C7) sebagai kriteria mutlak di atas segalanya.")
            c12, c13, c14, c15, c16, c17 = 1, 1, 1, 1, 1, 1
            c23, c24, c25, c26, c27 = 1, 1, 1, 1, 1
            c34, c35, c36, c37 = 1, 1, 1, 1
            c45, c46, c47 = 1, 1, 1
            c56, c57 = 1, 1
            c67 = 1
            # Override manual untuk menjamin dominasi mutlak C7 secara konsisten
            matriks_ahp[:, 6] = [8, 7, 5, 5, 7, 7, 1]
            matriks_ahp[6, :] = [1/8, 1/7, 1/5, 1/5, 1/7, 1/7, 1]

        elif "8. Pengusaha Home Industry" in tipe_buyer:
            st.info("Template Aktif: Luas Bangunan (C2) sangat dominan untuk ruang produksi/gudang penyimpanan.")
            c12, c13, c14, c15, c16, c17 = 0.25, 0.2, 0.2, 1, 1, 1
            c23, c24, c25, c26, c27 = 4, 4, 5, 4, 5
            c34, c35, c36, c37 = 1, 2, 1, 2
            c45, c46, c47 = 2, 1, 2
            c56, c57 = 0.5, 1
            c67 = 2

        elif "9. Pemburu Rumah Baru" in tipe_buyer:
            st.info("Template Aktif: Memprioritaskan faktor Fisik Umur Rumah (C5) sekecil mungkin agar bebas renovasi.")
            c12, c13, c14, c15, c16, c17 = 1, 2, 2, 0.2, 1, 2
            c23, c24, c25, c26, c27 = 2, 2, 0.14, 1, 1
            c34, c35, c36, c37 = 1, 0.14, 0.5, 1
            c45, c46, c47 = 0.14, 0.5, 1
            c56, c57 = 5, 6
            c67 = 1

        else: # 10. Kaum Urban / Praktis
            st.info("Template Aktif: Mengutamakan Jenis Properti (C6) spesifik seperti Townhouse/Condo tengah kota demi efisiensi.")
            c12, c13, c14, c15, c16, c17 = 1, 2, 2, 1, 0.2, 1
            c23, c24, c25, c26, c27 = 1, 1, 1, 0.14, 1
            c34, c35, c36, c37 = 1, 1, 0.14, 1
            c45, c46, c47 = 1, 0.14, 1
            c56, c57 = 5, 6
            c67 = 0.2
            
    else:
        st.info("Atur parameter 21 komponen slider di bawah ini secara manual:")
        c12 = st.slider("Harga (C1) VS Luas Bangunan (C2)", 1, 9, 3)
        c13 = st.slider("Harga (C1) VS Jumlah Kamar Tidur (C3)", 1, 9, 5)
        c14 = st.slider("Harga (C1) VS Jumlah Kamar Mandi (C4)", 1, 9, 5)
        c15 = st.slider("Harga (C1) VS Umur Rumah (C5)", 1, 9, 4)
        c16 = st.slider("Harga (C1) VS Jenis Rumah (C6)", 1, 9, 3)
        c17 = st.slider("Harga (C1) VS Fasilitas Garasi (C7)", 1, 9, 4)
        
        c23 = st.slider("Luas Bangunan (C2) VS Jumlah Kamar Tidur (C3)", 1, 9, 3)
        c24 = st.slider("Luas Bangunan (C2) VS Jumlah Kamar Mandi (C4)", 1, 9, 3)
        c25 = st.slider("Luas Bangunan (C2) VS Umur Rumah (C5)", 1, 9, 2)
        c26 = st.slider("Luas Bangunan (C2) VS Jenis Rumah (C6)", 1, 9, 2)
        c27 = st.slider("Luas Bangunan (C2) VS Fasilitas Garasi (C7)", 1, 9, 3)
        
        c34 = st.slider("Jumlah Kamar Tidur (C3) VS Jumlah Kamar Mandi (C4)", 1, 9, 1)
        c35 = st.slider("Jumlah Kamar Tidur (C3) VS Umur Rumah (C5)", 1, 9, 1)
        c36 = st.slider("Jumlah Kamar Tidur (C3) VS Jenis Rumah (C6)", 1, 9, 2)
        c37 = st.slider("Jumlah Kamar Tidur (C3) VS Fasilitas Garasi (C7)", 1, 9, 2)
        
        c45 = st.slider("Jumlah Kamar Mandi (C4) VS Umur Rumah (C5)", 1, 9, 1)
        c46 = st.slider("Jumlah Kamar Mandi (C4) VS Jenis Rumah (C6)", 1, 9, 1)
        c47 = st.slider("Jumlah Kamar Mandi (C4) VS Fasilitas Garasi (C7)", 1, 9, 2)
        
        c56 = st.slider("Umur Rumah (C5) VS Jenis Rumah (C6)", 1, 9, 1)
        c57 = st.slider("Umur Rumah (C5) VS Fasilitas Garasi (C7)", 1, 9, 1)
        
        c67 = st.slider("Jenis Rumah (C6) VS Fasilitas Garasi (C7)", 1, 9, 1)

    # Sinkronisasi pemetaan data ke dalam matriks berpasangan beraturan resiprokal
    if metode_input != "Gunakan Template Buyer Properti (10 Persona)" or "7. Kolektor Mobil" not in tipe_buyer:
        matriks_ahp[0, 1] = c12; matriks_ahp[1, 0] = 1 / c12
        matriks_ahp[0, 2] = c13; matriks_ahp[2, 0] = 1 / c13
        matriks_ahp[0, 3] = c14; matriks_ahp[3, 0] = 1 / c14
        matriks_ahp[0, 4] = c15; matriks_ahp[4, 0] = 1 / c15
        matriks_ahp[0, 5] = c16; matriks_ahp[5, 0] = 1 / c16
        matriks_ahp[0, 6] = c17; matriks_ahp[6, 0] = 1 / c17
        
        matriks_ahp[1, 2] = c23; matriks_ahp[2, 1] = 1 / c23
        matriks_ahp[1, 3] = c24; matriks_ahp[3, 1] = 1 / c24
        matriks_ahp[1, 4] = c25; matriks_ahp[4, 1] = 1 / c25
        matriks_ahp[1, 5] = c26; matriks_ahp[5, 1] = 1 / c26
        matriks_ahp[1, 6] = c27; matriks_ahp[6, 1] = 1 / c27
        
        matriks_ahp[2, 3] = c34; matriks_ahp[3, 2] = 1 / c34
        matriks_ahp[2, 4] = c35; matriks_ahp[4, 2] = 1 / c35
        matriks_ahp[2, 5] = c36; matriks_ahp[5, 2] = 1 / c36
        matriks_ahp[2, 6] = c37; matriks_ahp[6, 2] = 1 / c37
        
        matriks_ahp[3, 4] = c45; matriks_ahp[4, 3] = 1 / c45
        matriks_ahp[3, 5] = c46; matriks_ahp[5, 3] = 1 / c46
        matriks_ahp[3, 6] = c47; matriks_ahp[6, 3] = 1 / c47
        
        matriks_ahp[4, 5] = c56; matriks_ahp[5, 4] = 1 / c56
        matriks_ahp[4, 6] = c57; matriks_ahp[6, 4] = 1 / c57
        
        matriks_ahp[5, 6] = c67; matriks_ahp[6, 5] = 1 / c67

    st.write("---")
    jalankan_hitung = st.button("Eksekusi Perhitungan Matriks & Perangkingan")
    
    if jalankan_hitung:
        # Komputasi Nilai Bobot Eigenvector Kriteria Utama
        kolom_sum = matriks_ahp.sum(axis=0)
        matriks_normalisasi = matriks_ahp / kolom_sum
        bobot_kriteria = matriks_normalisasi.mean(axis=1)
        
        # Validasi Uji Konsistensi Logika Matematis (CR Saaty Ordo 7)
        RI = 1.32
        weighted_sum = np.dot(matriks_ahp, bobot_kriteria)
        consistency_vector = weighted_sum / bobot_kriteria
        lambda_max = np.mean(consistency_vector)
        CI = (lambda_max - 7) / 6
        CR = CI / RI if CI > 0 else 0
        
        if CR < 0.1:
            st.success(f"Preferensi Pengisian Konsisten! (Nilai CR = {CR:.4f})")
        else:
            st.warning(f"Pola Kurang Konsisten, disarankan meninjau ulang susunan slider (Nilai CR = {CR:.4f})")
            
        # PROSES TAMPILAN 3 TAHAP VISUALISASI MATRIKS UTAMA
        st.subheader("Visualisasi Tahapan Perhitungan Matriks AHP")
        
        st.write("1. Matriks Perbandingan Berpasangan Asli (Pairwise Comparison Matrix):")
        df_view_pairwise = pd.DataFrame(matriks_ahp, columns=kriteria_label, index=kriteria_label)
        st.dataframe(df_view_pairwise.style.format("{:.2f}"), use_container_width=True)
        
        st.write("2. Matriks Perbandingan Berpasangan Ternormalisasi Kolom:")
        df_view_normal = pd.DataFrame(matriks_normalisasi, columns=kriteria_label, index=kriteria_label)
        st.dataframe(df_view_normal.style.format("{:.3f}"), use_container_width=True)
        
        st.write("3. Hasil Akhir Vektor Bobot Kriteria Utama (Eigenvector):")
        df_bobot = pd.DataFrame({
            'Kriteria Utama': kriteria_label,
            'Bobot Pengaruh': bobot_kriteria
        })
        st.dataframe(df_bobot.style.format({'Bobot Pengaruh': '{:.4f}'}), use_container_width=True)
        
        # VISUALISASI 1: GRAFIK PEMBOBOTAN SEBARAN BOBOT KRITERIA UTAMA
        st.write("4. Grafik Distribusi Pembobotan Prioritas Kriteria:")
        df_grafik_bobot = df_bobot.sort_values(by='Bobot Pengaruh', ascending=True)
        fig_bobot = px.bar(
            df_grafik_bobot, x='Bobot Pengaruh', y='Kriteria Utama', orientation='h',
            title="Prioritas Kontribusi Bobot Pengaruh Kriteria",
            color='Bobot Pengaruh', color_continuous_scale='GnBu'
        )
        fig_bobot.update_layout(template="plotly_dark")
        st.plotly_chart(fig_bobot, use_container_width=True)
        
        # Penyaringan Data Berdasarkan Subset Kota Terpilih
        if kota_pilihan != 'Semua Kota':
            alternatif = df_rumah[df_rumah['city'] == kota_pilihan].copy()
        else:
            alternatif = df_rumah.head(1000).copy()
            
        if alternatif.empty:
            st.error("Properti tidak ditemukan pada kota yang dipilih.")
        else:
            # PROSES FILTER FILTER DINAMIS BERDASARKAN KUANTIL STATISTIK DATA
            p_low, p_high = alternatif['price'].quantile([0.33, 0.66])
            l_low, l_high = alternatif['livingArea'].quantile([0.33, 0.66])
            a_low, a_high = alternatif['house_age'].quantile([0.33, 0.66])
            
            def get_r_price(x): return 'Murah' if x <= p_low else ('Sedang' if x <= p_high else 'Mahal')
            def get_r_area(x): return 'Sempit' if x <= l_low else ('Cukup' if x <= l_high else 'Luas')
            def get_r_beds(x): return 'Sedikit' if x <= 2 else ('Standar' if x == 3 else 'Banyak')
            def get_r_baths(x): return 'Sedikit' if x <= 1.5 else ('Standar' if x <= 2.5 else 'Banyak')
            def get_r_age(x): return 'Baru' if x <= a_low else ('Sedang' if x <= a_high else 'Tua')
            def get_r_garage(x): return 'Tidak Ada Garasi' if x == 0 else ('Ada Garasi Standar' if x <= 2 else 'Ada Garasi Luas')
            
            alternatif['r_price'] = alternatif['price'].apply(get_r_price)
            alternatif['r_area'] = alternatif['livingArea'].apply(get_r_area)
            alternatif['r_beds'] = alternatif['bedrooms'].apply(get_r_beds)
            alternatif['r_baths'] = alternatif['bathrooms'].apply(get_r_baths)
            alternatif['r_age'] = alternatif['house_age'].apply(get_r_age)
            alternatif['r_garage'] = alternatif['garageSpaces'].apply(get_r_garage)
            
            def hitung_skor(row):
                s_price = bobot_kriteria[0] * bobot_rating['price'][row['r_price']]
                s_area = bobot_kriteria[1] * bobot_rating['livingArea'][row['r_area']]
                s_beds = bobot_kriteria[2] * bobot_rating['bedrooms'][row['r_beds']]
                s_baths = bobot_kriteria[3] * bobot_rating['bathrooms'][row['r_baths']]
                s_age = bobot_kriteria[4] * bobot_rating['house_age'][row['r_age']]
                s_type = bobot_kriteria[5] * bobot_rating['homeType'].get(row['homeType'], 0.10)
                s_garage = bobot_kriteria[6] * bobot_rating['garageSpaces'][row['r_garage']]
                return s_price + s_area + s_beds + s_baths + s_age + s_type + s_garage

            alternatif['Skor Akhir'] = alternatif.apply(hitung_skor, axis=1)
            hasil_ranking = alternatif.sort_values(by='Skor Akhir', ascending=False).head(10).reset_index()
            hasil_ranking['ID Rumah'] = "Properti ID-" + hasil_ranking['index'].astype(str)
            
            tabel_final = hasil_ranking[['ID Rumah', 'streetAddress', 'city', 'price', 'livingArea', 'bedrooms', 'bathrooms', 'house_age', 'homeType', 'garageSpaces', 'Skor Akhir']].copy()
            tabel_final.columns = ['ID Rumah', 'Alamat', 'Kota', 'Harga (USD)', 'Luas (Sqft)', 'Kamar Tidur', 'Kamar Mandi', 'Umur Rumah', 'Jenis Properti', 'Kapasitas Garasi', 'Skor Akhir']
            
            st.subheader("Hasil Akhir Perangkingan (Top 10 Rekomendasi)")
            st.dataframe(tabel_final.style.format({
                'Harga (USD)': '${:,.2f}',
                'Luas (Sqft)': '{:,.0f}',
                'Kapasitas Garasi': '{:.0f} mobil',
                'Skor Akhir': '{:.4f}'
            }), use_container_width=True)
            
            # VISUALISASI 2: GRAFIK KOMPARASI PEMERINGKATAN SKOR AKHIR ALTERNATIF TOP 10
            st.write("Grafik Pemeringkatan Nilai Skor Akhir Alternatif Properti (Top 10):")
            fig_skor = px.bar(
                tabel_final, x='ID Rumah', y='Skor Akhir',
                title="Peringkat Skor Akhir Akumulasi Global SPK AHP",
                color='Skor Akhir', color_continuous_scale='Viridis'
            )
            fig_skor.update_layout(template="plotly_dark")
            st.plotly_chart(fig_skor, use_container_width=True)
            
            st.session_state.hasil_terakhir = hasil_ranking
    else:
        st.info("Atur tingkat kepentingan antar kriteria di atas, kemudian tekan tombol 'Eksekusi Perhitungan Matriks & Perangkingan' untuk melihat hasil.")

# ---------------------------------------------------------
# HALAMAN 4: VISUALISASI SEBARAN SPASIAL (PETA)
# ---------------------------------------------------------
elif menu_halaman == "Halaman Visualisasi Peta":
    st.title("Distribusi Geografis Properti")
    st.write("Halaman ini menyajikan peta sebaran alternatif rumah rekomendasi.")
    
    if st.session_state.hasil_terakhir is not None and not st.session_state.hasil_terakhir.empty:
        st.map(st.session_state.hasil_terakhir[['latitude', 'longitude']].dropna(), latitude='latitude', longitude='longitude')
    else:
        st.warning("Belum ada data perangkingan untuk ditampilkan. Silakan hitung terlebih dahulu di halaman 'Halaman Hitung SPK'.")
