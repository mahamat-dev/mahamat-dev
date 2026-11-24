#!/usr/bin/env python3
"""Generates the SVGs in assets/. Edit the data below, run `python3 build.py`, commit."""
import base64
import re
from html import escape
from math import ceil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "assets"
# Geist (SIL OFL, see fonts/OFL.txt), embedded so text renders the same on every OS.
FONT = base64.b64encode((ROOT / "fonts/geist-latin-wght-normal.woff2").read_bytes()).decode()
SURFACE, RAISED, LINE = "#0d1117", "#151b23", "#262c36"
TEXT, SOFT, MUTED, ACCENT = "#f0f3f6", "#b7bfc8", "#7d8590", "#3fb950"

NAME = "Mahamat Ali Youssouf."
ROLES = ["Full-stack web developer", "iOS apps in SwiftUI", "Fast sites with Next.js", "Clean, animated interfaces"]

PROJECTS = [
    dict(slug="deoli", title="Deoli", lang="Swift · iOS",
         desc=["A focused reminder app: capture tasks fast,", "sort by priority and category, stay on top."],
         tags=["SwiftUI", "XCTest", "iOS"]),
    dict(slug="cgm", title="Chad Global Market", lang="TypeScript · Web",
         desc=["Website for a general goods trading company,", "with product filtering and WhatsApp contact."],
         tags=["React 19", "Vite", "Tailwind v4", "React Query"]),
    dict(slug="madian", title="Madian Foundation", lang="TypeScript · Web",
         desc=["Multilingual site for the Madian Foundation,", "with smooth motion and localized content."],
         tags=["Next.js", "next-intl", "Framer Motion"]),
    dict(slug="nouahlabs", title="Nouah Labs", lang="TypeScript · Web",
         desc=["Landing page for Nouah Labs, built for speed", "with motion-driven sections."],
         tags=["Next.js", "Motion", "Tailwind"]),
    dict(slug="indie", title="Indie Landing", lang="TypeScript · Web",
         desc=["A lean landing page starter for indie", "products, on the Next.js App Router."],
         tags=["Next.js", "React", "TypeScript"]),
    dict(slug="pokedex", title="Pokédex", lang="TypeScript · Web",
         desc=["Browse and search Pokémon with a fast,", "typed client for the public PokéAPI."],
         tags=["TypeScript", "React", "REST"]),
]

# (label, Simple Icons file in logos/ or None when the tool has no logo there)
STACK = [
    [("TypeScript", "typescript"), ("React", "react"), ("Next.js", "nextdotjs"), ("Swift", "swift"),
     ("SwiftUI", "swift"), ("React Native", "react"), ("Expo", "expo")],
    [("Tailwind CSS", "tailwindcss"), ("Vite", "vite"), ("Framer Motion", "framer"), ("React Query", "reactquery"),
     ("Zustand", None), ("next-intl", None), ("Contentful", "contentful"), ("Git", "git")],
]


def svg(w, h, label, style, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'fill="none" role="img" aria-label="{escape(label)}"><style>'
            f"@font-face{{font-family:G;font-weight:100 900;src:url(data:font/woff2;base64,{FONT}) format('woff2')}}"
            f"text{{font-family:G,ui-sans-serif,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}}"
            f'{style}</style>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="{SURFACE}" stroke="{LINE}"/>'
            f'{body}</svg>\n')


def header():
    W, H, n = 1200, 300, len(ROLES)
    hold = 100 / n
    photo = base64.b64encode((ROOT / "photo/avatar.jpg").read_bytes()).decode()
    roles = "".join(f'<text x="64" y="210" class="role{" r0" if i == 0 else ""}" style="animation-delay:{i * 3}s">'
                    f'{escape(r)}</text>' for i, r in enumerate(ROLES))
    style = f"""
.name{{font-weight:620;font-size:78px;letter-spacing:-2.8px;fill:{TEXT}}}
.role{{font-weight:400;font-size:30px;letter-spacing:-.5px;fill:{SOFT};transform:translateY(44px);
animation:roll {n * 3}s cubic-bezier(.65,0,.35,1) infinite both}}
@keyframes roll{{0%{{transform:translateY(44px)}}{hold * .14:.1f}%,{hold * .86:.1f}%{{transform:none}}{hold:.1f}%,100%{{transform:translateY(-44px)}}}}
@media (prefers-reduced-motion:reduce){{.role{{animation:none}}.r0{{transform:none}}}}"""
    body = f"""<defs><clipPath id="band"><rect x="0" y="178" width="900" height="50"/></clipPath>
<clipPath id="ph"><rect x="916" y="34" width="232" height="232" rx="14"/></clipPath></defs>
<text x="60" y="150" class="name">{escape(NAME)}</text>
<g clip-path="url(#band)">{roles}</g>
<image href="data:image/jpeg;base64,{photo}" x="916" y="34" width="232" height="232" preserveAspectRatio="xMidYMid slice" clip-path="url(#ph)"/>"""
    return svg(W, H, f"{NAME} {ROLES[0]}", style, body)


def project(i, p):
    W, H = 760, 180
    desc = "".join(f'<text x="72" y="{92 + k * 26}" class="d">{escape(line)}</text>' for k, line in enumerate(p["desc"]))
    style = f"""
.i{{font-weight:500;font-size:15px;fill:{MUTED};font-variant-numeric:tabular-nums}}
.t{{font-weight:600;font-size:28px;letter-spacing:-.7px;fill:{TEXT}}}
.m{{font-weight:450;font-size:15px;fill:{MUTED}}}
.d{{font-weight:400;font-size:17.5px;fill:{SOFT}}}"""
    body = f"""<text x="32" y="53" class="i">{i:02d}</text>
<text x="72" y="54" class="t">{escape(p["title"])}</text>
<text x="{W - 64}" y="52" text-anchor="end" class="m">{escape(p["lang"])}</text>
<path d="M{W - 50} 52 {W - 36} 38m-11 0h11v11" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
{desc}
<text x="72" y="150" class="m">{escape("  ·  ".join(p["tags"]))}</text>"""
    return svg(W, H, f'{p["title"]}: {" ".join(p["desc"])}', style, body)


def logo(slug):
    d = re.search(r'\sd="([^"]+)"', (ROOT / "logos" / f"{slug}.svg").read_text()).group(1)
    return f'<path transform="translate(20 17) scale(.9167)" d="{escape(d)}" fill="{TEXT}"/>'


def label_width(s):
    # Geist 500 at 17px, measured in a browser; good to a few px, which the tile padding absorbs.
    return sum(4.2 if c in "ijlI." else 4.6 if c == " " else 6.1 if c in "frt1-" else
               14.8 if c in "mwMW" else 11.2 if c.isupper() else 9.5 for c in s)


def stack():
    W, H, css, body = 880, 182, "", ""
    for r, row in enumerate(STACK):
        tiles, x = [], 0
        for label, slug in row:
            tx = 54 if slug else 22
            w = round(tx + label_width(label) + 22)
            tiles.append(f'<g transform="translate({x} 0)"><rect x=".5" y=".5" width="{w - 1}" height="55" rx="12" '
                         f'fill="{RAISED}" stroke="{LINE}"/>{logo(slug) if slug else ""}'
                         f'<text x="{tx}" y="34" class="l">{escape(label)}</text></g>')
            x += w + 12
        frm, to = (0, -x) if r % 2 == 0 else (-x, 0)
        css += (f".m{r}{{animation:m{r} {x / 28:.0f}s linear infinite}}"
                f"@keyframes m{r}{{from{{transform:translateX({frm}px)}}to{{transform:translateX({to}px)}}}}")
        reps = "".join(f'<use href="#t{r}" x="{k * x}"/>' for k in range(1, ceil(W / x) + 1))
        body += (f'<g transform="translate(0 {28 + r * 70})"><g class="m{r}"><g id="t{r}">{"".join(tiles)}</g>'
                 f'{reps}</g></g>')
    style = (f".l{{font-weight:500;font-size:17px;letter-spacing:-.2px;fill:{SOFT}}}{css}"
             "@media (prefers-reduced-motion:reduce){[class^=m]{animation:none}}")
    defs = (f'<defs><linearGradient id="f" x1="0" x2="1"><stop stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".07" stop-color="#fff"/><stop offset=".93" stop-color="#fff"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="fade"><rect width="{W}" height="{H}" fill="url(#f)"/></mask></defs>')
    names = ", ".join(label for row in STACK for label, _ in row)
    return svg(W, H, names, style, f'{defs}<g mask="url(#fade)">{body}</g>')


if __name__ == "__main__":
    (OUT / "projects").mkdir(parents=True, exist_ok=True)
    (OUT / "header.svg").write_text(header())
    (OUT / "stack.svg").write_text(stack())
    for i, p in enumerate(PROJECTS, 1):
        (OUT / "projects" / f"{p['slug']}.svg").write_text(project(i, p))
    print(f"wrote header, stack and {len(PROJECTS)} project rows to {OUT}")
