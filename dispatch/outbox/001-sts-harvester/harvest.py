"""Capture full master.m3u8 request headers from Chrome DevTools Protocol."""
from __future__ import annotations
import json, os, re, subprocess, time, urllib.request
from pathlib import Path
import websocket

ROOT = Path(__file__).resolve().parent
CAPTURES = ROOT / "captures"
DEBUG = "http://127.0.0.1:9222"
CHROME = Path(os.environ.get("STS_CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe"))
PROFILE = Path(os.environ.get("STS_CHROME_PROFILE", r"C:\Users\vitos\AppData\Local\Google\Chrome\User Data"))

def get_json(url):
    with urllib.request.urlopen(url, timeout=3) as r:
        return json.loads(r.read().decode("utf-8"))

def slugify(url):
    leaf = re.sub(r"[?#].*$", "", url.rstrip("/")).rsplit("/", 1)[-1]
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", leaf).strip("-") or "lesson"

def ensure_chrome():
    try:
        get_json(DEBUG + "/json/version")
        return
    except Exception:
        pass
    if not CHROME.exists():
        raise RuntimeError(f"Chrome executable not found: {CHROME}")
    subprocess.Popen([str(CHROME), "--remote-debugging-port=9222",
                      f"--user-data-dir={PROFILE}", "--no-first-run",
                      "--no-default-browser-check"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline, error = time.monotonic() + 30, None
    while time.monotonic() < deadline:
        try:
            get_json(DEBUG + "/json/version")
            return
        except Exception as exc:
            error = exc
            time.sleep(.5)
    raise RuntimeError(f"Chrome DevTools did not start at {DEBUG}: {error}")

def capture(url):
    tabs = get_json(DEBUG + "/json")
    tab = next((x for x in tabs if x.get("type") == "page"), None)
    if not tab:
        raise RuntimeError("DevTools returned no page target")
    ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=1, suppress_origin=True)
    seq = 0
    def call(method, params=None):
        nonlocal seq
        seq += 1
        ident = seq
        ws.send(json.dumps({"id": ident, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == ident:
                if "error" in msg:
                    raise RuntimeError(f"CDP {method}: {msg['error']}")
                return msg.get("result", {})
    try:
        call("Network.enable")
        call("Page.enable")
        call("Page.navigate", {"url": url})
        seen, extras = {}, {}
        captured = None
        deadline, last_play = time.monotonic() + 75, 0
        while time.monotonic() < deadline:
            try:
                ev = json.loads(ws.recv())
            except websocket.WebSocketTimeoutException:
                if time.monotonic() - last_play > 5:
                    last_play = time.monotonic()
                    try:
                        call("Runtime.evaluate", {"expression":
                            "(()=>{const v=document.querySelector('video');if(v){v.muted=true;return v.play().then(()=>true).catch(e=>String(e))}return 'no video'})()",
                            "awaitPromise": True})
                    except Exception:
                        pass
                continue
            method, p = ev.get("method"), ev.get("params", {})
            if method == "Network.requestWillBeSent":
                req = p.get("request", {})
                if "master.m3u8" in req.get("url", ""):
                    seen[p["requestId"]] = {"url": req["url"], "headers": req.get("headers", {}),
                        "method": req.get("method", "GET"), "resourceType": p.get("type"),
                        "documentURL": p.get("documentURL")}
            elif method == "Network.requestWillBeSentExtraInfo":
                extras[p["requestId"]] = p.get("headers", {})
            elif method == "Network.responseReceived" and p.get("requestId") in seen:
                seen[p["requestId"]]["response"] = {
                    "status": p.get("response", {}).get("status"),
                    "mimeType": p.get("response", {}).get("mimeType")}
            for rid, req in seen.items():
                if rid in extras:
                    req["headers"] = extras[rid]
                    captured = req
                    break
            if captured:
                break
        if not captured:
            raise RuntimeError("No master.m3u8 request with full headers observed within 75 seconds")
        kind = "medias" if "/hls/medias/" in captured["url"] else (
            "memberships" if re.search(r"/hls/(?:v2/)?memberships/", captured["url"]) else "unknown")
        slug = slugify(url)
        out = CAPTURES / f"{slug}.json"
        out.write_text(json.dumps({"lesson_url": url, "lesson_slug": slug, "kind": kind,
            "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "request": captured}, indent=2), encoding="utf-8")
        print(f"Captured {kind}: {out}")
    finally:
        ws.close()

def main():
    CAPTURES.mkdir(parents=True, exist_ok=True)
    lessons = [x.strip() for x in (ROOT / "lessons.txt").read_text(encoding="utf-8-sig").splitlines()
               if x.strip() and not x.lstrip().startswith("#")]
    if not lessons:
        raise RuntimeError("lessons.txt contains no URLs")
    ensure_chrome()
    errors = 0
    for url in lessons:
        try:
            capture(url)
        except Exception as exc:
            errors += 1
            print(f"ERROR {url}: {type(exc).__name__}: {exc}")
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
