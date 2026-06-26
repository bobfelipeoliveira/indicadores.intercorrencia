# SGOI — Sistema de Gestão Operacional da Intercorrência
**Solar Cuidados © 2026**

Sistema corporativo completo para gestão operacional da equipe de Intercorrência.

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.9 ou superior
- pip

### 1. Clone o projeto
```bash
git clone <repo-url>
cd sgoi
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Execute o sistema
```bash
streamlit run app.py
```

O sistema abrirá automaticamente no navegador em `http://localhost:8501`

---

## 📂 Estrutura do Projeto

```
sgoi/
├── app.py                    # Ponto de entrada principal
├── requirements.txt
├── README.md
├── database/
│   ├── db.py                 # Conexão e inicialização SQLite
│   └── sgoi.db               # Banco de dados (gerado automaticamente)
├── services/
│   └── import_service.py     # Serviço de importação Excel/CSV
├── repository/
│   └── data_repo.py          # Camada de acesso a dados
├── pages/
│   ├── dashboard_exec.py     # Dashboard Executivo
│   ├── dashboard_diretoria.py
│   ├── indicadores_mensais.py
│   ├── tickets.py
│   └── other_pages.py        # Demais módulos
├── utils/
│   └── charts.py             # Utilitários de gráficos Plotly
├── styles/
│   └── theme.py              # CSS/Tema Solar Cuidados
├── assets/
│   └── logo.png              # (coloque aqui o logotipo oficial)
├── config/
├── models/
├── components/
└── logs/
```

---

## 📋 Módulos do Sistema

| Módulo | Descrição |
|--------|-----------|
| 🏠 Início | Tela inicial com KPIs e ações rápidas |
| 📊 Dashboard Executivo | Visão operacional completa com gráficos |
| 👔 Dashboard Diretoria | Visão estratégica e Meta × Resultado |
| 📅 Indicadores Mensais | Análise diária detalhada por mês |
| 📆 Indicadores Anuais | Comparativo entre meses |
| 👥 Pacientes | Cadastro e histórico de pacientes |
| 🎫 Tickets | Gestão completa de tickets (2 abas) |
| 🔁 Call Back | Controle de retornos pendentes |
| 📞 Ligações | Análise de ligações transferidas |
| 👁️ Monitoramentos | Registro e acompanhamento |
| ⚠️ Pendências | Painel de pendências por criticidade |
| 🎯 SLA | Central de controle de SLA |
| 📅 Timeline | Histórico cronológico por paciente |
| 🔍 Central de Causas | Pareto e análise de causas |
| 🌡️ Mapa de Calor | Heatmaps de ligações e tickets |
| 📄 Relatórios | Geração e exportação de relatórios |
| 📤 Importação | Importação de Excel/CSV/ODS |
| ⚙️ Configurações | Configurações do sistema |

---

## 📥 Importação de Dados

1. Acesse o menu **Importação**
2. Faça upload do arquivo Excel (`.xlsx`) exportado do sistema CRM/telefonia
3. O sistema mapeia automaticamente as colunas e importa os dados
4. Formatos suportados: `.xlsx`, `.xls`, `.csv`, `.ods`

### Estrutura esperada do Excel:
- **Sheet "Tickets - MAIO/JUN"**: tickets com colunas SOLICITANTE, DATA, PACIENTE, etc.
- **Sheet "Ligações Transferidas MAIO/JUN"**: relatório de chamadas transferidas
- **Sheet "INDICADORES - MAIO/JUN"**: indicadores diários por data
- **Sheet "CONSOLIDADO-MAIO"**: totalizadores mensais
- **Sheet "PACIENTES DE MAIO"**: lista de pacientes e volume de tickets

---

## 🔒 Segurança

- Banco SQLite local — dados nunca saem do servidor
- Estrutura preparada para migração para PostgreSQL/MySQL
- Separação clara entre camadas (repository, service, presentation)

---

## 🔄 Migração para PostgreSQL

Altere apenas `database/db.py`:
```python
# Substituir sqlite3 por psycopg2 ou sqlalchemy
import psycopg2
DB_URL = "postgresql://user:pass@host:5432/sgoi"
```
Toda a camada de repository permanece inalterada.

---

## 🤖 Preparado para IA

A arquitetura em camadas permite integração futura com:
- Claude API para análise automática de tickets
- Modelos de predição de SLA
- Classificação automática de causas
- Geração de relatórios em linguagem natural

---

## 📞 Suporte
Sistema desenvolvido exclusivamente para Solar Cuidados — Intercorrência.
