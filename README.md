# Desafio Técnico — Data Engineering

Pipeline **ETL (Extract → Transform → Load)** para coleta, tratamento e análise de dados automotivos extraídos do site Hubbi Data.

---

## Visão Geral

| Etapa | Tecnologia | Saída |
|---|---|---|
| Extract | Requests + Inertia.js | `data/raw/raw_parts.json` |
| Transform | Pandas | `data/processed/parts.csv` |
| Load | SQLAlchemy + SQLite | `data/parts.db` |
| Análise | SQL + Pandas + Matplotlib | `analysis/eda.ipynb` |

---

## Arquitetura

```
Website Hubbi (Cloudflare + Inertia.js)
        │
        ▼
┌─────────────────────────────────────────────┐
│  EXTRACT — scraper/scraper.py               │
│  Requests com header X-Inertia              │
│  10 workers paralelos (ThreadPoolExecutor)  │
└─────────────────┬───────────────────────────┘
                  │  data/raw/raw_parts.json
                  ▼
┌─────────────────────────────────────────────┐
│  TRANSFORM — transform/transform.py         │
│  Normalização, tipagem e serialização       │
└─────────────────┬───────────────────────────┘
                  │  data/processed/parts.csv
                  ▼
┌─────────────────────────────────────────────┐
│  LOAD — database/ingest.py                  │
│  SQLAlchemy ORM + SQLite                    │
│  Upsert por PART_NUMBER (sem duplicatas)    │
└─────────────────┬───────────────────────────┘
                  │  data/parts.db
                  ▼
┌─────────────────────────────────────────────┐
│  EDA — analysis/eda.ipynb                   │
│  Consultas SQL + Pandas + Matplotlib        │
└─────────────────────────────────────────────┘
```

---

## Estrutura do Projeto

```
desafio-etl/
│
├── analysis/
│   └── eda.ipynb               # Análise exploratória de dados
│
├── data/
│   ├── raw/
│   │   └── raw_parts.json      # Dados brutos coletados
│   ├── processed/
│   │   └── parts.csv           # Dados tratados
│   └── parts.db                # Banco de dados SQLite
│
├── database/
│   ├── database.py             # Configuração da conexão
│   ├── ingest.py               # Lógica de carga
│   └── models.py               # Modelos ORM (SQLAlchemy)
│
├── logs/
│   └── scraper.log             # Log de execução
│
├── scraper/
│   ├── config.py               # Configurações e constantes
│   ├── scraper.py              # Lógica de coleta
│   └── storage.py              # Persistência dos dados brutos
│
├── transform/
│   └── transform.py            # Transformações com Pandas
│
├── .env                        # Variáveis de ambiente (não versionado)
├── .env.example                # Modelo de configuração
├── main.py                     # Ponto de entrada do pipeline
├── requirements.txt
└── README.md
```

---

## Instalação

**1. Clone o repositório**

```bash
git clone <url-do-repositorio>
cd tl
```

**2. Crie e ative o ambiente virtual**

```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

---

## Configuração

Copie o arquivo de exemplo e preencha as variáveis:

```bash
cp .env.example .env
```

```env
# .env
COOKIE=hubbi-data-session=...; XSRF-TOKEN=...
```

### Obtendo o cookie de sessão

O site utiliza **Cloudflare Turnstile** como proteção anti-bot. Qualquer automação de browser (Playwright, Selenium, etc.) é bloqueada pelo sistema de forma proativa. A abordagem adotada foi capturar o cookie de sessão do browser real do usuário, que já possui a reputação de navegação reconhecida pelo Cloudflare.

**Passo a passo:**

1. Acesse `https://teste-tecnico-dados.hubbi.app` no seu navegador
2. Pressione **F12** para abrir o DevTools
3. Vá até a aba **Network (Rede)**
4. Recarregue a página (**F5**)
5. Clique na primeira requisição da lista (domínio principal)
6. Em **Request Headers**, localize o campo `Cookie`
7. Copie o valor completo — ele contém os dois tokens necessários:

```
hubbi-data-session=...; XSRF-TOKEN=...
```

8. Cole esse valor na variável `COOKIE` do arquivo `.env`

> **Nota:** Os cookies têm tempo de expiração de algumas horas. Se expirarem durante a execução, o pipeline detecta automaticamente e exibe uma mensagem solicitando a renovação — sem perda do progresso já coletado.

---

## Execução

```bash
python main.py
```

O pipeline verifica se `data/raw/raw_parts.json` já existe antes de iniciar o scraping. Se existir, reutiliza os dados brutos e executa apenas Transform e Load — evitando requisições desnecessárias.

**Fluxo completo:**

```
python main.py
      │
      ├── raw_parts.json existe?
      │       ├── Sim → pula scraping
      │       └── Não → executa scraping (834 páginas, ~20.000 peças)
      │
      ├── Transformação dos dados
      ├── Exportação do CSV tratado
      └── Ingestão no SQLite
```

**Arquivos gerados ao final:**

```
data/
├── raw/raw_parts.json
├── processed/parts.csv
└── parts.db
```

---

## Transformações Aplicadas

| Campo | Transformação |
|---|---|
| Campos de texto | Convertidos para `MAIÚSCULO` |
| `price` | `float` com 2 casas decimais (formato americano) |
| `gross_weight`, `width`, `length` | `float` em kg/cm; zeros convertidos para `NULL` |
| `product_url` | Montada a partir do `part_number` |
| `applications` | Serializada como array JSON |
| Duplicatas | Removidas por `part_number` |

---

## Modelo Relacional

```
parts
─────────────────────────────
id               INTEGER  PK
name             TEXT
product_url      TEXT
part_number      TEXT     UNIQUE
brand_name       TEXT
category         TEXT
type             TEXT
price            NUMERIC
gross_weight     NUMERIC
width            NUMERIC
length           NUMERIC
warranty         TEXT
material         TEXT
photo_url        TEXT
stock_quantity   INTEGER
applications     TEXT     (JSON array)
```

---

## Análise Exploratória (EDA)

O notebook `analysis/eda.ipynb` contém as seguintes análises:

- Total de produtos e marcas cadastrados
- Ranking de marcas por volume de produtos
- Ranking de categorias
- Estatísticas de preço (mínimo, máximo, média, mediana)
- Produtos mais caros
- Produtos com maior estoque
- Peso médio por categoria
- Produtos sem estoque
- Visualizações gráficas dos principais indicadores

---

## Tecnologias

- **Python 3.12**
- **Requests** — coleta HTTP com sessão paralela
- **Pandas** — transformação e normalização dos dados
- **SQLAlchemy** — ORM e abstração do banco
- **SQLite** — persistência relacional
- **Matplotlib** — visualizações na EDA
- **Jupyter Notebook** — análise exploratória interativa

---

## Logs

A execução gera logs detalhados em `logs/scraper.log`, incluindo progresso do scraping, avisos de falha por página e status da ingestão.