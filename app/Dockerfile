
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code

RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir \
  --trusted-host pypi.org \
  --trusted-host files.pythonhosted.org \
  -r /code/requirements.txt


COPY manage.py /code/manage.py
COPY eschecker /code/eschecker
COPY checks /code/checks
COPY templates /code/templates
COPY static /code/static
COPY start.sh /code/start.sh


EXPOSE 8000
