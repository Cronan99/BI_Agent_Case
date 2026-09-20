FROM python:3.13-slim

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt

RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY scripts ./scripts
COPY data ./data

RUN chmod +x backend/entrypoint.sh

CMD ["./backend/entrypoint.sh"]