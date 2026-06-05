#!/usr/bin/env python3
"""Minimal markdown-ish → HTML for blog posts."""
from __future__ import annotations

import re


def md_block_to_html(text: str) -> str:
    lines = text.strip().splitlines()
    out: list[str] = []
    buf: list[str] = []
    in_table = False
    table_rows: list[str] = []

    def flush_para() -> None:
        nonlocal buf
        if buf:
            p = " ".join(s.strip() for s in buf if s.strip())
            if p:
                out.append(f"<p>{inline(p)}</p>")
            buf = []

    def flush_table() -> None:
        nonlocal in_table, table_rows
        if not table_rows:
            return
        html = ["<table><tbody>"]
        for i, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip("|").split("|")]
            tag = "th" if i == 0 else "td"
            html.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
        html.append("</tbody></table>")
        out.append("".join(html))
        table_rows = []
        in_table = False

    for line in lines:
        s = line.strip()
        if s.startswith("|") and "|" in s[1:]:
            flush_para()
            if not in_table:
                in_table = True
            if re.match(r"^\|[\s\-:|]+\|$", s):
                continue
            table_rows.append(s)
            continue
        if in_table:
            flush_table()

        if s.startswith("#### "):
            flush_para()
            out.append(f"<h3>{inline(s[5:])}</h3>")
        elif s.startswith("### "):
            flush_para()
            out.append(f"<h2>{inline(s[4:])}</h2>")
        elif s.startswith("## "):
            flush_para()
            out.append(f"<h2>{inline(s[3:])}</h2>")
        elif not s:
            flush_para()
        elif s.startswith("☐"):
            flush_para()
            out.append(f"<p>{inline(s)}</p>")
        else:
            buf.append(s)

    flush_para()
    if in_table:
        flush_table()
    return "\n".join(out)


def inline(s: str) -> str:
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" rel="noopener noreferrer">\1</a>', s)
    s = re.sub(r"\[([^\]]+)\]\((/[^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s
