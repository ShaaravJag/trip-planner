#!/usr/bin/env python3
"""Export a trip's plan.md to one self-contained, phone-friendly HTML file.

Usage:
  export_html.py <trip dir> [--icloud] [--source plan.md]

Writes <trip dir>/<slug>.html (no external resources, no JavaScript, light/dark mode). With
--icloud, also copies it to iCloud Drive/Trips/ so it shows up in the iPhone Files app.
Standard library only (Python 3.9+). Supports the markdown the skill writes: headings, lists
(nested, task lists), tables, links, bold/italic, code, blockquotes, rules, and <details> lines.
"""
import html
import os
import re
import shutil
import sys
from datetime import date

ICLOUD = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/Trips")
RAW_HTML = re.compile(r"^\s*</?(details|summary)\b[^>]*>(.*</summary>)?\s*$", re.I)


# ---------- inline ----------
def inline(text):
    text = re.sub(r"<!--.*?-->", "", text)
    slots = []

    def keep(s):
        slots.append(s)
        return "\x00%d\x00" % (len(slots) - 1)

    text = re.sub(r"`([^`]+)`", lambda m: keep("<code>%s</code>" % html.escape(m.group(1))), text)

    def link(m):
        label, url = m.group(1), m.group(2).strip()
        if not re.match(r"^(https?:|mailto:|tel:|#)", url):
            return m.group(0)
        return keep('<a href="%s">%s</a>' % (html.escape(url, quote=True), fmt(label)))

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"(?<![\"'=(])\bhttps?://[^\s<>)]+",
                  lambda m: keep('<a href="%s">%s</a>' % (html.escape(m.group(0), quote=True),
                                                          html.escape(m.group(0)))), text)
    text = fmt(text)
    return re.sub(r"\x00(\d+)\x00", lambda m: slots[int(m.group(1))], text)


def fmt(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w])_(?!\s)(.+?)(?<!\s)_(?![\w])", r"<em>\1</em>", text)
    return text


def slugify(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[^\w\s-]", "", s.lower()).strip()
    return re.sub(r"[\s_]+", "-", s)[:60] or "section"


# ---------- blocks ----------
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def render_list(items):
    """items: list of (indent, ordered, text). Returns HTML for nested lists."""
    out = []
    stack = []  # (indent, tag)

    def li(text):
        m = re.match(r"^\[([ xX])\]\s+(.*)$", text)
        if m:
            checked = " checked" if m.group(1) in "xX" else ""
            return '<li class="task"><input type="checkbox" disabled%s> %s' % (checked, inline(m.group(2)))
        return "<li>" + inline(text)

    for indent, ordered, text in items:
        tag = "ol" if ordered else "ul"
        if not stack or indent > stack[-1][0]:
            out.append("<%s>" % tag)
            stack.append((indent, tag))
        else:
            while stack and indent < stack[-1][0]:
                out.append("</li></%s>" % stack.pop()[1])
            out.append("</li>")
        out.append(li(text))
    while stack:
        out.append("</li></%s>" % stack.pop()[1])
    return "".join(out)


def md_to_blocks(md):
    """Return list of (kind, data) blocks; kind 'h1'..'h4' carry text, others carry HTML."""
    lines = md.replace("\r\n", "\n").split("\n")
    blocks, para, i = [], [], 0
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    lines = md.split("\n")

    def flush():
        if para:
            blocks.append(("html", "<p>%s</p>" % "<br>".join(inline(p) for p in para)))
            del para[:]

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            flush()
            j, code = i + 1, []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                code.append(lines[j]); j += 1
            blocks.append(("html", "<pre><code>%s</code></pre>" % html.escape("\n".join(code))))
            i = j + 1; continue
        if not s:
            flush(); i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            flush(); blocks.append(("h%d" % len(m.group(1)), m.group(2).strip())); i += 1; continue
        if RAW_HTML.match(line):
            flush()
            sm = re.match(r"^\s*<summary>(.*)</summary>\s*$", s, re.I)
            dm = re.match(r"^\s*<details><summary>(.*)</summary>\s*$", s, re.I)
            if dm:
                blocks.append(("html", "<details><summary>%s</summary>" % inline(dm.group(1))))
            elif sm:
                blocks.append(("html", "<summary>%s</summary>" % inline(sm.group(1))))
            else:
                blocks.append(("html", s))
            i += 1; continue
        if s.startswith("|") and i + 1 < len(lines) and TABLE_SEP.match(lines[i + 1]):
            flush()
            head = split_row(s)
            aligns = []
            for c in split_row(lines[i + 1]):
                aligns.append("right" if c.endswith(":") and not c.startswith(":") else
                              "center" if c.startswith(":") and c.endswith(":") else "")
            rows, j = [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(split_row(lines[j])); j += 1

            def cell(tag, c, k):
                a = aligns[k] if k < len(aligns) and aligns[k] else ""
                return '<%s%s>%s</%s>' % (tag, ' style="text-align:%s"' % a if a else "", inline(c), tag)

            h = "<thead><tr>%s</tr></thead>" % "".join(cell("th", c, k) for k, c in enumerate(head))
            b = "".join("<tr>%s</tr>" % "".join(cell("td", c, k) for k, c in enumerate(r)) for r in rows)
            blocks.append(("html", '<div class="tw"><table>%s<tbody>%s</tbody></table></div>' % (h, b)))
            i = j; continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            flush(); blocks.append(("html", "<hr>")); i += 1; continue
        if s.startswith(">"):
            flush()
            q = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q.append(lines[i].strip()[1:].strip()); i += 1
            blocks.append(("html", "<blockquote>%s</blockquote>" % "<br>".join(inline(x) for x in q)))
            continue
        if LIST_RE.match(line):
            flush()
            items = []
            while i < len(lines):
                lm = LIST_RE.match(lines[i])
                if lm:
                    items.append([len(lm.group(1).expandtabs(4)), lm.group(2)[0].isdigit(), lm.group(3)])
                    i += 1
                elif lines[i].strip() and lines[i].startswith((" ", "\t")) and items:
                    items[-1][2] += " " + lines[i].strip(); i += 1  # continuation line
                else:
                    break
            blocks.append(("html", render_list([tuple(x) for x in items])))
            continue
        para.append(s); i += 1
    flush()
    return blocks


CSS = """
:root{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1f;--muted:#6b6b70;--line:#e4e2dd;--accent:#0a66c2;
--chip:#ecebe6;--day:#fff8ec;--dayline:#f0d9a8}
@media (prefers-color-scheme:dark){:root{--bg:#121214;--card:#1c1c1f;--ink:#ececf0;--muted:#a0a0a8;
--line:#2e2e33;--accent:#6cb2ff;--chip:#26262b;--day:#1f1b14;--dayline:#4a3c22}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,
"Segoe UI",Roboto,sans-serif}
header{padding:20px 16px 8px;max-width:760px;margin:0 auto}
h1{font-size:1.6rem;line-height:1.2;margin:0 0 6px}
.sub{color:var(--muted);font-size:.92rem}
nav{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
overflow-x:auto;white-space:nowrap;padding:8px 16px;-webkit-overflow-scrolling:touch}
nav a{display:inline-block;margin-right:6px;padding:5px 11px;border-radius:999px;background:var(--chip);
color:var(--ink);text-decoration:none;font-size:.85rem}
main{max-width:760px;margin:0 auto;padding:8px 16px 40px}
section{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px;
margin:14px 0;scroll-margin-top:56px}
section.day{background:var(--day);border-color:var(--dayline)}
h2{font-size:1.15rem;margin:0 0 8px}h3{font-size:1rem;margin:14px 0 6px}h4{font-size:.95rem;margin:12px 0 4px}
p{margin:6px 0}ul,ol{margin:6px 0;padding-left:20px}li{margin:4px 0}li.task{list-style:none;margin-left:-20px}
li.task input{transform:scale(1.15);margin-right:6px}
a{color:var(--accent);text-decoration:none}a:active{opacity:.6}
.tw{overflow-x:auto;margin:8px 0}table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}
code{background:var(--chip);padding:1px 5px;border-radius:5px;font-size:.88em}
pre{background:var(--chip);padding:10px;border-radius:8px;overflow-x:auto}
blockquote{margin:8px 0;padding:4px 12px;border-left:3px solid var(--line);color:var(--muted)}
details{margin:8px 0}summary{cursor:pointer;color:var(--accent)}
hr{border:0;border-top:1px solid var(--line);margin:12px 0}
footer{color:var(--muted);font-size:.8rem;text-align:center;padding:0 16px 30px}
"""


def build(md, fallback_title):
    blocks = md_to_blocks(md)
    title, intro, sections, cur = fallback_title, [], [], None
    for kind, data in blocks:
        if kind == "h1" and title == fallback_title and not sections:
            title = data
        elif kind == "h2":
            cur = {"title": data, "body": []}
            sections.append(cur)
        elif kind in ("h3", "h4", "h1"):
            tag = "h3" if kind == "h1" else kind
            (cur["body"] if cur else intro).append("<%s>%s</%s>" % (tag, inline(data), tag))
        else:
            (cur["body"] if cur else intro).append(data)
    used, nav, secs = set(), [], []
    for s in sections:
        sid = slugify(s["title"])
        while sid in used:
            sid += "-x"
        used.add(sid)
        is_day = bool(re.match(r"^day\s*\d+", s["title"], re.I))
        short = re.split(r"\s+[—–-]\s+|\s+·\s+", re.sub(r"<[^>]+>", "", s["title"]))[0]
        nav.append('<a href="#%s">%s</a>' % (sid, html.escape(short)))
        secs.append('<section id="%s"%s><h2>%s</h2>%s</section>' % (
            sid, ' class="day"' if is_day else "", inline(s["title"]), "".join(s["body"])))
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>%s</title><style>%s</style></head>
<body><header><h1>%s</h1><div class="sub">%s</div></header>
<nav>%s</nav>
<main>%s</main>
<footer>Exported %s · prices are as checked during planning — confirm before booking</footer>
</body></html>
""" % (html.escape(re.sub(r"<[^>]+>", "", title)), CSS, inline(title), "".join(intro),
       "".join(nav), "".join(secs), date.today().isoformat())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    trip = os.path.abspath(args[0])
    src = "plan.md"
    if "--source" in sys.argv:
        src = sys.argv[sys.argv.index("--source") + 1]
        args = [a for a in args if a != src]
    path = os.path.join(trip, src)
    if not os.path.exists(path):
        raise SystemExit("not found: %s (run /trip plan first)" % path)
    slug = os.path.basename(trip.rstrip("/"))
    with open(path, encoding="utf-8") as f:
        page = build(f.read(), slug)
    out = os.path.join(trip, slug + ".html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote %s (%d KB)" % (out, (len(page.encode("utf-8")) + 1023) // 1024))
    if "--icloud" in sys.argv:
        if os.path.isdir(os.path.dirname(ICLOUD)):
            os.makedirs(ICLOUD, exist_ok=True)
            dest = os.path.join(ICLOUD, slug + ".html")
            shutil.copyfile(out, dest)
            print("copied to iCloud Drive: %s" % dest)
        else:
            print("iCloud Drive not found; AirDrop the file instead")


if __name__ == "__main__":
    main()
