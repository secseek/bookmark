import re
import html
import os


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

    # 完全なHTMLドキュメントの生成
    html_document = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>secseekのブックマーク集</title>
  <meta name="description" content="secseekによる技術ブックマーク集（ネットワーク・データベース・Web開発）">
  <meta name="author" content="secseek">
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

    # .nojekyll ファイルの作成
    with open("out/.nojekyll", "w", encoding="utf-8") as f:
        f.write("")


if __name__ == "__main__":
    build()
