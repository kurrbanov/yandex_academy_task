FROM python:3.9
LABEL maintainer="kurrbanov"
ENV PYTHONUNBUFFERED=1

RUN apt-get update

WORKDIR /usr/src
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./
CMD python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000 \
