# AGENTS.md — このリポジトリで作業するAIエージェント(Codex / Claude Code)向けのルール

## 必ず守ること

- 作業ブランチは `claude/loving-wright-wu1w7r`。**`main` には push しない**（`main` は GitHub Pages で公開中の本番）。
- オーナーはプログラミング初心者。報告は**日本語**で、専門用語は噛み砕いて書く。
- `index.html` は約74MBの1ファイル（画像・音声が base64 で埋め込まれている）。
  - **ファイル全体を読み込んだり表示したりしない。** 必要な部分だけ `grep -o` や Python で扱う。
  - 画像の差し替えは `tools/sprite_pipeline.py inject` を使う。手で base64 を貼らない。
- 作業を始める前に `docs/HANDOFF.md`（現状）と、依頼に関係する `docs/` の文書を読む。

## 主な文書

| 文書 | 内容 |
|---|---|
| `docs/HANDOFF.md` | プロジェクトの現状・これまでの変更・次にやること |
| `docs/sprite-spec.md` | キャラのモーションを画像生成で作り直すための仕様・プロンプト |
| `docs/codex-task.md` | **Codex への具体的な作業依頼（スプライトの作り直し）** |
| `tools/sprite_pipeline.py` | 生成画像を整えてゲームに組み込むツール（`--help` で使い方） |

## コミット

- 1つの作業ごとにコミットし、`git push origin claude/loving-wright-wu1w7r` する。
- コミットメッセージは日本語で「何を・なぜ」を書く。
