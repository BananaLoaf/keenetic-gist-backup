FROM python:3.10-alpine

WORKDIR /app

# Deps
RUN apk add --no-cache gcc musl-dev libffi-dev
RUN pip install --no-cache-dir poetry

# Install python app globaly
COPY pyproject.toml poetry.lock README.md ./
COPY keenetic_gist_backup/ ./keenetic_gist_backup
ENV POETRY_VIRTUALENVS_CREATE=false
RUN poetry install

ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=1m --timeout=10s \
  CMD keenetic-gist-backup healthcheck

CMD sh -c 'echo "*/10 * * * * keenetic-gist-backup backup" | crontab -; crond -l 2 -f'
