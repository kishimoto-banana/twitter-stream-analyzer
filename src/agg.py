import collections
import json
import pathlib
from typing import Any, Dict, List


def json_dump(d: Dict[Any, Any], filepath: str):
    with open(filepath, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def agg_geowords(tweet_geowords: List[Any]):
    surface_geojsons = {}
    surface_words = {}
    for tweet_geoword in tweet_geowords:
        geos = tweet_geoword["geo"]
        words = tweet_geoword["words"]

        tweet_surfeces = set([])
        for geo in geos:
            surface = geo["properties"]["surface"]
            # 同一ツイートに同じ位置（surface）があった場合スキップ（単語の重複カウントを防ぐ）
            if surface in tweet_surfeces:
                continue

            if surface not in surface_geojsons:
                surface_geojsons[surface] = geo

            if surface not in surface_words:
                surface_words[surface] = []
                # 同一ツイートでの同じ単語は1つにする
                # 指している位置(surface)の単語と"RT"は除去する
            surface_words[surface] += [
                word for word in set(words) if word not in [surface, "RT"]
            ]

    return surface_geojsons, surface_words


def main():
    data_path = pathlib.Path("data")

    print("load tweet geowords")
    tweet_geowords = []
    for path in data_path.glob("*.json"):
        with open(path, mode="r") as f:
            d = json.load(f)
            tweet_geowords += d

    print("agg tweet geowords")
    surface_geojsons, surface_words = agg_geowords(tweet_geowords)

    print("count words")
    aggs = []
    for surface, words in surface_words.items():
        c = collections.Counter(words)
        d = {
            "geojson": surface_geojsons[surface],
            "freq_words": [{"word": t[0], "count": t[1]} for t in (c.most_common(10))],
        }
        aggs.append(d)

    print("dump")
    json_dump(aggs, "output/agg.json")


if __name__ == "__main__":
    main()
