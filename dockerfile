FROM python:3.12-slim
RUN mkdir /app

# WORKDIR /app
COPY ./app /app/
COPY ./README.md ./pyproject.toml ./poetry.lock /


# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry==1.4.0
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .
WORKDIR /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]