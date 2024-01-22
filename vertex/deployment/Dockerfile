FROM python:3.10-slim-buster

ARG PROJECT_ID
ENV PROJECT_ID=${PROJECT_ID}

COPY requirements.txt .
COPY pyproject.toml .
COPY ./vertex ./vertex
RUN pip install -r requirements.txt
