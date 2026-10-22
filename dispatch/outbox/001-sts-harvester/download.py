"""Replay medias HLS requests with captured headers; probe memberships once."""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
CAPTURES, AUDIO = ROOT / "captures", ROOT / "audio"
LOG = CAPTURES / "memberships-test.log"
FFMPEG = os.environ.get("STS_FFMPEG", "ffmpeg")

def header_block(headers):
    return "".join(f"{k}: {v}\r\n" for k, v in headers.items())

def memberships_probe(data):
    req = data["request"]
    stamp = datetime.now(timezone.utc).isoformat()
    try:
        # One GET only, using the complete captured header set; do not follow redirects.
        response = requests.get(req["url"], headers=req["headers"], timeout=25,
                                allow_redirects=False, stream=True)
        code = response.status_code
        server = response.headers.get("server", "")
        body = response.raw.read(512, decode_content=True).decode("utf-8", "replace")
        response.close()
        result = f"HTTP {code}; server={server!r}; body_prefix={body!r}"
    except requests.RequestException as exc:
        result = f"REQUEST_ERROR {type(exc).__name__}: {exc}"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{stamp}\t{data.get('lesson_slug')}\t{result}\n")
    print("Memberships single replay:", result)

def download_medias(data):
    req, slug = data["request"], data["lesson_slug"]
    out = AUDIO / f"{slug}.mp3"
    cmd = [FFMPEG, "-y", "-headers", header_block(req["headers"]), "-i", req["url"],
           "-vn", "-map", "0:a:0", "-c:a", "libmp3lame", "-q:a", "2", str(out)]
    print("Running ffmpeg for", slug)
    subprocess.run(cmd, check=True)

def main():
    AUDIO.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    failures = 0
    for path in sorted(CAPTURES.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        try:
            if data.get("kind") == "medias":
                download_medias(data)
            elif data.get("kind") == "memberships":
                memberships_probe(data)
            else:
                print(f"Skipping unknown kind: {path.name}")
        except Exception as exc:
            failures += 1
            print(f"ERROR {path.name}: {type(exc).__name__}: {exc}", file=sys.stderr)
    if failures:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
