"""Generate an iPhone-friendly human review page. Escapes user-supplied metadata."""
from html import escape
from pathlib import Path

def build_review(items, output):
    cards = []
    for item in items:
        if not item.get("license_ok"):
            continue
        title = escape(str(item.get("title", "")))
        license_name = escape(str(item.get("license", "")))
        author = escape(str(item.get("author", "")))
        src = escape(str(item.get("preview_url", "")), quote=True)
        url = escape(str(item.get("source_url", "")), quote=True)
        img = f'<img loading="lazy" src="{src}" alt="preview">' if src.startswith("https://") else ""
        cards.append(f'<article>{img}<div><b>{title}</b><p>{license_name} — {author}</p><a href="{url}" target="_blank" rel="noopener noreferrer">素材原典を見る</a></div></article>')
    html = """<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MV候補素材</title><style>body{background:#111;color:#eee;font:16px system-ui;margin:20px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}article{background:#222;border-radius:12px;overflow:hidden}article div{padding:12px}img{width:100%;aspect-ratio:16/9;object-fit:cover}p{color:#aaa;font-size:13px}a{color:#bde0ff}</style>
<h1>MV候補素材（権利・内容要レビュー）</h1><p>未ダウンロード・未編集。映像の内容とライセンスは原典で最終確認してください。</p><main>""" + "".join(cards) + "</main></html>"
    Path(output).write_text(html, encoding="utf-8")
