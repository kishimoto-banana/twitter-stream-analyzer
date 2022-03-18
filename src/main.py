import argparse
import json
from datetime import datetime, timedelta
from typing import List

import pygeonlp.api as api
from pymongo import MongoClient
from sudachipy import dictionary
from sudachipy import tokenizer as sudachi_tokenizer


class GeoParse:
    def __init__(self):
        dict_manager = api.dict_manager.DictManager()
        dict_manager.setupBasicDatabase()
        api.init()

    def parse(self, text: str):
        geowords = []
        try:
            result = api.geoparse(text)
        except Exception as e:
            print(e)
            return []
        for r in result:
            if r["properties"]["node_type"] == "GEOWORD":
                geowords.append(r)
        return geowords


class SudachiTokenizer:
    def __init__(self) -> None:
        self.tokenizer = dictionary.Dictionary().create()
        self.pos_filter = ["名詞"]
        self.mode = sudachi_tokenizer.Tokenizer.SplitMode.C

    def parse(self, text: str) -> List[str]:
        words = [
            m.surface()
            for m in self.tokenizer.tokenize(text, self.mode)
            if m.part_of_speech()[0] in self.pos_filter and m.surface()
        ]
        return words


class TweetMongodb:
    def __init__(self):
        self.client = MongoClient("mongodb://root:example@mongo:27017/")
        self.db = self.client.tweet_db
        self.collection = self.db.tweets

    def read_tweets(self, start_datetime: datetime) -> List[str]:
        end_datetime = start_datetime + timedelta(hours=1)
        cur = self.collection.find(
            filter={
                "language": "ja",
                "tweeted_at": {"$gte": start_datetime, "$lt": end_datetime},
            }
        )
        tweets = []
        for row in cur:
            tweets.append(row["text"])

        return tweets


def json_dump(d, filepath):
    with open(filepath, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--start_ymdh",
        required=True,
    )
    args = parser.parse_args()
    if len(args.start_ymdh) != 10:
        raise ValueError("yyyymmddhhで入力してね")

    start_ymdh = args.start_ymdh
    start_datetime = datetime.strptime(start_ymdh, "%Y%m%d%H") - timedelta(hours=9)

    print(f"fetch tweets {start_ymdh}")
    mongo = TweetMongodb()
    tweets = mongo.read_tweets(start_datetime)
    print(len(tweets))

    print("geo and tokenize parse")
    geo_parser = GeoParse()
    tokenize_parser = SudachiTokenizer()
    geowords = []
    for i, tweet in enumerate(tweets):
        if i % 10000 == 0:
            print(f"{i+1} / {len(tweets)}")
        result = geo_parser.parse(tweet)
        if result:
            words = tokenize_parser.parse(tweet)
            geowords += [{"geo": result, "words": words}]

    print("dump json")
    dump_path = f"data/{start_ymdh}.json"
    json_dump(geowords, dump_path)


if __name__ == "__main__":
    main()
