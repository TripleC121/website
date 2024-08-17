FROM python:3.12
ENV PYTHONUNBUFFERED=1
WORKDIR /website
COPY requirements-docker.txt /website/
RUN pip install -r requirements-docker.txt
COPY . /website/
