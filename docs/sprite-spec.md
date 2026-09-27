# ダルライザー モーション作り直し 仕様書

画像生成AI（GPT-Image 2.5 など）で主人公のモーションを作り直し、ゲームに組み込むための手順と仕様です。
Codex・Claude Code のどちらが作業しても同じ結果になるように書いています。

---

## 1. 方針

- **キャラクターデザインは今のまま。** 赤い全身スーツ、胸の金のエンブレム、白と赤のヘルメット、黒いバイザー、黒いひざ当てとベルト。
- **等身も今のまま**（大人のヒーロー体型、約7.5頭身）。デフォルメ（ちびキャラ）にはしない。
- **向きは全モーション「斜め前（3/4ビュー）・右向き」で統一する。**
  今の歩きだけ真横向きで、立ち姿や攻撃（斜め前向き）と切り替わるときに体の向きが急に変わる。これを直すのが一番の目的。
- **コマ数を増やして滑らかにする。** 特に歩き・ダウン〜起き上がり。
- 参考画像：`sprites/reference/Dharuriser_design_sheet.png`（立ち・パンチ・キック・ガード・今の歩き）、`sprites/reference/Dharuriser_idle_x3.png`（立ち姿の拡大）

## 2. 作る順番（優先度順）

| 順 | 名前 | ゲーム内の画像名 | 並べ方 | コマの内容（左上から順に） |
|---|---|---|---|---|
| 1 | 立ち＋歩き | `Dharuriser_walk` | 3列×3行（9コマ） | 0 立ち（構え）/ 1 右足を前に踏み出して接地 / 2 体が沈む / 3 左足が右足を追い越す / 4 体が浮く / 5 左足を前に踏み出して接地 / 6 体が沈む / 7 右足が左足を追い越す / 8 体が浮く |
| 2 | 被弾〜ダウン〜起き上がり | `Dharuriser_damage` | 3列×3行（9コマ） | 0 立ち（大きさの基準）/ 1 殴られてのけぞる / 2 足が浮いて後ろへ吹き飛ぶ（空中）/ 3 背中から落ちる（空中）/ 4 仰向けに倒れている / 5 片ひじをついて上半身を起こす / 6 片ひざ立ち / 7 立ち上がる途中 / 8 立ち（構え直し） |
| 3 | パンチ | `Dharuriser_punch` | 3列×2行（5〜6コマ） | 0 構え / 1 振りかぶり / 2 腕を伸ばす途中 / 3 腕が伸びきる（命中の瞬間）/ 4 戻し / 5 構えに戻る直前 |
| 4 | 飛び蹴り（ライダーキック風） | `Dharuriser_kick` | 今は作らなくてよい | 今の画像のコマをプログラムで回転・移動させて動かしている（`riderKick()`）。作り直す場合は、**コマ番号の役割（1 しゃがみ・宙返り用 / 2 跳び上がり / 3 急降下の蹴り / 5 着地 / 6 立ち直り）を変えない**こと。専用に「宙返り中の丸まった姿勢」のコマを増やすとさらに良くなる |
| 5 | 立ちキック | `Dharuriser_kick02` | 3列×2行（5コマ） | 構え / 足を引く / 蹴り足を伸ばす / 戻す / 構え |
| 6 | ガード | `Dharuriser_guard` | 3列×1行（3コマ） | 構え / 両腕で顔を守る / 攻撃を受け止めて少し押される |
| 7 | 必殺技 | `Dharuriser_smash` | 3列×2行（6コマ） | 構え / 力を溜める / エネルギーを拳に集める / 突き出す / 光が伸びる / 構えに戻る |

**どのシートも「0コマ目＝普通に立っている構え」にしてください。** ツールはこのコマの身長を基準に大きさを揃えます。

## 3. 生成するときの約束（プロンプトに必ず入れる）

1. 背景は**真緑（#00FF00）の単色**。影・地面・文字・コマ番号・枠線は入れない。
   （「透過背景」と指定しても白や灰色で出てくることが多いので、最初から緑にしてツールで消します）
2. **全コマ同じ大きさ・同じ縮尺**で、キャラがコマからはみ出さない。
3. **足元は全コマ同じ高さの地面の線**に置く（空中のコマは、その線より上に描く）。
4. 右向き・斜め前（3/4ビュー）。参考画像の立ち姿と同じカメラの角度。
5. ドット絵。1ピクセルの暗い輪郭線。参考画像と同じ色数・同じ配色。

### プロンプトの例（歩き）

英語の方がコマ割りの指示が通りやすいので、英語の例を載せます。

```
Use the attached images as the exact character design reference (Dharuriser, a Japanese tokusatsu hero):
red full-body suit, gold emblem on the chest, white-and-red helmet with a black visor, black knee pads and belt.
Keep his realistic adult hero proportions (about 7.5 heads tall). NOT chibi, NOT super-deformed.

Create a pixel-art sprite sheet, 3 columns x 3 rows, 9 cells of identical size.
Every cell: the same character at the same scale, 3/4 front view facing RIGHT
(same camera angle as the attached idle pose), feet on the same ground line near the bottom of the cell.
Crisp 1-pixel dark outline, limited palette matching the reference.
Background: solid flat pure green #00FF00 in every cell. No shadow, no floor, no text, no numbers, no grid lines.

Cells in reading order:
1. idle fighting stance (same as the reference)
2. walking: right foot steps forward and touches the ground (contact)
3. walking: weight comes down on the right foot, body slightly lower (down)
4. walking: left foot passes the right leg (passing)
5. walking: body rises onto the right toes (up)
6. walking: left foot steps forward and touches the ground (contact)
7. walking: weight comes down on the left foot, body slightly lower (down)
8. walking: right foot passes the left leg (passing)
9. walking: body rises onto the left toes (up)
Arms swing opposite to the legs. Keep the fists loosely clenched.
```

他のモーションは、最初の2段落をそのまま使い、「Cells in reading order」以降を上の表の内容に差し替えます。

## 4. ゲームに組み込む手順

リポジトリのルートで実行します。必要なもの：Python 3、Pillow、numpy（`pip install pillow numpy`）。

```bash
# 1) 生成した画像を sprites/generated/ に置く(例: walk_v1.png)

# 2) 整える: 背景を消し、全コマの大きさ・足元・腰の位置を揃えて 1コマ400x300 の横並びにする
python3 tools/sprite_pipeline.py build sprites/generated/walk_v1.png --grid 3x3 --name Dharuriser_walk --anchor hip

# 3) 確認: sprites/build/ の
#    Dharuriser_walk_preview.gif … 動きの確認
#    Dharuriser_walk_check.png  … 1コマ目を薄く重ねた並び。黄線=足元、水色線=腰の位置
#    デザインが崩れたコマ(ヘルメットの形・色が違う等)があれば生成し直す

# 4) ゲームに組み込む
python3 tools/sprite_pipeline.py inject sprites/build/Dharuriser_walk.png --key Dharuriser_walk
```

モーションごとのオプション：

| モーション | build のオプション |
|---|---|
| 立ち＋歩き | `--grid 3x3 --anchor hip` |
| 被弾〜起き上がり | `--grid 3x3 --anchor first --air 2,3` |
| パンチ | `--grid 3x2 --frames 6 --anchor first` |
| 飛び蹴り | `--grid 4x2 --frames 7 --anchor first --air 2,3,4`（作り直す場合のみ）|
| 立ちキック | `--grid 3x2 --frames 5 --anchor first` |
| ガード | `--grid 3x1 --anchor first` |
| 必殺技 | `--grid 3x2 --anchor first` |

- `--anchor hip`：毎コマ腰の位置を揃える（その場の動き向け）
- `--anchor first`：0コマ目に合わせたずらし量を全コマに使う。生成画像の中での踏み込み・のけぞりの移動が残る
- `--air`：空中にいるコマ。足元を地面に揃えない
- 左向きで生成されたら `--flip`

## 5. 組み込んだあとにコード側で直す所（index.html）

画像のコマ数や並びが変わるので、`const ANIM={ p:{...} }` の該当行を直します。

| 画像 | 直す所 |
|---|---|
| walk | `idle:['walk',[0],1]`、`walk:['walk',[1,2,3,4,5,6,7,8],6]`。`FOFS.p.walk` は削除（ツールで揃うので不要）。`WALK_STRIDE.p` は「1歩の歩幅(px)×0.45÷4」に合わせ直す |
| damage | `hurt:['damage',[1,1,0],4]`（描画時ののけぞり `dsRot` は不要になるので外す）、`down:['damage',[1,2,2,3,3,4,4,4,4,4],5]`、`dead:['damage',[4],1]`、`getup:['damage',[5,6,7,8],6]`、`FLOOR_F.p=4` |
| punch | 振りかぶり6・伸ばし6・戻し6フレームを守る。例：`punch:['punch',[1,1,2,3,4,5],3]`。当たり判定は `hit=(vf>=2&&vf<=3)` |
| kick | 飛び蹴りは `riderKick()` がコマ・高さ・回転を決める。各コマの体の中心を `RKC` に登録し直す（`tools/sprite_pipeline.py` の `_check.png` で確認） |

タイミングの数字は、アーケード版ダブルドラゴンのプレイ映像を1コマずつ測った値です（`docs/HANDOFF.md` 参照）。

## 6. 注意

- 生成AIはコマごとにデザインが少しずつ変わりやすい（ヘルメットの形、胸のエンブレム、色）。`_check.png` で全コマを見比べ、違うコマがあれば作り直す。
- 同じシートの中で大きさが揃っていないと、ツールで揃えても不自然になる。0コマ目の身長を基準にするので、0コマ目は必ず普通に立った構えにする。
- 敵キャラも同じ手順で作り直せる（画像名は `enemyA_walk` など。`extract` で今の画像を取り出して参考にする）。
