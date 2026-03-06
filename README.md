# Semantic Search Engine with Vector Database

A document search system showing the difference between keyword search and semantic (meaning-based) search, powered by Ollama embeddings and pgvector.

## How It Works

```
User Query
    │
    ├── Keyword Search → SQL LIKE matching → Results
    │
    └── Semantic Search → Ollama embeds query → pgvector cosine similarity → Results
```

Both searches are Redis-cached after the first call.

## Prerequisites

- Python 3.10+
- PostgreSQL 15 with pgvector extension
- Ollama running locally with `nomic-embed-text` model
- Redis running locally

```bash
ollama pull nomic-embed-text
brew services start postgresql@15
brew services start redis
```

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure environment**

Copy `.env.example` to `.env` (or edit `.env` directly). Defaults work for a local setup with user `apple` and no password.

```bash
DB_NAME=semantic_search
DB_USER=apple         # your macOS username
DB_PASSWORD=
OLLAMA_EMBED_MODEL=nomic-embed-text
REDIS_URL=redis://localhost:6379/0
```

**3. Create the database**
```bash
psql -U apple -d postgres -c "CREATE DATABASE semantic_search;"
psql -U apple -d semantic_search -c "CREATE EXTENSION vector;"
```

**4. Run migrations**
```bash
cd backend
DJANGO_SETTINGS_MODULE=config.settings python manage.py migrate
```

**5. Load sample documents** (30 documents across tech, science, health, history)
```bash
DJANGO_SETTINGS_MODULE=config.settings python manage.py ingest
```
This step takes ~1 minute as it generates embeddings via Ollama.

## Running

Open two terminals:

**Terminal 1 — Django backend (port 8010)**
```bash
cd backend
DJANGO_SETTINGS_MODULE=config.settings python manage.py runserver 8010
```

**Terminal 2 — Streamlit UI (port 8511)**
```bash
cd ui
streamlit run app.py --server.port 8511
```

Then open http://localhost:8511

## API Endpoints

```
GET /api/search/keyword?q=<query>    # SQL LIKE search
GET /api/search/semantic?q=<query>   # Vector similarity search
```

Example:
```bash
curl "http://localhost:8010/api/search/semantic?q=how+do+computers+communicate"
```

## Seeing the Difference

| Query | Keyword | Semantic |
|---|---|---|
| `PostgreSQL` | Finds docs with exact word | Also finds database-related docs |
| `how do computers communicate` | No results | Finds internet/networking articles |
| `staying fit` | No results | Finds exercise and health articles |

Semantic search understands *meaning*, not just word matching. This is the key advantage of vector databases.
