# 🏆 GerenciaTorneio

Sistema web para gerenciar campeonatos de **futebol**, **videogame**, **interclasses** e qualquer outra disputa.

## ✨ Funcionalidades

- 🏆 **Copa** (eliminatória com chaveamento visual/bracket)
- 📋 **Liga** (pontos corridos, tabela automática)
- ⚽ Futebol com artilheiros e cartões
- 🎮 Videogame / Genérico (só placar)
- 🏫 Interclasses com múltiplos esportes
- 📊 Exportar Excel e PDF
- 💾 Banco SQLite (dados persistem entre sessões)

## 🚀 Como Rodar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USER/gerencia-torneio.git
cd gerencia-torneio

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Rode o app
streamlit run app.py
```

Acesse: `http://localhost:8501`

## ☁️ Deploy no Streamlit Cloud (grátis)

1. Suba o projeto no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu repositório
4. Defina `app.py` como entry point
5. Clique em **Deploy** ✅

## 📁 Estrutura

```
torneio/
├── app.py                  # Entry point
├── requirements.txt
├── data/                   # Banco SQLite (gerado automaticamente)
├── pages/
│   ├── novo_campeonato.py
│   ├── times_page.py
│   ├── copa_page.py
│   ├── liga_page.py
│   ├── resultados_page.py
│   └── exportar_page.py
└── utils/
    ├── database.py         # Camada SQLite
    ├── logica.py           # Geração de chaves, rodadas, classificação
    └── exportar.py         # Excel e PDF
```

## 🛠️ Tecnologias

- [Streamlit](https://streamlit.io) — Interface web
- SQLite — Banco de dados local
- openpyxl — Exportação Excel
- ReportLab — Exportação PDF
- Pandas — Tabelas e análise
