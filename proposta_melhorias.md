# Diagnóstico e Proposta de Melhorias - Mapa de Sites e Compromissos

O projeto atual consiste em uma aplicação **Streamlit** que consome dados de uma planilha do Google Sheets para visualizar torres de telecomunicações em um mapa interativo utilizando **Folium**.

## 📊 Estrutura Atual do Projeto

O repositório contém:
- `app.py`: Aplicação principal em Streamlit.
- `script`: Script Python para geração de mapa estático (`mapa_torres.html`).
- `mapa_torres.html`: Arquivo HTML gerado pelo script.

### Funcionalidades Implementadas
1. **Integração com Planilha**: Consumo automático via exportação CSV do Google Sheets.
2. **Geolocalização**: Uso de `geopy` (Nominatim) para obter coordenadas de endereços faltantes.
3. **Métricas**: Exibição de total de torres e status de coordenadas.
4. **Filtros Dinâmicos**: Filtros automáticos na barra lateral para colunas categóricas.
5. **Busca Global**: Filtragem de dados baseada em texto.
6. **Agrupamento (Clustering)**: Uso de `MarkerCluster` para melhor performance com muitos pontos.

---

## 🚀 Proposta de Melhorias

Com base nos seus objetivos, proponho as seguintes evoluções:

### 1. Filtragem Avançada (Região, Estado, Modelo)
- **Organização**: Criar uma seção específica no topo da barra lateral para os filtros principais (`REGIÃO`, `ESTADO`, `MODELO`).
- **Dependência**: Implementar filtros em cascata (ex: ao selecionar um Estado, mostrar apenas as Cidades daquele estado).

### 2. Busca por Geolocalização (Centralização)
- **Funcionalidade**: Adicionar um campo de busca que, ao invés de filtrar a tabela, **centraliza o mapa** na localização digitada (ex: buscar "Fortaleza, CE" e o mapa focar lá).
- **Marker de Busca**: Colocar um marcador temporário no local buscado.

### 3. Preparação para Integração Zabbix
- **Status Visual**: Adicionar uma coluna de `STATUS` (Online/Offline) que altera a cor do ícone no mapa (Verde/Vermelho).
- **Camada de Dados**: Criar uma função para enriquecer o DataFrame do Pandas com dados vindos da API do Zabbix ou de uma coluna específica da planilha.
- **Alertas**: Espaço para exibir notificações de sites que ficaram offline recentemente.

### 4. Interface e Experiência (UI/UX)
- **Popups Detalhados**: Melhorar a formatação HTML dos popups para facilitar a leitura.
- **Exportação**: Adicionar botão para baixar os dados filtrados em Excel/CSV diretamente da interface.

---

## 🛠️ Próximos Passos Sugeridos
1. **Refatoração do `app.py`** para incluir os filtros organizados.
2. **Implementação da Busca de Centralização** com `geopy`.
3. **Simulação do Status Zabbix** para demonstrar como os alertas funcionarão.

Você gostaria que eu procedesse com a implementação dessas melhorias no código agora?
