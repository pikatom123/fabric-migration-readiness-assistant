from __future__ import annotations

import csv
import subprocess
from pathlib import Path

import xlsxwriter
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "demo-assets"
SHOTS = ASSETS / "screenshots"
OUT = ASSETS / "output"
FRAMES = ASSETS / "source" / "frames"
TEAM_IMAGE = ASSETS / "source" / "team-table-10.png"
OUT.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)

BG = "F7F4EF"
SURFACE = "FFFFFF"
INK = "242424"
MUTED = "5C5C5C"
ACCENT = "B11F4B"
ACCENT_DARK = "851637"
TEAL = "087E8B"
GREEN = "16834A"
AMBER = "D97706"
RED = "C62828"
BORDER = "DDD8D1"

TITLE_FONT = "Aptos Display"
BODY_FONT = "Aptos"

NARRATION = """Microsoft Fabric migrations rarely begin with one tidy platform. Customer estates span Power BI, Analysis Services, Azure SQL, Synapse, Databricks, Data Factory, Logic Apps, Spark, and automation. Today, a CSA must manually discover dependencies, check feature support, estimate capacity pressure, and turn all of that into a customer-ready recommendation. The result can be slow, inconsistent, and difficult to repeat.

Our Fabric Migration Readiness and Optimisation Assistant creates one guided assessment workflow. We can start in three ways. For a spreadsheet inventory, use the included Excel template and save it as CSV for direct browser import. For architecture or estate PDFs, use the packaged CLI or Copilot discovery agent to extract text for confirmation. Or enter a workload manually during the customer conversation.

The prototype captures customer outcomes, constraints, scale, concurrency, and workload dependencies. Imported inventory is never marked ready automatically. It stays in Needs Discovery until the CSA confirms the workload-specific facts.

The assessment then maps each workload to an appropriate Fabric pattern. It identifies blockers, optimisation opportunities, and the next questions to ask. The deterministic rules engine keeps the result repeatable, while Microsoft Learn evidence and specialist Fabric skills support deeper validation.

Finally, the summary turns technical findings into an executive position, target patterns, priority next steps, and directional SKU Estimator inputs such as data volume, daily movement, concurrency, refresh overlap, real-time demand, growth, and region.

For this hackathon, the prototype demonstrates the complete journey from estate intake to an explainable customer-ready recommendation. The next step is to validate it on real engagements, expand native import options, and connect measured capacity telemetry for production-grade sizing."""

PRESENTER_NOTES = """FABRIC MIGRATION READINESS AND OPTIMISATION ASSISTANT
Hackathon presentation guide

DEMO ASSETS
- Fabric_Migration_Readiness_Assistant_Hackathon_Deck.pptx: editable 8-slide deck.
- Fabric_Migration_Readiness_Assistant_2min_Demo.mp4: 120-second narrated overview.
- Fabric_Migration_Readiness_Assistant_Demo_Script.txt: narration and live-demo runbook.
- Contoso_Estate_Inventory.xlsx: spreadsheet template for customer inventory.
- Contoso_Estate_Inventory.csv: browser-ready export of the same spreadsheet.
- Contoso_Estate_Overview.pdf: text-based PDF for the CLI/Copilot extraction path.

TWO-MINUTE LIVE DEMO RUNBOOK
1. Open index.html in Edge or Chrome and select Reset.
2. Explain the three intake paths: manual form, Excel saved as CSV, or PDF through Copilot/CLI.
3. Select Upload PDF or CSV and choose Contoso_Estate_Inventory.csv.
4. Open Workloads and point out that imported rows are Needs Discovery, not guessed as ready.
5. Select Load sample to show a completed conversational assessment.
6. Open Assessment and expand one workload to show blockers, optimisation actions, and questions.
7. Open Summary to show executive position, target patterns, next steps, and SKU Estimator inputs.
8. Close with: deterministic rules make it repeatable; Learn evidence and specialist Fabric skills keep it current.

IMPORTANT DEMO LANGUAGE
- Say "Excel inventory saved as CSV"; the browser does not natively parse .xlsx.
- Say "directional SKU Estimator inputs," not "capacity quote."
- PDF extraction runs through the CLI or Copilot workflow, not inside the browser-only page.
"""

INVENTORY_ROWS = [
    ["Executive sales semantic model", "Power BI", 85, "Shared model; composite mode and calculated columns"],
    ["Finance planning cube", "SSAS", 420, "MDX scripts and writeback workflow"],
    ["Retail data integration", "Azure Data Factory", 2600, "On-premises SQL Server and SAP through SHIR"],
    ["Customer feature engineering", "Databricks", 7400, "Custom Python wheels and private networking"],
    ["Order analytics replica", "Azure SQL", 1200, "Operational source with CDC requirements"],
]


def rgb(value: str) -> RGBColor:
    return RGBColor.from_string(value)


def font(size: int, bold: bool = False, color: str = INK, name: str = BODY_FONT) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/aptos.ttf"),
        Path("C:/Windows/Fonts/aptos-display.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
    ]
    if bold:
        candidates = [Path("C:/Windows/Fonts/aptos-bold.ttf"), Path("C:/Windows/Fonts/segoeuib.ttf")] + candidates
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, size: int, *, bold: bool = False,
              color: str = INK, max_width: int | None = None, spacing: int = 10) -> int:
    fnt = font(size, bold=bold)
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not max_width:
            lines.append(paragraph)
            continue
        words = paragraph.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)
    y = xy[1]
    for line in lines:
        draw.text((xy[0], y), line, font=fnt, fill=f"#{color}")
        box = draw.textbbox((xy[0], y), line or " ", font=fnt)
        y += (box[3] - box[1]) + spacing
    return y


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str = SURFACE,
            outline: str = BORDER, radius: int = 22, width: int = 2) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=f"#{fill}", outline=f"#{outline}", width=width)


def base_frame(kicker: str, title: str, subtitle: str = "") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (W, H), f"#{BG}")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 18, H), fill=f"#{ACCENT}")
    draw_text(draw, (86, 64), kicker.upper(), 24, bold=True, color=ACCENT)
    draw_text(draw, (86, 112), title, 54, bold=True, max_width=1650, spacing=8)
    if subtitle:
        draw_text(draw, (88, 190), subtitle, 25, color=MUTED, max_width=1660, spacing=6)
    return image, draw


def paste_shot(image: Image.Image, shot_name: str, box: tuple[int, int, int, int]) -> None:
    shot = Image.open(SHOTS / shot_name).convert("RGB")
    x1, y1, x2, y2 = box
    ratio = min((x2 - x1) / shot.width, (y2 - y1) / shot.height)
    size = (int(shot.width * ratio), int(shot.height * ratio))
    shot = shot.resize(size, Image.Resampling.LANCZOS)
    x = x1 + ((x2 - x1) - shot.width) // 2
    y = y1 + ((y2 - y1) - shot.height) // 2
    image.paste(shot, (x, y))


def paste_mobile_shot(image: Image.Image, shot_name: str, box: tuple[int, int, int, int]) -> None:
    shot = Image.open(SHOTS / shot_name).convert("RGB")
    shot = shot.crop((0, 0, min(390, shot.width), shot.height))
    x1, y1, x2, y2 = box
    ratio = min((x2 - x1) / shot.width, (y2 - y1) / shot.height)
    shot = shot.resize((int(shot.width * ratio), int(shot.height * ratio)), Image.Resampling.LANCZOS)
    image.paste(shot, (x1 + ((x2 - x1) - shot.width) // 2, y1 + ((y2 - y1) - shot.height) // 2))


def save_frames() -> list[Path]:
    frames: list[Path] = []

    team_image = Image.open(TEAM_IMAGE).convert("RGB")
    scale = min(W / team_image.width, H / team_image.height)
    team_image = team_image.resize(
        (round(team_image.width * scale), round(team_image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    image = Image.new("RGB", (W, H), "#07182E")
    image.paste(team_image, ((W - team_image.width) // 2, (H - team_image.height) // 2))
    frames.append(FRAMES / "00-title.png"); image.save(frames[-1])

    image, draw = base_frame("Why this is needed", "The first migration conversation is harder than it should be", "Customers know they want to explore Fabric, but rarely know where to start or what must change.")
    problems = [
        ("Fragmented estate", "Power BI, Synapse, SQL, Databricks, Spark, pipelines, and reporting carry different dependencies.", TEAL),
        ("Sizing too early", "Capacity discussions begin before workload behaviour, refresh overlap, concurrency, and growth are understood.", AMBER),
        ("Hidden redesign", "Unsupported features, transformation placement, semantic-model design, and orchestration changes surface late.", RED),
    ]
    for index, (title, body, color) in enumerate(problems):
        x = 88 + index * 590
        rounded(draw, (x, 315, x + 535, 665), fill=SURFACE, outline=color, radius=20, width=3)
        draw_text(draw, (x + 32, 355), f"0{index + 1}", 20, bold=True, color=color)
        draw_text(draw, (x + 32, 410), title, 29, bold=True)
        draw_text(draw, (x + 32, 485), body, 22, color=MUTED, max_width=455)
    rounded(draw, (88, 750, 1773, 940), fill="FFF8FA", outline=ACCENT, radius=22, width=3)
    draw_text(draw, (135, 790), "PROBLEM SOLVED", 20, bold=True, color=ACCENT)
    draw_text(draw, (135, 845), "Give the CSA a consistent way to structure discovery, expose risks early, and leave the customer with a credible next step.", 29, bold=True, max_width=1570)
    frames.append(FRAMES / "01-problem.png"); image.save(frames[-1])

    image, draw = base_frame("Who uses it", "Built for the people shaping the migration decision", "CSA-led, customer-collaborative, and useful before a formal migration assessment begins.")
    users = [
        ("Primary user", "Cloud Solution Architect", "Lead discovery, challenge assumptions, identify blockers, and frame the migration path.", ACCENT),
        ("Customer collaborators", "Data & analytics leaders", "Confirm outcomes, constraints, priorities, risk tolerance, and investment appetite.", TEAL),
        ("Technical contributors", "BI, data, and platform teams", "Validate workload facts, dependencies, performance behaviour, and redesign effort.", AMBER),
        ("Decision audience", "Sponsors & architects", "Understand readiness, risk, required change, sequencing, and next-step evidence.", GREEN),
    ]
    for index, (label, title, body, color) in enumerate(users):
        col, row = index % 2, index // 2
        x, y = 88 + col * 880, 300 + row * 330
        rounded(draw, (x, y, x + 815, y + 275), fill=SURFACE, outline=color, radius=20, width=3)
        draw_text(draw, (x + 32, y + 30), label.upper(), 18, bold=True, color=color)
        draw_text(draw, (x + 32, y + 78), title, 29, bold=True)
        draw_text(draw, (x + 32, y + 145), body, 22, color=MUTED, max_width=735)
    frames.append(FRAMES / "02-inputs.png"); image.save(frames[-1])

    image, draw = base_frame("The engagement moment", "A better initial conversation with the customer", "The assistant creates structure without pretending incomplete discovery is complete.")
    stages = [
        ("BEFORE", "Bring what exists", "Upload an Excel-exported CSV, use a PDF through Copilot/CLI, or start manually.", TEAL),
        ("DURING", "Ask what matters", "Capture outcomes, constraints, scale, concurrency, refresh overlap, dependencies, and critical features.", ACCENT),
        ("AFTER", "Leave with direction", "Summarise readiness, target patterns, risks, design changes, actions, and sizing inputs.", GREEN),
    ]
    for index, (stage, title, body, color) in enumerate(stages):
        x = 88 + index * 590
        rounded(draw, (x, 325, x + 535, 735), fill=SURFACE, outline=color, radius=20, width=3)
        draw_text(draw, (x + 32, 365), stage, 20, bold=True, color=color)
        draw_text(draw, (x + 32, 430), title, 29, bold=True)
        draw_text(draw, (x + 32, 510), body, 23, color=MUTED, max_width=455)
        if index < 2:
            draw.line((x + 535, 530, x + 580, 530), fill=f"#{BORDER}", width=5)
    rounded(draw, (250, 825, 1610, 965), fill="FFF8FA", outline=ACCENT, radius=20, width=3)
    draw_text(draw, (305, 865), "Unknown facts remain Needs Discovery until the customer confirms them.", 29, bold=True, color=ACCENT, max_width=1250)
    frames.append(FRAMES / "03-discovery.png"); image.save(frames[-1])

    image, draw = base_frame("What it assesses", "Beyond migration mapping: readiness and optimisation", "The recommendation considers whether each workload should migrate, change, coexist, or remain where it is.")
    checks = [
        ("Target pattern", "Direct Lake, Warehouse, Lakehouse, Data Factory, Real-Time Intelligence, or Power BI", TEAL),
        ("Blockers", "Unsupported features, connectivity, security, orchestration, custom code, and operating constraints", RED),
        ("Design changes", "Semantic-model redesign, Gold-layer transformations, pipeline changes, and workload decomposition", AMBER),
        ("Optimisation", "Refresh overlap, model efficiency, data movement, Spark strategy, and capacity pressure", GREEN),
    ]
    for index, (title, body, color) in enumerate(checks):
        col, row = index % 2, index // 2
        x, y = 88 + col * 880, 300 + row * 320
        rounded(draw, (x, y, x + 815, y + 265), fill=SURFACE, outline=color, radius=20, width=3)
        draw_text(draw, (x + 32, y + 35), title, 28, bold=True, color=color)
        draw_text(draw, (x + 32, y + 105), body, 22, color=MUTED, max_width=735)
    draw_text(draw, (90, 950), "Examples: Direct Lake suitability • calculated columns into Gold • refresh collisions • Spark/pipeline redesign", 23, bold=True, color=ACCENT, max_width=1700)
    frames.append(FRAMES / "04-inventory.png"); image.save(frames[-1])

    image, draw = base_frame("What the customer receives", "An explainable starting point for the migration journey", "Not a black-box verdict and not a capacity quote: a transparent recommendation grounded in confirmed facts.")
    outputs = [
        ("Readiness score", "Directional position by workload", TEAL),
        ("Target patterns", "Recommended Fabric landing zones", ACCENT),
        ("Risks & blockers", "What could delay or prevent migration", RED),
        ("Required changes", "What must be redesigned or optimised", AMBER),
        ("Action plan", "Prioritised questions and next steps", GREEN),
        ("SKU inputs", "Volume, movement, concurrency, overlap, and growth", TEAL),
    ]
    for index, (title, body, color) in enumerate(outputs):
        col, row = index % 3, index // 3
        x, y = 88 + col * 590, 305 + row * 300
        rounded(draw, (x, y, x + 535, y + 245), fill=SURFACE, outline=color, radius=18, width=3)
        draw_text(draw, (x + 30, y + 35), title, 26, bold=True, color=color)
        draw_text(draw, (x + 30, y + 105), body, 21, color=MUTED, max_width=455)
    rounded(draw, (320, 920, 1540, 1010), fill="FFF8FA", outline=ACCENT, radius=18, width=3)
    draw_text(draw, (375, 946), "Outcome: agreement on where deeper assessment should focus next.", 25, bold=True, color=ACCENT)
    frames.append(FRAMES / "05-assessment.png"); image.save(frames[-1])

    image, draw = base_frame("How it stays current", "A maintained skill, not a static questionnaire", "The conversational workflow and deterministic assessment knowledge can evolve independently of the user experience.")
    layers = [
        ("Guided skill", "Controls the CSA conversation, asks adaptive questions, and preserves unknowns.", ACCENT),
        ("Versioned rules", "Maps confirmed facts to patterns, blockers, readiness, and optimisation actions.", TEAL),
        ("Current evidence", "Microsoft Learn grounding and specialist Fabric skills validate changing capabilities.", GREEN),
        ("Feedback loop", "Real engagements add questions, edge cases, evidence, and regression tests.", AMBER),
    ]
    for index, (title, body, color) in enumerate(layers):
        x, y = 90 + index * 430, 330
        rounded(draw, (x, y, x + 385, y + 360), fill=SURFACE, outline=color, radius=20, width=3)
        draw_text(draw, (x + 28, y + 35), f"0{index + 1}", 19, bold=True, color=color)
        draw_text(draw, (x + 28, y + 92), title, 27, bold=True)
        draw_text(draw, (x + 28, y + 165), body, 21, color=MUTED, max_width=320)
        if index < 3:
            draw.line((x + 385, y + 180, x + 420, y + 180), fill=f"#{BORDER}", width=5)
    rounded(draw, (250, 790, 1610, 955), fill="FFF8FA", outline=ACCENT, radius=22, width=3)
    draw_text(draw, (305, 830), "Maintain → validate → version → test → release", 28, bold=True, color=ACCENT)
    draw_text(draw, (305, 885), "Recommendations remain repeatable while Fabric capabilities continue to change.", 23, color=MUTED)
    frames.append(FRAMES / "06-summary.png"); image.save(frames[-1])

    image, draw = base_frame("Why it matters", "Turn uncertainty into a credible next conversation", "The prototype demonstrates the journey from estate intake to an explainable, customer-ready recommendation.")
    outcomes = [
        ("FOR THE CSA", "A repeatable way to lead initial migration discovery", ACCENT),
        ("FOR THE CUSTOMER", "Clarity on readiness, risk, change, and next steps", TEAL),
        ("FOR DELIVERY", "Earlier visibility of redesign and dependency work", AMBER),
        ("FOR FABRIC", "Better-qualified sizing and architecture conversations", GREEN),
    ]
    for i, (label, body, color) in enumerate(outcomes):
        col, row = i % 2, i // 2
        x, y = 88 + col * 900, 300 + row * 260
        rounded(draw, (x, y, x + 820, y + 205), fill=SURFACE, outline=color, radius=22, width=3)
        draw_text(draw, (x + 34, y + 35), label, 24, bold=True, color=color)
        draw_text(draw, (x + 34, y + 90), body, 25, max_width=735)
    draw_text(draw, (90, 885), "HACKATHON ASK", 20, bold=True, color=ACCENT)
    draw_text(draw, (90, 930), "Pilot with CSAs on real customer estates, then expand evidence, telemetry, and non-Microsoft coverage.", 28, bold=True, max_width=1700)
    frames.append(FRAMES / "07-impact.png"); image.save(frames[-1])
    return frames


def add_bg(slide) -> None:
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    shape.fill.solid(); shape.fill.fore_color.rgb = rgb(BG)
    shape.line.fill.background()
    slide.shapes._spTree.remove(shape._element)
    slide.shapes._spTree.insert(2, shape._element)
    rail = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.12), SLIDE_H)
    rail.fill.solid(); rail.fill.fore_color.rgb = rgb(ACCENT); rail.line.fill.background()


def add_textbox(slide, x, y, w, h, text, size=24, bold=False, color=INK, font_name=BODY_FONT,
                align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame; frame.clear(); frame.vertical_anchor = valign
    p = frame.paragraphs[0]; p.text = text; p.alignment = align
    run = p.runs[0]; run.font.name = font_name; run.font.size = Pt(size); run.font.bold = bold; run.font.color.rgb = rgb(color)
    return box


def add_header(slide, kicker, title, subtitle="") -> None:
    add_textbox(slide, 0.6, 0.35, 11.8, 0.3, kicker.upper(), 12, True, ACCENT)
    add_textbox(slide, 0.6, 0.72, 12.0, 0.75, title, 30, True, INK, TITLE_FONT)
    if subtitle:
        add_textbox(slide, 0.62, 1.42, 11.8, 0.55, subtitle, 15, False, MUTED)


def add_frame_slide(prs: Presentation, frame: Path, notes: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.shapes.add_picture(str(frame), 0, 0, width=SLIDE_W, height=SLIDE_H)
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = notes


def build_deck(frames: list[Path]) -> Path:
    prs = Presentation(); prs.slide_width = SLIDE_W; prs.slide_height = SLIDE_H
    notes = [
        "Open with the engagement outcome: help a CSA start the right migration conversation before architecture and sizing decisions are made.",
        "Explain why the initial conversation is difficult: fragmented workloads, premature sizing, and redesign needs that surface too late.",
        "Name the primary user and collaborators: the CSA leads, customer leaders set outcomes, technical teams confirm facts, and sponsors consume the recommendation.",
        "Show how the assistant supports the engagement before, during, and after the customer conversation while keeping unknowns explicit.",
        "Explain that the assessment goes beyond mapping: it tests blockers, required design changes, optimisation opportunities, and capacity pressure.",
        "Describe the customer-ready output and reinforce that SKU data is directional estimator input, not a capacity quote.",
        "Position the solution as a maintained skill with versioned deterministic rules, current Microsoft Learn evidence, specialist skills, and engagement feedback.",
        "Close on the value to the CSA, customer, delivery team, and Fabric conversation; ask to pilot it on real customer estates.",
    ]
    for frame, note in zip(frames, notes):
        add_frame_slide(prs, frame, note)
    path = OUT / "Fabric_Migration_Readiness_Assistant_Hackathon_Deck.pptx"
    prs.save(path)
    return path


def build_inputs() -> None:
    xlsx_path = OUT / "Contoso_Estate_Inventory.xlsx"
    workbook = xlsxwriter.Workbook(xlsx_path)
    sheet = workbook.add_worksheet("Estate Inventory")
    header_fmt = workbook.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": f"#{ACCENT}", "border": 0, "align": "left"})
    text_fmt = workbook.add_format({"border": 1, "border_color": f"#{BORDER}", "valign": "top"})
    number_fmt = workbook.add_format({"border": 1, "border_color": f"#{BORDER}", "num_format": "0"})
    headers = ["name", "workload_type", "size_gb", "notes"]
    for col, header in enumerate(headers): sheet.write(0, col, header, header_fmt)
    for row_index, row in enumerate(INVENTORY_ROWS, start=1):
        for col, value in enumerate(row): sheet.write(row_index, col, value, number_fmt if col == 2 else text_fmt)
    sheet.set_column("A:A", 34); sheet.set_column("B:B", 24); sheet.set_column("C:C", 12); sheet.set_column("D:D", 52)
    sheet.freeze_panes(1, 0); sheet.autofilter(0, 0, len(INVENTORY_ROWS), len(headers) - 1)
    workbook.close()

    with (OUT / "Contoso_Estate_Inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(headers); writer.writerows(INVENTORY_ROWS)

    styles = getSampleStyleSheet()
    pdf = SimpleDocTemplate(str(OUT / "Contoso_Estate_Overview.pdf"), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    story = [Paragraph("Contoso Retail - Analytics Estate Overview", styles["Title"]), Spacer(1, 8),
             Paragraph("Prepared for Fabric migration discovery. All details require customer confirmation before readiness decisions.", styles["BodyText"]), Spacer(1, 14)]
    data = [["Workload", "Platform", "Scale", "Dependency"]] + [[r[0], r[1], f"{r[2]:,} GB", r[3]] for r in INVENTORY_ROWS]
    table = Table(data, colWidths=[42*mm, 34*mm, 22*mm, 72*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor(f"#{ACCENT}")), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor(f"#{BORDER}")), ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F7F4EF")]), ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6), ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.extend([table, Spacer(1, 16), Paragraph("Known constraints", styles["Heading2"]),
                  Paragraph("Private connectivity is mandatory. Month-end reporting has a fixed two-hour processing window. Data Factory currently reaches on-premises SQL Server through a self-hosted integration runtime.", styles["BodyText"])])
    pdf.build(story)


def write_supporting_files() -> None:
    (OUT / "Fabric_Migration_Readiness_Assistant_Narration.txt").write_text(NARRATION, encoding="utf-8")
    (OUT / "Fabric_Migration_Readiness_Assistant_Demo_Script.txt").write_text(PRESENTER_NOTES + "\n\nVIDEO NARRATION\n" + NARRATION, encoding="utf-8")


def main() -> None:
    frames = save_frames()
    build_deck(frames)
    print(f"Generated {len(frames)} frames and presentation deck in {OUT}")


if __name__ == "__main__":
    main()
