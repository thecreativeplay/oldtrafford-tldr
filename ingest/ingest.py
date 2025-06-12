'''
Reads RSS, strips exact/near duplicates (cos ≥ 0.95), writes one clean list.
Keeps state only for this run—simple for a personal site.
'''

import feedparser, json, hashlib, datetime as dt
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

FEEDS = {                             # ⬅ add more RSS feeds anytime
    "BBC MU": "https://www.bbc.co.uk/sport/football/teams/manchester-united/rss.xml",
    "MEN":     "https://www.manchestereveningnews.co.uk/all-about/manchester-united-fc/?service=rss",
}
MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
SIM = 0.95

def sha(txt): return hashlib.sha256(txt.encode()).hexdigest()
def summarise(txt): return txt[:300]+"…" if len(txt)>300 else txt

def main():
    seen_sha, vecs, news = set(), [], []
    for src, url in FEEDS.items():
        for e in feedparser.parse(url).entries:
            body = (e.get("summary") or e.get("description") or "")
            if (h := sha(body)) in seen_sha: continue
            seen_sha.add(h)

            v = MODEL.encode(body, normalize_embeddings=True)
            if any(util.cos_sim(v, w).item() >= SIM for w in vecs): continue
            vecs.append(v)

            news.append({
                "title": e.title, "url": e.link, "source": src,
                "published": e.get("published",
                                   dt.datetime.utcnow().isoformat()),
                "summary": summarise(body)
            })
    news.sort(key=lambda n: n["published"], reverse=True)
    Path("data/news.json").write_text(json.dumps(news, indent=2))
    print("Wrote", len(news), "stories")

if __name__ == "__main__":
    main()
