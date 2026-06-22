# ClashRecruit

ClashRecruit is a full-stack web application for Clash of Clans recruiting. Recruiters can publish clan listings, players can browse and filter listings, and logged-in users can save clans.

The backend is a Flask API backed by MongoDB, Redis, and Celery. The frontend is a React app created with Create React App.

## Tech Stack

Frontend:
- React
- React Router
- Native Fetch API
- Create React App tooling

Backend:
- Python 3.12
- Flask
- MongoDB
- Redis
- Celery
- Clash of Clans API

## Repository Layout

```text
ClashRecruit/
├── api/                 Clash API wrappers
├── routes/              Flask route handlers
├── services/            Backend service modules
├── tests/               Backend pytest suite
├── frontend/            React frontend
├── app.py               Flask application entrypoint
├── clash_http_client.py Shared Clash API HTTP client
├── config.py            Environment-backed config
├── docker-compose.yml   Local Nginx/Gunicorn/worker/Redis stack
├── Dockerfile           Backend image
├── pyproject.toml       Ruff and pytest config
└── requirements.txt     Pinned backend dependencies
```

## Runtime Versions

Use the versions declared in the repo:

- Python: `3.12` via `.python-version`
- Node: `20` via `.nvmrc`
- npm: `10.x` via `frontend/package.json`

The backend Docker image also uses Python 3.12.

## Environment

Create a `.env` file in the repository root:

```env
FLASKSECRETKEY=your_secret_key
DBURI=your_mongodb_connection_string
APIKEY=your_clash_of_clans_api_key
```

Optional development flags:

```env
CLASH_DEV_PREFLIGHT=False
CLASH_INIT_DB_ON_START=False
```

- `CLASH_DEV_PREFLIGHT=true` runs a lightweight Clash API reachability check at backend startup.
- `CLASH_INIT_DB_ON_START=true` pings MongoDB and creates required indexes at backend startup.

## Local Development

### Full Stack with Docker Compose

From the repository root:

```bash
docker compose up --build
```

This starts:
- Nginx on `http://127.0.0.1`
- Gunicorn-backed Flask app on the private Docker network
- Redis
- Celery worker
- Celery beat scheduler

Nginx serves the production React build and proxies backend requests to Gunicorn.

Stop the stack:

```bash
docker compose down
```

### Backend Manually

Create a virtual environment and install backend dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Start Redis separately, then run the backend from the repository root:

```bash
PYTHONPATH="$(pwd)/.." CLASH_DEV_PREFLIGHT=False CLASH_INIT_DB_ON_START=False \
  flask --app ClashRecruit.app run --host=127.0.0.1 --port=5000
```

In separate terminals, run Celery when background jobs are needed:

```bash
PYTHONPATH="$(pwd)/.." celery -A ClashRecruit.services.celery_app:app worker --loglevel=info
PYTHONPATH="$(pwd)/.." celery -A ClashRecruit.services.celery_app:app beat --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm start
```

The frontend runs at `http://localhost:3000` and proxies API requests to `http://127.0.0.1:5000`.

When running through Docker Compose, Nginx serves the frontend at `http://127.0.0.1` and proxies API requests to the `web` service at `http://web:5000`.

## Checks

Backend checks:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest
```

Frontend checks:

```bash
cd frontend
npm test -- --watchAll=false --passWithNoTests
npm run build
```

There is not currently an explicit frontend `lint` script.

## CI

Backend CI is defined in `.github/workflows/backend-ci.yml`.

On pull requests and pushes to `main`, it:
- sets up Python 3.12
- installs `requirements.txt`
- runs Ruff
- runs pytest

Frontend CI is not currently defined.

## Deployment Checklist

This is not a full production hardening guide, but these items should be
checked before putting the app behind a public URL.

For a small deployment, configure at minimum:
- `FLASKSECRETKEY`
- `DBURI`
- `APIKEY`
- Redis/Celery if scheduled import or refresh jobs are needed
- Redis bound only to the private app network; do not publish port `6379`
- a production frontend build
- a production Flask runner such as Gunicorn rather than `flask run`
- a trusted CORS/frontend origin instead of local development defaults
- Cloudflare set to Full or Full (strict) SSL mode, with only ports `80`, `443`, and restricted SSH open on EC2

Before deploying publicly, verify:
- backend tests pass
- frontend build passes
- MongoDB indexes are initialized
- Clash API key is valid for the deployment IP

## License

MIT
