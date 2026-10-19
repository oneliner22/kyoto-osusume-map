"""各スポットを Google Places (New) searchText で引き、候補を places_log.json に書き出す（目視用）。"""
import json, os, pathlib, requests

Q = {
    "green-terrace": "グリーンテラス 京都 おばんざい",
    "hokkyokusei": "北極星 オムライス 京都",
    "restaurant-star": "レストランスター 京都 オムライス",
    "chuka-sakai": "中華サカイ 本店 京都 冷やし中華",
    "swan": "すわん 洋食 宇治",
    "sugari": "和醸良麺 すがり 京都",
    "soiree": "喫茶ソワレ 京都",
    "gion-koishi": "祇園小石 祇園本店",
    "ikkyuan": "一休庵 円山公園 わらび餅",
    "itoken-sousou": "伊藤軒 SOU・SOU 清水店",
    "nakajima": "夷川餃子なかじま 団栗店",
    "que-pasa": "ケパサ 京都 メキシコ料理",
}
FIELDS = "places.id,places.displayName,places.formattedAddress,places.location,places.businessStatus,places.regularOpeningHours.weekdayDescriptions,places.websiteUri,places.primaryTypeDisplayName"
key = os.environ["PLACES_API_KEY"]
log = {}
for slug, q in Q.items():
    r = requests.post("https://places.googleapis.com/v1/places:searchText",
                      headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": FIELDS},
                      json={"textQuery": q, "languageCode": "ja", "regionCode": "JP", "maxResultCount": 3,
                            "locationBias": {"circle": {"center": {"latitude": 34.97, "longitude": 135.77}, "radius": 30000}}},
                      timeout=30)
    log[slug] = r.json().get("places", [])
out = pathlib.Path(__file__).resolve().parent.parent / "places_log.json"
out.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
for slug, ps in log.items():
    print(slug)
    for p in ps:
        print("   ", p["displayName"]["text"], "|", p.get("formattedAddress"), "|", p.get("businessStatus"), "|", p.get("primaryTypeDisplayName", {}).get("text"))
