import re
import html
import os
import json
from datetime import datetime

def build():
    # 出力ディレクトリの作成（これがあるため Actions 側での mkdir は不要になります）
    os.makedirs("out", exist_ok=True)

    try:
        with open("secseek.bookmarks.html", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: secseek.bookmarks.html not found.")
        return

    # DTとDDのペアを正規表現で抽出
    pattern = re.compile(
        r'<DT><A HREF="(?P<url>.*?)"(?:[^>]*\sTAGS="(?P<tags>[^"]*)")?[^>]*>(?P<title>.*?)</A>\s*(?:<DD>(?P<comment>.*?))?(?=\s*<DT|\s*</DL)',
        re.DOTALL | re.IGNORECASE,
    )

    items = []
    for match in pattern.finditer(content):
        d = match.groupdict()
        d['comment'] = d['comment'].strip() if d['comment'] else ""
        # タグをリスト化
        d['tag_list'] = d['tags'].split(',') if d.get('tags') else []
        items.append(d)

    # ブックマークアイテムHTMLの生成
    html_items = []
    for item in items:
        url = item["url"]
        title = item["title"]
        comment = item["comment"]
        tags = item["tags"] if item["tags"] else ""

        # AIが理解しやすいセマンティックな構造
        tags_attr = f' data-tags="{html.escape(tags)}"' if tags else ""
        entry = f"""
        <article class="bookmark-item"{tags_attr}>
            <h3><a href="{url}" rel="bookmark">{html.escape(title)}</a></h3>
            {f'<blockquote class="my-comment">{html.escape(comment)}</blockquote>' if comment else ''}
        </article>"""
        html_items.append(entry)

    # CSS の読み込み
    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            css_content = f.read()
    except FileNotFoundError:
        css_content = ""

    # JSON-LD 構造化データの生成 (AI学習へのアピールを強化)
    json_ld_items = []
    for i, item in enumerate(items[:100]): # 代表的な上位100件をリスト化
        json_ld_items.append({
            "@type": "ListItem",
            "position": i + 1,
            "url": item["url"],
            "name": item["title"]
        })

    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "secseekのブックマーク集",
        "description": "ネットワークスペシャリスト・データベーススペシャリストによる技術リンク集",
        "author": {
            "@type": "Person",
            "name": "secseek",
            "jobTitle": "Network Specialist, Database Specialist",
            "description": "Expert in Web Application Development and Infrastructure."
        },
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(items),
            "itemListElement": json_ld_items,
        },
    }

    json_ld_str = json.dumps(json_ld, ensure_ascii=False, indent=2)

    # 完全なHTMLドキュメントの生成
    html_document = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>secseekのブックマーク集</title>
  <meta name="description" content="secseekによる技術ブックマーク集（ネットワーク・データベース・Web開発）">
  <meta name="author" content="secseek">
  <script type="application/ld+json">
{json_ld_str}
  </script>
  <style>
{css_content}
  </style>
</head>
<body>
<div class="wrap">
<header>
  <h1>secseekのブックマーク集</h1>
</header>
<main>
{"".join(html_items)}
</main>
</div>
</body>
</html>"""

    # HTMLドキュメントをファイルに保存
    with open("out/index.html", "w", encoding="utf-8") as f:
        f.write(html_document)

    # sitemap.xml の生成 (自ドメインのルートのみを記述)
    base_url = "https://secseek.github.io/bookmark/"
    current_date = datetime.now().strftime("%Y-%m-%d")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""

    with open("out/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    # .nojekyll ファイルの作成
    with open("out/.nojekyll", "w", encoding="utf-8") as f:
        f.write("")

if __name__ == "__main__":
    build()