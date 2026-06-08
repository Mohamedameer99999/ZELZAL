FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs npm && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY frontend/package.json frontend/package-lock.json frontend/
RUN cd frontend && npm ci

COPY . .

RUN cd frontend && npm run build
RUN rm -rf frontend/node_modules frontend/src frontend/public

EXPOSE 5000

ENV FLASK_DEBUG=0
CMD ["python", "backend/app.py"]
