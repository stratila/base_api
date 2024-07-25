FROM python:3.12.3
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"
WORKDIR /app
COPY . /app/
# COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root --no-dev
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]