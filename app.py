import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import io

# =========================
# CONFIG
# =========================
URL = "https://docs.google.com/spreadsheets/d/1Oy2N6iGrDHnGSimR6AoNiHtCKUQaqKbQHqMwKM9pX9o/export?format=csv&gid=0"

st.set_page_config(layout="wide", page_title="Mapa de Torres - Monitoramento")

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

col_nome = encontrar_coluna(["TORRE", "SITE", "NAME", "SINGLE RAN NAME"])
col_lat = encontrar_coluna(["LAT"])
col_lng = encontrar_coluna(["LON", "LONG"])
col_end = encontrar_coluna(["END", "ADDRESS", "LOCAL"])
col_regiao = encontrar_coluna(["REGIÃO", "REGION"])
col_estado = encontrar_coluna(["ESTADO", "STATE"])
col_modelo = encontrar_coluna(["MODELO", "MODEL"])
col_cidade = encontrar_coluna(["CIDADE", "CITY"])

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
geolocator = Nominatim(user_agent="mapa_torres_v2")
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
st.title("📍 Mapa Inteligente de Torres - Monitoramento ANATEL")
st.markdown("**Sistema de Monitoramento de Sites e Compromissos Obrigatórios**")

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

col1.metric("📡 Total de Torres", total)
col2.metric("✅ Com Coordenadas", com_coord)
col3.metric("❌ Sem Coordenadas", sem_coord)

# =========================
# 🔎 BUSCA POR GEOLOCALIZAÇÃO
# =========================
st.subheader("🔍 Busca por Geolocalização")

col_busca1, col_busca2 = st.columns([3, 1])

with col_busca1:
    busca_localizacao = st.text_input(
        "Digite um local para centralizar o mapa (ex: Fortaleza, CE)",
        placeholder="Fortaleza, Ceará"
    )

with col_busca2:
    busca_button = st.button("🔎 Buscar Localização", use_container_width=True)

centro_mapa = [-5.0, -39.0]  # Centro padrão (Brasil)
marker_busca = None

if busca_button and busca_localizacao:
    with st.spinner("🔄 Buscando localização..."):
        lat, lng = obter_coordenadas(busca_localizacao)
        if lat and lng:
            centro_mapa = [lat, lng]
            marker_busca = (lat, lng)
            st.success(f"✅ Localização encontrada: {lat:.4f}, {lng:.4f}")
        else:
            st.error("❌ Localização não encontrada. Tente novamente.")

# =========================
# 🎛️ FILTROS ORGANIZADOS
# =========================
st.sidebar.title("🎛️ Filtros Avançados")

df_filtrado = df.copy()

# Filtros em cascata
filtro_regiao = None
filtro_estado = None
filtro_modelo = None
filtro_cidade = None

if col_regiao:
    regioes = sorted(df[col_regiao].dropna().unique())
    filtro_regiao = st.sidebar.multiselect(
        "📍 Região",
        regioes,
        default=regioes,
        key="filtro_regiao"
    )
    if filtro_regiao:
        df_filtrado = df_filtrado[df_filtrado[col_regiao].isin(filtro_regiao)]

if col_estado:
    estados_disponiveis = sorted(df_filtrado[col_estado].dropna().unique())
    filtro_estado = st.sidebar.multiselect(
        "🏛️ Estado",
        estados_disponiveis,
        default=estados_disponiveis,
        key="filtro_estado"
    )
    if filtro_estado:
        df_filtrado = df_filtrado[df_filtrado[col_estado].isin(filtro_estado)]

if col_cidade:
    cidades_disponiveis = sorted(df_filtrado[col_cidade].dropna().unique())
    filtro_cidade = st.sidebar.multiselect(
        "🏙️ Cidade",
        cidades_disponiveis,
        default=cidades_disponiveis,
        key="filtro_cidade"
    )
    if filtro_cidade:
        df_filtrado = df_filtrado[df_filtrado[col_cidade].isin(filtro_cidade)]

if col_modelo:
    modelos = sorted(df_filtrado[col_modelo].dropna().unique())
    filtro_modelo = st.sidebar.multiselect(
        "📶 Modelo",
        modelos,
        default=modelos,
        key="filtro_modelo"
    )
    if filtro_modelo:
        df_filtrado = df_filtrado[df_filtrado[col_modelo].isin(filtro_modelo)]

# Filtros adicionais dinâmicos
st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Filtros Adicionais")

for col in df.columns:
    if col not in [col_regiao, col_estado, col_modelo, col_cidade, col_lat, col_lng, col_nome]:
        if df[col].dtype == 'object' and 5 < df_filtrado[col].nunique() < 50:
            valores = sorted(df_filtrado[col].dropna().unique())
            selecionados = st.sidebar.multiselect(
                col,
                valores,
                default=valores,
                key=f"filtro_{col}"
            )
            if selecionados:
                df_filtrado = df_filtrado[df_filtrado[col].isin(selecionados)]

# =========================
# 🔎 BUSCA GLOBAL
# =========================
busca = st.text_input("🔎 Buscar (Sites, Cidade, Geolocalização)")
st.sidebar.markdown("---")
busca_global = st.sidebar.text_input("🔎 Busca Global", placeholder="Torre, cidade, etc")

if busca_global:
    df_filtrado = df_filtrado[df_filtrado.apply(
        lambda row: row.astype(str).str.contains(busca_global, case=False).any(),
        axis=1
    )]

# =========================
# 📍 CENTRO DO MAPA
# =========================
if not marker_busca and col_lat and col_lng:
    coords_validas = df_filtrado[[col_lat, col_lng]].dropna()

    if not coords_validas.empty:
        centro_mapa = [
            coords_validas[col_lat].mean(),
            coords_validas[col_lng].mean()
        ]

# =========================
# 🗺️ CRIAR MAPA
# =========================
mapa = folium.Map(location=centro_mapa, zoom_start=6)
cluster = MarkerCluster().add_to(mapa)

# Adicionar marcador de busca se houver
if marker_busca:
    folium.Marker(
        location=marker_busca,
        popup="📍 Localização Buscada",
        icon=folium.Icon(color='blue', icon='search')
    ).add_to(mapa)

# =========================
# ADICIONAR TORRES AO MAPA
# =========================
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

        # Montar popup com informações formatadas
        popup_html = f"""
        <div style="font-family: Arial; width: 300px;">
            <h4 style="margin: 0 0 10px 0; color: #1f77b4;">{nome}</h4>
            <hr style="margin: 5px 0;">
        """

        # Adicionar informações principais
        if col_regiao and pd.notna(row[col_regiao]):
            popup_html += f"<b>📍 Região:</b> {row[col_regiao]}<br>"
        if col_estado and pd.notna(row[col_estado]):
            popup_html += f"<b>🏛️ Estado:</b> {row[col_estado]}<br>"
        if col_cidade and pd.notna(row[col_cidade]):
            popup_html += f"<b>🏙️ Cidade:</b> {row[col_cidade]}<br>"
        if col_modelo and pd.notna(row[col_modelo]):
            popup_html += f"<b>📶 Modelo:</b> {row[col_modelo]}<br>"

        popup_html += f"<b>📌 Latitude:</b> {lat:.6f}<br>"
        popup_html += f"<b>📌 Longitude:</b> {lng:.6f}<br>"

        # Adicionar outras colunas
        popup_html += "<hr style='margin: 5px 0;'>"
        for col in df.columns:
            if col not in [col_nome, col_lat, col_lng, col_regiao, col_estado, col_cidade, col_modelo]:
                valor = row[col]
                if pd.notna(valor):
                    popup_html += f"<small><b>{col}:</b> {valor}</small><br>"

        popup_html += "</div>"

        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=nome
        ).add_to(cluster)

# =========================
# 📍 EXIBIR MAPA
# =========================
st.subheader("🗺️ Mapa de Torres")
st_folium(mapa, width=1400, height=700)

# =========================
# 📋 TABELA DE DADOS
# =========================
st.subheader("📋 Dados Filtrados")

# Métricas dos dados filtrados
col_info1, col_info2, col_info3 = st.columns(3)
col_info1.metric("Registros Filtrados", len(df_filtrado))
col_info2.metric("Registros Removidos", len(df) - len(df_filtrado))
col_info3.metric("% do Total", f"{(len(df_filtrado)/len(df)*100):.1f}%")

# Exibir tabela
st.dataframe(df_filtrado, use_container_width=True)

# =========================
# 💾 EXPORTAR DADOS
# =========================
st.subheader("💾 Exportar Dados")

col_export1, col_export2 = st.columns(2)

with col_export1:
    if st.button("📥 Baixar como CSV", use_container_width=True):
        csv = df_filtrado.to_csv(index=False, encoding='utf-8')
        st.download_button(
            label="⬇️ Clique para baixar CSV",
            data=csv,
            file_name="torres_filtradas.csv",
            mime="text/csv"
        )

with col_export2:
    if st.button("📥 Baixar como Excel", use_container_width=True):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Torres')
        buffer.seek(0)
        st.download_button(
            label="⬇️ Clique para baixar Excel",
            data=buffer,
            file_name="torres_filtradas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# =========================
# 🔔 PREPARAÇÃO PARA ZABBIX
# =========================
st.markdown("---")
st.subheader("🔔 Sistema de Alertas (Preparação Zabbix)")

st.info("""
**Status Atual:** Sistema preparado para integração com Zabbix.

**Funcionalidades Futuras:**
- ✅ Conexão com API do Zabbix para monitoramento de status
- ✅ Indicadores visuais (Verde = Online, Vermelho = Offline)
- ✅ Histórico de alertas e downtime
- ✅ Notificações em tempo real

**Como Configurar:**
1. Adicione uma coluna `STATUS` na planilha com valores: Online/Offline
2. Configure as credenciais do Zabbix no arquivo `.env`
3. Implemente a função `obter_status_zabbix()` para sincronizar dados
""")

# Placeholder para status Zabbix
if 'STATUS' in df.columns or 'STATUS_ZABBIX' in df.columns:
    col_status = 'STATUS' if 'STATUS' in df.columns else 'STATUS_ZABBIX'
    status_counts = df_filtrado[col_status].value_counts()
    st.write("**Status das Torres Filtradas:**")
    st.bar_chart(status_counts)
