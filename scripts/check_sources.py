"""Load every URL in sources.yaml live and confirm it is the page we think it is.

Writes sources_check.md. Exits non-zero if any source fails. Nothing is saved
except the report: storing the pages themselves is step 2 (ingest).

    python scripts/check_sources.py
"""

from __future__ import annotations

import io
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
USER_AGENT = "caseline-source-check/0.1 (research prototype)"


def page_text(resp: requests.Response) -> tuple[str, str]:
    """Return (title, searchable text) for an HTML page or a PDF."""
    ctype = resp.headers.get("Content-Type", "")
    if "pdf" in ctype or resp.content[:5] == b"%PDF-":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(resp.content))
        text = " ".join((p.extract_text() or "") for p in reader.pages[:3])
        title = (reader.metadata.title if reader.metadata else None) or ""
        first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
        return (title or first_line)[:120], text
    soup = BeautifulSoup(resp.text, "lxml")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    return title[:120], soup.get_text(" ", strip=True)


def check(src: dict, session: requests.Session) -> dict:
    row = {"id": src["id"], "url": src["url"], "ok": False}
    try:
        resp = session.get(src["url"], timeout=30, allow_redirects=True)
    except requests.RequestException as exc:
        row["problem"] = f"request failed: {type(exc).__name__}"
        return row
    row["status"] = resp.status_code
    row["final_url"] = resp.url
    row["ctype"] = resp.headers.get("Content-Type", "").split(";")[0]
    if resp.status_code != 200:
        row["problem"] = f"HTTP {resp.status_code}"
        if resp.status_code == 403 and src.get("verified") is False:
            row["blocked"] = True  # known: the site refuses scripted clients
        return row
    try:
        row["title"], text = page_text(resp)
    except Exception as exc:  # unreadable PDF/HTML is a failure, not a crash
        row["problem"] = f"could not read content: {type(exc).__name__}"
        return row
    if src["expect"].lower() not in text.lower():
        row["problem"] = f"expected text {src['expect']!r} not found"
        return row
    if re.search(r"page not found|404", row["title"], re.I):
        row["problem"] = "title looks like an error page"
        return row
    if src["kind"] == "policy-manual-part":
        part = src["url"].rsplit("/", 1)[1]
        soup = BeautifulSoup(resp.text, "lxml")
        chapters = {a["href"] for a in soup.find_all("a", href=True)
                    if re.fullmatch(rf"/policy-manual/{part}-chapter-\d+", a["href"])}
        if not chapters:
            row["problem"] = "no chapter links found on part page"
            return row
        row["title"] += f" ({len(chapters)} chapters)"
    row["ok"] = True
    return row


def main() -> int:
    sources = yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8"))["sources"]
    ids = [s["id"] for s in sources]
    if len(ids) != len(set(ids)):
        print("duplicate source ids", file=sys.stderr)
        return 2

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    rows = []
    for src in sources:
        row = check(src, session)
        rows.append(row)
        label = "OK  " if row["ok"] else ("BLKD" if row.get("blocked") else "FAIL")
        print(label, src["id"], row.get("problem", row.get("title", "")))
        time.sleep(1)  # be polite to government servers

    checked = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Source check",
        "",
        f"Checked {checked} by `scripts/check_sources.py`. "
        f"{sum(r['ok'] for r in rows)}/{len(rows)} OK, "
        f"{sum(bool(r.get('blocked')) for r in rows)} blocked (site refuses scripted "
        "clients; marked `verified: false`, needs a manual browser check).",
        "",
        "| id | result | type | title | url |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        result = "OK" if r["ok"] else ("BLOCKED" if r.get("blocked") else "FAIL") + f": {r.get('problem')}"
        url = r.get("final_url", r["url"])
        moved = " (redirected)" if url != r["url"] else ""
        title = r.get("title", "").replace("|", "/")
        lines.append(f"| {r['id']} | {result} | {r.get('ctype', '')} | {title} | {url}{moved} |")
    (ROOT / "sources_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Blocked sources don't fail the run, but they keep step 1's "all OK" box unticked.
    return 0 if all(r["ok"] or r.get("blocked") for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
