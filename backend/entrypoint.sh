#!/bin/sh
set -e

echo "Importing data..."
python -m scripts.import_data

echo "Seeding demo passwords..."
python -m scripts.seed_passwords

echo "Starting FastAPI..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000