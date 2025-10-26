
IdeaBridge - FastAPI backend
=========================================

Contents:
- app/ (FastAPI app, models, crud, schemas)
- requirements.txt
- docker-compose.yml
- Dockerfile
- .env.example

Quickstart (Docker)
-------------------
1. Copy the repo to your machine and in the project root (where docker-compose.yml is):
   - Edit .env.example -> create .env with your DB password OR edit docker-compose.yml to set desired POSTGRES_PASSWORD.
2. Build and run:
   docker-compose up --build

- Postgres will be available on port 5432 (host), Adminer on 8080, backend on 8000.

Quickstart (local without Docker)
--------------------------------
1. Create Python venv and install dependencies:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. Set DATABASE_URL env var, e.g.:
   export DATABASE_URL=postgresql://postgres:yourpass@localhost:5432/your_db_name

3. Start backend:
   uvicorn app.main:app --reload

Notes
-----
- The app uses SQLAlchemy sync models and Base.metadata.create_all on startup as a dev fallback.

