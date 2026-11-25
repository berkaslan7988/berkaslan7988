#!/usr/bin/env python3
"""Build the art for the profile README: a header and one sheet per project.

Every image comes in a light and a dark version, picked by GitHub's theme
through <picture>. The SVGs embed their own font subsets and screenshots, so
they render the same everywhere GitHub shows an <img>.

    python tools/build.py              # use cached screenshots
    python tools/build.py --refresh    # download and capture them again

Screenshots come from each project's own repository (raw files) or, for web
apps, from a Playwright capture of the live site. They are cached in
tools/.cache, which git ignores.
"""
from __future__ import annotations

import argparse
import base64
import io
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

import uharfbuzz as hb
from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
CACHE = ROOT / "tools" / ".cache"
OUT = ROOT / "assets"

W = 840          # every image is 840 units wide; GitHub scales it to the column
PAD = 20


# --------------------------------------------------------------------------- theme

THEMES = {
    "light": dict(
        paper="#fbfaf8", ink="#16171a", soft="#37383d", muted="#6b6a66", faint="#9a978f",
        line="#dcd8cf", red="#cf2a1d", frame="#d3cfc5",
    ),
    "dark": dict(
        paper="#12161c", ink="#ebe9e4", soft="#c9cbcf", muted="#959ba4", faint="#68707a",
        line="#2b323c", red="#ff5d4f", frame="#323a45",
    ),
}


# --------------------------------------------------------------------------- fonts

@dataclass
class Face:
    file: str
    family: str
    weight: int

    def __post_init__(self) -> None:
        self.path = FONTS / self.file
        blob = hb.Blob.from_file_path(str(self.path))
        self.face = hb.Face(blob)
        self.font = hb.Font(self.face)
        self.upem = self.face.upem

    def _shape(self, text: str):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"kern": True, "liga": True})
        return buf

    def width(self, text: str, size: float, tracking: float = 0.0) -> float:
        """Advance width in px; tracking is CSS letter-spacing in em."""
        buf = self._shape(text)
        adv = sum(p.x_advance for p in buf.glyph_positions) / self.upem * size
        return adv + tracking * size * len(text)

    def ink(self, text: str, size: float) -> tuple[float, float]:
        """Left and right edge of the drawn glyphs, relative to the text origin."""
        buf = self._shape(text)
        infos, pos = buf.glyph_infos, buf.glyph_positions
        scale = size / self.upem
        first = self.font.get_glyph_extents(infos[0].codepoint)
        last = self.font.get_glyph_extents(infos[-1].codepoint)
        before_last = sum(p.x_advance for p in pos[:-1])
        left = first.x_bearing * scale
        right = (before_last + last.x_bearing + last.width) * scale
        return left, right

    def wrap(self, text: str, size: float, width: float) -> list[str]:
        lines: list[str] = []
        line = ""
        for word in text.split():
            trial = f"{line} {word}".strip()
            if line and self.width(trial, size) > width:
                lines.append(line)
                line = word
            else:
                line = trial
        if line:
            lines.append(line)
        return lines


FACES = {
    "cond": Face("SofiaSansCondensed-ExtraBold.ttf", "Sheet Cond", 800),
    "cond6": Face("SofiaSansCondensed-SemiBold.ttf", "Sheet Cond", 600),
    "sans": Face("SofiaSans-Regular.ttf", "Sheet Sans", 400),
    "sans6": Face("SofiaSans-SemiBold.ttf", "Sheet Sans", 600),
    "mono": Face("FragmentMono-Regular.ttf", "Sheet Mono", 400),
}
FALLBACK = {
    "cond": "'Arial Narrow',sans-serif", "cond6": "'Arial Narrow',sans-serif",
    "sans": "system-ui,sans-serif", "sans6": "system-ui,sans-serif", "mono": "ui-monospace,monospace",
}


def woff2(face: Face, chars: set[str]) -> str:
    font = TTFont(face.path)
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["kern", "liga", "calt"]
    sub = subset.Subsetter(options)
    sub.populate(text="".join(sorted(chars)) + " ")
    sub.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


# --------------------------------------------------------------------------- svg

def num(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Svg:
    def __init__(self, height: float, theme: str, title: str, background: bool):
        self.h = height
        self.t = THEMES[theme]
        self.title = title
        self.background = background
        self.parts: list[str] = []
        self.defs: list[str] = []
        self.css: list[str] = []
        self.used: dict[str, set[str]] = {k: set() for k in FACES}

    # primitives
    def text(self, x, y, s, face, size, fill, anchor="start", tracking=0.0, cls=""):
        self.used[face].update(s)
        attrs = [f'x="{num(x)}"', f'y="{num(y)}"', f'class="{(face + " " + cls).strip()}"',
                 f'font-size="{num(size)}"', f'fill="{fill}"']
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if tracking:
            attrs.append(f'letter-spacing="{num(tracking * size)}"')
        self.parts.append(f"<text {' '.join(attrs)}>{escape(s)}</text>")

    def spans(self, x, y, runs, size, anchor="start"):
        """One line made of (text, face, fill, tracking) runs."""
        out = []
        for s, face, fill, tracking in runs:
            self.used[face].update(s)
            ls = f' letter-spacing="{num(tracking * size)}"' if tracking else ""
            out.append(f'<tspan class="{face}" fill="{fill}"{ls}>{escape(s)}</tspan>')
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        self.parts.append(f'<text x="{num(x)}" y="{num(y)}" font-size="{num(size)}"{a}>{"".join(out)}</text>')

    def line(self, x1, y1, x2, y2, stroke, width=1.0, extra=""):
        self.parts.append(
            f'<line x1="{num(x1)}" y1="{num(y1)}" x2="{num(x2)}" y2="{num(y2)}" '
            f'stroke="{stroke}" stroke-width="{num(width)}"{extra}/>'
        )

    def raw(self, s: str) -> None:
        self.parts.append(s)

    def render(self) -> str:
        faces = []
        for key, chars in self.used.items():
            if not chars:
                continue
            f = FACES[key]
            faces.append(
                f"@font-face{{font-family:'{f.family}';font-weight:{f.weight};"
                f"src:url(data:font/woff2;base64,{woff2(f, chars)}) format('woff2')}}"
            )
        classes = [
            f".{k}{{font-family:'{f.family}',{FALLBACK[k]};font-weight:{f.weight}}}" for k, f in FACES.items()
        ]
        style = "".join(faces + classes + self.css)
        bg = (
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{num(self.h - 1)}" rx="10" '
            f'fill="{self.t["paper"]}" stroke="{self.t["line"]}"/>'
            if self.background else ""
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {num(self.h)}" '
            f'width="{W}" height="{num(self.h)}" role="img" aria-label="{escape(self.title)}">'
            f"<title>{escape(self.title)}</title><style>{style}</style>"
            f"<defs>{''.join(self.defs)}</defs>{bg}{''.join(self.parts)}</svg>"
        )


# --------------------------------------------------------------------------- content

@dataclass
class Note:
    term: str
    text: str


@dataclass
class Project:
    slug: str
    field: str
    stack: str
    title: str
    lede: str
    link: str
    shots: dict[str, str]           # theme -> source (URL or "live:<url>")
    crop: tuple[int, int, int, int]
    specs: list[tuple[str, str]] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    kind: str = "sheet"             # "sheet" (big, with notes) or "strip" (compact, no notes)
    live_js: str = ""               # run on the live page before capture
    live_init: str = ""             # run before the live page loads (e.g. seed localStorage)
    ready: bool = True              # False keeps it out of the README build
    no: str = ""                    # set from the order of PROJECTS
    side: str = "left"              # set so sheets alternate left/right


RAW = "https://raw.githubusercontent.com/berkaslan7988"

PROJECTS = [
    Project(
        slug="cysec", field="SECURITY · LEARNING",
        stack="REACT · CLOUDFLARE WORKERS · D1",
        title="CySec Academy",
        lede="A cybersecurity study site in Turkish and English: 105 guided lessons across "
             "fundamentals, red team, blue team and modern security, plus case labs in a "
             "terminal simulated in the browser.",
        link="cysec.aslanlabs.online",
        shots={t: f"{RAW}/CyberSec-Academy/main/assets/screens/landing-{t}.png" for t in THEMES},
        crop=(40, 0, 1400, 850),
        specs=[("LESSONS", "105"), ("SOURCE", "CLOSED"), ("STATUS", "LIVE")],
        notes=[
            Note("Progress seal",
                 "Each lesson is one loop in a four-ring seal, inked when you finish it."),
            Note("Four pages a lesson",
                 "The lesson, a deep dive with a worked case, hands-on practice, a check question."),
            Note("Case labs",
                 "Short incident briefs worked through in a simulated terminal."),
        ],
    ),
    Project(
        slug="sunless-crown", field="SOFTWARE · GAME",
        stack="GODOT 4.7 · GDSCRIPT · GLSL",
        title="Sunless Crown",
        lede="A top-down roguelite in English and Turkish. Nine procedural floors, three "
             "Wardens, and a flame-headed knight who is the only warm light in the game.",
        link="crown.aslanlabs.online",
        shots={t: f"{RAW}/2d-dungeon-crawler/main/docs/screens/game.png" for t in THEMES},
        crop=(64, 0, 1216, 720),
        specs=[("FLOORS", "9"), ("LICENCE", "MIT"), ("REV", "2.0.0")],
        notes=[
            Note("Ember light",
                 "Stone shifts from cold slate to warm brown by light level, dithered between steps."),
            Note("Drawn in code",
                 "Every sprite, tile and icon is a text grid in one 32-colour palette."),
            Note("Three Wardens",
                 "Bosses on floors 3, 6 and 9, each with two phases and their own lines."),
        ],
    ),
    Project(
        slug="netsentinel", field="SECURITY · MACHINE LEARNING",
        stack="PYTHON · SCAPY · SCIKIT-LEARN · PYTORCH",
        title="NetSentinel",
        lede="Real-time intrusion detection with a desktop SOC console. Live traffic "
             "becomes flows, three models score each one, and threats turn into quiet alerts.",
        link="github.com/berkaslan7988/NetSentinel",
        shots={t: f"{RAW}/NetSentinel/main/assets/screens/overview-{t}.png" for t in THEMES},
        crop=(0, 0, 1440, 900),
        specs=[("TESTS", "83"), ("LICENCE", "MIT"), ("REV", "2.0.0")],
        notes=[
            Note("Flow timeline",
                 "Ten minutes in 5 s buckets, threat flows stacked on top."),
            Note("Three detectors",
                 "RandomForest, IsolationForest and an autoencoder score every flow."),
            Note("Grouped alerts",
                 "One alert per source per minute, with a 0–100 risk score."),
        ],
    ),
    Project(
        slug="optik", field="SOFTWARE · EXAM PREP",
        stack="REACT · CLOUDFLARE WORKERS · D1",
        title="Optik",
        lede="A study site for exam week, in Turkish and English. Bring your questions "
             "as JSON or CSV, work through them section by section, then sit a timed mock exam.",
        link="optik.aslanlabs.online",
        shots={t: "live:https://optik.aslanlabs.online/" for t in THEMES},
        crop=(140, 100, 1300, 825),
        specs=[("LANGUAGES", "TR + EN"), ("SOURCE", "CLOSED"), ("STATUS", "LIVE")],
        notes=[
            Note("Your own question bank",
                 "JSON or CSV, multiple choice and open-ended, with notes beside them."),
            Note("Practice by section",
                 "Pick sections, retry only your mistakes, answer with the 1–5 or A–E keys."),
            Note("Timed mock exams",
                 "Net scoring where 4 or 3 wrong cancel 1 right, then a review of every miss."),
        ],
        live_init="localStorage.setItem('optik:display', JSON.stringify({theme: '{theme}', lang: 'en'}))",
    ),
    Project(
        slug="night-fair", field="SOFTWARE · BROWSER GAMES",
        stack="REACT · TYPESCRIPT · CLOUDFLARE",
        title="Night Fair",
        lede="A pocket fairground of 68 browser games in English and Turkish: arcade, "
             "puzzles, words, cards, and chess and draughts against a bot. Plays offline.",
        link="nf.aslanlabs.online",
        shots={t: f"{RAW}/night-fair/main/assets/screens/midway-{t}.png" for t in THEMES},
        crop=(40, 0, 1400, 850),
        specs=[("GAMES", "68"), ("SOURCE", "CLOSED"), ("STATUS", "LIVE")],
        notes=[
            Note("Ticket stubs",
                 "Every game is a roll ticket; a finished game prints a results ticket."),
            Note("Punch cards",
                 "Three goals per game, 204 in all, paid in tickets for the Prize Booth."),
            Note("New booths",
                 "Chess with four bot levels, Turkish draughts, Klondike and Mahjong."),
        ],
    ),
    Project(
        slug="caki", field="SECURITY · TERMINAL TOOLKIT",
        stack="PYTHON · TEXTUAL · ASYNCIO",
        title="Çakı",
        lede="A pocket knife for everyday security work: eleven small tools in one terminal "
             "app and one command, from port and site checks to log review and phishing.",
        link="github.com/berkaslan7988/Caki",
        shots={t: f"{RAW}/Caki/main/docs/screens/ports-{t}.png" for t in THEMES},
        crop=(380, 64, 1951, 1046),
        specs=[("TESTS", "96"), ("LICENCE", "MIT"), ("REV", "1.0.0")],
        notes=[
            Note("Shows its command",
                 "Every screen shows the exact CLI command it runs; c copies it."),
            Note("Findings say what to do",
                 "Banners checked against local CVE rules, each ending in a next step."),
            Note("Explains, not just scores",
                 "Phishing signals name their evidence; odd traffic names the value."),
        ],
    ),
    Project(
        slug="netscope", field="SECURITY · WINDOWS DESKTOP",
        stack="PYTHON · PYSIDE6 · WLAN API · SQLITE",
        title="NetScope",
        lede="A Wi-Fi field analyzer. It shows every network in range, the channels "
             "they fight over, and the ones that put you at risk.",
        link="github.com/berkaslan7988/NetScope",
        shots={t: f"{RAW}/NetScope/main/assets/screens/networks-{t}.png" for t in THEMES},
        crop=(236, 0, 1440, 752),
        specs=[("TESTS", "65"), ("LICENCE", "MIT"), ("REV", "1.0.0")],
        notes=[
            Note("Spectrum screen",
                 "Every access point by channel and signal strength."),
            Note("Security meter",
                 "Four steps from open to WPA3, plus evil-twin and rogue-AP checks."),
            Note("Readout",
                 "A dBm dial, a 60-second trace, and who shares the channel."),
        ],
    ),
    Project(
        slug="firlat", field="SOFTWARE · LOCAL NETWORK",
        stack="PYTHON STDLIB · REACT · SSE",
        title="Fırlat",
        lede="Send files and text across your own Wi-Fi. One computer runs it, and phones "
             "and laptops join from the browser: no app, no cloud, no size limit.",
        link="github.com/berkaslan7988/Firlat",
        shots={t: f"{RAW}/Firlat/main/assets/screens/board-{t}.png" for t in THEMES},
        crop=(40, 0, 1400, 850),
        specs=[("SERVER", "STDLIB"), ("LICENCE", "MIT"), ("REV", "2.0.0")],
        notes=[
            Note("Shipping labels",
                 "Every parcel shows its route, a stencilled type box and a barcode."),
            Note("Pair once",
                 "Scan the QR code or type the 6-digit code; the device is remembered."),
            Note("No size limit",
                 "Uploads stream to disk, downloads resume, and a batch comes as one ZIP."),
        ],
    ),
    Project(
        slug="person-ai", field="SOFTWARE · SELF-HOSTED",
        stack="PYTHON · REACT · SQLITE · OLLAMA",
        title="Person AI",
        lede="A self-hosted character roleplay chat. Make characters or import "
             "SillyTavern cards, pick a cloud or local model, and write the story together.",
        link="github.com/berkaslan7988/Person-AI",
        shots={t: f"{RAW}/Person-AI/main/docs/screens/landing-{t}.png" for t in THEMES},
        crop=(200, 20, 1600, 895),
        specs=[("PROVIDERS", "5"), ("SERVER", "STDLIB"), ("REV", "3.0.0")],
        notes=[
            Note("The cast",
                 "Four starter characters; make your own or drop in SillyTavern V2 cards."),
            Note("Any model",
                 "Gemini, Groq, DeepSeek and OpenRouter, or a local model through Ollama."),
            Note("Long-term memory",
                 "Older messages get summarised, and pinned notes are never forgotten."),
        ],
    ),
]

PERSON = dict(
    name="Berk Talha Aslan",
    dimension="SECURITY  +  SOFTWARE",
    tagline=("Security, AI and software development.",),
    block=[
        ("ROLE", "Developer, security"),
        ("STUDY", "Information Systems & Technologies, yr 4"),
        ("SCHOOL", "Sivas Cumhuriyet University"),
        ("BASED", "Balıkesir, Türkiye"),
    ],
    index_tags={
        "netscope": "WI-FI ANALYZER", "netsentinel": "NETWORK IDS",
        "cysec": "COURSE", "person-ai": "ROLEPLAY CHAT", "night-fair": "BROWSER ARCADE", "optik": "EXAM PREP",
        "firlat": "LAN FILE DROP", "sunless-crown": "ROGUELITE", "caki": "SECURITY TOOLKIT",
    },
)


# --------------------------------------------------------------------------- screenshots

def source(project: Project, theme: str, refresh: bool) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    src = project.shots[theme]
    path = CACHE / f"{project.slug}-{theme}.png"
    if path.exists() and not refresh:
        return path
    if src.startswith("live:"):
        capture(src[5:], theme, project.live_js.format(theme=theme), path, project.live_init.replace("{theme}", theme))
    else:
        with urllib.request.urlopen(src, timeout=60) as r:
            path.write_bytes(r.read())
    print(f"  fetched {path.name}")
    return path


def capture(url: str, theme: str, js: str, path: Path, init: str = "") -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900}, color_scheme=theme)
        if init:
            page.add_init_script(init)
        page.goto(url, wait_until="networkidle")
        if js:
            page.evaluate(js)
        page.wait_for_timeout(1200)
        page.screenshot(path=str(path))
        browser.close()


def image_uri(path: Path, crop, size) -> str:
    im = Image.open(path).convert("RGB").crop(crop)
    im = im.resize((round(size[0] * 2), round(size[1] * 2)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=84, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


# --------------------------------------------------------------------------- pieces

def top_strip(s: Svg, p: Project) -> None:
    t = s.t
    s.spans(PAD, 29, [(p.no, "mono", t["red"], 0.08), ("  /  " + p.field, "mono", t["muted"], 0.08)], 10.5)
    s.text(W - PAD, 29, p.stack, "mono", 10.5, t["muted"], anchor="end", tracking=0.08)
    s.line(PAD, 40.5, W - PAD, 40.5, t["line"])


def screenshot(s: Svg, p: Project, theme: str, box, refresh: bool) -> None:
    t = s.t
    x, y, w, h = box
    clip = f"clip-{p.slug}"
    s.defs.append(f'<clipPath id="{clip}"><rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="6"/></clipPath>')
    uri = image_uri(source(p, theme, refresh), p.crop, (w, h))
    s.raw(f'<image href="{uri}" x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" '
          f'clip-path="url(#{clip})" preserveAspectRatio="xMidYMid slice"/>')
    s.raw(f'<rect x="{num(x + .5)}" y="{num(y + .5)}" width="{num(w - 1)}" height="{num(h - 1)}" rx="6" '
          f'fill="none" stroke="{t["frame"]}"/>')


def footer(s: Svg, p: Project, y: float, total: int) -> None:
    """Bottom strip: sheet count on the left, the link on the right."""
    t = s.t
    s.line(PAD, y + .5, W - PAD, y + .5, t["line"])
    base = y + 25
    s.text(PAD, base, f"SHEET {p.no} OF {total:02d}", "mono", 10, t["faint"], tracking=0.08)
    s.spans(W - PAD, base, [(p.link, "mono", t["ink"], 0), ("  →", "mono", t["red"], 0)], 11.5, anchor="end")


def title_block(s: Svg, x: float, y_bottom: float, w: float, specs) -> None:
    """A drafting title block: one row per spec, closed by hairlines."""
    t = s.t
    row = 27
    y = y_bottom - row * len(specs)
    for label, value in specs:
        s.line(x, y + .5, x + w, y + .5, t["line"])
        s.text(x, y + 18, label, "mono", 9.5, t["faint"], tracking=0.1)
        s.text(x + w, y + 18, value, "mono", 11, t["ink"], anchor="end")
        y += row
    s.line(x, y + .5, x + w, y + .5, t["line"])


def sheet(p: Project, theme: str, refresh: bool, total: int) -> str:
    top, shot_w, shot_h, gap = 58, 520, 325, 28
    if p.side == "left":
        shot_x, col_x = PAD, PAD + shot_w + gap
    else:
        shot_x, col_x = W - PAD - shot_w, PAD
    col_w = W - 2 * PAD - shot_w - gap

    # notes run in three columns under the screenshot
    note_w = (W - 2 * PAD - 2 * 28) / 3
    note_lines = [FACES["sans"].wrap(n.text, 13.5, note_w) for n in p.notes]
    notes_top = top + shot_h + 32
    notes_h = 18 + 18 * max(len(ls) for ls in note_lines)
    foot_y = notes_top + notes_h + 10
    H = round(foot_y + 40)

    s = Svg(H, theme, f"{p.title}: {p.lede}", background=True)
    t = s.t
    top_strip(s, p)
    screenshot(s, p, theme, (shot_x, top, shot_w, shot_h), refresh)

    y = top + 32
    s.text(col_x - 1, y, p.title, "cond", 42, t["ink"], tracking=-0.005)
    y += 31
    for ln in FACES["sans"].wrap(p.lede, 15, col_w):
        s.text(col_x, y, ln, "sans", 15, t["soft"])
        y += 21
    block_top = top + shot_h - 27 * len(p.specs)
    if y - 21 + 16 > block_top:
        print(f"  ! {p.slug}: lede runs into the title block by {y - 21 + 16 - block_top:.0f}px")
    title_block(s, col_x, top + shot_h, col_w, p.specs)

    for i, (note, lines) in enumerate(zip(p.notes, note_lines)):
        x = PAD + i * (note_w + 28)
        s.text(x, notes_top, note.term, "sans6", 13.5, t["ink"])
        for j, ln in enumerate(lines):
            s.text(x, notes_top + 18 * (j + 1), ln, "sans", 13.5, t["muted"])
    footer(s, p, foot_y, total)
    return s.render()


def strip(p: Project, theme: str, refresh: bool, total: int) -> str:
    """A compact sheet: text and title block on the left, screenshot on the right."""
    top, shot_w, shot_h, gap = 58, 304, 190, 28
    shot_x = W - PAD - shot_w
    col_w = shot_x - gap - PAD
    foot_y = top + shot_h + 18
    H = foot_y + 40
    s = Svg(H, theme, f"{p.title}: {p.lede}", background=True)
    t = s.t
    top_strip(s, p)
    screenshot(s, p, theme, (shot_x, top, shot_w, shot_h), refresh)
    y = top + 32
    s.text(PAD - 1, y, p.title, "cond", 42, t["ink"], tracking=-0.005)
    y += 31
    for ln in FACES["sans"].wrap(p.lede, 15, col_w):
        s.text(PAD, y, ln, "sans", 15, t["soft"])
        y += 21
    block_top = top + shot_h - 27 * len(p.specs)
    if y - 21 + 16 > block_top:
        print(f"  ! {p.slug}: lede runs into the title block by {y - 21 + 16 - block_top:.0f}px")
    title_block(s, PAD, top + shot_h, col_w, p.specs)
    footer(s, p, foot_y, total)
    return s.render()


def header(theme: str, projects: list[Project]) -> str:
    H = 318
    s = Svg(H, theme, f"{PERSON['name']}. {' '.join(PERSON['tagline'])}", background=False)
    t = s.t
    cond, mono, sans = FACES["cond"], FACES["mono"], FACES["sans"]

    s.text(0, 18, "SHEET 00  /  INDEX", "mono", 10.5, t["muted"], tracking=0.08)
    s.text(W, 18, "BERKASLAN7988  ·  REV 2026.11", "mono", 10.5, t["muted"], anchor="end", tracking=0.08)
    s.line(0, 30.5, W, 30.5, t["line"])

    # name, sized to fill the left column
    name, size = PERSON["name"], 92
    while cond.width(name, size) > 520:
        size -= 1
    left, right = cond.ink(name, size)
    x0 = -left            # put the first stem exactly on x = 0
    y_name = 124
    s.text(x0, y_name, name, "cond", size, t["ink"], tracking=0)
    a, b = x0 + left, x0 + right

    # dimension line measuring the name
    y_dim = y_name + 32
    for x in (a, b):
        s.line(x, y_name + 12, x, y_dim + 9, t["red"], 1.1)
    label = PERSON["dimension"]
    lw = mono.width(label, 10.5, 0.1)
    mid = (a + b) / 2
    g0, g1 = mid - lw / 2 - 12, mid + lw / 2 + 12
    s.css.append(
        "@keyframes draw{from{stroke-dashoffset:var(--len)}to{stroke-dashoffset:0}}"
        "@keyframes show{from{opacity:0}to{opacity:1}}"
        ".dl{animation:draw .9s cubic-bezier(.25,.7,.2,1) .2s both}"
        ".dh{animation:show .3s ease 1s both}.dt{animation:show .5s ease .15s both}"
        "@media (prefers-reduced-motion:reduce){.dl,.dh,.dt{animation:none}}"
    )
    for x_from, x_to in ((g0, a + 1), (g1, b - 1)):
        length = abs(x_to - x_from)
        s.line(x_from, y_dim, x_to, y_dim, t["red"], 1.1,
               f' class="dl" stroke-dasharray="{num(length)}" style="--len:{num(length)}"')
    ah = 8.5
    s.raw(f'<path class="dh" d="M{num(a)} {y_dim}l{ah} -3v6z M{num(b)} {y_dim}l-{ah} -3v6z" fill="{t["red"]}"/>')
    s.text(mid, y_dim + 3.8, label, "mono", 10.5, t["red"], anchor="middle", tracking=0.1, cls="dt")

    # tagline: one line sits between the dimension line and the title block
    lines = PERSON["tagline"]
    if len(lines) == 1:
        s.text(0, 226, lines[0], "sans", 19, t["ink"])
    else:
        s.text(0, 212, lines[0], "sans", 19, t["ink"])
        s.text(0, 238, lines[1], "sans", 19, t["muted"])

    # sheet index
    xr = 574
    s.line(xr + .5, 46, xr + .5, 248, t["line"])
    xi = xr + 24
    s.text(xi, 62, "SHEETS", "mono", 10, t["faint"], tracking=0.1)
    # rows tighten as sheets are added, so the last one stays clear of the title block at y = 262
    y = 96
    step = min(33, (236 - y) / max(1, len(projects) - 1))
    for p in projects:
        tag = PERSON["index_tags"][p.slug]
        s.text(xi, y, p.no, "mono", 10.5, t["red"], tracking=0.06)
        s.text(xi + 28, y, p.title, "cond6", 20, t["ink"])
        nw = FACES["cond6"].width(p.title, 20)
        tw = mono.width(tag, 9.5, 0.06)
        s.text(W, y, tag, "mono", 9.5, t["muted"], anchor="end", tracking=0.06)
        s.line(xi + 28 + nw + 8, y - 3.5, W - tw - 8, y - 3.5, t["faint"], 1,
               ' stroke-dasharray="1 4" stroke-linecap="round"')
        y += step

    # title block
    yb = 262
    s.line(0, yb + .5, W, yb + .5, t["line"])
    s.line(0, H - .5, W, H - .5, t["line"])
    cells = PERSON["block"]
    widths = [max(mono.width(l, 9.5, 0.1), sans.width(v, 15)) for l, v in cells]
    spare = (W - sum(widths)) / len(cells)
    x = 0
    for i, ((label, value), w) in enumerate(zip(cells, widths)):
        cx = x if i == 0 else x + 14
        s.text(cx, yb + 21, label, "mono", 9.5, t["faint"], tracking=0.1)
        s.text(cx, yb + 44, value, "sans", 15, t["ink"])
        x += w + spare
        if i < len(cells) - 1:
            s.line(x - 6 + .5, yb + 1, x - 6 + .5, H - 1, t["line"])
            x -= 6
    return s.render()


# --------------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--refresh", action="store_true", help="download and capture the screenshots again")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    projects = [p for p in PROJECTS if p.ready]
    sheets = 0
    for i, p in enumerate(projects, 1):
        p.no = f"{i:02d}"
        if p.kind == "sheet":
            p.side = "left" if sheets % 2 == 0 else "right"
            sheets += 1
    for theme in THEMES:
        files = {f"header-{theme}.svg": header(theme, projects)}
        for p in projects:
            build = sheet if p.kind == "sheet" else strip
            files[f"{p.slug}-{theme}.svg"] = build(p, theme, args.refresh, len(projects))
        for name, svg in files.items():
            (OUT / name).write_text(svg, encoding="utf-8")
            print(f"{name:28} {len(svg.encode()) // 1024:4} KB")


if __name__ == "__main__":
    main()
