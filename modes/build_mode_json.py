# -*- coding: utf-8 -*-
"""
スライドモード各YAML（modes/*.yaml）から、コード自動実装用のJSON（同名.json）を再生成する。

modesのYAMLは taste/overrides/composition/notes など「LLMが解釈して当てはめる」prose が
大部分を占める。そのため、ここではそのYAML全体をJSON化するのではなく、コードがそのまま
代入できる値だけを抜き出す：
  - palette（flatなhex辞書。そのまま）
  - components.*.render_spec（数値・pxレンジなどの再現用スペック）
overrides・composition・notesはLLMが読んで解釈する情報のため、生成JSONには含めない
（含めても自動実装コードは使い道がなく、YAML本体との二重管理になるだけのため）。

使い方:
    python build_mode_json.py            # modes/配下の全*.yamlを再生成
    python build_mode_json.py <file.yaml>  # 指定ファイルのみ再生成

YAML編集後は必ず実行してJSONを同期させること。
"""
import json
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent


def build(src: dict) -> dict:
    components = {}
    for name, comp in (src.get("components") or {}).items():
        if isinstance(comp, dict) and comp.get("render_spec"):
            components[name] = comp["render_spec"]

    return {
        "meta": {
            "mode_id": src["mode_id"],
            "label": src.get("label"),
            "base": src.get("base"),
            "render_target": src.get("render_target"),
            "generated_from": f"modes/{src['mode_id']}.yaml",
            "generated_by": "modes/build_mode_json.py",
            "do_not_edit_directly": True,
            "role": "コード自動実装がpaletteとrender_specの値だけを読み込む機械可読版。"
            "taste・overrides・composition等の解釈情報は同名のYAMLを参照。",
        },
        "palette": src.get("palette", {}),
        "components": components,
    }


def convert(yaml_path: Path) -> Path:
    src = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    out = build(src)
    json_path = yaml_path.with_suffix(".json")
    json_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return json_path


def main():
    if len(sys.argv) > 1:
        targets = [Path(sys.argv[1])]
    else:
        targets = sorted(SCRIPT_DIR.glob("*.yaml"))

    for yaml_path in targets:
        json_path = convert(yaml_path)
        print(f"generated: {json_path}")


if __name__ == "__main__":
    main()
