FROM python:3.11-alpine

ENV PYTHONPATH=/exchange_rate_viewer/exchange_rate_viewer

WORKDIR /exchange_rate_viewer

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-interaction --no-ansi

COPY exchange_rate_viewer/ exchange_rate_viewer/

CMD [ "poetry", "run", "python", "exchange_rate_viewer/app.py" ]
