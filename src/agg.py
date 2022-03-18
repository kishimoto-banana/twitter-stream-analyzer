import collections
import json
import pathlib


def json_dump(d, filepath):
    with open(filepath, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def agg_geowords(geowords):
    surfece_words = {}
    for geoword in geowords:
        geos = geoword["geo"]
        words = geoword["words"]
        surfeces = set([])

        for geo in geos:
            surface = geo["properties"]["surface"]
            if surface not in surfeces:
                surfeces.add(surface)
                if surface not in surfece_words:
                    surfece_words[surface] = {"geojson": geo, "words": []}
                surfece_words[surface]["words"] += [
                    word for word in words if word not in [surface, "RT"]
                ]

    return surfece_words


def main():
    data_path = pathlib.Path("data")

    print("load geowords")
    geowords = []
    for path in data_path.glob("*.json"):
        with open(path, mode="r") as f:
            d = json.load(f)
            geowords += d

    print("agg geowords")
    surfece_words = agg_geowords(geowords)

    print("count words")
    for key in surfece_words.keys():
        c = collections.Counter(surfece_words[key]["words"])
        surfece_words[key]["freq_words"] = [
            {"word": t[0], "count": t[1]} for t in (c.most_common(10))
        ]
        del surfece_words[key]["words"]

    print("dump")
    json_dump(surfece_words, "data/agg.json")


if __name__ == "__main__":
    main()
