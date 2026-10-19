"""data/spots.json を組み立てる。紹介文・ジャンルは手書きの元メモどおり、座標と住所だけ places_log.json から取る。"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
log = json.loads((ROOT / "places_log.json").read_text(encoding="utf-8"))

AREAS = [
    {"id": "kawaramachi", "name": "四条河原町・烏丸", "color": "#e8543f"},
    {"id": "gion", "name": "祇園・東山・清水", "color": "#7b5cd6"},
    {"id": "rakuhoku", "name": "洛北・哲学の道", "color": "#2f9e7d"},
    {"id": "uji", "name": "宇治", "color": "#3f7fd6"},
]

# slug, 表示名, エリア, ジャンル, 紹介文, 写真, places_log の何番目の候補か
SPOTS = [
    ("green-terrace", "グリーンテラス", "rakuhoku", "ごはん",
     "丁寧なおばんざいがいただける。気候によってはテラス席が気持ちいい。カヌレもおすすめ。",
     ["green-terrace-1.jpg", "green-terrace-2.png", "green-terrace-3.png"], 0),
    ("hokkyokusei", "北極星", "kawaramachi", "ごはん",
     "定番オムライスがいただける。", ["hokkyokusei.jpg"], 0),
    ("restaurant-star", "レストランスター", "kawaramachi", "ごはん",
     "オムライスの種類が豊富。パフェもある。", ["restaurant-star.jpg"], 0),
    ("chuka-sakai", "中華サカイ", "rakuhoku", "ごはん",
     "冷やし中華がおいしい。麺がいい。", ["chuka-sakai.jpg"], 0),
    ("swan", "すわん", "uji", "ごはん",
     "街の洋食屋さん。宇治に行くなら考えてみても。", ["swan.jpg"], 0),
    ("sugari", "和醸良麺 すがり", "kawaramachi", "ごはん",
     "おいしいラーメン屋さん。古民家っぽい空間も良い。", ["sugari.jpg"], 0),
    ("soiree", "ソワレ", "kawaramachi", "喫茶・甘味",
     "空間がよい。", ["soiree-1.png", "soiree-2.png"], 0),
    ("gion-koishi", "祇園小石 祇園本店", "gion", "喫茶・甘味",
     "抹茶パフェがよい。", ["gion-koishi.png"], 0),
    ("ikkyuan", "一休庵", "gion", "喫茶・甘味",
     "円山公園の中にある。わらび餅の食べ比べができる。", ["ikkyuan.png"], 0),
    ("itoken-sousou", "伊藤軒／SOU・SOU 清水店", "gion", "食べ歩き",
     "かわいいお菓子がある。", ["itoken-sousou.jpg"], 0),
    ("nakajima", "夷川餃子なかじま 団栗店", "gion", "ごはん",
     "いい感じの餃子定食がいただける。", ["nakajima.jpg"], 0),
    ("que-pasa", "ケパサ", "kawaramachi", "ごはん",
     "いい感じのメキシコ料理（ブリトーなど）がいただける。", ["que-pasa.jpg"], 1),
]


# ぽこピー関連の店（地図・一覧・詳細に 🥜 を付ける）
MARK = {"nakajima", "que-pasa"}
# Places の websiteUri が公式でないもの（グルメサイト）は載せない
NOT_OFFICIAL = ("hotpepper.jp", "gnavi.co.jp", "tabelog.com")
# url_check.py（safe_url）の結果で差し替えたもの。http → https の最終URL、None は載せない
URL_FIX = {
    "chuka-sakai": "https://www.reimen.jp/",
    "sugari": "https://www.sugari.net/",
    "soiree": "https://www.soiree-kyoto.com/",
    "que-pasa": None,  # Places の値は Facebook ページで、safe_url で確認できない（HTTP 400）
}


def short_addr(a):
    a = re.sub(r"^〒\d{3}-\d{4}\s*", "", a)
    return a.replace("京都府", "", 1)


spots = []
for slug, name, area, cat, desc, photos, idx in SPOTS:
    p = log[slug][idx]
    s = {
        "slug": slug, "name": name, "area": area, "cat": cat,
        "lat": round(p["location"]["latitude"], 6), "lng": round(p["location"]["longitude"], 6),
        "approx": False, "desc": desc, "address": short_addr(p["formattedAddress"]),
    }
    hours = p.get("regularOpeningHours", {}).get("weekdayDescriptions")
    if hours:
        s["hours"] = hours
    url = URL_FIX.get(slug, p.get("websiteUri"))
    if url and not any(d in url for d in NOT_OFFICIAL):
        s["url"] = url
    if slug in MARK:
        s["mark"] = True
    s["photos"] = ["photos/" + f for f in photos]
    s["sources"] = []
    spots.append(s)
    for f in photos:
        assert (ROOT / "photos" / f).exists(), f

(ROOT / "data" / "spots.json").write_text(
    json.dumps({"areas": AREAS, "spots": spots}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(len(spots), "spots")
