FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libssl-dev libffi-dev python-dev libmecab-dev mecab-ipadic-utf8 libboost-all-dev

RUN pip install poetry==1.1.4
COPY pyproject.toml poetry.lock ./

# ライブラリ追加時に毎回pygeonlpのインストール走るのどうにかしたい
RUN poetry add pygeonlp==1.2.0 
RUN poetry install --no-root
# RUN poetry install --no-root --no-dev

COPY ./src ./src
