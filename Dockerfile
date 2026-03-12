FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=natlife.config.production

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ /app/requirements/
RUN pip install --upgrade pip \
    && pip install -r /app/requirements/production.txt

COPY natlife/ /app/natlife/
COPY .env /app/natlife/.env

WORKDIR /app/natlife

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "natlife.wsgi:application", "--worker-class", "gevent", "--worker-connections", "1000", "--workers", "4"]
