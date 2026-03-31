import streamlit as st

# TEM QUE SER A PRIMEIRA COISA DO STREAMLIT
st.set_page_config(
    layout="wide",
    page_title="Mapa de Sites Compromisso - Monitoramento"
)

# AGORA SIM o resto
import pkg_resources

try:
    pkg_resources.get_distribution("folium")
except:
    pass

import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import io

# =========================
# CONFIG
# =========================
URL = "https://docs.google.com/spreadsheets/d/1Oy2N6iGrDHnGSimR6AoNiHtCKUQaqKbQHqMwKM9pX9o/export?format=csv&gid=0"

st.set_page_config(layout="wide", page_title="Mapa de Sites Compromisso - Monitoramento")

# ============================
#  ESTADO DO MAPA (NÃO RESETAR)
# ============================
if "map_lat" not in st.session_state:
    st.session_state.map_lat = -5.7945  # padrão inicial

if "map_lon" not in st.session_state:
    st.session_state.map_lon = -38.4526

if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 10

# =========================
# INICIALIZAR SESSION STATE
# =========================
if 'centro_mapa' not in st.session_state:
    st.session_state.centro_mapa = [-5.0, -39.0]
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 6
if 'marker_busca' not in st.session_state:
    st.session_state.marker_busca = None
if 'msg_busca' not in st.session_state:
    st.session_state.msg_busca = ""
if 'termo_busca_anterior' not in st.session_state:
    st.session_state.termo_busca_anterior = ""

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
col_vendor = encontrar_coluna(["VENDOR"])

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
geolocator = Nominatim(user_agent="mapa_torres_v3")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def obter_coordenadas(endereco):
    try:
        location = geolocator.geocode(endereco, timeout=30)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        return None, None

    return None, None
    
    # Se não encontrar com contexto, tenta sem
    try:
        location = geocode(endereco)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    
    return None, None

# =========================
# FUNÇÕES DE BUSCA INTELIGENTE
# =========================

def buscar_site_por_nome(termo):
    """Busca um site pelo SINGLE RAN NAME"""
    if col_nome is None:
        return None
    
    termo_lower = termo.lower().strip()
    resultado = df[df[col_nome].astype(str).str.lower().str.contains(termo_lower, na=False)]
    
    if not resultado.empty:
        return resultado.iloc[0]
    return None

def buscar_por_coordenadas(termo):
    """Tenta interpretar como coordenadas (lat,lng ou lat lng)"""
    termo = termo.strip()
    
    # Tenta separar por vírgula ou espaço
    partes = termo.replace(',', ' ').split()
    
    if len(partes) == 2:
        try:
            lat = float(partes[0])
            lng = float(partes[1])
            
            # Valida se são coordenadas válidas do Brasil
            if -5 <= lat <= 5 and -45 <= lng <= -35:
                return lat, lng
        except ValueError:
            pass
    
    return None, None

def buscar_localizacao_geografica(termo):
    """Busca uma localização geográfica"""
    lat, lng = obter_coordenadas(termo)
    return lat, lng

def busca_inteligente(termo):
    """
    Realiza busca inteligente em ordem de prioridade:
    1. Nome do site (SINGLE RAN NAME)
    2. Coordenadas diretas
    3. Localização geográfica
    """
    
    if not termo or not termo.strip():
        return None, None, None
    
    termo = termo.strip()
    
    # 1. Tenta buscar por nome de site
    site = buscar_site_por_nome(termo)
    if site is not None:
        lat = site[col_lat] if col_lat and pd.notna(site[col_lat]) else None
        lng = site[col_lng] if col_lng and pd.notna(site[col_lng]) else None
        
        if lat and lng:
            return float(lat), float(lng), f"Site encontrado: {termo}"
    
    # 2. Tenta interpretar como coordenadas
    lat, lng = buscar_por_coordenadas(termo)
    if lat and lng:
        return lat, lng, f"Coordenadas: {lat}, {lng}"
    
    # 3. Tenta buscar como localização geográfica
    lat, lng = buscar_localizacao_geografica(termo)
    if lat and lng:
        return lat, lng, f"Localização: {termo}"
    
    return None, None, None

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
# 🔎 BUSCA UNIFICADA INTELIGENTE
# =========================
st.subheader("🔍 Busca Inteligente Unificada")

col_busca_input, col_busca_btn, col_limpar = st.columns([3, 1, 1])

with col_busca_input:
    busca_termo = st.text_input(
        "Buscar por: Nome do Site (ex: CEIAU010) | Coordenadas (ex: -6.45 -39.38) | Local (ex: Sobral)",
        placeholder="Digite um site, coordenadas ou localização...",
        key="busca_unificada"
    )

with col_busca_btn:
    busca_button = st.button("🔎 Buscar", use_container_width=True, key="btn_busca")

with col_limpar:
    limpar_button = st.button("🔄 Limpar", use_container_width=True, key="btn_limpar")

# Processar busca
if busca_button and busca_termo:
    with st.spinner("🔄 Buscando..."):

        lat, lng, mensagem = busca_inteligente(busca_termo)

        if lat is not None and lng is not None:
            # 🔥 ATUALIZA O MAPA DE VERDADE
            st.session_state.map_lat = float(lat)
            st.session_state.map_lon = float(lng)
            st.session_state.map_zoom = 12
            st.session_state.busca_manual = True

            st.success(f"✅ {mensagem}")

        else:
            st.error("❌ Local não encontrado")
# Limpar busca
if limpar_button:
    st.session_state.centro_mapa = [-5.0, -39.0]
    st.session_state.zoom_level = 6
    st.session_state.marker_busca = None
    st.session_state.msg_busca = ""
    st.session_state.termo_busca_anterior = ""
    st.info("🔄 Mapa resetado para a visualização padrão.")

# =========================
# ABAS LATERAIS
# =========================
st.sidebar.title("🎛️ Painel de Controle")

tab_filtros, tab_sem_coord = st.sidebar.tabs(["🔧 Filtros", "⚠️ Sem Coordenadas"])

# =========================
# ABA 1: FILTROS
# =========================
with tab_filtros:

    st.subheader("🔍 Buscar localização")

    col1, col2 = st.columns(2)

    with col1:
        nova_lat = st.number_input("Latitude", value=st.session_state.map_lat)

    with col2:
        nova_lon = st.number_input("Longitude", value=st.session_state.map_lon)

    if st.button("📍 Atualizar mapa"):
        st.session_state.map_lat = nova_lat
        st.session_state.map_lon = nova_lon
        st.session_state.map_zoom = 13

    if st.button("🔄 Resetar mapa"):
        st.session_state.map_lat = -5.7945
        st.session_state.map_lon = -38.4526
        st.session_state.map_zoom = 10


        st.subheader("Filtros Avançados")
    
    df_filtrado = df.copy()

    # Filtros em cascata
    if col_regiao:
        regioes = sorted(df[col_regiao].dropna().unique())
        filtro_regiao = st.multiselect(
            "📍 Região",
            regioes,
            default=regioes,
            key="filtro_regiao"
        )
        if filtro_regiao:
            df_filtrado = df_filtrado[df_filtrado[col_regiao].isin(filtro_regiao)]

    if col_estado:
        estados_disponiveis = sorted(df_filtrado[col_estado].dropna().unique())
        filtro_estado = st.multiselect(
            "🏛️ Estado",
            estados_disponiveis,
            default=estados_disponiveis,
            key="filtro_estado"
        )
        if filtro_estado:
            df_filtrado = df_filtrado[df_filtrado[col_estado].isin(filtro_estado)]

    if col_cidade:
        cidades_disponiveis = sorted(df_filtrado[col_cidade].dropna().unique())
        filtro_cidade = st.multiselect(
            "🏙️ Cidade",
            cidades_disponiveis,
            default=cidades_disponiveis,
            key="filtro_cidade"
        )
        if filtro_cidade:
            df_filtrado = df_filtrado[df_filtrado[col_cidade].isin(filtro_cidade)]

    if col_modelo:
        modelos = sorted(df_filtrado[col_modelo].dropna().unique())
        filtro_modelo = st.multiselect(
            "📶 Modelo",
            modelos,
            default=modelos,
            key="filtro_modelo"
        )
        if filtro_modelo:
            df_filtrado = df_filtrado[df_filtrado[col_modelo].isin(filtro_modelo)]

    # Filtros adicionais dinâmicos
    st.markdown("---")
    
    for col in df.columns:
        if col not in [col_regiao, col_estado, col_modelo, col_cidade, col_lat, col_lng, col_nome, col_vendor]:
            if df[col].dtype == 'object' and 5 < df_filtrado[col].nunique() < 50:
                valores = sorted(df_filtrado[col].dropna().unique())
                selecionados = st.multiselect(
                    col,
                    valores,
                    default=valores,
                    key=f"filtro_{col}"
                )
                if selecionados:
                    df_filtrado = df_filtrado[df_filtrado[col].isin(selecionados)]

    # Busca global
    st.markdown("---")
    busca_global = st.text_input("🔎 Busca Global", placeholder="Torre, cidade, etc", key="busca_global_sidebar")

    if busca_global:
        df_filtrado = df_filtrado[df_filtrado.apply(
            lambda row: row.astype(str).str.contains(busca_global, case=False).any(),
            axis=1
        )]

# =========================
# ABA 2: SITES SEM COORDENADAS
# =========================
with tab_sem_coord:
    st.subheader("⚠️ Sites Sem Coordenadas")
    
    # Identificar sites sem coordenadas
    df_sem_coord = df[(df[col_lat].isna()) | (df[col_lng].isna())].copy()
    
    if len(df_sem_coord) > 0:
        st.warning(f"**{len(df_sem_coord)} sites sem coordenadas precisam ser preenchidos**")
        
        # Mostrar informações essenciais
        cols_essenciais = [col_nome, col_regiao, col_estado, col_cidade, col_modelo, col_vendor]
        cols_essenciais = [c for c in cols_essenciais if c is not None]
        
        if cols_essenciais:
            df_sem_coord_display = df_sem_coord[cols_essenciais].drop_duplicates()
            st.dataframe(df_sem_coord_display, use_container_width=True)
            
            # Botão para exportar
            csv = df_sem_coord_display.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Baixar Lista (CSV)",
                data=csv,
                file_name="sites_sem_coordenadas.csv",
                mime="text/csv"
            )
        else:
            st.dataframe(df_sem_coord, use_container_width=True)
    else:
        st.success("✅ Todos os sites possuem coordenadas!")

# =========================
# 📍 CENTRO DO MAPA (CORRIGIDO)
# =========================

if col_lat and col_lng:

    coords_validas = df_filtrado[[col_lat, col_lng]].dropna()

    if not coords_validas.empty:

        # Só atualiza automaticamente se NÃO houve busca manual
        if "busca_manual" not in st.session_state:
            st.session_state.busca_manual = False

        if not st.session_state.busca_manual:
            st.session_state.map_lat = float(coords_validas[col_lat].mean())
            st.session_state.map_lon = float(coords_validas[col_lng].mean())
# =========================
# 🗺️ CRIAR MAPA
# =========================
mapa = folium.Map(
    location=[st.session_state.map_lat, st.session_state.map_lon],
    zoom_start=st.session_state.map_zoom
)
cluster = MarkerCluster().add_to(mapa)

# Adicionar marcador de busca se houver
if st.session_state.marker_busca:
    folium.Marker(
        location=st.session_state.marker_busca,
        popup=f"📍 {st.session_state.msg_busca}",
        icon=folium.Icon(color='blue', icon='search', prefix='fa')
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

        # Montar popup SIMPLIFICADO
        popup_html = f"""
        <div style="font-family: Arial; width: 280px; font-size: 12px;">
            <h4 style="margin: 0 0 8px 0; color: #1f77b4; font-size: 14px;">{nome}</h4>
            <hr style="margin: 5px 0;">
        """

        # Adicionar apenas informações principais
        if col_regiao and pd.notna(row[col_regiao]):
            popup_html += f"<b>Região:</b> {row[col_regiao]}<br>"
        if col_estado and pd.notna(row[col_estado]):
            popup_html += f"<b>Estado:</b> {row[col_estado]}<br>"
        if col_cidade and pd.notna(row[col_cidade]):
            popup_html += f"<b>Cidade:</b> {row[col_cidade]}<br>"
        if col_modelo and pd.notna(row[col_modelo]):
            popup_html += f"<b>Modelo:</b> {row[col_modelo]}<br>"
        if col_vendor and pd.notna(row[col_vendor]):
            popup_html += f"<b>Vendor:</b> {row[col_vendor]}<br>"

        popup_html += f"<b>Lat:</b> {lat:.6f}<br>"
        popup_html += f"<b>Lng:</b> {lng:.6f}<br>"

        popup_html += "</div>"

        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=300),
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
    csv = df_filtrado.to_csv(index=False, encoding='utf-8')
    st.download_button(
        label="📥 Baixar como CSV",
        data=csv,
        file_name="torres_filtradas.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_export2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Torres')
    buffer.seek(0)
    st.download_button(
        label="📥 Baixar como Excel",
        data=buffer,
        file_name="torres_filtradas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# =========================
# 🔔 PREPARAÇÃO PARA ZABBIX
# =========================
st.markdown("---")
st.subheader("🔔 Sistema de Alertas (Preparação Zabbix)")

st.info("""
**Status Atual:** Sistema preparado para integração com Zabbix.

**Funcionalidades Futuras:**
- Conexão com API do Zabbix para monitoramento de status
- Indicadores visuais (Verde = Online, Vermelho = Offline)
- Histórico de alertas e downtime
- Notificações em tempo real
""")
