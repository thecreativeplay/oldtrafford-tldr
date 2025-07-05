'''
Reads RSS, strips exact/near duplicates (cos ≥ 0.95), writes one clean list.
Keeps state only for this run—simple for a personal site.
'''
import feedparser, json, hashlib, datetime as dt, torch
import re, textwrap
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from dateutil import parser as dateparser



SENT_RX = re.compile(r'(?<=[.!?])\s+')   # crude sentence splitter



FEEDS = {
    "BBC MU": "https://www.bbc.co.uk/sport/football/teams/manchester-united/rss.xml",
    "MEN":     "https://www.manchestereveningnews.co.uk/all-about/manchester-united-fc/?service=rss",
}
MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
SIM = 0.95

def sha(txt): return hashlib.sha256(txt.encode()).hexdigest()
def summarise(txt: str, max_sentences: int = 3, max_chars: int = 500) -> str:
    """Return the first 2–3 sentences, trimmed to max_chars."""
    sentences = SENT_RX.split(txt.strip())
    snippet = " ".join(sentences[:max_sentences]).strip()
    if len(snippet) > max_chars:
        snippet = textwrap.shorten(snippet, max_chars, placeholder="…")
    return snippet


def main():
    Path("data").mkdir(parents=True, exist_ok=True)
    seen_sha, vecs, news = set(), [], []

    for src, url in FEEDS.items():
        parsed = feedparser.parse(url)
        if parsed.bozo:
            print(f"Warning: Could not parse feed {src}: {parsed.bozo_exception}")
            continue

        for e in parsed.entries:
            body = (e.get("summary") or e.get("description") or "")
            if not isinstance(body, str) or not body.strip():
                continue

            if (h := sha(body)) in seen_sha: continue
            seen_sha.add(h)

            v = torch.tensor(MODEL.encode(body, normalize_embeddings=True))
            if any(util.cos_sim(v, w).item() >= SIM for w in vecs): continue
            vecs.append(v)

            try:
                published = dateparser.parse(e.published).isoformat()
            except:
                published = dt.datetime.utcnow().isoformat()

            news.append({
                "title": e.title, "url": e.link, "source": src,
                "published": published,
                "summary": summarise(body)
            })

    news.sort(key=lambda n: dateparser.parse(n["published"]), reverse=True)
    Path("data/news.json").write_text(json.dumps(news, indent=2))
    print("Wrote", len(news), "stories")

if __name__ == "__main__":
    main()
