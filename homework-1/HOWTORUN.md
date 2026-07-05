# How to Run the Application

## Setup

```bash
cd homework-1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run API

```bash
./demo/run.sh
```

The API runs at `http://127.0.0.1:3000`.

## API Key

Read endpoints require an API key:

```bash
X-API-Key: homework-api-key
```

You can override the default key:

```bash
export BANKING_API_KEY="your-local-key"
```

## Run Tests

```bash
PYTHONPATH=src pytest -q
```

## Try Sample Requests

In another terminal:

```bash
./demo/sample-requests.sh
```
