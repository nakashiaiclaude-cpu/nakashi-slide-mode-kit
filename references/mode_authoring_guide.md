# モードの仕組み・追加のしかた

`slide-mode-kit` に同梱の15モードをそのまま使うだけなら、このファイルを読む必要はありません（`SKILL.md`と`index.yaml`だけで足ります）。**自分だけの新しいモードを追加したい**ときに読んでください。

スライド生成における「見た目の系統（テイスト）」を再利用可能なYAML指示として蓄積する仕組みです。

各モードは特定の用途（営業資料・教育資料等）に縛られない、**純粋な見た目のデザインシステム**として定義します。与えられた内容（見出し・本文・リスト・比較・表・数値・結論等、どんな構成でも）に対して、そのモードの配色・書体・部品を確実に・再現性高く適用できることを目的とします。「このモードは営業資料専用」のような制限は設けません — テイストが合えば、どんな用途のスライドにも使ってよい設計です。

## 構成

```
slide-mode-kit/
├── index.yaml   # 登録済みモードの一覧（タグ検索用の軽量レジストリ）
├── modes/
│   ├── <mode_id>.yaml   # モード定義本体（人間・LLMが読む正本）
│   └── <mode_id>.json   # コード自動実装用の機械可読版（build_mode_json.pyで自動生成）
└── confirm/
    └── <mode_id>.html   # モード適用の確認用スライド（1280x720、参照実装を兼ねる）
```

自社の主力ブランドと配色系統が一致するモードは `base: config/brand_guide.yaml`（運用者が用意するブランド設定。`references/brand_guide.template.md`参照）を持たせ、差分をoverridesに書く運用も可能です。ただし各モードのpaletteには実際の色値を必ずインラインで持たせます（baseは「由来の記録」であり、実行時の値解決を`base`参照だけに依存させません）。系統が独立したモード（クライアント/テーマ別配色）は `base: null` とします。

**YAML/JSONの使い分け**：`base:` フィールドや各モードYAMLはあくまで人間（あなた・メイン会話）がモードを設計・改訂するための正本です。実際にPythonスクリプト等のコードが自動実装（レンダリング）時に色の値を読み込む場合は、YAMLを都度パースするのではなく、そこから自動生成されたJSON（`modes/build_mode_json.py`で再生成、値のみでprose無し）を読み込んでください。ハードコードで値を都度コピーしないこと。

各モードYAML自体も、`modes/build_mode_json.py` によって同名の `modes/<mode_id>.json`（palette＋components.*.render_specのみ抽出）が自動生成されます。overrides・composition・notes等はLLMが解釈して都度当てはめる前提のprose情報のためJSON化の対象外とし、YAML側に残します。コードが特定モードの色を自動実装する場合は、この`<mode_id>.json`を読み込みます。

YAML編集後は `python modes/build_mode_json.py` を実行してJSONを同期させてください（対応するファイルだけ更新したい場合は `python modes/build_mode_json.py <file.yaml>`）。Claude Codeで運用する場合、PostToolUseフック（`.claude/settings.json`）でYAML編集時に自動実行させる設定も可能です。

## モードYAMLのスキーマ

```yaml
mode_id: calm_natural_photobg   # 英数slug、ファイル名と一致
label: "静か・ナチュラル・写真ブラー背景"
created: 2026-07-09
source: "サンプルの由来メモ（任意）"

taste: 静か・ナチュラル・落ち着き    # このモードの見た目の系統をひとことで表す。選定の唯一の軸

base: config/brand_guide.yaml   # またはnull

render_target: html_claude_design   # html_claude_design / notebooklm のいずれか（下記「レンダラーの使い分け」参照）

overrides:                  # 記述順も統一する（存在しない項目は省略可）
  color_emphasis: ""         # 配色の使い方・機能色かムード色か
  photo_treatment: ""        # 写真を使うモードのみ
  typography: ""             # 書体の使い分け
  icon_style: ""
  copy_style: ""             # 文体の傾向（用途は問わず、言葉選びのトーンのみ）
  element_density: ""        # 要素数の傾向（このモードが心地よく感じられる密度）

composition:                # 内容の「形」ごとに、どの部品を当てるかの汎用マッピング
                             # 特定の用途（表紙/営業資料/教育資料等）ではなく、
                             # 「見出し1つ」「箇条書き」「表・数値」「2項目の対比」
                             # 「まとめの一文」等、内容の形状で書く
  heading: "component名"
  body_text: "component名"
  list: "component名"
  comparison_2: "component名"
  table_or_data: "component名"
  summary_statement: "component名"
  background: "component名"

palette:                    # 実際の色値（hex）。プローズではなく必ず値で書く
  primary: "#123456"

components:                 # 再利用部品。必ず description を持つdict形式
  part_name:
    description: "何をどこに置くか（内容非依存の汎用的な記述）"
    render_spec:             # 再現に必要な数値（px・opacity・構造上の注意）。任意
      key: "値"

notes: ""                   # 使いどころの制約・参照実装（confirm/のファイル名）等
```

### スキーマ運用ルール

- **用途・業種・対象読者でモードを縛らない**。`taste`（見た目の系統）だけを選定軸にし、どんな内容にも同じ品質でデザインを適用できることを目指す
- **componentsは内容非依存**にする。「悩み提起で使うリスト」のような用途限定の説明ではなく、「箇条書き全般に使うリスト部品」のように書く
- **composition**は、内容の「形」（見出し／箇条書き／表／対比／まとめ文等）とcomponentsの対応表として書く。これにより、営業資料でも教育資料でもSNS投稿でも、内容の形が同じならこのモードで同じ品質の見た目を再現できる
- **components は文字列不可**、必ず `description:` を持つdictにする（形式が揃っていないと自動選定時にパースが安定しないため）
- **色はpaletteに集約**し、overrides/components からは色名（例: accent_pink）で参照する
- 再現検証で得た構造上のノウハウ（例：「2色の8の字は1本のパスをdasharrayで塗り分けず、左右2本の別パスで描く」）は該当componentの `render_spec` に残す
- 確認用HTMLを `confirm/<mode_id>.html` に置き、notesから参照する。これがモードの参照実装になる
- **ロゴ・ブランドマークをcomponentsに含めない**。「幾何学マーク＋社名」のような抽象的なロゴ部品は、NotebookLM等の生成系レンダラーにかけるとスライドごとに違うマークを勝手に発明し、デッキ内の統一感を崩す。実在のロゴが必要な場合は本物のロゴ資産（画像ファイル）をそのまま配置する前提とし、モード側では新規生成させない
- **同じcomponentは毎回同じ描き方で再現されるべき**。1つのデッキ内で同じ部品（波飾り・リング装飾等）の太さ・形が回によって変わるのも統一感崩壊の典型パターン。render_specの数値をそのまま守らせ、都度の再解釈を許さない

## レンダラーの使い分け（render_target）

同じYAMLでも、どのツールで最終的に作るかで出てくる質が大きく変わります。選択肢は2つに絞ります：

- **`html_claude_design`**：Claude Code自身が扱うツール（HTML/CSS/SVG、およびClaude Design）で作る。色・px単位のレイアウト・情報構造を正確に制御できるのが強みで、フラットな図形・グラデーション・グロー表現や、情報の正確性が優先される資料（表・図・チェックリスト等）に向く
- **`notebooklm`**：NotebookLM（実際の画像生成モデルを使うパイプライン）で作る。写真・繊細なテクスチャ・手描き風のムラなど「それらしい絵」の質感が要るモードに向く。YAMLの記述が多少ざっくりでも美的に補完してくれる分、色やレイアウトの再現精度はモデル任せになる

判断基準：**そのモードの価値の大半が「情報構造の正確さ」なら html_claude_design、「質感・写真・雰囲気」ならnotebooklm**。

| render_target | 選ぶ理由 |
|---|---|
| `html_claude_design` | フラットな図形・グラデーション・グローが中心、または表・図・チェックリスト等の情報精度が優先される |
| `notebooklm` | 実写人物写真、細かい粒状テクスチャ（グリッター等）、繊細な手描きイラストが核で、コードで描くと質感が頭打ちになる |

**運用ルール**：
- `confirm/<mode_id>.html` によるデザイン確認は、render_targetによらず基本的にhtmlで素早く行ってよい（構造・配色・レイアウトの検証が目的のため）
- 実際の納品物を作る段になったら、render_targetが`notebooklm`のモードはNotebookLM側で質感パートを作る
- render_targetの判断がついた根拠（何を検証してhtmlでは弱いと分かったか）は、該当モードYAMLの`notes`に残す

## 新しいモードを追加する運用フロー

1. サンプルスライド（画像/PDF/説明文）を用意する
2. Claude Codeにtasteとoverrides各項目をサンプルから抽出させる。名前・日付・社名などの固有情報は反映せず、汎用的なデザイン要素のみ読み取る。サンプルがたまたまある用途（営業資料等）だったとしても、そこに引きずられずcompositionは内容の形状ベースで一般化する
3. `modes/<mode_id>.yaml` を新規作成し、`index.yaml` に1行追加する
4. `confirm/<mode_id>.html` を作成し、スクリーンショットで確認する（内容は汎用のダミーテキスト・ダミー見出しに限定し、実在の顧客名・実データは使わない）
5. `python modes/build_mode_json.py` でJSONを同期する

## 選定ロジック（今後の拡張余地）

- **手動**：taste を明示して選ぶ（例：「信頼感のある単色ブルーで」）
- **自動**：依頼文のキーワード・文脈からtasteを推測し、最も近いモードYAMLを選定する

このロジック自体は、モードYAMLが一定数蓄積されてから設計するとよいでしょう。
