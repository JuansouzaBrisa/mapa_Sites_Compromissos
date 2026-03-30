# 📍 Mapa Inteligente de Torres - Monitoramento ANATEL

Sistema de monitoramento e visualização de torres de telecomunicações com integração a planilha Google Sheets, filtros avançados, busca por geolocalização e preparação para integração com Zabbix.

## 🎯 Funcionalidades

### ✅ Implementadas
- **Integração com Google Sheets**: Consumo automático de dados via CSV
- **Mapa Interativo**: Visualização em tempo real com Folium e Streamlit
- **Filtros Avançados em Cascata**:
  - Filtro por Região
  - Filtro por Estado
  - Filtro por Cidade
  - Filtro por Modelo
  - Filtros dinâmicos adicionais
- **Busca Global**: Filtragem rápida de dados
- **Busca por Geolocalização**: Centraliza o mapa em um local específico
- **Geolocalização Automática**: Obtém coordenadas de endereços faltantes
- **Agrupamento de Markers**: Clustering para melhor performance
- **Exportação de Dados**: Download em CSV e Excel
- **Métricas em Tempo Real**: Total de torres, com/sem coordenadas

### 🔜 Preparadas para Integração Zabbix
- Estrutura base para adicionar coluna de `STATUS`
- Indicadores visuais (cores de marcadores)
- Seção de alertas e monitoramento
- Placeholder para conexão com API Zabbix

## 📋 Modificações Realizadas

### Versão 2.0 - Melhorias Implementadas

#### 1. **Filtros Organizados e em Cascata**
```python
# Filtros principais na barra lateral
- Região (com cascata para Estados)
- Estado (com cascata para Cidades)
- Cidade
- Modelo
- Filtros adicionais dinâmicos
```

#### 2. **Busca por Geolocalização**
```python
# Novo campo de busca que centraliza o mapa
busca_localizacao = st.text_input("Digite um local para centralizar o mapa")
# Adiciona marcador azul no local buscado
```

#### 3. **Popups Melhorados**
```python
# HTML formatado com emojis e melhor organização
# Exibe informações principais (Região, Estado, Cidade, Modelo)
# Outras informações em seção secundária
```

#### 4. **Exportação de Dados**
```python
# Botões para download em CSV e Excel
# Exporta apenas dados filtrados
```

#### 5. **Métricas Aprimoradas**
```python
# Exibe registros filtrados, removidos e percentual
# Gráfico de status (quando disponível)
```

#### 6. **Preparação para Zabbix**
```python
# Seção informativa sobre integração futura
# Estrutura pronta para adicionar STATUS
# Placeholder para gráfico de status
```

## 🚀 Como Usar

### Instalação

```bash
# Clone o repositório
git clone https://github.com/JuansouzaBrisa/mapa_Sites_Compromissos.git
cd mapa_Sites_Compromissos

# Instale as dependências
pip install -r requirements.txt
```

### Executar a Aplicação

```bash
# Com Streamlit
streamlit run app.py

# A aplicação abrirá em http://localhost:8501
```

### Gerar Mapa Estático

```bash
# Execute o script para gerar HTML estático
python script
```

## 📦 Dependências

- `pandas`: Manipulação de dados
- `folium`: Criação de mapas interativos
- `streamlit`: Framework web
- `streamlit-folium`: Integração Folium + Streamlit
- `geopy`: Geolocalização de endereços
- `openpyxl`: Exportação para Excel

## 📊 Estrutura de Dados Esperada

A planilha Google Sheets deve conter as seguintes colunas (nomes flexíveis):

| Coluna | Alternativas | Tipo | Obrigatório |
|--------|-------------|------|------------|
| SINGLE RAN NAME | TORRE, SITE, NAME | String | ✅ Sim |
| LAT | LATITUDE | Float | ✅ Sim |
| LONG | LONGITUDE, LON | Float | ✅ Sim |
| REGIÃO | REGION | String | ✅ Sim |
| ESTADO | STATE | String | ✅ Sim |
| CIDADE | CITY | String | ✅ Sim |
| MODELO | MODEL | String | ✅ Sim |
| Outras colunas | - | Variável | ❌ Não |

## 🔔 Integração com Zabbix (Futuro)

Para integrar com Zabbix, siga os passos:

### 1. Adicione Coluna de Status
Na planilha, adicione uma coluna chamada `STATUS` com valores:
- `Online`
- `Offline`
- `Maintenance`

### 2. Configure Credenciais
Crie um arquivo `.env` na raiz do projeto:
```env
ZABBIX_URL=https://seu-zabbix.com
ZABBIX_USER=seu_usuario
ZABBIX_PASSWORD=sua_senha
ZABBIX_API_TOKEN=seu_token
```

### 3. Implemente Função de Sincronização
```python
def obter_status_zabbix():
    # Conectar à API do Zabbix
    # Obter status de cada host
    # Retornar DataFrame com status atualizado
    pass
```

### 4. Cores de Indicadores
- 🟢 **Verde**: Online
- 🔴 **Vermelho**: Offline
- 🟡 **Amarelo**: Manutenção

## 📝 Notas Importantes

- A aplicação atualiza os dados a cada **5 minutos** (cache)
- Geolocalização de endereços tem limite de requisições (1 por segundo)
- Recomenda-se ter coordenadas (LAT/LONG) preenchidas na planilha
- O mapa centraliza automaticamente na média das coordenadas filtradas

## 🤝 Contribuições

Para melhorias ou sugestões, abra uma issue ou pull request.

## 📄 Licença

Este projeto é de uso interno para monitoramento ANATEL.

---

**Última Atualização:** 30/03/2026
**Versão:** 2.0
**Status:** ✅ Produção
