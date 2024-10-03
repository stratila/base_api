FROM stratila/python-poetry:3.12-1.4.0 as base
RUN mkdir /app

# WORKDIR /app
COPY ./app /app/
COPY ./tests /tests
COPY ./README.md ./pyproject.toml ./poetry.lock /


# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


### DEVELOPMENT BUILD STAGE
FROM base AS development

RUN poetry export -f requirements.txt --output requirements.txt --with test
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

WORKDIR /app

CMD ["/bin/bash", "-c",  \
      "python3 scripts/python/postgres_is_ready.py && \
      alembic upgrade head && \
      python3 scripts/python/update_roles_and_permissions.py && \
      uvicorn api.app:app --host 0.0.0.0 --reload" ]


### PRODUCTION BUILD STAGE
FROM base AS production

RUN poetry export -f requirements.txt --output requirements.txt --without dev,test
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

WORKDIR /app

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0"]
