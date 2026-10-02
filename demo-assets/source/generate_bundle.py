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

    image, draw = base_frame("Hackathon prototype", "Fabric Migration Readiness\nand Optimisation Assistant")
    draw_text(draw, (90, 330), "From fragmented estates to an explainable Fabric migration plan", 31, color=MUTED, max_width=1050)
    for index, (label, color) in enumerate([("DISCOVER", TEAL), ("ASSESS", AMBER), ("MAP", ACCENT), ("SIZE", GREEN)]):
        x = 92 + index * 300
        rounded(draw, (x, 540, x + 250, 635), fill=SURFACE, outline=color, radius=18, width=3)
        draw_text(draw, (x + 28, 570), label, 25, bold=True, color=color)
    draw_text(draw, (92, 895), "Microsoft Fabric | CSA repeatable assessment workflow", 24, color=MUTED)
    frames.append(FRAMES / "00-title.png"); image.save(frames[-1])

    image, draw = base_frame("The problem", "Migration decisions are fragmented", "Customers do not arrive with a single platform or a single migration path.")
    technologies = ["Power BI", "SSAS / AAS", "Azure SQL", "Synapse", "Databricks", "ADF", "Logic Apps", "Spark", "Runbooks"]
    for i, technology in enumerate(technologies):
        row, col = divmod(i, 3)
        x, y = 90 + col * 365, 320 + row * 120
        rounded(draw, (x, y, x + 320, y + 82), fill=SURFACE, outline=BORDER, radius=16)
        draw_text(draw, (x + 24, y + 25), technology, 23, bold=True)
    rounded(draw, (1240, 302, 1828, 790), fill="FFF8FA", outline=ACCENT, radius=24, width=3)
    draw_text(draw, (1290, 345), "CSA challenge", 24, bold=True, color=ACCENT)
    bullets = ["Ask the right follow-up questions", "Find blockers and redesign needs", "Map to Fabric target patterns", "Estimate capacity pressure", "Produce a customer-ready answer"]
    y = 425
    for bullet in bullets:
        draw.ellipse((1294, y + 7, 1312, y + 25), fill=f"#{ACCENT}")
        y = draw_text(draw, (1330, y), bullet, 23, max_width=430, spacing=6) + 20
    frames.append(FRAMES / "01-problem.png"); image.save(frames[-1])

    image, draw = base_frame("The solution", "Three intake paths. One governed assessment.", "Facts remain explicit; unknowns stay unknown until the CSA confirms them.")
    cards = [
        ("Excel / CSV", "Inventory template\nBrowser-ready CSV export", TEAL),
        ("PDF", "CLI or Copilot extraction\nHuman confirmation required", AMBER),
        ("Manual", "Guided customer discovery\nWorkload-by-workload facts", ACCENT),
    ]
    for i, (title, body, color) in enumerate(cards):
        x = 86 + i * 430
        rounded(draw, (x, 310, x + 380, 580), fill=SURFACE, outline=color, radius=24, width=3)
        draw_text(draw, (x + 30, 350), title, 30, bold=True, color=color)
        draw_text(draw, (x + 30, 430), body, 22, color=MUTED, max_width=315)
        draw.line((x + 380, 445, x + 418, 445), fill=f"#{BORDER}", width=5)
    rounded(draw, (1385, 300, 1832, 590), fill="FFF8FA", outline=ACCENT, radius=28, width=4)
    draw_text(draw, (1430, 355), "Assistant", 34, bold=True, color=ACCENT)
    draw_text(draw, (1430, 435), "Discovery\nRules engine\nLearn evidence\nSpecialist skills", 24, color=MUTED)
    draw.line((960, 720, 960, 820), fill=f"#{ACCENT}", width=5)
    rounded(draw, (430, 820, 1490, 980), fill=SURFACE, outline=GREEN, radius=24, width=3)
    draw_text(draw, (485, 862), "Customer-ready output: readiness + target patterns + risks + next steps + SKU inputs", 27, bold=True, color=GREEN, max_width=950)
    frames.append(FRAMES / "02-inputs.png"); image.save(frames[-1])

    for frame_name, kicker, title, subtitle, shot, callouts in [
        ("03-discovery.png", "Prototype step 1", "Capture customer context", "Outcomes, constraints, region, users, concurrency, and preferred migration strategy.", "01-discovery.png", ["Manual customer context", "Upload Excel-exported CSV", "PDF handoff to Copilot or CLI"]),
        ("04-inventory.png", "Prototype step 2", "Build the estate inventory", "Imported facts remain unconfirmed until workload-specific discovery is complete.", "02-workloads.png", ["Needs Discovery by default", "Edit scale and dependencies", "Start adaptive AI discovery"]),
        ("05-assessment.png", "Prototype step 3", "Map, explain, and challenge", "Every workload exposes its Fabric pattern, blockers, optimisations, and open questions.", "03-assessment.png", ["Directional readiness profile", "Fabric target pattern", "Blockers, actions, and questions"]),
        ("06-summary.png", "Prototype step 4", "Deliver an executive-ready summary", "Readiness position, target patterns, next steps, and directional SKU Estimator inputs.", "04-summary.png", ["Executive migration position", "Prioritised next steps", "Capacity-sizing inputs"]),
    ]:
        image, draw = base_frame(kicker, title, subtitle)
        rounded(draw, (85, 270, 575, 1020), fill=SURFACE, outline=BORDER, radius=24)
        paste_mobile_shot(image, shot, (115, 292, 545, 998))
        draw_text(draw, (650, 300), "WHAT THE CSA SEES", 22, bold=True, color=ACCENT)
        for index, callout in enumerate(callouts, start=1):
            y = 365 + (index - 1) * 185
            rounded(draw, (650, y, 1815, y + 140), fill=SURFACE, outline=[TEAL, AMBER, GREEN][index - 1], radius=20, width=3)
            draw.ellipse((685, y + 42, 741, y + 98), fill=f"#{[TEAL, AMBER, GREEN][index - 1]}")
            draw_text(draw, (704, y + 53), str(index), 22, bold=True, color="FFFFFF")
            draw_text(draw, (780, y + 48), callout, 28, bold=True, max_width=970)
        draw_text(draw, (650, 955), "Responsive browser prototype • customer data remains local", 21, color=MUTED)
        frames.append(FRAMES / frame_name); image.save(frames[-1])

    image, draw = base_frame("Why it matters", "A repeatable assessment, not a one-off opinion")
    outcomes = [
        ("FASTER", "Start with an inventory and focus the conversation", TEAL),
        ("EXPLAINABLE", "Trace findings to customer facts and explicit rules", ACCENT),
        ("ACTIONABLE", "Separate migration-ready, optimise, redesign, and retain", AMBER),
        ("SIZABLE", "Collect inputs needed for the Fabric SKU Estimator", GREEN),
    ]
    for i, (label, body, color) in enumerate(outcomes):
        col, row = i % 2, i // 2
        x, y = 88 + col * 900, 300 + row * 260
        rounded(draw, (x, y, x + 820, y + 205), fill=SURFACE, outline=color, radius=22, width=3)
        draw_text(draw, (x + 34, y + 35), label, 24, bold=True, color=color)
        draw_text(draw, (x + 34, y + 90), body, 25, max_width=735)
    draw_text(draw, (90, 915), "Next: pilot on real estates | expand native imports | connect measured capacity telemetry", 27, bold=True, color=ACCENT)
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
        "Introduce the prototype and the outcome: a repeatable Fabric migration assessment.",
        "Explain the fragmented estate and why ad hoc assessment is slow and inconsistent.",
        "Show the three supported intake routes and the governed assessment flow.",
        "The discovery screen captures business context and measurable workload pressure.",
        "Spreadsheet inventory is saved as CSV for browser upload; PDF uses Copilot or CLI; manual entry is available.",
        "The engine maps workloads and explains blockers, optimisation actions, and open questions.",
        "The summary is customer-ready and includes directional inputs for the SKU Estimator, not a capacity quote.",
        "Close on impact and the path from hackathon prototype to a validated engagement tool.",
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
    build_inputs()
    write_supporting_files()
    print(f"Generated {len(frames)} frames and presentation assets in {OUT}")


if __name__ == "__main__":
    main()
