## Async Content Summarizer

### Local (Docker Compose)

- Copy env: `cp .env.example .env` and fill values
- Start: `docker compose up --build`
- Migrate: `docker compose run --rm -e PYTHONPATH=/app api alembic -c alembic.ini upgrade head`
- API docs: `http://localhost:8000/docs`

### Environment variables

- `DATABASE_URL`
- `REDIS_URL`
- `OPENAI_API_KEY` (optional)
- `OPENAI_MODEL` (optional, default `gpt-4o-mini`)
- `OPENAI_TIMEOUT_SECONDS` (optional)

### Demo (curl)

Submit:

```bash
curl -sS -X POST http://localhost:8000/submit \
  -H 'Content-Type: application/json' \
  -d '{"text":"hello world"}'
```

Poll:

```bash
curl -sS http://localhost:8000/status/<job_id>
```

Result:

```bash
curl -sS http://localhost:8000/result/<job_id>
```

Duplicate (cache hit on second submit):

```bash
curl -sS -X POST http://localhost:8000/submit -H 'Content-Type: application/json' -d '{"text":"dup"}'
curl -sS -X POST http://localhost:8000/submit -H 'Content-Type: application/json' -d '{"text":"dup"}'
```

### Tests

```bash
pytest -q
```

### What to submit

1. **GitHub repository**
   - Working code with clear structure
   - `README.md` with setup instructions
   - `.env.example` with required environment variables

2. **Video walkthrough (5–7 minutes)**
   - Architecture overview (quick diagram)
   - Code walkthrough (key files only)
   - Live demo: submit → poll → get result
   - Edge cases (validation, failures, caching)

### Local (without Docker)

- Install: `pip install -r requirements.txt`
- Run API: `uvicorn app.main:app --reload --port 8000`
- Health: `GET /health`