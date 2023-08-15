FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./api /app
COPY pyproject.toml /app/
WORKDIR /app

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
