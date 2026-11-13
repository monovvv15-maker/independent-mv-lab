"""Remote metadata discovery only. Fails if the real live search has no usable results."""
import argparse
import json
from pathlib import Path
from media_sources import commons_search
from review import build_review

SEARCH_TERMS = ["morning street", "rain puddles", "shoes door", "walking street", "window wind", "sunlit neighborhood"]

def discover(terms=SEARCH_TERMS, limit=8):
    results, errors = [], []
    for term in terms:
        try:
            results.extend(commons_search(term, limit=limit))
        except Exception as exc:
            errors.append({"term": term, "error": type(exc).__name__ + ": " + str(exc)[:200]})
    dedup = {}
    for row in results:
        if row.get("license_ok") and row.get("source_url") and row.get("download_url"):
            dedup[row["id"]] = row
    return list(dedup.values()), errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="discovery_output")
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()
    target = Path(args.out)
    target.mkdir(parents=True, exist_ok=True)
    catalog, errors = discover(limit=args.limit)
    (target / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    (target / "errors.json").write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8")
    build_review(catalog, target / "review.html")
    print(json.dumps({"usable_items": len(catalog), "errors": errors}, ensure_ascii=False))
    if not catalog:
        raise SystemExit("No verifiably reusable live footage metadata returned")

if __name__ == "__main__":
    main()
