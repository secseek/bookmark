import re
import html


def build():
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

    # HTMLの生成
    html_out = []
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
        html_out.append(entry)

    with open("out/index_content.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_out))


if __name__ == "__main__":
    build()
