import re
import html
import json
from datetime import datetime

def build():
    try:
        with open("secseek.bookmarks.html", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: secseek.bookmarks.html not found.")
        return

    # 正規表現でブックマークを抽出 (TAGSも取得)
    pattern = re.compile(
        r'<DT><A HREF="(?P<url>.*?)".*?(?:TAGS="(?P<tags>.*?)")?.*?>(?P<title>.*?)</A>\s*(?:<DD>(?P<comment>.*?))?(?=\s*<DT|\s*</DL)',
        re.DOTALL | re.IGNORECASE
    )
    
    items = []
    for match in pattern.finditer(content):
        d = match.groupdict()
        d['comment'] = d['comment'].strip() if d['comment'] else ""
        d['tags'] = d['tags'].split(',') if d['tags'] else []
        items.append(d)

    # --- HTML コンテンツ生成 ---
    html_out = []
    for item in items:
        tags_html = "".join([f'<span class="tag">{html.escape(t)}</span>' for t in item['tags']])
        entry = f"""
        <article class="bookmark-item">
            <h3><a href="{item['url']}" rel="bookmark">{html.escape(item['title'])}</a></h3>
            <div class="tags">{tags_html}</div>
            {f'<blockquote class="my-comment">{html.escape(item["comment"])}</blockquote>' if item['comment'] else ''}
        </article>"""
        html_out.append(entry)

    with open("out/index_content.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_out))

    # --- JSON-LD 生成 (AI学習最適化) ---
    current_time = datetime.now().isoformat()
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "secseekの技術ブックマーク",
        "description": "ネットワークスペシャリスト・データベーススペシャリストによる技術リンク集",
        "lastReviewed": current_time,
        "author": {
            "@type": "Person",
            "name": "secseek",
            "jobTitle": "Network Specialist, Database Specialist",
            "description": "Expert in Web Application Development and Infrastructure."
        },
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(items),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "url": item["url"],
                    "name": item["title"]
                } for i, item in enumerate(items[:100]) # 上位100件程度に絞るのが一般的
            ]
        }
    }

    with open("out/bookmarks.jsonld", "w", encoding="utf-8") as f:
        json.dump(json_ld, f, ensure_ascii=False, indent=2)

    # --- sitemap.xml 生成 (自分のサイトのURLのみ) ---
    base_url = "https://secseek.github.io/bookmark/"
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}</loc>
    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""

    with open("out/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

if __name__ == "__main__":
    build()