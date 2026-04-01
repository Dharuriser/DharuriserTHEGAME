# ダルライザー THE GAME 引き継ぎ資料 v4

**更新日:** 2026年4月2日
**最新版:** `dalraizer-game-v10.html`（約43MB、単一HTMLファイル）
**バックアップ:** `dalraizer-game-v10-backup.html`（v4改修前のスナップショット）

---

## 1. プロジェクト概要

ダブルドラゴン（SFC版）風のベルトスクロールアクションゲーム。ブラウザ上で動作する**単一HTMLファイル**に、全素材（スプライト画像・BGM・効果音・背景画像）をbase64エンコードして埋め込んでいる。

### ゲームの流れ

```
タイトル画面（Title.png + Title.mp3）
  ↓ PRESS START
ステージ1「白河の街」（Stage 1.png + Stage 1.mp3）→ ポンチョ軍団15人
  ↓ クリア
ステージ2「小峰城跡」（Stage 2.png + Stage 2.mp3）→ ポンチョ軍団20人
  ↓ クリア
ステージ3「ダイスの拠点」（Stage 3.png + Stage 3.mp3）→ ポンチョ軍団10人 → ボス:DICE
  ↓ クリア
エンディング（Clear.png + Clear.mp3 + CONGRATULATIONS!）
```

---

## 2. フォルダ構成

```
DharuriserTHEGAME/
├── dalraizer-game-v10.html          ← 最新版ゲーム本体（約43MB）
├── dalraizer-game-v10-backup.html   ← v4改修前バックアップ
├── dalraizer-game-v10-modified.html ← 旧修正版（参考用）
├── dalraizer-game-v9-audio.html     ← v9+音声版（39MB）
├── dalraizer-game-v9.html           ← v9（改善版、2MB）
├── dalraizer-game-v8b.html          ← v8b（旧版、参考用、2MB）
│
├── character motion/                ← スプライト原本（アクション別PNG）★v4で刷新
│   ├── Dharuriser_walk.png          (2800x306, 5フレーム)
│   ├── Dharuriser_punch.png         (2800x303, 5フレーム)
│   ├── Dharuriser_kick.png          (2800x305, 7フレーム)
│   ├── Dharuriser_kick02.png        (2800x302, 3フレーム)
│   ├── Dharuriser_damage.png        (2800x302, 5フレーム)
│   ├── Dharuriser_guard.png         (2800x305, 3フレーム)
│   ├── Dharuriser_smash.png         (2800x300, 5フレーム)
│   ├── enemyA_walk.png              (2800x301, 7フレーム)
│   ├── enemyA_punch.png             (2800x303, 7フレーム)
│   ├── enemyA_kick.png              (2800x302, 4フレーム)
│   ├── enemyA_damage.png            (2800x301, 8フレーム)
│   ├── enemyB_walk.png              (2800x300, 6フレーム)
│   ├── enemyB_punch.png             (2800x302, 4フレーム)
│   ├── enemyB_kick.png              (2800x301, 4フレーム)
│   ├── enemyB_damage.png            (2800x300, 7フレーム)
│   ├── enemyC_walk.png              (2800x301, 7フレーム)
│   ├── enemyC_punch.png             (2800x300, 4フレーム)
│   ├── enemyC_kick.png              (2800x300, 6フレーム)
│   ├── enemyC_damage.png            (2800x301, 7フレーム)
│   ├── DICE_walk.png                (2800x303, 6フレーム)
│   ├── DICE_punch.png               (2800x300, 7フレーム)
│   ├── DICE_kick.png                (2800x300, 7フレーム)
│   ├── DICE_damage.png              (2800x300, 5フレーム)
│   └── DICE_smash.png               (2800x300, 7フレーム)
│
├── Back ground/                     ← 背景画像原本（PNG）
│   ├── Title.png    (1MB)  タイトル画面
│   ├── Stage 1.png  (7.7MB) 白河の街（夜景）
│   ├── Stage 2.png  (8.5MB) 小峰城跡（桜）
│   ├── Stage 3.png  (7.6MB) ダイスの拠点（森・鳥居）
│   ├── Clear.png    (8.3MB) エンディング（夕焼け・飛行船）
│   ├── front_Stage 1.png  ★v4追加（前景レイヤー、未実装）
│   ├── front_Stage 2.png  ★v4追加（前景レイヤー、未実装）
│   ├── front_Stage 3.png  ★v4追加（前景レイヤー、未実装）
│   └── reference_ground.jpg  歩行エリア参考画像
│
├── music/                           ← BGM原本（MP3、SUNOで生成）
├── sound effect/                    ← 効果音原本（WAV）
├── For reference/                   ← 参考素材
│   ├── character_motion_grid_data.jpg      グリッド定義
│   └── character_motion_original_data01.jpg  グリッドにダルライザー配置例
└── dalraizer-game-handover-v4.md    ← この引き継ぎ書
```

---

## 3. v4改修内容（2026年4月1日〜2日）

### 3-1. スプライトシステム完全刷新 ★最大の変更

旧システム（キャラごとに1枚の結合シート）から、**アクション別ファイル方式**に移行。

#### 旧システム
```javascript
const SPR = {p: 'base64...', n: 'base64...', ...};  // キャラごとに1画像
const SP = {p: {cw:218, ch:301, sc:0.45}, ...};       // キャラごとにセルサイズ・倍率
function ds(type, x, y, frame, faceDir, alpha) {...}   // フレーム番号で描画
```

#### 新システム
```javascript
const SPR_ACT = {'Dharuriser_walk': 'base64...', 'Dharuriser_punch': 'base64...', ...};
const CW=400, CH=306, SC=0.45;  // 全キャラ共通セルサイズ
const ANIM = {p: {walk:['walk',[0,1,2,3,4,3,2,1]], punch:['punch',[0,1,2,3,4]], ...}, ...};
function ds(charType, state, x, y, frameIdx, faceDir, alpha) {...}
```

- `ds()`がキャラタイプ+状態名から自動で正しいスプライトシートとフレームを選択
- フレーム番号はアクション別ストリップ内の0始まりインデックス
- `ANIM`テーブルで各状態→[アクションファイル名, フレーム配列]をマッピング

#### スプライトストリップの仕様
- 全ファイル: 2800px幅 × 約300px高の1行ストリップ
- **セルストライド: 400px**（2800÷7=400。キャラは各400pxスロットの中央に配置）
- スケール: 0.45（全キャラ共通）
- 描画サイズ: DW=180px, DH=138px

### 3-2. 歩行エリア制限

背景画像（4128×1024）の歩行可能エリアをキャンバス座標に変換して制限。

```javascript
const WALK_Y_TOP=325, WALK_Y_BOT=352;
// プレイヤー: P.y = max(WALK_Y_TOP-P.h, min(WALK_Y_BOT-P.h, P.y))
// 敵も同様
```

- キャラの足元（y+h）がWALK_Y_TOP〜WALK_Y_BOTの範囲内に制限される
- 参考画像: `Back ground/reference_ground.jpg`の緑帯が歩行エリア

### 3-3. 敵AI改善

- **攻撃クールダウン修正**: 500-2000フレーム（バグ）→ 30-80フレーム
- **回り込み行動(circle)追加**: 攻撃待ちの敵がプレイヤーの周囲を回る
- **同時攻撃上限**: 2体→3体に増加
- **退却行動改善**: retreat後すぐにchaseに戻る

### 3-4. 敵の倒れ・死亡演出

```
hurt（15tick被弾）→ down（30tick倒れアニメ）
  ├→ HP残りあり: getup（30tick起き上がり）→ idle復帰
  └→ HP0: dead（120tick = 2秒間点滅）→ 消滅
```

- 敵は倒れてから起き上がって再攻撃してくる
- 死亡時は2秒間点滅してからフェードアウト

### 3-5. ゲームバランス調整

| 項目 | 旧値 | 新値 |
|------|------|------|
| プレイヤー移動速度 | 2.5 | 4.0 |
| 敵A(n) HP | 15 | 40 |
| 敵B(l) HP | 30 | 60 |
| 敵C(s) HP | 10 | 25 |
| 敵D(t) HP | 18 | 45 |
| ボスDICE HP | 100 | 200 |
| 敵攻撃力 | 各種 | 微増 |

### 3-6. その他の修正

- **ボタン入力**: `e.code`ベース検出を追加（CapsLock/日本語入力対応）
- **ガード音**: 毎フレーム再生→ガード開始時のみ1回に修正
- **効果音**: パンチ/キック/必殺技の音が毎フレーム再生→攻撃開始時のみに修正
- **ボスDICEスポーン**: 固定位置→プレイヤー右前方（`sx+W+50`）に修正
- **ステージ3敵数**: 9人(バグ)→10人に修正（totE=11: 10人+ボス1）
- **残り人数表示**: SCORE/STAGEの下に配置し重なりを解消
- **影の位置**: プレイヤー-12px、敵-10px上方に調整
- **キャラ比率統一**: 全キャラsc=0.45に統一（元の300×360グリッド設計を尊重）

---

## 4. 技術仕様（v4版）

### キャンバス
- サイズ: **640×360**（16:9）
- レンダリング: `image-rendering: pixelated`

### スプライトシステム

```javascript
// セル定数（全キャラ共通）
const CW=400, CH=306, SC=0.45;
const DW=Math.floor(CW*SC);  // 180
const DH=Math.floor(CH*SC);  // 138

// キャラタイプ→ファイルプレフィックス
const CPFX = {p:'Dharuriser', n:'enemyA', l:'enemyB', t:'enemyC', b:'DICE'};

// ANIM[charType][state] = ['actionFile', [frame0, frame1, ...]]
// frame番号はストリップ内の0始まりスロット番号
```

### アニメーション定義（ANIM）

#### ダルライザー (p)
| 状態 | アクションファイル | フレーム | 速度(tick/コマ) |
|------|-------------------|---------|----------------|
| idle | walk | [0] | - |
| walk | walk | [0,1,2,3,4,3,2,1] | 4 |
| punch | punch | [0,1,2,3,4] | 3 |
| kick | kick | [0,1,2,3,4,5,6] | ~3 |
| kick2/jump_kick | kick02 | [0,1,2] | ~5 |
| special | smash | [0,1,2,3,4] | 8 |
| guard | guard | [0,1] | 6 |
| guard_hit | guard | [2] | - |
| hurt | damage | [0,1] | 8 |
| down | damage | [1,2] | 12 |
| dead | damage | [2] | - |
| getup | damage | [3,4] | 8 |

#### 敵A (n) / 敵B (l) / 敵C (t) / ボスDICE (b)
- 全員共通: walk, punch(=attack), kick, hurt, down, dead, getup
- DICEのみ追加: smash, victory
- 敵のattack状態はpunchアニメーションを使用

### 敵キャラタイプ（ETテーブル）

| コード | タイプ | HP | 速度 | 攻撃力 | スプライト |
|--------|--------|-----|------|--------|-----------|
| n | 通常 | 40 | 1.8 | 8 | n (enemyA) |
| l | 大型 | 60 | 1.2 | 14 | l (enemyB) |
| s | 小柄 | 25 | 2.5 | 5 | t (enemyC) |
| t | 中型 | 45 | 2.0 | 10 | t (enemyC) |
| b | ボス | 200 | 1.3 | 18 | b (DICE) |

### 操作方法

| PC | スマホ | アクション |
|----|--------|-----------|
| ←→↑↓ / WASD | D-pad | 移動 |
| Z / J | パンチ | パンチ |
| X / K | キック | キック |
| V / Shift | ガード | ガード |
| C / L | 必殺 | 必殺技（ゲージMAX時） |
| Enter / Space | タップ | スタート |

※ `e.code`ベースの検出も追加済み（CapsLock/IME状態に依存しない）

---

## 5. コード構成（v4版・行番号の目安）

| 行 | 内容 |
|----|------|
| 1-14 | HTML/CSS（タッチコントロールUI含む） |
| 15 | `BG_IMAGES` 定数（背景base64、巨大） |
| 16-42 | `SPR_ACT` スプライトデータ（アクション別base64、24ファイル分） |
| 43-44 | `CW/CH/SC/DW/DH` セル定数、`CPFX` プレフィックスマップ |
| 45-47 | `im` イメージオブジェクト生成（SPR_ACTから全画像をロード） |
| 48-116 | `ANIM` アニメーション定義（p/n/l/t/b × 各状態） |
| 118-134 | `ds()` スプライト描画関数、`gd()` サイズ取得 |
| 137-149 | 入力処理（キーボード・タッチ、e.code対応） |
| 151-190 | 音声システム（initAudio, playBGM, stopBGM, playSFX） |
| 191-200 | ゲーム状態変数・定数 |
| 201-300 | spawn, setup, ユーティリティ関数 |
| 305-320 | pFr/eFr アニメーションフレーム計算（新方式） |
| 322-360 | updateEnemyAI（回り込み行動付き）、update() メインループ |
| 432-445 | 敵処理（hurt→down→dead/getup遷移） |
| 452-470 | drawBG() 背景描画（パララックスPNG） |
| 475-520 | UI描画、draw() メイン描画関数 |
| 525-534 | ゲームループ開始、音声初期化 |

---

## 6. 未実装・要対応事項

### 優先度: 高

1. **前景レイヤー（front）の実装**
   - `Back ground/front_Stage 1〜3.png`（4128×1024、透過PNG）が作成済み
   - 背景→キャラ→前景の3レイヤー描画が必要
   - 前景はキャラと同じ1xスクロール速度が適切
   - base64変換してHTMLに埋め込み、drawFront()関数を新規作成

2. **スプライトフレーム番号の確認**
   - ANIM定義のフレーム番号は目視推定。ユーザーが正確な対応表を作成予定
   - 特にdamage系（hurt/down/dead/getup）のフレーム分割が要確認

3. **被弾時のモーション問題**
   - ダルライザーが攻撃を受けた時にパンチモーションが出る報告あり
   - hurt状態のフレームが正しいか要確認

### 優先度: 中

4. **アニメーション速度の微調整**
   - レトロ基準: 歩行8-12fps、攻撃15-20fps
   - 現在の設定が「早すぎる」とのフィードバックあり

5. **ボタン入力の確認**
   - e.code対応を追加済みだが、まだ反応しないとの報告
   - 具体的にどのキーが効かないか要確認

6. **敵AIのさらなる改善**
   - 「近づくだけで押し引きがない」とのフィードバック
   - retreat距離・頻度の調整が必要かもしれない

### 優先度: 低

7. **スマホタッチコントロールの確認**
8. **パフォーマンス最適化**（43MBファイルの読み込み）
9. **エンディング演出の改善**

---

## 7. スプライト差し替え手順（v4版）

1. 新しいPNG画像を`character motion/`に配置（2800px幅、1行ストリップ、400pxストライド）
2. base64に変換: `base64 -i ファイル.png | tr -d '\n'`
3. HTML内の`SPR_ACT`オブジェクトの該当キーを差し替え
4. 必要に応じて`ANIM`テーブルのフレーム番号を更新
5. `CW`（現在400）はストライドに合わせて調整

---

## 8. 過去バージョンの変遷

| バージョン | サイズ | 変更内容 |
|-----------|--------|---------|
| v8b | 2MB | 旧スプライト版。プロシージャル背景。基本ゲームプレイ完成。 |
| v9 | 2MB | 敵AI改善（FSM）、コンボシステム、ステージメッセージ追加 |
| v9-audio | 39MB | v9 + BGM 5曲/SFX 6種をbase64埋め込み |
| v10 | 44MB | 新スプライト5種（TAKEAKIさん作成）、背景PNG 5枚を埋め込み |
| v10(v3修正)| 44MB | 背景をPNG画像パララックスに修正、アニメ速度調整 |
| **v10(v4修正)** | **43MB** | **スプライトシステム全面刷新（アクション別24ファイル）、敵AI改善、死亡演出追加、歩行エリア制限、バランス調整** |

---

## 9. 著作権

©ダルライザープランニング
