# 京都おすすめごはんMAP

京都のおすすめ食事処・喫茶店を、写真つきでエリア別の地図にまとめた静的サイト。

- `index.html` … 表示（`data/config.json` / `data/spots.json` を実行時に読む。ビルド不要）
- `data/spots.json` … スポット（紹介文・ジャンル・座標・住所・写真パス）
- `photos/` … 写真（撮影位置などのメタデータは `tools/strip_meta.py` で除去済み）
- `tools/build_data.py` … spots.json の組み立て（座標と住所は Google Places で確認したもの）

ローカル確認: `python -m http.server` → http://localhost:8000/
