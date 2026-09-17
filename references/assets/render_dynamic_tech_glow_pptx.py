# -*- coding: utf-8 -*-
"""
content.yaml + dynamic_tech_glow モード色値からハイブリッドPPTXを生成する参照実装。
ネイティブ: heading / body_text / list(comparison_column, card_3col) / table_or_data /
            summary_statement(highlight_pill) はすべて python-pptx の図形・テキスト・表。
画像埋め込み: glow_divider（見出し直下の区切り線）、center_graphic（8の字グラフィック）のみ
            （同梱の pptx_assets/ を使用。他モードに応用する場合はそのモードの
            componentsに合わせて画像・図形を差し替える）。

このスクリプトは dynamic_tech_glow モード専用の実装例。他モードのPPTX化に流用する
場合は、対象モードの components / palette に合わせて draw_* 関数と色定数を書き換える。

使い方:
    python render_dynamic_tech_glow_pptx.py [content.yamlのあるフォルダ]
    # 省略時はこのスクリプトと同階層のcontent.yaml/pptx_assets/を使う

ロゴを合成する場合は、実行フォルダ（BASE_DIRの親、通常はプロジェクトルート）に
config/brand/logo.png を配置する。無ければロゴなしで出力される（サンプルテキストの
代入は行わない）。
"""
import os
import sys
import copy
import yaml
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 対象デッキフォルダは第1引数で指定可能。省略時はスクリプトと同階層を使う。
if len(sys.argv) > 1:
    BASE_DIR = os.path.abspath(sys.argv[1])
else:
    BASE_DIR = SCRIPT_DIR

CONTENT_YAML = os.path.join(BASE_DIR, "content.yaml")
ASSETS_DIR = os.path.join(BASE_DIR, "pptx_assets")
OUT_PPTX = os.path.join(BASE_DIR, "slides.pptx")
# ロゴ画像は環境変数 SLIDE_MODE_LOGO_PATH で上書き可能。既定は
# 実行ディレクトリ（プロジェクトルート想定）直下の config/brand/logo.png。
LOGO_PATH = os.environ.get(
    "SLIDE_MODE_LOGO_PATH",
    os.path.join(os.getcwd(), "config", "brand", "logo.png"),
)

GLOW_DIVIDER_PNG = os.path.join(ASSETS_DIR, "glow_divider.png")
CENTER_GRAPHIC_PNG = os.path.join(ASSETS_DIR, "center_graphic.png")

# ---- モード色値 (dynamic_tech_glow.yaml palette) ----
NAVY_TEXT = RGBColor(0x1A, 0x22, 0x33)
BG = RGBColor(0xFA, 0xFB, 0xFD)
ACCENT_ORANGE = RGBColor(0xE8, 0x77, 0x2E)
ACCENT_BLUE = RGBColor(0x2F, 0x6F, 0xED)
PILL_BG = RGBColor(0xFD, 0xF0, 0xE4)
CARD_BORDER = RGBColor(0x1A, 0x22, 0x33)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BLUE_RING_BG = RGBColor(0xE4, 0xEC, 0xFD)
LIGHT_ORANGE_RING_BG = RGBColor(0xFD, 0xEA, 0xDE)
TABLE_ROW_LINE = RGBColor(0xE4, 0xEC, 0xFD)
BODY_GRAY_NAVY = RGBColor(0x3A, 0x45, 0x60)

JP_FONT = "Yu Gothic"  # 游ゴシック。無ければ Meiryo / Noto Sans JP にフォールバック可

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


# ---------------------------------------------------------------
# フォントヘルパー: run に日本語(a:ea)と欧文(latin)の両方を明示設定する
# ---------------------------------------------------------------
def set_jp_font(run, font_name=JP_FONT, size=None, bold=None, color=None):
    run.font.name = font_name
    if size is not None:
        run.font.size = size
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", font_name)
    cs = rPr.find(qn("a:cs"))
    if cs is None:
        cs = rPr.makeelement(qn("a:cs"), {})
        rPr.append(cs)
    cs.set("typeface", font_name)


def add_textbox(slide, left, top, width, height, text, size=Pt(18), bold=True,
                 color=NAVY_TEXT, align=PP_ALIGN.LEFT, font_name=JP_FONT,
                 anchor=MSO_ANCHOR.TOP, line_spacing=1.3, word_wrap=True):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = word_wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    if line_spacing:
        p.line_spacing = line_spacing
    run = p.add_run()
    run.text = text
    set_jp_font(run, font_name=font_name, size=size, bold=bold, color=color)
    return tb


def add_rich_textbox(slide, left, top, width, height, segments, size=Pt(18),
                      align=PP_ALIGN.LEFT, font_name=JP_FONT, anchor=MSO_ANCHOR.MIDDLE,
                      line_spacing=1.4):
    """segments: list of (text, bold, color) tuples rendered in one paragraph."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    for text, bold, color in segments:
        run = p.add_run()
        run.text = text
        set_jp_font(run, font_name=font_name, size=size, bold=bold, color=color)
    return tb


def add_logo(slide):
    # config/brand/logo.png があれば右上に合成する。無ければ何も描かない
    # （生成AIにロゴを描かせない方針のため、代替テキストの自動生成もしない）。
    if os.path.exists(LOGO_PATH):
        slide.shapes.add_picture(LOGO_PATH, Inches(11.55), Inches(0.28), height=Inches(0.32))


def set_no_line(shape):
    shape.line.fill.background()


def set_fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def set_line(shape, color, width_pt):
    shape.line.color.rgb = color
    shape.line.width = Pt(width_pt)


def add_slide_bg(slide, prs):
    """背景を bg 色で塗る（矩形を最背面に追加）。"""
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    set_fill(rect, BG)
    set_no_line(rect)
    rect.shadow.inherit = False
    # 最背面へ移動
    spTree = slide.shapes._spTree
    spTree.remove(rect._element)
    spTree.insert(2, rect._element)
    return rect


# ---------------------------------------------------------------
# 見出し + glow_divider
# ---------------------------------------------------------------
def draw_heading(slide, text, top=Inches(0.55), center=False):
    if center:
        add_textbox(slide, Inches(1.0), top, Inches(11.33), Inches(1.1), text,
                    size=Pt(34), bold=True, color=NAVY_TEXT, align=PP_ALIGN.CENTER,
                    anchor=MSO_ANCHOR.MIDDLE)
        divider_w = Inches(6.0)
        left = (SLIDE_W - divider_w) / 2
        slide.shapes.add_picture(GLOW_DIVIDER_PNG, left, top + Inches(1.05), width=divider_w)
    else:
        add_textbox(slide, Inches(0.7), top, Inches(11.9), Inches(0.85), text,
                    size=Pt(30), bold=True, color=NAVY_TEXT, align=PP_ALIGN.LEFT,
                    anchor=MSO_ANCHOR.MIDDLE)
        divider_w = Inches(5.5)
        slide.shapes.add_picture(GLOW_DIVIDER_PNG, Inches(0.7), top + Inches(0.82), width=divider_w)


# ---------------------------------------------------------------
# comparison_column ペア（listが2件の場合）
# ---------------------------------------------------------------
def draw_comparison_pair(slide, lists, top, height):
    n = len(lists)
    gap = Inches(0.6)
    col_w = (Inches(11.93) - gap * (n - 1)) / n
    left0 = Inches(0.7)
    colors = [ACCENT_BLUE, ACCENT_ORANGE]
    ring_bgs = [LIGHT_BLUE_RING_BG, LIGHT_ORANGE_RING_BG]
    for i, lst in enumerate(lists):
        color = colors[i % 2]
        ring_bg = ring_bgs[i % 2]
        left = left0 + i * (col_w + gap)
        # ring icon
        ring_d = Inches(0.62)
        ring = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, ring_d, ring_d)
        set_fill(ring, WHITE)
        set_line(ring, color, 2.0)
        ring.shadow.inherit = False
        tf = ring.text_frame
        tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = "●"
        set_jp_font(run, size=Pt(18), bold=True, color=color)
        # heading
        head_top = top + ring_d + Inches(0.08)
        add_textbox(slide, left, head_top, col_w, Inches(0.55), lst["label"],
                    size=Pt(17), bold=True, color=color, align=PP_ALIGN.LEFT,
                    anchor=MSO_ANCHOR.TOP, line_spacing=1.15)
        # items
        item_top = head_top + Inches(0.55)
        for j, item in enumerate(lst["items"]):
            row_top = item_top + Inches(0.5) * j
            mark_d = Inches(0.2)
            mark = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, row_top + Inches(0.03), mark_d, mark_d)
            set_fill(mark, color)
            set_no_line(mark)
            mark.shadow.inherit = False
            mtf = mark.text_frame
            mtf.margin_left = 0; mtf.margin_right = 0; mtf.margin_top = 0; mtf.margin_bottom = 0
            mp = mtf.paragraphs[0]
            mp.alignment = PP_ALIGN.CENTER
            mrun = mp.add_run()
            mrun.text = "✓"
            set_jp_font(mrun, size=Pt(9), bold=True, color=WHITE)
            add_textbox(slide, left + mark_d + Inches(0.1), row_top, col_w - mark_d - Inches(0.1),
                        Inches(0.48), item, size=Pt(13.5), bold=True, color=NAVY_TEXT,
                        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.2)


# ---------------------------------------------------------------
# card_3col（listが3-4件の場合）
# ---------------------------------------------------------------
def draw_card_row(slide, lists, top, height):
    n = len(lists)
    gap = Inches(0.3)
    card_w = (Inches(11.93) - gap * (n - 1)) / n
    left0 = Inches(0.7)
    for i, lst in enumerate(lists):
        left = left0 + i * (card_w + gap)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, card_w, height)
        card.adjustments[0] = 0.06
        set_fill(card, WHITE)
        set_line(card, CARD_BORDER, 1.4)
        card.shadow.inherit = False
        card.text_frame.word_wrap = True
        # badge
        badge_d = Inches(0.55)
        badge_left = left + (card_w - badge_d) / 2
        badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, badge_left, top + Inches(0.25), badge_d, badge_d)
        set_fill(badge, LIGHT_ORANGE_RING_BG)
        set_no_line(badge)
        badge.shadow.inherit = False
        btf = badge.text_frame
        btf.margin_left = 0; btf.margin_right = 0; btf.margin_top = 0; btf.margin_bottom = 0
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        brun = bp.add_run()
        brun.text = str(i + 1)
        set_jp_font(brun, size=Pt(18), bold=True, color=ACCENT_ORANGE)
        # heading
        head_top = top + Inches(0.9)
        add_textbox(slide, left + Inches(0.15), head_top, card_w - Inches(0.3), Inches(0.65),
                    lst["label"], size=Pt(15), bold=True, color=NAVY_TEXT,
                    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP, line_spacing=1.15)
        # underline
        underline_w = Inches(0.42)
        uline = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                        left + (card_w - underline_w) / 2,
                                        head_top + Inches(0.62), underline_w, Inches(0.035))
        set_fill(uline, ACCENT_ORANGE)
        set_no_line(uline)
        uline.shadow.inherit = False
        # items
        item_top = head_top + Inches(0.82)
        item_text = "\n".join(["・" + it for it in lst["items"]])
        tb = slide.shapes.add_textbox(left + Inches(0.18), item_top, card_w - Inches(0.36),
                                       height - (item_top - top) - Inches(0.15))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
        for k, it in enumerate(lst["items"]):
            p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            p.line_spacing = 1.25
            p.space_after = Pt(6)
            run = p.add_run()
            run.text = "・" + it
            set_jp_font(run, size=Pt(11.5), bold=True, color=BODY_GRAY_NAVY)


# ---------------------------------------------------------------
# phrase variant: セリフ例カードを2xNグリッド配置
#   各item = {label: "例①", text: "「…」"}
#   カード=白背景・accent_orange枠・角丸。上部にオレンジ丸ラベル＋下にセリフ本文。
#   command_chip的な雰囲気だが文字はネイティブ編集可能。
# ---------------------------------------------------------------
def draw_phrase_cards(slide, items, top, height, cols=2):
    n = len(items)
    rows = (n + cols - 1) // cols
    gap_x = Inches(0.5)
    gap_y = Inches(0.4)
    left0 = Inches(1.1)
    grid_w = Inches(11.13)
    card_w = (grid_w - gap_x * (cols - 1)) / cols
    card_h = (height - gap_y * (rows - 1)) / rows
    for idx, item in enumerate(items):
        r = idx // cols
        c = idx % cols
        left = left0 + c * (card_w + gap_x)
        ctop = top + r * (card_h + gap_y)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, ctop, card_w, card_h)
        card.adjustments[0] = 0.10
        set_fill(card, WHITE)
        set_line(card, ACCENT_ORANGE, 1.5)
        card.shadow.inherit = False
        # オレンジ丸ラベル（例①〜④）
        lbl_d = Inches(0.5)
        lbl = slide.shapes.add_shape(MSO_SHAPE.OVAL, left + Inches(0.28),
                                      ctop + (card_h - lbl_d) / 2, lbl_d, lbl_d)
        set_fill(lbl, ACCENT_ORANGE)
        set_no_line(lbl)
        lbl.shadow.inherit = False
        ltf = lbl.text_frame
        ltf.margin_left = 0; ltf.margin_right = 0; ltf.margin_top = 0; ltf.margin_bottom = 0
        lp = ltf.paragraphs[0]
        lp.alignment = PP_ALIGN.CENTER
        lrun = lp.add_run()
        lrun.text = item["label"]
        set_jp_font(lrun, size=Pt(12), bold=True, color=WHITE)
        # セリフ本文
        text_left = left + Inches(0.28) + lbl_d + Inches(0.2)
        text_w = card_w - (Inches(0.28) + lbl_d + Inches(0.2)) - Inches(0.2)
        add_textbox(slide, text_left, ctop, text_w, card_h, item["text"],
                    size=Pt(15), bold=True, color=NAVY_TEXT, align=PP_ALIGN.LEFT,
                    anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.3)


# ---------------------------------------------------------------
# comparison_2 (center_graphic + 左右comparison_column)
# ---------------------------------------------------------------
def draw_comparison_2(slide, columns, top, height):
    center_w = Inches(2.4)
    gap = Inches(0.35)
    col_w = (Inches(11.93) - center_w - gap * 2) / 2
    left0 = Inches(0.7)
    colors = [ACCENT_BLUE, ACCENT_ORANGE]
    ring_bgs = [LIGHT_BLUE_RING_BG, LIGHT_ORANGE_RING_BG]
    ring_icons = ["◉", "✧"]
    col_positions = [left0, left0 + col_w + gap + center_w + gap]
    for i, col in enumerate(columns):
        color = colors[i % 2]
        left = col_positions[i]
        ring_d = Inches(0.62)
        ring_top = top
        ring = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, ring_top, ring_d, ring_d)
        set_fill(ring, WHITE)
        set_line(ring, color, 2.0)
        ring.shadow.inherit = False
        rtf = ring.text_frame
        rtf.margin_left = 0; rtf.margin_right = 0; rtf.margin_top = 0; rtf.margin_bottom = 0
        rp = rtf.paragraphs[0]
        rp.alignment = PP_ALIGN.CENTER
        rrun = rp.add_run()
        rrun.text = ring_icons[i % 2]
        set_jp_font(rrun, size=Pt(18), bold=True, color=color)
        head_top = ring_top + ring_d + Inches(0.08)
        add_textbox(slide, left, head_top, col_w, Inches(0.75), col["label"],
                    size=Pt(16), bold=True, color=color, align=PP_ALIGN.LEFT,
                    anchor=MSO_ANCHOR.TOP, line_spacing=1.15)
        item_top = head_top + Inches(0.75)
        for j, item in enumerate(col["items"]):
            row_top = item_top + Inches(0.62) * j
            mark_d = Inches(0.19)
            mark = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, row_top + Inches(0.03), mark_d, mark_d)
            set_fill(mark, color)
            set_no_line(mark)
            mark.shadow.inherit = False
            mtf = mark.text_frame
            mtf.margin_left = 0; mtf.margin_right = 0; mtf.margin_top = 0; mtf.margin_bottom = 0
            mp = mtf.paragraphs[0]
            mp.alignment = PP_ALIGN.CENTER
            mrun = mp.add_run()
            mrun.text = "✓"
            set_jp_font(mrun, size=Pt(8.5), bold=True, color=WHITE)
            add_textbox(slide, left + mark_d + Inches(0.1), row_top, col_w - mark_d - Inches(0.1),
                        Inches(0.6), item, size=Pt(12.5), bold=True, color=NAVY_TEXT,
                        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.2)
    # center graphic image
    cg_w = Inches(2.4)
    cg_h = Inches(1.8)
    cg_left = left0 + col_w + gap
    cg_top = top + Inches(0.5)
    slide.shapes.add_picture(CENTER_GRAPHIC_PNG, cg_left, cg_top, width=cg_w, height=cg_h)


# ---------------------------------------------------------------
# table_or_data
# ---------------------------------------------------------------
def draw_table(slide, headers, rows, top, height):
    left = Inches(0.7)
    width = Inches(11.93)
    n_rows = len(rows) + 1
    n_cols = len(headers)
    gtable = slide.shapes.add_table(n_rows, n_cols, left, top, width, height).table
    # column widths: 工程/担当 narrower, 責務/強み wider
    col_ratios = [0.14, 0.16, 0.4, 0.3] if n_cols == 4 else [1.0 / n_cols] * n_cols
    for i, ratio in enumerate(col_ratios[:n_cols]):
        gtable.columns[i].width = Emu(int(width * ratio))

    def style_cell(cell, text, bold, color, size, align=PP_ALIGN.LEFT, fill=None):
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill if fill else WHITE
        cell.margin_left = Inches(0.12)
        cell.margin_right = Inches(0.12)
        cell.margin_top = Inches(0.06)
        cell.margin_bottom = Inches(0.06)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = align
        run = p.add_run()
        run.text = text
        set_jp_font(run, size=Pt(size), bold=bold, color=color)

    for c, h in enumerate(headers):
        style_cell(gtable.cell(0, c), h, True, NAVY_TEXT, 15, fill=WHITE)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            color = ACCENT_BLUE if c == 1 else NAVY_TEXT
            style_cell(gtable.cell(r + 1, c), val, True, color, 14, fill=WHITE)
    return gtable


# ---------------------------------------------------------------
# summary_statement -> highlight_pill
# ---------------------------------------------------------------
def draw_summary_pill(slide, text):
    pill_h = Inches(0.85)
    pill_top = Inches(6.35)
    pill_left = Inches(0.7)
    pill_w = Inches(11.93)
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pill_left, pill_top, pill_w, pill_h)
    pill.adjustments[0] = 0.5
    set_fill(pill, PILL_BG)
    set_line(pill, ACCENT_ORANGE, 1.4)
    pill.shadow.inherit = False

    bulb_d = Inches(0.42)
    bulb = slide.shapes.add_shape(MSO_SHAPE.OVAL, pill_left + Inches(0.25),
                                   pill_top + (pill_h - bulb_d) / 2, bulb_d, bulb_d)
    set_fill(bulb, ACCENT_ORANGE)
    set_no_line(bulb)
    bulb.shadow.inherit = False
    btf = bulb.text_frame
    btf.margin_left = 0; btf.margin_right = 0; btf.margin_top = 0; btf.margin_bottom = 0
    bp = btf.paragraphs[0]
    bp.alignment = PP_ALIGN.CENTER
    brun = bp.add_run()
    brun.text = "💡"
    set_jp_font(brun, size=Pt(16), bold=True, color=WHITE)

    text_left = pill_left + Inches(0.85)
    text_w = pill_w - Inches(1.1)
    segments = parse_bold_segments(text)
    add_rich_textbox(slide, text_left, pill_top, text_w, pill_h, segments,
                      size=Pt(15), align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.3)


def parse_bold_segments(text):
    """content.yaml summary_statementはプレーンテキストのため強調語なしで返す。
    将来 **強調** 記法を入れた場合はここでパースする。"""
    segments = []
    buf = ""
    i = 0
    bold_mode = False
    while i < len(text):
        if text[i:i+2] == "**":
            if buf:
                segments.append((buf, bold_mode, ACCENT_ORANGE if bold_mode else NAVY_TEXT))
                buf = ""
            bold_mode = not bold_mode
            i += 2
            continue
        buf += text[i]
        i += 1
    if buf:
        segments.append((buf, bold_mode, ACCENT_ORANGE if bold_mode else NAVY_TEXT))
    if not segments:
        segments = [(text, False, NAVY_TEXT)]
    return segments


# ---------------------------------------------------------------
# body_text
# ---------------------------------------------------------------
def draw_body_text(slide, text, top, height, center=False):
    segments = parse_bold_segments(text)
    align = PP_ALIGN.CENTER if center else PP_ALIGN.LEFT
    add_rich_textbox(slide, Inches(0.9), top, Inches(11.53), height, segments,
                      size=Pt(16.5), align=align, anchor=MSO_ANCHOR.TOP, line_spacing=1.5)


# ---------------------------------------------------------------
# 表紙スライド
# ---------------------------------------------------------------
def draw_cover(slide, heading_text, body_text):
    add_textbox(slide, Inches(1.0), Inches(2.35), Inches(11.33), Inches(1.7), heading_text,
                size=Pt(40), bold=True, color=NAVY_TEXT, align=PP_ALIGN.CENTER,
                anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.3)
    divider_w = Inches(5.4)
    left = (SLIDE_W - divider_w) / 2
    slide.shapes.add_picture(GLOW_DIVIDER_PNG, left, Inches(4.05), width=divider_w)
    add_textbox(slide, Inches(1.0), Inches(4.35), Inches(11.33), Inches(0.7), body_text,
                size=Pt(19), bold=True, color=RGBColor(0x2A, 0x3A, 0x5C), align=PP_ALIGN.CENTER,
                anchor=MSO_ANCHOR.MIDDLE)


# ---------------------------------------------------------------
# メイン: スライドごとの組み立て
# ---------------------------------------------------------------
def build_slide(prs, slide_data, index):
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    add_slide_bg(slide, prs)
    add_logo(slide)

    blocks = slide_data["blocks"]
    heading_block = next((b for b in blocks if b["shape"] == "heading"), None)

    list_blocks = [b for b in blocks if b["shape"] == "list"]
    comparison2_block = next((b for b in blocks if b["shape"] == "comparison_2"), None)
    table_block = next((b for b in blocks if b["shape"] == "table_or_data"), None)
    body_blocks = [b for b in blocks if b["shape"] == "body_text"]
    summary_block = next((b for b in blocks if b["shape"] == "summary_statement"), None)
    phrase_block = next((b for b in list_blocks if b.get("variant") == "phrase"), None)

    # 表紙判定は内容ベース: 先頭スライドで、見出し＋body_textのみ
    # （リスト・表・比較図が無い）場合のみカバーとして扱う。
    is_cover = (index == 0 and not list_blocks and not comparison2_block
                and not table_block and body_blocks)

    if is_cover:
        body_block = body_blocks[0]
        draw_cover(slide, heading_block["text"], body_block["text"])
        return

    # 見出し
    draw_heading(slide, heading_block["text"])
    content_top = Inches(2.15)

    cursor_top = content_top
    has_visual_block = bool(comparison2_block or table_block or list_blocks)

    # body_text (責務分離スライド・まとめスライド)
    # 図解・表・リストが無いスライド(例:まとめ)は本文に十分な縦幅を与える
    body_height = Inches(1.3) if has_visual_block else Inches(3.6)
    for bb in body_blocks:
        draw_body_text(slide, bb["text"], cursor_top, body_height)
        cursor_top += body_height + Inches(0.15)

    if comparison2_block:
        draw_comparison_2(slide, comparison2_block["columns"], cursor_top, Inches(3.6))
    elif table_block:
        draw_table(slide, table_block["headers"], table_block["rows"], cursor_top, Inches(1.7))
    elif phrase_block:
        draw_phrase_cards(slide, phrase_block["items"], cursor_top, Inches(3.5), cols=2)
    elif len(list_blocks) == 2:
        draw_comparison_pair(slide, list_blocks, cursor_top, Inches(3.6))
    elif len(list_blocks) >= 3:
        draw_card_row(slide, list_blocks, cursor_top, Inches(3.6))

    if summary_block:
        draw_summary_pill(slide, summary_block["text"])


def main():
    with open(CONTENT_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    for i, slide_data in enumerate(data["slides"]):
        build_slide(prs, slide_data, i)

    prs.save(OUT_PPTX)
    print(f"saved: {OUT_PPTX}")
    print(f"slide count: {len(data['slides'])}")


if __name__ == "__main__":
    main()
