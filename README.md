# 京都おすすめごはんMAP

京都のおすすめ食事処・喫茶店を、写真つきでエリア別の地図にまとめた静的サイト。

- `index.html` … 表示（`data/config.json` / `data/spots.json` を実行時に読む。ビルド不要）
- `data/spots.json` … スポット（紹介文・ジャンル・座標・住所・営業時間・公式サイト・写真パス）。`mark: true` はぽこピー関連（🥜）
- `photos/` … 写真（撮影位置などのメタデータは `tools/strip_meta.py` で除去済み）
- `tools/build_data.py` … spots.json の組み立て（座標・住所・営業時間・公式サイトは Google Places の値）
- `tools/url_check.py` + `tools/safe_url.py` … 公式サイトURLの安全確認（URLを変えたら公開前に実行）

ローカル確認: `python -m http.server` → http://localhost:8000/
