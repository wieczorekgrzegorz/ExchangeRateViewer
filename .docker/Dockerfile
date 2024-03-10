FROM python:3.11-alpine
WORKDIR /exchange_rate_viewer
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry update && poetry install --no-interaction --no-ansi
COPY exchange_rate_viewer/ exchange_rate_viewer/
CMD [ "python3", "exchange_rate_viewer/app.py" ]
