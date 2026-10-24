---
name: slide-mode-kit
description: スライド生成の「見た目の系統（テイスト）」を15種類のYAMLモードとして持ち、依頼内容の「形」（見出し・箇条書き・表・対比・まとめ文等）に自動マッピングして再現するデザインシステム。「スライド作って」「〇〇系統のテイストで資料作って」「モード一覧見せて」「新しいモード追加して」のトリガーで使う。writing-crew-starterやseamless-content-pipelineのスライド生成工程からも呼び出せる。
---

# SKILL: スライドモードキット (slide-mode-kit)

スライドの「見た目」を毎回ゼロから考えないための、再利用可能なデザインシステムです。15種類の**モード**（taste=見た目の系統）を`modes/*.yaml`に定義済みで、どんな内容（見出し・本文・箇条書き・比較・表・まとめ）が来ても、そのモードの配色・書体・部品を確実に・再現性高く適用できます。

このスキルは**用途を選びません**。営業資料でも、セミナー資料でも、SNS投稿画像でも、1枚ペライチでも、選んだモードのtasteが合えばそのまま使えます。「このモードは営業資料専用」のような制限は設けていません。

---

## 収録モード一覧（`index.yaml`が正本）

| mode_id | taste | render_target |
|---|---|---|
| `calm_natural_photobg` | 静か・ナチュラル・写真ブラー背景 | html_claude_design |
| `dynamic_tech_glow` | 先進的・ダイナミック（紺×オレンジ グロー訴求） | html_claude_design |
| `corporate_blue_standard` | オーソドックス・信頼感（単色ブルーの標準資料） | html_claude_design |
| `wafu_illustrated` | 和風イラストテーマ（桜×朱色の陽×墨絵シルエット） | notebooklm |
| `beauty_pastel_glow` | パステル×写真×グロー統計 | html_claude_design |
| `dark_gold_luxury` | 高級・華やか（ダーク×ゴールドのプレミアム演出） | notebooklm |
| `chalkboard_study_notes` | 黒板・チョーク学習ノート（高密度・暗記重視） | html_claude_design |
| `minimal_mono` | ミニマル白黒モノトーン | html_claude_design |
| `pop_vivid_sns` | ポップ・ビビッド（SNS向け元気なカラー） | html_claude_design |
| `nordic_paper_warm` | 北欧・ペーパー質感（温かみ） | html_claude_design |
| `tech_neon_pitch` | テック・ネオン（ITピッチ向け） | html_claude_design |
| `handwritten_notebook` | 手書き風ノート（講座資料向け） | html_claude_design |
| `glassmorphism_saas` | ガラスモーフィズム（透明感、SaaS系） | html_claude_design |
| `earth_sustainable` | アースカラー・サステナブル | html_claude_design |
| `editorial_magazine` | エディトリアル雑誌風（シャープなグリッド） | html_claude_design |

各モードの詳細（配色・部品・使いどころ）は `modes/<mode_id>.yaml` に、確認用の参照実装は `confirm/<mode_id>.html`（既存7種）または `confirm/<mode_id>.png`（新規8種、ChatGPT生成のサンプル画像）にあります。**迷ったら`confirm/`のファイルを開いて見た目を確認してから選んでください。**

---

## 使い方（Claude Codeでの動かし方）

### 0. 相手と準備状況を確かめる
- **利用者はパソコン操作に慣れていない前提で話す**。専門用語・ファイルの場所（パス）・コマンドを説明なしに出さない。返事は短くし、最後に「次にやること」を1つだけ示す。
- 作業フォルダの直下に `config/brand_guide.md` がない場合は、資料を作る前に「先にブランドガイドを作りますか（質問に答えるだけで5〜10分）／作らずにモードの配色だけで進めますか」と2択で聞く。作る場合は、配色（3〜5色。色コードではなく色の名前や雰囲気で聞く）・文字の雰囲気・ロゴの置き場所・避けたい表現を1つずつ質問し、`references/brand_guide.template.md` の形に整えて `config/brand_guide.md` に保存する。
- `config/brand/logo.png` がない場合はロゴなしで進め、完成時に「ロゴを入れたいときは、画像をこのフォルダに入れて教えてください」と一言添える。

### 1. モードを選ぶ
- **モードを提案する前に、必ず関連フォルダ（`config/`一式、および作業中のプロジェクト・作業フォルダ）にユーザーが残した過去のテンプレ・サンプルスライド・ブランドナレッジがないか確認する**。見つかった場合は、それを候補選定の材料にする（過去資産のテイストに近いモードを優先候補にする、または「過去資料と近いテイストで続けますか、それとも新しいテイストにしますか」を選択肢に含める）。見つからなければ通常通り`index.yaml`のtasteから提案する。
- ユーザーがモードを明示した場合（例：「dynamic_tech_glowで」「グロー系で」）はそれを使う。
- 明示がない場合は、上記で見つけた既存資産の有無と、依頼内容・トーン・業種の雰囲気から`index.yaml`の`tags`を手がかりに最も近いtasteを提案し、**必ず自分の推奨案を1つ明言**してから進める（「どれでもいい」で投げない）。
- 判断に迷ったら `confirm/<mode_id>.html`（または`.png`）を確認してユーザーに見た目を見せる。

### 2. モードYAML/JSONを読む
- `modes/<mode_id>.yaml`：taste・overrides（配色の使い方・書体・アイコン・文体・要素密度）・composition（内容の形→部品の対応表）・components（部品の詳細記述）を読む。**overrides・composition・notesはLLMであるあなたが解釈して当てはめるprose情報**なので、必ずYAML側を読む。
- `modes/<mode_id>.json`：paletteとcomponents.*.render_specだけを抜き出した機械可読版。コードで自動実装する場合（Pythonスクリプト等）はこちらを読み込む（YAMLを都度パースしてハードコードしない）。

### 3. ブランドを適用する（任意）
- 運用者が `config/brand_guide.md`（テンプレート: `references/brand_guide.template.md`）を用意していれば、ロゴ配置・配色の最終判断はそちらを優先する。
- モード側のpaletteはすでに実値を持っているため、ブランドガイドが無くてもそのモードの配色だけで完結して動く。

### 4. レンダリングする
- **`render_target: html_claude_design`のモード**：Claude Code自身でHTML/CSS/SVG（またはClaude Design）を組み立てる。色・px単位のレイアウトを正確に制御できるのが強み。既存7種は`confirm/<mode_id>.html`を土台に内容だけ差し替えるのが最も再現性が高い。新規8種は`confirm/<mode_id>.png`（ChatGPT生成のサンプル画像）を見た目の参照にしつつ、`modes/<mode_id>.yaml`のcomponents/paletteの記述通りにHTML/CSS/SVGを組み立てる。
- **`render_target: notebooklm`のモード**：写真・グリッター・手描き風の質感が要るため、コードで描くよりAI画像生成に任せた方が質が出る。**生成先を「ChatGPT」「NotebookLM」の両方とも選択肢としてユーザーに提示し（いずれもClaude in Chromeでのブラウザ操作で対応可能）、ユーザーが選んだ方を使う**。どちらか一方に固定しない。YAMLのoverridesをそのまま生成指示に含める。
- **PPTX（編集可能な形）で欲しい場合**：`references/assets/render_dynamic_tech_glow_pptx.py`を参照実装として使う（`dynamic_tech_glow`モード専用の実装例。他モードに転用する場合はcomponents/paletteに合わせて書き換える）。入力は`content.yaml`（スキーマは`references/assets/example_content.yaml`参照）。`dynamic_tech_glow`以外のモードでPPTXを頼まれたときは、書き換えに時間がかかることを先に伝え、「PDF（ブラウザの印刷から保存）で足りるか」を確認してから進める。Pythonや追加ライブラリの準備が要る場合は、利用者に1手順ずつ案内する。
- **作り終えたら**：完成したHTMLの場所を一言で伝え、「ブラウザで開きましょうか」と聞く。開くよう頼まれたら、そのままブラウザで開く。

### 5. ロゴについて
- **モードにロゴを新規生成させない**。「幾何学マーク＋社名」のような抽象ロゴをNotebookLM等の生成系レンダラーにかけると、スライドごとに違うマークを勝手に発明してしまい統一感が崩れる（実際に発生した既知の問題）。ロゴは実画像ファイル（`config/brand/logo.png`）をそのまま配置する。
- html_claude_designレンダリングなら生成物に直接`<img>`で埋め込めばよい。PPTX化スクリプトは`config/brand/logo.png`があれば自動で右上に合成する。

### 6. 新しいモードを追加したい場合
- `references/mode_authoring_guide.md` を読む（スキーマ・スキーマ運用ルール・追加フローを解説）。

---

## 動作モード

### モード一覧・選定のみ
トリガー: 「モード一覧見せて」「どのテイストがある？」
- `index.yaml`のtaste一覧を提示し、`confirm/`のファイル（HTML/PNG）を見せる。

### 資料作成（フル）
トリガー: 「スライド作って」「〇〇系統で資料作って」
- 上記「使い方」の1〜5を順に実行する。

### モード追加
トリガー: 「新しいモード追加して」「このサンプルをモード化して」
- `references/mode_authoring_guide.md`の追加フローに従う。

---

## 守るべき原則

- **taste（見た目の系統）だけを選定軸にする**。用途・業種でモードを縛らない。
- **componentsは内容非依存**で解釈する。特定の用途に引きずられて内容を歪めない。
- **色はpaletteの値をそのまま使う**。似た色を目分量で作らない。
- **ロゴは実画像を配置する。生成AIに新規発明させない。**
- 同じcomponentは毎回同じ描き方（render_specの数値通り）で再現する。デッキ内で太さ・形がブレると統一感が崩れる。
- 生成物に実在の顧客名・機密情報を書き込まない（confirm用のダミーコンテンツはあくまでサンプル）。
