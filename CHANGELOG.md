# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [2.0] - 2026-03-30

### ✨ Adicionado
- **Filtros Avançados em Cascata**: Região → Estado → Cidade → Modelo
- **Busca por Geolocalização**: Campo para centralizar mapa em um local específico
- **Marcador de Busca**: Indicador visual do local buscado (marcador azul)
- **Popups Melhorados**: HTML formatado com emojis e informações organizadas
- **Exportação de Dados**: Botões para download em CSV e Excel
- **Métricas Aprimoradas**: Exibição de registros filtrados e percentual
- **Seção de Alertas**: Preparação para integração com Zabbix
- **Arquivo README**: Documentação completa do projeto
- **Arquivo requirements.txt**: Gerenciamento de dependências
- **Arquivo .env.example**: Template de configuração

### 🔧 Melhorado
- Reorganização da barra lateral com filtros principais
- Melhor performance com clustering de marcadores
- Identificação automática de colunas mais robusta
- Tratamento de erros em geolocalização
- Interface mais intuitiva e profissional

### 🐛 Corrigido
- Tratamento de valores faltantes (NaN) nos filtros
- Validação de coordenadas antes de adicionar ao mapa
- Encoding de caracteres especiais

### 📝 Documentação
- Adicionado guia completo de uso
- Instruções para integração com Zabbix
- Estrutura de dados esperada documentada

## [1.0] - 2026-03-15

### ✨ Adicionado
- Versão inicial do projeto
- Integração com Google Sheets
- Mapa interativo com Folium
- Filtros dinâmicos básicos
- Busca global de dados
- Geolocalização automática de endereços
- Agrupamento de marcadores (clustering)
- Tabela de dados filtrados

---

**Próximas Melhorias Planejadas:**
- [ ] Integração com API do Zabbix
- [ ] Sistema de alertas em tempo real
- [ ] Histórico de status das torres
- [ ] Notificações por email/Slack
- [ ] Dashboard de KPIs
- [ ] Autenticação de usuários
- [ ] Temas escuro/claro
