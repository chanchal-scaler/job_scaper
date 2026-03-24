# LinkedIn Tech Jobs API (JobSpy)

Simple FastAPI service that fetches tech jobs from LinkedIn using `python-jobspy`.

## Python Version Requirement

Use **Python 3.11** for this project.

`python-jobspy` currently installs `numpy==1.26.3`, and with Python `3.14` pip may try to build NumPy from source and fail on macOS.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you already created a `3.14` venv, delete and recreate it:

```bash
deactivate 2>/dev/null || true
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run API

```bash
uvicorn main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`
- Simple frontend: `http://127.0.0.1:8000/`

## Deploy To Railway

### Option A (recommended): Deploy via Dockerfile + GitHub

1. Push this project to a GitHub repository.
2. In Railway, click **New Project** -> **Deploy from GitHub repo**.
3. Select your repo. Railway will auto-detect the `Dockerfile`.
4. Deploy.
5. Open the generated Railway domain and test:
   - `/health`
   - `/docs`
   - `/` (frontend)

This project already includes:
- `Dockerfile` (Python 3.11, production uvicorn command)
- `.dockerignore`

### Option B: Railway CLI

```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

After deploy:

```bash
railway open
```

## Endpoints

- `GET /health` - basic service health
- `GET /jobs` - fetch jobs from LinkedIn
  - default source is LinkedIn, but you can pass one or more `site_name` values

### Example

```bash
curl "http://127.0.0.1:8000/jobs?search_term=python%20developer&location=India&results_wanted=15&hours_old=72"
```

Multiple sources example:

```bash
curl "http://127.0.0.1:8000/jobs?site_name=linkedin&site_name=indeed&search_term=software%20engineer&location=United%20States"
```

### Query Params

- `site_name` (repeatable, default: `linkedin`)
  - Supported values: `linkedin`, `indeed`, `zip_recruiter`, `glassdoor`, `google`, `bayt`, `naukri`, `bdjobs`
- `search_term` (default: `software engineer`)
- `location` (default: `United States`)
- `results_wanted` (default: `20`, range: `1-100`)
- `hours_old` (default: `72`, range: `1-720`)
- `linkedin_fetch_description` (default: `false`)
