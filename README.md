# FastAPI + Celery Prime Service

 FastAPI app that offloads prime-number computation to Celery workers using Redis as broker and result backend.

## Project structure
- `main.py` — FastAPI app with `/submit`, `/result/{request_id}`, `/worker-status`
- `tasks.py` — Celery app + `compute_first_n_primes` task
- `prime_utils.py` — pure prime helpers (`is_prime`, `first_n_primes`)
- `tests/` — pytest suite (`test_api.py`, `test_prime_utils.py`)
- `requirements.txt` — Python deps
- `prime-service.postman_collection.json` — Postman collection
- `.gitignore` — ignores venv/caches

## Requirements
- Python 3.10+
- Redis running locally (default `redis://localhost:6379/0`)

## Setup
```bash
cd /Users/VivekSharma/Desktop/fastapi-celery-prime-service
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Start Redis (e.g., `brew services start redis` or `redis-server`).

## Run Celery worker
```bash
celery -A tasks.celery_app worker --loglevel=info
```

## Run FastAPI app
```bash
uvicorn main:app --reload  # add --port 8001 if 8000 is busy
```

## API quickstart
- **POST `/submit`**: body `{"n": 10}` → returns `{"request_id": "<id>"}`
- **GET `/result/{request_id}`**: returns status (`PENDING`/`SUCCESS`/`...`) and result when ready
- **GET `/worker-status`**: reports worker liveness plus queue/active task info

Swagger UI: `http://localhost:8000/docs`

## Postman
Import `prime-service.postman_collection.json`, set `baseUrl` to your server (default `http://localhost:8000`), and use the three requests provided.

## Tests
Run all tests (Celery runs in eager mode for tests):
```bash
pytest
```

## Notes
- Default Redis URL comes from `REDIS_URL` env var (fallback `redis://localhost:6379/0`).
- If you see `Address already in use` when starting uvicorn, stop the existing process (`lsof -i :8000` / `kill <pid>`) or run with `--port 8001`.

