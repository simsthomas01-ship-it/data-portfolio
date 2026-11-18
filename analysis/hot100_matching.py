#!/usr/bin/env python3
"""Weekly Billboard Hot 100 -> match against Navidrome -> hot100.json for the website + a Navidrome playlist. Stdlib only."""
import argparse, getpass, hashlib, json, os, re, secrets, sys, unicodedata, urllib.parse, urllib.request, datetime, tempfile
from difflib import SequenceMatcher

CHART_URL = os.environ.get("HOT100_URL", "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/recent.json")
ENV_FILE = os.path.expanduser("~/.hot100.env")
OUT_FILE = os.path.expanduser("~/pi-site/data/hot100.json")
PLAYLIST = "Billboard Hot 100"

def fold(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c))

def norm(s):
    s = fold(s).lower().replace("&", " and ")
    s = re.sub(r"[‘’`']", "", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\b(the|a)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def title_variants(t):
    """Possible title forms: whole, without (...) parts, and each '/' piece."""
    out = []
    parts = [t] + [p for p in t.split("/") if p.strip()] if "/" in t else [t]
    for p in parts:
        out.append(norm(p))
        out.append(norm(re.sub(r"\(.*?\)", " ", p)))
        for g in re.findall(r"\((.*?)\)", p):   # "(Sittin' On) The Dock Of The Bay" keeps words
            out.append(norm(p.replace("(", " ").replace(")", " ")))
    out = [o for o in dict.fromkeys(out) if o]
    return out

def artist_variants(a):
    full = norm(a)
    primary = re.split(r"\b(?:featuring|feat|ft|with)\b", fold(a), flags=re.I)[0]
    primary_n = norm(primary)
    first = norm(re.split(r"\s+(?:and|&)\s+", primary, maxsplit=1, flags=re.I)[0])
    return [v for v in dict.fromkeys([full, primary_n, first]) if v]

BAD = re.compile(r"\b(live|remix|karaoke|instrumental|demo|acoustic|cover|tribute|version|edit|mix|remaster(?:ed)?)\b", re.I)

def score(want_t, want_a, got_t, got_a):
    gt = title_variants(got_t)
    best_t = max(SequenceMatcher(None, w, g).ratio() for w in want_t for g in gt)
    ga = norm(got_a)
    best_a = 0.0
    for w in want_a:
        if not w: continue
        if w == ga: s = 1.0
        elif w in ga or ga in w: s = 0.9
        else: s = SequenceMatcher(None, w, ga).ratio()
        best_a = max(best_a, s)
    return best_t, best_a

class Nav:
    def __init__(self, base, user, pw):
        self.base, self.user, self.pw = base.rstrip("/"), user, pw
    def call(self, ep, **params):
        salt = secrets.token_hex(6)
        q = {"u": self.user, "t": hashlib.md5((self.pw + salt).encode()).hexdigest(), "s": salt,
             "v": "1.16.1", "c": "billboard-script", "f": "json"}
        lst = []
        for k, v in params.items():
            if isinstance(v, list): lst += [(k, x) for x in v]
            else: q[k] = v
        url = f"{self.base}/rest/{ep}.view?" + urllib.parse.urlencode(list(q.items()) + lst)
        with urllib.request.urlopen(url, timeout=30) as r:
            d = json.load(r)["subsonic-response"]
        if d.get("status") != "ok":
            raise RuntimeError(f"{ep}: {d.get('error', {}).get('message', 'failed')}")
        return d

def find_song(nav, title, artist):
    want_t, want_a = title_variants(title), artist_variants(artist)
    seen, cands = set(), []
    queries = [f"{want_t[0]} {want_a[-1]}", want_t[0]] + want_t[1:3]
    for q in dict.fromkeys(queries):
        d = nav.call("search3", query=q, songCount=40, artistCount=0, albumCount=0)
        for s in d.get("searchResult3", {}).get("song", []):
            if s["id"] not in seen:
                seen.add(s["id"]); cands.append(s)
    best = None
    for s in cands:
        ts, as_ = score(want_t, want_a, s.get("title", ""), s.get("artist", ""))
        alb_art = s.get("albumArtist") or ""
        if alb_art:
            _, a2 = score(want_t, want_a, s.get("title", ""), alb_art)
            as_ = max(as_, a2)
        if ts < 0.86 or as_ < 0.8: continue
        pen = 0.1 if BAD.search(s.get("title", "") + " " + s.get("album", "")) and not BAD.search(title) else 0
        total = ts + as_ - pen + (0.01 if s.get("suffix") in ("flac",) else 0)
        if best is None or total > best[0]: best = (total, s)
    return best[1] if best else None


def load_env():
    cfg = {}
    with open(ENV_FILE) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.rstrip("\n").split("=", 1); cfg[k] = v
    return cfg

def setup():
    print("One-time setup: Navidrome login for the weekly Hot 100 job (saved only in ~/.hot100.env, readable only by you).")
    url = input("Navidrome address [http://127.0.0.1:4533]: ").strip() or "http://127.0.0.1:4533"
    user = input("Navidrome username: ").strip()
    pw = getpass.getpass("Navidrome password (hidden): ")
    try: Nav(url, user, pw).call("ping")
    except Exception as e: sys.exit(f"Could not log in: {e}  (nothing saved)")
    fd = os.open(ENV_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f: f.write(f"NAVIDROME_URL={url}\nNAVIDROME_USER={user}\nNAVIDROME_PASS={pw}\n")
    print("Login saved.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--setup", action="store_true", help="ask for the Navidrome login and save it")
    ap.add_argument("--no-playlist", action="store_true")
    ap.add_argument("--out", default=OUT_FILE)
    a = ap.parse_args()
    if a.setup or not os.path.exists(ENV_FILE): setup()
    cfg = load_env()
    nav = Nav(cfg["NAVIDROME_URL"], cfg["NAVIDROME_USER"], cfg["NAVIDROME_PASS"])
    nav.call("ping")
    req = urllib.request.Request(CHART_URL, headers={"User-Agent": "crustycrab-hot100/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r: chart = json.load(r)
    entries = chart["data"]
    if len(entries) < 50: sys.exit("Chart looks incomplete, keeping the old data.")
    songs, ids = [], []
    for e in entries:
        s = find_song(nav, e["song"], e["artist"])
        songs.append({"rank": e["this_week"], "last_week": e.get("last_week"), "peak": e.get("peak_position"),
                      "weeks": e.get("weeks_on_chart"), "title": e["song"], "artist": e["artist"], "have": bool(s),
                      "album": s.get("album") if s else None, "dl_album": "", "library_artist": s.get("artist") if s else None})
        if s: ids.append(s["id"])
    try:
        import mbalbum
        mbalbum.add_albums(songs, os.path.join(os.path.dirname(a.out), "hot100_albums.json"))
    except Exception as e:
        print("Album lookup skipped:", e)
    out = {"chart_date": chart.get("date"), "updated": datetime.datetime.now().isoformat(timespec="seconds"),
           "have": len(ids), "total": len(songs), "playlist": PLAYLIST, "songs": songs}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(a.out)); os.close(fd)
    with open(tmp, "w", encoding="utf-8") as f: json.dump(out, f, ensure_ascii=False, indent=1)
    os.chmod(tmp, 0o644); os.replace(tmp, a.out)
    print(f"Chart dated {chart.get('date')}: you have {len(ids)} of {len(songs)}. Saved {a.out}")
    if not a.no_playlist and ids:
        existing = {p["name"]: p["id"] for p in nav.call("getPlaylists").get("playlists", {}).get("playlist", [])}
        if PLAYLIST in existing: nav.call("createPlaylist", playlistId=existing[PLAYLIST], songId=ids)
        else: nav.call("createPlaylist", name=PLAYLIST, songId=ids)
        print(f"Playlist '{PLAYLIST}' {'updated' if PLAYLIST in existing else 'created'} with {len(ids)} songs.")

if __name__ == "__main__":
    main()
