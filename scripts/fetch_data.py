"""
fetch_data.py - Download project data files and log their provenance.

Usage (run from the repository root):
    python scripts/fetch_data.py

Reads:   data/sources.csv     (columns: name,url,note)
Writes:  data/raw/<name>      (the downloaded files, never edited by hand)
         data/provenance.csv  (name,url,date_utc,sha256,bytes,downloaded_by,note)
"""

import csv
import getpass
import hashlib
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "sources.csv"
RAW_DIR = ROOT / "data" / "raw"
PROVENANCE = ROOT / "data" / "provenance.csv"

# Some servers (including itu.int) reject requests without a browser-like User-Agent.
HEADERS = {"User-Agent": "Mozilla/5.0 (PH035IU student project; data download script)"}


def sha256_of(path: Path) -> str:
    """Return the SHA-256 checksum of a file, read in 1 MB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(name: str, url: str, attempts: int = 3) -> Path:
    """Download one URL into data/raw/<name>. Skip if the file already exists.

    Large files are streamed to a temporary .part file in 1 MB chunks and only
    renamed to the final name when complete, so a broken connection never leaves
    a half-written file behind. Failed attempts are retried up to `attempts` times.
    """
    target = RAW_DIR / name
    if target.exists():
        print(f"[skip] {name} already downloaded")
        return target
    part = target.with_name(target.name + ".part")
    for attempt in range(1, attempts + 1):
        print(f"[get ] {name} <- {url}  (attempt {attempt}/{attempts})")
        try:
            with requests.get(url, headers=HEADERS, timeout=120, stream=True) as r:
                r.raise_for_status()  # stop with an error if the server returned 4xx/5xx
                with open(part, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        f.write(chunk)
            part.replace(target)  # complete download -> final file name
            return target
        except requests.exceptions.HTTPError:
            raise  # 404/403 will not fix itself by retrying
        except Exception as e:
            print(f"[warn] {name}: attempt {attempt} failed ({e.__class__.__name__})")
            if part.exists():
                part.unlink()
            if attempt == attempts:
                raise
            time.sleep(5 * attempt)  # wait a little longer before each retry
    return target


def log_provenance(name: str, url: str, path: Path, note: str) -> None:
    """Append one row to data/provenance.csv (creates the header the first time)."""
    new_file = not PROVENANCE.exists()
    with open(PROVENANCE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["name", "url", "date_utc", "sha256", "bytes", "downloaded_by", "note"])
        w.writerow([
            name,
            url,
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            sha256_of(path),
            path.stat().st_size,
            getpass.getuser(),
            note,
        ])


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    already_logged = set()
    if PROVENANCE.exists():
        with open(PROVENANCE, encoding="utf-8") as f:
            already_logged = {row["name"] for row in csv.DictReader(f)}

    failures = 0
    with open(SOURCES, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name, url, note = row["name"], row["url"], row.get("note", "")
            try:
                path = download(name, url)
                if name not in already_logged:
                    log_provenance(name, url, path, note)
            except Exception as e:  # report and continue with the next file
                failures += 1
                print(f"[FAIL] {name}: {e}")

    print("Done." if failures == 0 else f"Done with {failures} failure(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())