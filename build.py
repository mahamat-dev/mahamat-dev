#!/usr/bin/env python3
"""Builds README.md and assets/profile.svg (the whole profile as one poster) from profile.json and languages.json.

    python3 build.py              # rebuild
    python3 build.py --refresh    # recount languages from GitHub first (needs the gh CLI, logged in)
"""
import base64
import collections
import json
import re
import subprocess
import sys
from html import escape
from math import ceil, pi
from pathlib import Path

ROOT = Path(__file__).parent
P = json.loads((ROOT / "profile.json").read_text())
# Geist (SIL OFL, see fonts/OFL.txt), embedded so text renders the same on every OS.
FONT = base64.b64encode((ROOT / "fonts/geist-latin-wght-normal.woff2").read_bytes()).decode()

W, PAD = 880, 40
SAND, CARD, LINE = "#f3e9d8", "#fffbf3", "#e6d9c6"
INK, SOFT, MUTED = "#2b2621", "#574f46", "#877c6e"
# Sahel pastels: fill, and the darker ink that reads on it.
TONE = {
    "clay": ("#f2b9a0", "#8c3b1f"), "sage": ("#c7dbb9", "#3f5b2e"), "sky": ("#c0d8eb", "#2a4f6e"),
    "ochre": ("#f3d28b", "#7a5410"), "teal": ("#b6ddd6", "#1f5f57"), "dune": ("#e5cba8", "#6e4e2b"),
    "steel": ("#cbd3df", "#3b4a63"), "olive": ("#d9d9a3", "#5a5c1e"), "apricot": ("#f7c59f", "#8a4b14"),
    "stone": ("#ddd5c9", "#5a5249"),
}
LANG_TONE = {"TypeScript": "sky", "JavaScript": "ochre", "HTML": "clay", "CSS": "steel", "Dart": "teal",
             "Java": "olive", "Python": "sage", "Swift": "dune"}
PROJECT_TONES = ["clay", "sage", "sky", "ochre", "teal", "dune"]
BRAND = {"typescript": "#3178c6", "react": "#58c4dc", "swift": "#f05138", "tailwindcss": "#06b6d4", "vite": "#646cff",
         "framer": "#0055ff", "reactquery": "#ff4154", "contentful": "#2478cc", "git": "#f05032", "flutter": "#02569b",
         "dart": "#0175c2", "javascript": "#e8c900", "html5": "#e34f26", "css": "#663399", "nodedotjs": "#5fa04e",
         "mongodb": "#47a248", "graphql": "#e10098", "firebase": "#dd2c00", "ionic": "#3880ff", "supabase": "#3ecf8e",
         "python": "#3776ab", "clerk": "#6c47ff"}  # anything else is drawn in INK


def text_width(s, size=17):
    # Geist 500, measured in a browser at 17px; good to a few px.
    return size / 17 * sum(4.2 if c in "ijlI." else 4.6 if c == " " else 6.1 if c in "frt1-" else
                           14.8 if c in "mwMW" else 11.2 if c.isupper() or c.isdigit() else 9.5 for c in s)


def rich(line):
    """'**bold**' segments become ink-coloured semibold tspans."""
    return "".join(f'<tspan class="b">{escape(part)}</tspan>' if i % 2 else escape(part)
                   for i, part in enumerate(line.split("**")))


def plain(line):
    return line.replace("**", "")


def header(y):
    roles, n = P["roles"], len(P["roles"])
    hold = 100 / n
    first, last = P["name"].rsplit(" ", 1)
    photo = base64.b64encode((ROOT / P["photo"]).read_bytes()).decode()
    since = f"Developer since {P['since']}"
    sage, sage_ink = TONE["sage"]
    rolls = "".join(f'<text x="{PAD}" y="{y + 276}" class="role{" r0" if i == 0 else ""}" '
                    f'style="animation-delay:{i * 3}s">{escape(r)}</text>' for i, r in enumerate(roles))
    css = f"""
.chip{{font-weight:600;font-size:14px;fill:{sage_ink}}}
.name{{font-weight:720;font-size:64px;letter-spacing:-2.2px;fill:{INK}}}
.role{{font-weight:450;font-size:26px;letter-spacing:-.3px;fill:{SOFT};transform:translateY(40px);
animation:roll {n * 3}s cubic-bezier(.65,0,.35,1) infinite both}}
@keyframes roll{{0%{{transform:translateY(40px)}}{hold * .14:.1f}%,{hold * .86:.1f}%{{transform:none}}{hold:.1f}%,100%{{transform:translateY(-40px)}}}}
@media (prefers-reduced-motion:reduce){{.r0{{transform:none}}}}
.f1{{animation:f1 8s ease-in-out infinite alternate}}.f2{{animation:f2 10s ease-in-out infinite alternate}}
.f3{{animation:f3 6s ease-in-out infinite alternate}}.f4{{animation:f4 9s ease-in-out infinite alternate}}
.sticker{{animation:f3 6s ease-in-out infinite alternate}}
.f1,.f2,.f3,.f4,.sticker{{transform-box:fill-box;transform-origin:center}}
@keyframes f1{{to{{transform:translate(-8px,10px)}}}}@keyframes f2{{to{{transform:translate(6px,-8px) rotate(10deg)}}}}
@keyframes f3{{to{{transform:translateY(-6px)}}}}@keyframes f4{{to{{transform:translate(-6px,-6px)}}}}"""
    body = f"""<defs><clipPath id="band"><rect x="0" y="{y + 244}" width="600" height="44"/></clipPath>
<clipPath id="ph"><rect x="8" y="8" width="196" height="196" rx="15"/></clipPath>
<filter id="lift" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#6b4a22" flood-opacity=".2"/></filter></defs>
<g class="f1"><circle cx="836" cy="{y + 300}" r="124" fill="{TONE['clay'][0]}"/></g>
<g class="f2"><rect x="560" y="{y + 30}" width="104" height="104" rx="28" transform="rotate(14 612 {y + 82})" fill="{sage}"/></g>
<g class="f3"><circle cx="846" cy="{y + 48}" r="18" fill="{TONE['ochre'][0]}"/></g>
<g class="f4"><circle cx="596" cy="{y + 266}" r="24" stroke="{TONE['sky'][0]}" stroke-width="10"/></g>
<g transform="translate(634 {y + 50}) rotate(-5 106 106)"><g class="sticker" filter="url(#lift)">
<rect width="212" height="212" rx="22" fill="#ffffff"/>
<image href="data:image/jpeg;base64,{photo}" x="8" y="8" width="196" height="196" preserveAspectRatio="xMidYMid slice" clip-path="url(#ph)"/>
</g></g>
<rect x="{PAD}" y="{y + 48}" width="{text_width(since, 14) * 1.05 + 32:.0f}" height="32" rx="16" fill="{sage}"/>
<text x="{PAD + 16}" y="{y + 69}" class="chip">{escape(since)}</text>
<text x="{PAD - 3}" y="{y + 156}" class="name">{escape(first)}</text>
<text x="{PAD - 3}" y="{y + 222}" class="name">{escape(last)}</text>
<g clip-path="url(#band)">{rolls}</g>"""
    return body, css, 320


def intro(y):
    lines = "".join(f'<text x="{PAD}" y="{y + 24 + i * 27}" class="intro">{rich(l)}</text>' for i, l in enumerate(P["intro"]))
    css = f".intro{{font-weight:420;font-size:17px;fill:{SOFT}}}.b{{font-weight:650;fill:{INK}}}"
    return lines, css, 24 + len(P["intro"]) * 27 + 20


def title(y, text):
    return f'<text x="{PAD}" y="{y + 30}" class="h">{escape(text)}</text>', 50


def projects(y):
    cw, ch, gap, out = W - 2 * PAD, 152, 14, []
    for i, p in enumerate(P["projects"]):
        fill, ink = TONE[PROJECT_TONES[i % len(PROJECT_TONES)]]
        top = y + i * (ch + gap)
        desc = "".join(f'<text x="{PAD + 84}" y="{top + 84 + k * 23}" class="pd">{escape(l)}</text>'
                       for k, l in enumerate(p["desc"]))
        out.append(f"""<g>
<rect x="{PAD}" y="{top}" width="{cw}" height="{ch}" rx="18" fill="{CARD}" stroke="{LINE}" stroke-width="1.5"/>
<rect x="{PAD + 22}" y="{top + 22}" width="44" height="44" rx="12" fill="{fill}"/>
<text x="{PAD + 44}" y="{top + 49.5}" text-anchor="middle" class="pi" fill="{ink}">{i + 1:02d}</text>
<text x="{PAD + 84}" y="{top + 52}" class="pt">{escape(p["title"])}</text>
<text x="{W - PAD - 70}" y="{top + 49}" text-anchor="end" class="pm">{escape(p["lang"])}</text>
<rect x="{W - PAD - 58}" y="{top + 26}" width="36" height="36" rx="11" fill="{fill}"/>
<path d="M{W - PAD - 45} {top + 49}l10-10m-8 0h8v8" stroke="{ink}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
{desc}
<text x="{PAD + 84}" y="{top + 94 + len(p["desc"]) * 23}" class="pm">{escape("  ·  ".join(p["tags"]))}</text>
</g>""")
    css = f"""
.pi{{font-weight:700;font-size:16px;font-variant-numeric:tabular-nums}}
.pt{{font-weight:700;font-size:24px;letter-spacing:-.6px;fill:{INK}}}
.pm{{font-weight:500;font-size:14px;fill:{MUTED}}}
.pd{{font-weight:420;font-size:16.5px;fill:{SOFT}}}"""
    return "".join(out), css, len(P["projects"]) * (ch + gap) - gap


def languages(y):
    data = json.loads((ROOT / "languages.json").read_text())
    langs = data["langs"][:7]
    if len(data["langs"]) > 7:
        langs.append(["Other", sum(c for _, c in data["langs"][7:])])
    total, H = sum(c for _, c in langs), 268
    cx, cy, r, sw, gap = PAD + 130, y + 126, 84, 34, 4
    C = 2 * pi * r
    arcs, legend, start = [], [], 0
    for i, (lang, count) in enumerate(langs):
        fill, _ = TONE[LANG_TONE.get(lang, "stone")]
        length = C * count / total
        arcs.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{fill}" stroke-width="{sw}" '
                    f'stroke-dasharray="{max(length - gap, 1):.2f} {C:.2f}" stroke-dashoffset="{-start:.2f}" '
                    f'transform="rotate(-90 {cx} {cy})" class="seg" style="animation-delay:{.2 + i * .09:.2f}s"/>')
        start += length
        col, row = divmod(i, 4)
        x, ly = PAD + 290 + col * 260, y + 62 + row * 46
        legend.append(f'<rect x="{x}" y="{ly - 19}" width="24" height="24" rx="7" fill="{fill}"/>'
                      f'<text x="{x + 38}" y="{ly - 1}" class="ln">{escape(lang)}</text>'
                      f'<text x="{x + 220}" y="{ly - 1}" text-anchor="end" class="lc">{count}</text>')
    css = f"""
.seg{{animation:grow 1s cubic-bezier(.3,.7,.2,1) both}}
@keyframes grow{{from{{stroke-dasharray:0 {C:.2f}}}}}
.big{{font-weight:720;font-size:46px;letter-spacing:-1.4px;fill:{INK}}}
.sub{{font-weight:500;font-size:14px;fill:{MUTED}}}
.ln{{font-weight:550;font-size:18px;fill:{INK}}}
.lc{{font-weight:500;font-size:16px;fill:{MUTED};font-variant-numeric:tabular-nums}}
.note{{font-weight:450;font-size:13px;fill:{MUTED}}}"""
    body = (f'<rect x="{PAD}" y="{y}" width="{W - 2 * PAD}" height="{H}" rx="18" fill="{CARD}" stroke="{LINE}" stroke-width="1.5"/>'
            f'{"".join(arcs)}<text x="{cx}" y="{cy + 10}" text-anchor="middle" class="big">{data["repos"]}</text>'
            f'<text x="{cx}" y="{cy + 34}" text-anchor="middle" class="sub">repos</text>{"".join(legend)}'
            f'<text x="{PAD + 290}" y="{y + H - 28}" class="note">Repos using each language, from my public, non-fork repos.</text>')
    return body, css, H


def logo(slug):
    d = re.search(r'\sd="([^"]+)"', (ROOT / "logos" / f"{slug}.svg").read_text()).group(1)
    return f'<path transform="translate(18 16) scale(.9167)" d="{escape(d)}" fill="{BRAND.get(slug, INK)}"/>'


def toolbox(y):
    H, css, rows = 160, "", ""
    for r, row in enumerate(P["stack"]):
        tiles, x = [], 0
        for label, slug in row:
            tx = 52 if slug else 20
            w = round(tx + text_width(label) + 20)
            tiles.append(f'<g transform="translate({x} 0)"><rect x=".75" y=".75" width="{w - 1.5}" height="52.5" rx="15" '
                         f'fill="#ffffff" stroke="{LINE}" stroke-width="1.5"/>{logo(slug) if slug else ""}'
                         f'<text x="{tx}" y="32.5" class="tl">{escape(label)}</text></g>')
            x += w + 12
        frm, to = (0, -x) if r % 2 == 0 else (-x, 0)
        css += (f".m{r}{{animation:m{r} {x / 26:.0f}s linear infinite}}"
                f"@keyframes m{r}{{from{{transform:translateX({frm}px)}}to{{transform:translateX({to}px)}}}}")
        reps = "".join(f'<use href="#t{r}" x="{k * x}"/>' for k in range(1, ceil(W / x) + 1))
        rows += f'<g transform="translate({PAD} {y + 20 + r * 66})"><g class="m{r}"><g id="t{r}">{"".join(tiles)}</g>{reps}</g></g>'
    css += f".tl{{font-weight:500;font-size:17px;letter-spacing:-.2px;fill:{INK}}}"
    body = (f'<defs><clipPath id="tb"><rect x="{PAD}" y="{y}" width="{W - 2 * PAD}" height="{H}" rx="18"/></clipPath>'
            f'<linearGradient id="fg" x1="0" x2="1"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".06" stop-color="#fff"/>'
            f'<stop offset=".94" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="fade"><rect x="{PAD}" y="{y}" width="{W - 2 * PAD}" height="{H}" fill="url(#fg)"/></mask></defs>'
            f'<rect x="{PAD}" y="{y}" width="{W - 2 * PAD}" height="{H}" rx="18" fill="{CARD}" stroke="{LINE}" stroke-width="1.5"/>'
            f'<g clip-path="url(#tb)" mask="url(#fade)"><g transform="translate(-{PAD} 0)">{rows}</g></g>')
    return body, css, H


def poster():
    parts, css, y = [], [f".h{{font-weight:700;font-size:22px;letter-spacing:-.4px;fill:{INK}}}"], 0
    for section in (header, intro):
        b, c, h = section(y)
        parts.append(b), css.append(c)
        y += h
    for label, section in (("Featured projects", projects), ("Languages", languages), ("Toolbox", toolbox)):
        t, th = title(y, label)
        b, c, h = section(y + th)
        parts += [t, b]
        css.append(c)
        y += th + h + 34
    H = y + 6
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" '
            f'role="img" aria-label="{escape(alt())}"><style>'
            f"@font-face{{font-family:G;font-weight:100 900;src:url(data:font/woff2;base64,{FONT}) format('woff2')}}"
            f"text{{font-family:G,ui-sans-serif,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}}"
            f"{''.join(css)}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>"
            f'<defs><clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath></defs>'
            f'<g clip-path="url(#frame)"><rect width="{W}" height="{H}" fill="{SAND}"/>{"".join(parts)}</g></svg>\n')


def alt():
    langs = json.loads((ROOT / "languages.json").read_text())["langs"]
    return (f"{P['name']} Developer since {P['since']}. {' / '.join(P['roles'])}. {' '.join(plain(l) for l in P['intro'])} "
            f"Projects: {'; '.join(p['title'] + ': ' + ' '.join(p['desc']).rstrip('.') for p in P['projects'])}. "
            f"Languages: {', '.join(f'{l} {c}' for l, c in langs)}. "
            f"Toolbox: {', '.join(label for row in P['stack'] for label, _ in row)}.")


def readme():
    url = f"https://github.com/{P['owner']}"
    links = " · ".join(f'<a href="{url}/{p["repo"]}">{escape(p["title"])}</a>' for p in P["projects"])
    return f"""<p align="center">
  <a href="{url}?tab=repositories"><img src="assets/profile.svg" width="100%" alt="{escape(alt())}"></a>
</p>

<p align="center">
  <b>Projects:</b> {links}
</p>
"""


def refresh_languages():
    """Counts, per language, the public non-fork repos where it is at least 15% of the code."""
    gh = lambda path: json.loads(subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True).stdout)
    skip = {"C++", "CMake", "C", "Ruby", "Objective-C", "Kotlin", "Batchfile", "Shell", "Dockerfile", "Makefile", "PLpgSQL"}
    counts, repos = collections.Counter(), 0
    for repo in gh(f"/users/{P['owner']}/repos?per_page=100"):
        if repo["fork"]:
            continue
        langs = {k: v for k, v in gh(f"/repos/{P['owner']}/{repo['name']}/languages").items() if k not in skip}
        used = [k for k, v in langs.items() if v / sum(langs.values()) >= .15]
        repos += bool(used)
        counts.update(used)
    (ROOT / "languages.json").write_text(json.dumps({"repos": repos, "langs": counts.most_common()}, indent=1) + "\n")


if __name__ == "__main__":
    if "--refresh" in sys.argv:
        refresh_languages()
    out = ROOT / "assets"
    out.mkdir(exist_ok=True)
    for old in [*out.glob("*.svg"), *out.glob("projects/*.svg")]:
        old.unlink()
    if (out / "projects").exists():
        (out / "projects").rmdir()
    (out / "profile.svg").write_text(poster())
    (ROOT / "README.md").write_text(readme())
    print("built README.md and assets/profile.svg")
