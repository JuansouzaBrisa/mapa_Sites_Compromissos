import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# =========================
# CONFIG
# =========================
URL = "https://docs.google.com/spreadsheets/d/1Oy2N6iGrDHnGSimR6AoNiHtCKUQaqKbQHqMwKM9pX9o/export?format=csv&gid=0"

st.set_page_config(layout="wide", page_title="Mapa de Torres")

# =========================
# CARREGAR DADOS
# =========================
@st.cache_data(ttl=300)
def carregar_dados():
    try:
        df = pd.read_csv(URL, encoding='utf-8')
    except:
        df = pd.read_csv(URL, encoding='latin1')

    df.columns = [col.strip().upper() for col in df.columns]
    return df

df = carregar_dados()

# =========================
# IDENTIFICAR COLUNAS
# =========================
def encontrar_coluna(possiveis):
    for col in df.columns:
        for p in possiveis:
            if p in col:
                return col
    return None

col_nome = encontrar_coluna(["TORRE", "SITE", "NAME"])
col_lat = encontrar_coluna(["LAT"])
col_lng = encontrar_coluna(["LON", "LONG"])
col_end = encontrar_coluna(["END", "ADDRESS", "LOCAL"])

# =========================
# TRATAR COORDENADAS
# =========================
if col_lat:
    df[col_lat] = pd.to_numeric(df[col_lat], errors='coerce')

if col_lng:
    df[col_lng] = pd.to_numeric(df[col_lng], errors='coerce')

# =========================
# GEOCODER
# =========================
geolocator = Nominatim(user_agent="mapa_torres")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def obter_coordenadas(endereco):
    try:
        location = geocode(endereco)
        if location:
            return location.latitude, location.longitude
    except:
        return None, None
    return None, None

# =========================
# 🎨 HEADER
# =========================
st.title("📍 Mapa Inteligente de Torres")

# =========================
# 📊 MÉTRICAS
# =========================
total = len(df)

if col_lat and col_lng:
    com_coord = df[[col_lat, col_lng]].dropna().shape[0]
else:
    com_coord = 0

sem_coord = total - com_coord

col1, col2, col3 = st.columns(3)

col1.metric("Total de Torres", total)
col2.metric("Com Coordenadas", com_coord)
col3.metric("Sem Coordenadas", sem_coord)

# =========================
# 🔎 BUSCA GLOBAL
# =========================
busca = st.text_input("🔎 Buscar (torre, cidade, etc)")

df_filtrado = df.copy()

if busca:
    df_filtrado = df_filtrado[df_filtrado.apply(
        lambda row: row.astype(str).str.contains(busca, case=False).any(),
        axis=1
    )]

# =========================
# 🎛️ FILTROS DINÂMICOS
# =========================
st.sidebar.title("Filtros")

for col in df.columns:
    if df[col].dtype == 'object' and df[col].nunique() < 50:
        valores = sorted(df[col].dropna().unique())
        selecionados = st.sidebar.multiselect(col, valores, default=valores)

        df_filtrado = df_filtrado[df_filtrado[col].isin(selecionados)]

# =========================
# 📍 CENTRO DO MAPA
# =========================
if col_lat and col_lng:
    coords_validas = df_filtrado[[col_lat, col_lng]].dropna()

    if not coords_validas.empty:
        centro = [
            coords_validas[col_lat].mean(),
            coords_validas[col_lng].mean()
        ]
    else:
        centro = [-5.0, -39.0]
else:
    centro = [-5.0, -39.0]

# =========================
# 🗺️ MAPA
# =========================
mapa = folium.Map(location=centro, zoom_start=6)
cluster = MarkerCluster().add_to(mapa)

for i, row in df_filtrado.iterrows():

    nome = str(row[col_nome]) if col_nome else f"Torre {i}"

    lat = row[col_lat] if col_lat else None
    lng = row[col_lng] if col_lng else None

    if pd.isna(lat) or pd.isna(lng):
        if col_end and pd.notna(row[col_end]):
            lat, lng = obter_coordenadas(str(row[col_end]))
        else:
            continue

    if pd.notna(lat) and pd.notna(lng):

        popup = f"<b>{nome}</b><br><hr>"

        for col in df.columns:
            popup += f"<b>{col}:</b> {row[col]}<br>"

        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup, max_width=300)
        ).add_to(cluster)

# =========================
# 📍 EXIBIR MAPA
# =========================
st_folium(mapa, width=1400, height=700)

# =========================
# 📋 TABELA
# =========================
st.subheader("📋 Dados filtrados")
st.dataframe(df_filtrado)