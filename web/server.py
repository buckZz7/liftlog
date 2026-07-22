#!/usr/bin/env python3
"""LiftLog web server — stdlib only, no dependencies.

Serves a mobile logging UI and a small JSON API.
Data lives in ~/.liftlog/: program.md (program), log.jsonl (append-only log).

Run:  python3 ~/.liftlog/web/server.py [--port 8377]
"""

import json
import os
import re
import sys
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

DATA = Path(os.environ.get("LIFTLOG_DIR", Path.home() / ".liftlog"))
WEB = Path(__file__).parent
LOG = DATA / "log.jsonl"
PROGRAM = DATA / "program.md"

# ---------- data ----------

def read_events():
    if not LOG.exists():
        return []
    out = []
    for line in LOG.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def append_event(ev):
    with LOG.open("a") as f:
        f.write(json.dumps(ev) + "\n")


def parse_program():
    """Parse program.md into days: [{num, name, exercises, mobility, cardio}]."""
    days = []
    day = None
    section = None  # None | "mobility" | "cardio"
    for line in PROGRAM.read_text().splitlines():
        m = re.match(r"## Day (\d+)\s*[—-]\s*(.+)", line)
        if m:
            day = {"num": int(m.group(1)), "name": m.group(2).strip(),
                   "exercises": [], "mobility": [], "cardio": []}
            days.append(day)
            section = None
            continue
        if day is None:
            continue
        if re.match(r"flexibility flow|mobility", line, re.I):
            section = "mobility"
            continue
        if re.match(r"^#{2,4}\s*.*cardio|^#{2,4}\s*Option", line, re.I):
            section = "cardio"
            continue
        if line.startswith("##"):
            section = None
            continue
        m = re.match(r"-\s+(.+?):\s*(\d+)\s*x\s*(\d+)(?:-(\d+))?(.*)", line)
        if m and section is None:
            name = m.group(1).strip()
            if re.search(r"(stretch|pose|fold|walk|warmup|cooldown|sprint|rest|min\b)", name, re.I) and not re.search(r"(press|row|curl|raise|fly|pulldown|pushdown|squat|press|crunch|swing|kickback|rdl)", name, re.I):
                continue
            day["exercises"].append({
                "name": name,
                "sets": int(m.group(2)),
                "lo": int(m.group(3)),
                "hi": int(m.group(4) or m.group(3)),
                "note": (m.group(5) or "").strip(" ()—-"),
            })
            continue
        if section == "mobility" and line.startswith("- "):
            day["mobility"].append(line[2:].strip())
        elif section == "cardio" and line.startswith("- "):
            day["cardio"].append(line[2:].strip())
    return days


def last_weights(events):
    """Most recent session's sets per exercise (normalized name)."""
    by_ex = {}
    for e in events:
        if e.get("type") == "set":
            key = norm(e["exercise"])
            by_ex.setdefault(key, []).append(e)
    last = {}
    for k, sets in by_ex.items():
        d = max(s["date"] for s in sets)
        last[k] = sorted([s for s in sets if s["date"] == d], key=lambda s: s.get("set", 0))
    return last


def norm(name):
    n = name.lower().strip()
    n = re.sub(r"[^a-z0-9 ]", "", n)
    # light aliasing between program names and logged names
    aliases = {
        "smith bench press": "smith bench",
        "incline dumbbell press": "incline db press",
        "lat pulldown": "lat pulldowns",
        "cable tricep pushdown": "cable tricep pushdowns",
        "dumbbell curls": "db curls",
    }
    return aliases.get(n, n)


def suggest_target(ex, prev_sets):
    """Double progression: hit top of range on all sets -> bump weight; else same weight."""
    if not prev_sets:
        return None, "first time — pick a weight you can control"
    w = max(s["weight"] for s in prev_sets)
    reps = [s["reps"] for s in prev_sets]
    if all(r >= ex["hi"] for r in reps):
        bump = 10 if re.search(r"squat|leg press|rdl|deadlift", ex["name"], re.I) else 5
        return w + bump, f"hit {ex['hi']} on all sets last time — bump up"
    return w, f"last time: {'/'.join(str(r) for r in reps)} @ {w:g}"


def today_payload():
    events = read_events()
    days = parse_program()
    lift_days = [d for d in days if d["exercises"]]
    # figure out next day in rotation from last session event
    last_num = 0
    for e in reversed(events):
        if e.get("type") == "session":
            m = re.search(r"Day (\d+)", e.get("day", ""))
            if m:
                last_num = int(m.group(1))
            break
    nxt = None
    for d in days:
        if d["num"] > last_num and (d["exercises"] or d["cardio"]):
            nxt = d
            break
    if nxt is None and lift_days:
        nxt = lift_days[0]

    prev = last_weights(events)
    exercises = []
    for ex in (nxt["exercises"] if nxt else []):
        prev_sets = prev.get(norm(ex["name"]))
        weight, hint = suggest_target(ex, prev_sets)
        exercises.append({**ex, "target_weight": weight, "hint": hint,
                          "prev": [{"weight": s["weight"], "reps": s["reps"]} for s in (prev_sets or [])]})

    # cardio prescription: from a cardio-only day, else generic from "How cardio fits" is omitted
    cardio = []
    mobility = []
    if nxt:
        mobility = nxt.get("mobility", [])
        cardio = nxt.get("cardio", [])

    logged_today = [e for e in events if e.get("date") == date.today().isoformat()]
    return {
        "date": date.today().isoformat(),
        "day": nxt,
        "exercises": exercises,
        "mobility": mobility,
        "cardio": cardio,
        "logged_today": logged_today,
    }


# ---------- http ----------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 - matches base class signature
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/" or u.path == "/index.html":
            body = (WEB / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif u.path == "/api/today":
            self._json(today_payload())
        elif u.path == "/api/history":
            q = parse_qs(u.query)
            name = norm(q.get("exercise", [""])[0])
            sets = [e for e in read_events()
                    if e.get("type") == "set" and norm(e["exercise"]) == name]
            self._json({"exercise": name, "sets": sets[-40:]})
        elif u.path == "/api/recent":
            self._json({"events": read_events()[-60:]})
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/api/log":
            self._json({"error": "not found"}, 404)
            return
        n = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            self._json({"error": "bad json"}, 400)
            return

        today = date.today().isoformat()
        day_label = payload.get("day") or ""
        events = read_events()
        if not any(e.get("type") == "session" and e.get("date") == today for e in events):
            append_event({"date": today, "type": "session", "day": day_label})

        added = []
        kind = payload.get("type", "sets")
        if kind == "sets":
            ex = payload["exercise"]
            existing = [e for e in events if e.get("type") == "set"
                        and e.get("date") == today and norm(e["exercise"]) == norm(ex)]
            for i, s in enumerate(payload["sets"]):
                if not s.get("reps"):
                    continue
                ev = {"date": today, "type": "set", "exercise": ex,
                      "weight": float(s.get("weight") or 0), "reps": int(s["reps"]),
                      "set": len(existing) + i + 1, "failure": bool(s.get("failure"))}
                append_event(ev)
                added.append(ev)
        elif kind in ("cardio", "mobility", "bodyweight", "note"):
            ev = {"date": today, "type": kind, **{k: v for k, v in payload.items() if k not in ("type", "day")}}
            append_event(ev)
            added.append(ev)
        self._json({"ok": True, "added": len(added)})


def main():
    port = 8377
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"LiftLog web → http://127.0.0.1:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
