FROM python:3.10-slim

ARG PROJECT_ID
ENV PROJECT_ID=${PROJECT_ID}

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY vertex .