"""写真から撮影メタデータ（GPS・機種・撮影日時など）を無劣化で取り除く。

JPEG: 再圧縮せず APP1(EXIF/XMP)・APP2(MPF)・APP3〜15・COM セグメントと EOI 以降の付属データを捨てる
      （APP0 JFIF と APP2 ICC は残す）。
      EXIF の向き(Orientation)が 1 以外なら、向きタグだけの最小 EXIF を入れ直す。
PNG:  テキスト系・eXIf・tIME チャンクを捨てる（画素データはそのまま）。

使い方: python tools/strip_meta.py <入力ディレクトリ> <出力ディレクトリ>
"""
import struct, sys, pathlib, zlib
from PIL import Image


def min_exif(orientation):
    # TIFF(II) ヘッダ + IFD0 に Orientation 1 件だけ
    ifd = struct.pack("<H", 1) + struct.pack("<HHIHH", 0x0112, 3, 1, orientation, 0) + struct.pack("<I", 0)
    tiff = b"II*\x00" + struct.pack("<I", 8) + ifd
    body = b"Exif\x00\x00" + tiff
    return b"\xff\xe1" + struct.pack(">H", len(body) + 2) + body


def strip_jpeg(data, orientation):
    assert data[:2] == b"\xff\xd8"
    out, i = [b"\xff\xd8"], 2
    if orientation not in (None, 1):
        out.append(min_exif(orientation))
    while i < len(data):
        assert data[i] == 0xFF, f"bad marker at {i}"
        m = data[i + 1]
        if m == 0xDA:  # SOS 以降は画像データ。EOI の後ろ（MPF の付属画像・モーションフォト等）は捨てる
            eoi = data.index(b"\xff\xd9", i)
            out.append(data[i:eoi + 2])
            break
        ln = struct.unpack(">H", data[i + 2:i + 4])[0]
        seg = data[i:i + 2 + ln]
        drop = (m == 0xFE or m == 0xE1 or 0xE3 <= m <= 0xEF
                or (m == 0xE2 and not seg[4:16].startswith(b"ICC_PROFILE")))
        if not drop:
            out.append(seg)
        i += 2 + ln
    return b"".join(out)


def strip_png(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    out, i = [data[:8]], 8
    while i < len(data):
        ln = struct.unpack(">I", data[i:i + 4])[0]
        typ = data[i + 4:i + 8]
        chunk = data[i:i + 12 + ln]
        if typ not in (b"tEXt", b"iTXt", b"zTXt", b"eXIf", b"tIME"):
            out.append(chunk)
        i += 12 + ln
    return b"".join(out)


def main(src, dst):
    dst = pathlib.Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(pathlib.Path(src).iterdir()):
        data = f.read_bytes()
        if f.suffix.lower() == ".jpg":
            ori = Image.open(f).getexif().get(0x0112)
            new = strip_jpeg(data, ori)
        else:
            ori, new = None, strip_png(data)
        o = dst / f.name
        o.write_bytes(new)
        im = Image.open(o)
        im.load()
        ex = im.getexif()
        left = {k: v for k, v in ex.items() if k != 0x0112}
        print(f"{f.name}: {len(data)//1024}KB -> {len(new)//1024}KB orientation={ori} "
              f"remaining_exif={left or '-'} gps={bool(ex.get_ifd(0x8825))} size={im.size}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
