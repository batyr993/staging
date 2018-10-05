FROM python:2.7-slim
LABEL maintainer="Batyr Atamamedov <batyr.ata93@gmail.com>"

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN pip install --editable .

CMD gunicorn -c "python:config.gunicorn" "toyetjek.app:create_app()"