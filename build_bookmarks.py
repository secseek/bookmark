import re
import html
import os
import json
from datetime import datetime


def build():
    # 出力ディレクトリの作成
    os.makedirs("out", exist_ok=True)

    with open("secseek.bookmarks.html", "r", encoding="utf-8") as f:
        content = f.read()

    # DTとDDのペアを正規表現で抽出
    # DT内のAタグからURLとタイトル、TAGS属性、直後のDDからコメントを取得
    pattern = re.compile(
        r'<DT><A HREF="(?P<url>.*?)"(?:[^>]*\sTAGS="(?P<tags>[^"]*)")?[^>]*>(?P<title>.*?)</A>\s*(?:<DD>(?P<comment>.*?))?(?=\s*<DT|\s*</DL)',
        re.DOTALL | re.IGNORECASE,
    )

    items = []
    for match in pattern.finditer(content):
        items.append(match.groupdict())

    # ブックマークアイテムHTMLの生成
    html_items = []
    for item in items:
        url = item["url"]
        title = item["title"]
        comment = item["comment"].strip() if item["comment"] else ""
        tags = item["tags"] if item["tags"] else ""

        # AIが理解しやすいセマンティックな構造
        tags_attr = f' data-tags="{html.escape(tags)}"' if tags else ""
        entry = f"""
        <article class="bookmark-item"{tags_attr}>
            <h3><a href="{url}" rel="bookmark">{title}</a></h3>
            {f'<blockquote class="my-comment">{comment}</blockquote>' if comment else ''}
        </article>"""
        html_items.append(entry)

    # CSS の読み込み
    with open("assets/style.css", "r", encoding="utf-8") as f:
        css_content = f.read()

    # JSON-LD 構造化データの生成
    json_ld_items = []
    for item in items:
        url = item["url"]
        title = item["title"]
        tags = item["tags"] if item["tags"] else ""

        # BreadcrumbList の代わりに WebPage アイテムを構築
        json_item = {
            "@type": "WebPage",
            "url": url,
            "name": title,
        }
        if tags:
            json_item["keywords"] = tags
        json_ld_items.append(json_item)

    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "secseekのブックマーク集",
        "description": "secseekによる技術ブックマーク集（ネットワーク・データベース・Web開発）",
        "author": {"@type": "Person", "name": "secseek"},
        "mainEntity": {
            "@type": "Collection",
            "name": "技術ブックマーク",
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
<main>
{"".join(html_items)}
</main>
</div>
</body>
</html>"""

    # HTMLドキュメントをファイルに保存
    with open("out/index.html", "w", encoding="utf-8") as f:
        f.write(html_document)

    # sitemap.xml の生成
    sitemap_urls = []
    # メインページ
    sitemap_urls.append({"loc": "index.html", "priority": "1.0"})
    # ブックマークアイテムのURL（外部サイト）も含める
    for item in items:
        url = item["url"]
        sitemap_urls.append({"loc": url, "priority": "0.8"})

    current_date = datetime.now().strftime("%Y-%m-%d")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""

    for url_entry in sitemap_urls:
        sitemap_xml += f"""  <url>
    <loc>{html.escape(url_entry['loc'])}</loc>
    <lastmod>{current_date}</lastmod>
    <priority>{url_entry['priority']}</priority>
  </url>
"""

    sitemap_xml += """</urlset>"""

    with open("out/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    # .nojekyll ファイルの作成
    with open("out/.nojekyll", "w", encoding="utf-8") as f:
        f.write("")


if __name__ == "__main__":
    build()
