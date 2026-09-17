# slide-mode-kit セットアップガイド

Claude Codeで「見た目のテイストが安定したスライド」を作るためのデザインシステムです。15種類のモード（taste）から選び、内容（見出し・箇条書き・表・対比・まとめ文）を渡すだけで、そのモードの配色・書体・部品を再現性高く適用できます。

## 1. ファイルの配置

- このフォルダごと `.claude/skills/slide-mode-kit/` としてコピーする（Claude Codeが自動でSKILL.mdを認識する）
- 依頼文に応じて自動選定させたい場合は、`writing-crew-starter`・`seamless-content-pipeline`等の記事制作スキルからこのスキルを呼び出す形でも使える（呼び出し方は各スキルのスライド生成工程を参照）

## 2. まず動かしてみる

1. `confirm/` フォルダの15件（HTML7件・PNG8件）を開き、どのテイストが自分の用途に合うか確認する
2. Claude Codeで「`dynamic_tech_glow`のテイストでスライド作って」のように、モード名を指定して依頼してみる
3. `modes/<mode_id>.yaml` を開くと、そのモードの配色・部品定義が読める

## 3. 自分のブランドを反映する（任意）

モード側の配色（palette）だけでも完結して動きますが、自社ロゴ・自社ブランドカラーを優先したい場合は以下を用意してください。

| ファイル | 用途 | テンプレート |
|---|---|---|
| `config/brand_guide.md` | ロゴ配置・配色・タイポグラフィのルール | `references/brand_guide.template.md` |
| `config/brand/logo.png` | ロゴ画像本体（PPTX化スクリプトが既定で参照） | — |

**ロゴは生成AIに描かせず、実画像ファイルを配置**する運用にしてください（詳細は`SKILL.md`「ロゴについて」）。

## 4. PPTX（編集可能なパワポ）で出力したい場合

`references/assets/render_dynamic_tech_glow_pptx.py` が `dynamic_tech_glow` モード向けの参照実装です。

```bash
pip install python-pptx pyyaml
python references/assets/render_dynamic_tech_glow_pptx.py <content.yamlのあるフォルダ>
```

- 入力スキーマのサンプルは `references/assets/example_content.yaml`（ダミー内容。中身を自分の内容に書き換えて使う）
- 見出し直下の区切り線・中央グラフィックの画像素材は `references/assets/pptx_assets/` に同梱
- 他モードのPPTX化に使いたい場合は、このスクリプトを土台に、対象モードの`components`・`palette`に合わせて`draw_*`関数と色定数を書き換えてください（1モード1スクリプトが基本方針。汎用テンプレートエンジンではありません）

## 5. YAML編集後のJSON同期

`modes/*.yaml` を編集したら、コードが読む機械可読版（`modes/*.json`）を再生成してください。

```bash
pip install pyyaml
python modes/build_mode_json.py            # 全モードを再生成
python modes/build_mode_json.py <file.yaml>  # 指定ファイルのみ
```

## 6. 新しいモードを追加する

`references/mode_authoring_guide.md` にスキーマと追加フローをまとめています。サンプルスライド（画像・PDF・説明文）から taste・overrides・composition を抽出し、`modes/`・`index.yaml`・`confirm/`に追加する手順です。

## 収録内容

```
slide-mode-kit/
├── SKILL.md                     # Claude Code向けの使い方指示（トリガー・動作モード）
├── README.md                    # このファイル
├── index.yaml                   # 15モードのレジストリ（taste・tags・render_target）
├── modes/
│   ├── <mode_id>.yaml            # モード定義本体（15件）
│   ├── <mode_id>.json            # コード自動実装用の機械可読版（15件）
│   └── build_mode_json.py        # yaml→json 再生成スクリプト
├── confirm/
│   └── <mode_id>.html / .png     # モードごとの確認用サンプルスライド（15件、参照実装。既存7件はHTML、新規8件はChatGPT生成PNG）
└── references/
    ├── mode_authoring_guide.md   # モードのスキーマ・追加のしかた
    ├── brand_guide.template.md   # 自社ブランド設定のテンプレート
    └── assets/
        ├── render_dynamic_tech_glow_pptx.py   # YAML→編集可能PPTXの参照実装
        ├── example_content.yaml               # 入力サンプル（ダミー内容）
        └── pptx_assets/                        # 参照実装が使う画像素材
```

## 15種類のモード概要

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

`render_target`が`notebooklm`のモードは、AI画像生成（ChatGPT・NotebookLMのいずれもClaude in Chrome経由で対応可能）で作ると質感が出ます。どちらを使うかはユーザーが選択します。`html_claude_design`のモードはClaude Code自身のHTML/CSS/SVGで実用十分な質を再現できます（判断基準は`references/mode_authoring_guide.md`「レンダラーの使い分け」参照）。
