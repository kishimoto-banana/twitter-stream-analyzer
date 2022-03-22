FROM python:3.9-buster as neologd_builder

RUN apt update \
    && apt upgrade -y \
    && apt install -y mecab \
    libmecab-dev \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git /tmp/neologd \
    && cd /tmp/neologd \
    && yes yes | ./bin/install-mecab-ipadic-neologd -n -u

FROM python:3.9
COPY --from=neologd_builder /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libssl-dev libffi-dev python-dev libmecab-dev mecab-ipadic-utf8 libboost-all-dev

RUN pip install poetry==1.1.4
COPY pyproject.toml poetry.lock ./

# ライブラリ追加時に毎回pygeonlpのインストール走るのどうにかしたい
RUN poetry add pygeonlp==1.2.0 
RUN poetry install --no-root
# RUN poetry install --no-root --no-dev

COPY ./src ./src
