FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install -r requirements.txt gunicorn

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/tmp

ARG APP_NAME=
ENV APP_NAME=${APP_NAME}

RUN if [ -z "$APP_NAME" ]; then echo "APP_NAME argument is required" >&2; exit 1; fi

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app
COPY . .

RUN mkdir -p /app && chmod -R 777 /app \
    && python manage.py collectstatic --noinput || true

EXPOSE 8000

USER appuser

CMD ["sh", "-c", "\
    python manage.py migrate && \
    gunicorn ${APP_NAME}.wsgi \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "]
