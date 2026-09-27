#!/usr/bin/env python3
"""画像生成AI(GPT-Image など)で作ったスプライトシートを、ゲームで使える形に整えるツール。

生成AIの出力は「背景が透過されていない」「コマごとに大きさや位置がずれる」ことが多い。
このツールはそれを自動で直し、ゲームの形式(1コマ 400x300px を横に並べた PNG)にする。

使い方(リポジトリのルートで実行):
  # 1. ゲームに入っている今の画像を取り出す(参考画像・比較用)
  python3 tools/sprite_pipeline.py extract

  # 2. 生成したシートを整える(例: 4列x2行に8コマ並んだ歩行シート)
  python3 tools/sprite_pipeline.py build sprites/generated/walk.png --grid 4x2 --frames 8 \
      --name Dharuriser_walk --anchor hip

  # 3. 結果(sprites/build/ の PNG・GIF・確認用画像)を見て問題なければゲームに組み込む
  python3 tools/sprite_pipeline.py inject sprites/build/Dharuriser_walk.png --key Dharuriser_walk

必要なもの: Python 3 と Pillow, numpy (pip install pillow numpy)
"""
import argparse
import base64
import io
import json
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

CELL_W, CELL_H = 400, 300   # ゲーム側の1コマの大きさ(index.html の CW と画像の高さ)
BASELINE_Y = 299            # 足の裏を揃える位置(今の画像と同じ)
ANCHOR_X = 168              # 腰の中心を揃える位置(今の立ちポーズの腰の位置)
REF_HEIGHT = 236            # 直立したときの身長(今の主人公: 頭のてっぺん64〜足299)
HTML = 'index.html'


# ---------------------------------------------------------------- 背景を消す
def detect_bg(rgb):
    """外周から少し内側の帯で一番多い色を背景色とみなす(コマの端にかかった格子線を避けるため)"""
    h, w, _ = rgb.shape
    m0 = 4; m1 = max(m0 + 4, int(min(h, w) * 0.06))
    ring = np.concatenate([rgb[m0:m1].reshape(-1, 3), rgb[h - m1:h - m0].reshape(-1, 3),
                           rgb[:, m0:m1].reshape(-1, 3), rgb[:, w - m1:w - m0].reshape(-1, 3)])
    q = (ring // 16).astype(np.int32)
    keys = q[:, 0] * 256 + q[:, 1] * 16 + q[:, 2]
    vals, counts = np.unique(keys, return_counts=True)
    top = vals[np.argmax(counts)]
    return ring[keys == top].mean(axis=0)


def is_chroma(bg):
    """背景がクロマキー色(鮮やかな緑やマゼンタなど)かどうか"""
    return bg.max() - bg.min() > 120


def remove_background(img, tol=48, mode='auto'):
    """背景を透明にする。
    - クロマキー背景(緑など): 背景色に近い画素を全部消す(腕と胴の間のすき間も消える)
    - 白や灰色の背景: 外周からつながっている背景だけ消す(キャラの白い部分を守るため)
    """
    rgba = np.array(img.convert('RGBA'))
    rgb = rgba[..., :3].astype(np.int32)
    bg = detect_bg(rgb)
    near = np.sqrt(((rgb - bg) ** 2).sum(-1)) < tol
    if mode == 'auto':
        mode = 'global' if is_chroma(bg) else 'flood'
    if mode == 'global':
        erase = near
        # 緑の映り込み(輪郭のにじみ)を弱める
        if bg[1] > bg[0] + 80 and bg[1] > bg[2] + 80:
            g = rgba[..., 1].astype(np.int32)
            lim = np.maximum(rgba[..., 0], rgba[..., 2]).astype(np.int32)
            rgba[..., 1] = np.minimum(g, lim + 10).astype(np.uint8)
    else:
        erase = flood_from_border(near)
    rgba[erase, 3] = 0
    return Image.fromarray(rgba), bg, mode


def flood_from_border(mask):
    h, w = mask.shape
    seen = np.zeros_like(mask)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if mask[y, x] and not seen[y, x]:
                seen[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if mask[y, x] and not seen[y, x]:
                seen[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; q.append((ny, nx))
    return seen


def components(alpha):
    """不透明部分のかたまり(8方向つながり)を面積つきで返す"""
    h, w = alpha.shape
    lab = np.zeros((h, w), np.int32)
    comps = []
    n = 0
    ys, xs = np.nonzero(alpha)
    for y0, x0 in zip(ys, xs):
        if lab[y0, x0]:
            continue
        n += 1
        lab[y0, x0] = n
        q = deque([(y0, x0)]); pts = []
        while q:
            y, x = q.popleft(); pts.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and alpha[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n; q.append((ny, nx))
        comps.append((n, len(pts)))
    return lab, comps


def clean_specks(cell, keep_ratio=0.02):
    """背景のゴミ(小さな点)を消す。一番大きなかたまりの2%未満のものを削除"""
    a = np.array(cell)
    lab, comps = components(a[..., 3] > 0)
    if not comps:
        return cell
    big = max(c[1] for c in comps)
    for n, area in comps:
        if area < big * keep_ratio:
            a[lab == n, 3] = 0; continue
        # 格子線や枠のような細長い線(面積が外接矩形の5%未満)も消す
        ys, xs = np.nonzero(lab == n)
        box = (ys.max() - ys.min() + 1) * (xs.max() - xs.min() + 1)
        if area < big and area < box * 0.05:
            a[lab == n, 3] = 0
    return Image.fromarray(a)


# ---------------------------------------------------------------- 位置と大きさを揃える
def bbox(cell):
    a = np.array(cell)[..., 3]
    ys, xs = np.nonzero(a > 0)
    if len(ys) == 0:
        return None
    return xs.min(), ys.min(), xs.max(), ys.max()


def hip_x(cell, base, height):
    """腰のあたり(足元から身長の40〜55%の高さ)の横方向の重心"""
    a = np.array(cell)[..., 3] > 0
    y0, y1 = int(base - height * 0.55), int(base - height * 0.40)
    band = a[max(0, y0):max(1, y1)]
    ys, xs = np.nonzero(band)
    if len(xs) == 0:
        ys, xs = np.nonzero(a)
    return float(xs.mean())


def split_grid(img, cols, rows, frames):
    W, H = img.size
    cw, ch = W / cols, H / rows
    cells = []
    for r in range(rows):
        for c in range(cols):
            if len(cells) >= frames:
                break
            m = 4  # コマの端にかかった格子線を切り落とす
            cells.append(img.crop((round(c * cw) + m, round(r * ch) + m, round((c + 1) * cw) - m, round((r + 1) * ch) - m)))
    return cells


def normalize(cells, anchor='hip', ref_frame=0, ref_height=REF_HEIGHT, scale=None, flip=False, keep_y=False, air=()):
    """全コマを同じ倍率で縮小し、足元の高さと腰の位置を揃えて 400x300 のコマにする。
    anchor='hip'  : 毎コマ腰の位置を揃える(歩き・待機など、その場の動き向け)
    anchor='first': 基準コマの腰に合わせた「同じずらし量」を全コマに使う
                    (踏み込みなど、生成画像の中での体の移動をそのまま残したい攻撃向け)
    keep_y=True   : 足元を揃えず、基準コマに合わせた同じ上下のずらし量を使う(ジャンプなど)
    air=(2,3)     : 指定したコマだけ keep_y と同じ扱いにする(空中にいるコマ)
    """
    if flip:
        cells = [c.transpose(Image.FLIP_LEFT_RIGHT) for c in cells]
    boxes = [bbox(c) for c in cells]
    if boxes[ref_frame] is None:
        raise SystemExit(f'{ref_frame}コマ目が空です')
    if scale is None:
        bx = boxes[ref_frame]
        scale = ref_height / (bx[3] - bx[1] + 1)
    scaled = []
    for c, bx in zip(cells, boxes):
        if bx is None:
            scaled.append(None); continue
        w, h = c.size
        # 縮小: 色はなめらかに、輪郭(透明度)はくっきりさせる
        sc = c.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
        arr = np.array(sc); arr[..., 3] = np.where(arr[..., 3] >= 128, 255, 0)
        scaled.append(Image.fromarray(arr))
    ref = scaled[ref_frame]; rb = bbox(ref)
    ref_dx = ANCHOR_X - hip_x(ref, rb[3], ref_height)
    ref_dy = BASELINE_Y - rb[3]
    out, info = [], []
    for i, sc in enumerate(scaled):
        if sc is None:
            out.append(Image.new('RGBA', (CELL_W, CELL_H))); info.append(None); continue
        sb = bbox(sc); base = sb[3]; hx = hip_x(sc, base, ref_height)
        dx = ANCHOR_X - hx if anchor == 'hip' else ref_dx
        dy = ref_dy if (keep_y or i in air) else BASELINE_Y - base
        cell = Image.new('RGBA', (CELL_W, CELL_H))
        paste_clip(cell, sc, dx, dy)
        out.append(cell)
        info.append({'hip': hx, 'base': base, 'bbox': sb, 'dx': dx, 'dy': dy})
    return out, scale, info


def paste_clip(dst, src, dx, dy):
    """はみ出す場合も切り取って貼る"""
    dx, dy = int(round(dx)), int(round(dy))
    sx0, sy0 = max(0, -dx), max(0, -dy)
    crop = src.crop((sx0, sy0, min(src.width, sx0 + dst.width - max(0, dx)), min(src.height, sy0 + dst.height - max(0, dy))))
    if crop.width > 0 and crop.height > 0:
        dst.alpha_composite(crop, (max(0, dx), max(0, dy)))


# ---------------------------------------------------------------- 出力
def save_outputs(frames, name, outdir, ms):
    os.makedirs(outdir, exist_ok=True)
    strip = Image.new('RGBA', (CELL_W * len(frames), CELL_H))
    for i, f in enumerate(frames):
        strip.alpha_composite(f, (i * CELL_W, 0))
    strip_path = os.path.join(outdir, name + '.png')
    strip.save(strip_path, optimize=True)
    # アニメ確認用GIF(灰色背景・足元の線つき)
    gif = []
    for f in frames:
        g = Image.new('RGBA', (CELL_W, CELL_H), (96, 96, 112, 255))
        d = ImageDraw.Draw(g); d.line([(0, BASELINE_Y), (CELL_W, BASELINE_Y)], fill=(255, 255, 0, 255))
        d.line([(ANCHOR_X, 0), (ANCHOR_X, CELL_H)], fill=(0, 255, 255, 160))
        g.alpha_composite(f)
        gif.append(g.convert('RGB').resize((CELL_W // 2, CELL_H // 2)))
    gif[0].save(os.path.join(outdir, name + '_preview.gif'), save_all=True, append_images=gif[1:], duration=ms, loop=0)
    # コマを並べた確認画像(1コマ目を薄く重ねて、ずれを見やすくする)
    chk = Image.new('RGBA', (CELL_W * len(frames), CELL_H + 20), (96, 96, 112, 255))
    ghost = frames[0].copy(); ga = np.array(ghost); ga[..., 3] = ga[..., 3] // 4; ghost = Image.fromarray(ga)
    d = ImageDraw.Draw(chk)
    for i, f in enumerate(frames):
        chk.alpha_composite(ghost, (i * CELL_W, 20)); chk.alpha_composite(f, (i * CELL_W, 20))
        d.text((i * CELL_W + 4, 4), f'f{i}', fill=(255, 255, 0, 255))
        d.line([(i * CELL_W, 20 + BASELINE_Y), ((i + 1) * CELL_W, 20 + BASELINE_Y)], fill=(255, 255, 0, 255))
        d.line([(i * CELL_W + ANCHOR_X, 20), (i * CELL_W + ANCHOR_X, 20 + CELL_H)], fill=(0, 255, 255, 255))
        d.line([(i * CELL_W, 20), (i * CELL_W, 20 + CELL_H)], fill=(0, 0, 0, 255))
    chk.convert('RGB').save(os.path.join(outdir, name + '_check.png'))
    return strip_path


# ---------------------------------------------------------------- index.html との出し入れ
def find_sprite(html, key):
    for pat in (f"'{key}':'data:image/png;base64,", f"{key}:'data:image/png;base64,"):
        i = html.find(pat)
        if i >= 0:
            start = i + len(pat)
            return start, html.index("'", start)
    return None


def sprite_keys(html):
    a = html.index('const SPR_ACT={'); b = html.index('};', a)
    keys = []
    for line in html[a:b].split('\n'):
        line = line.strip()
        if ":'data:image/png;base64," in line:
            keys.append(line.split(':')[0].strip("'"))
    return keys


def cmd_extract(args):
    html = open(args.html, encoding='utf-8').read()
    os.makedirs(args.out, exist_ok=True)
    for k in sprite_keys(html):
        if args.only and not k.startswith(args.only):
            continue
        s, e = find_sprite(html, k)
        open(os.path.join(args.out, k + '.png'), 'wb').write(base64.b64decode(html[s:e]))
        print('  ', k)
    print('->', args.out)


def cmd_build(args):
    cols, rows = map(int, args.grid.lower().split('x'))
    frames = args.frames or cols * rows
    src = Image.open(args.image)
    cells = split_grid(src, cols, rows, frames)
    cleaned = []
    for c in cells:
        c, bg, mode = remove_background(c, args.tol, args.bg_mode)
        cleaned.append(clean_specks(c))
    print(f'背景色 RGB{tuple(int(v) for v in bg)} / 消し方: {mode}')
    out, scale, info = normalize(cleaned, args.anchor, args.ref_frame, args.ref_height, args.scale, args.flip, args.keep_y,
                                  tuple(int(x) for x in args.air.split(',') if x.strip()))
    path = save_outputs(out, args.name, args.out, args.ms)
    meta = {'source': args.image, 'grid': args.grid, 'frames': frames, 'scale': scale, 'anchor': args.anchor,
            'frames_info': [None if f is None else {k: (float(v) if not isinstance(v, tuple) else [int(x) for x in v]) for k, v in f.items()} for f in info]}
    json.dump(meta, open(os.path.join(args.out, args.name + '.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'倍率 {scale:.3f} / {frames}コマ -> {path}')
    print(f'確認: {args.name}_preview.gif(動き) と {args.name}_check.png(ずれ)')


def cmd_inject(args):
    html = open(args.html, encoding='utf-8').read()
    loc = find_sprite(html, args.key)
    if not loc:
        raise SystemExit(f'index.html に {args.key} が見つかりません。候補: {", ".join(sprite_keys(html))}')
    im = Image.open(args.image)
    if im.height != CELL_H or im.width % CELL_W:
        raise SystemExit(f'画像サイズ {im.size} がゲームの形式(横{CELL_W}の倍数 x 縦{CELL_H})ではありません')
    b64 = base64.b64encode(open(args.image, 'rb').read()).decode()
    s, e = loc
    html = html[:s] + b64 + html[e:]
    open(args.html, 'w', encoding='utf-8').write(html)
    print(f'{args.key} を差し替えました({im.width // CELL_W}コマ)。コマ数が変わった場合は index.html の ANIM も直してください')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('extract', help='index.html から今のスプライト画像を取り出す')
    e.add_argument('--html', default=HTML); e.add_argument('--out', default='sprites/current'); e.add_argument('--only', default='')
    b = sub.add_parser('build', help='生成したシートを整えてゲーム形式にする')
    b.add_argument('image'); b.add_argument('--grid', required=True, help='列x行 (例: 4x2)')
    b.add_argument('--frames', type=int, help='使うコマ数(左上から順に)')
    b.add_argument('--name', required=True, help='出力名 (例: Dharuriser_walk)')
    b.add_argument('--out', default='sprites/build')
    b.add_argument('--anchor', choices=['hip', 'first'], default='hip',
                   help='hip: 毎コマ腰の位置を揃える(歩き・待機向け) / first: 1コマ目に揃えて体の移動を残す(攻撃向け)')
    b.add_argument('--ref-frame', type=int, default=0, help='直立しているコマの番号(大きさの基準)')
    b.add_argument('--ref-height', type=int, default=REF_HEIGHT, help='直立時の身長px(今の主人公は236)')
    b.add_argument('--scale', type=float, help='倍率を直接指定(他のシートと大きさを揃えたいとき)')
    b.add_argument('--flip', action='store_true', help='左向きに生成された場合に反転する')
    b.add_argument('--keep-y', action='store_true', help='全コマで足元を揃えない(ジャンプなど)')
    b.add_argument('--air', default='', help='空中にいるコマ番号(カンマ区切り 例: 2,3)。そのコマだけ足元を揃えない')
    b.add_argument('--tol', type=int, default=48, help='背景色とみなす色の近さ')
    b.add_argument('--bg-mode', choices=['auto', 'global', 'flood'], default='auto')
    b.add_argument('--ms', type=int, default=100, help='確認GIFの1コマの長さ(ミリ秒)')
    i = sub.add_parser('inject', help='整えた画像を index.html に組み込む')
    i.add_argument('image'); i.add_argument('--key', required=True); i.add_argument('--html', default=HTML)
    a = p.parse_args()
    {'extract': cmd_extract, 'build': cmd_build, 'inject': cmd_inject}[a.cmd](a)


if __name__ == '__main__':
    main()
