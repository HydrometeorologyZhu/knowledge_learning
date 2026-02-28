import os
import shutil
from app import app, CATEGORIES, get_posts

BUILD_DIR = "docs"

def save_html(path, content):
    full_path = os.path.join(BUILD_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # 修正绝对路径问题（核心关键）
    html = content.decode("utf-8")
    html = html.replace('href="/', 'href="')
    html = html.replace('src="/', 'src="')
    html = html.replace('url("/', 'url("')

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(html)

def try_get(client, url):
    response = client.get(url)
    if response.status_code == 200:
        return response
    return None

def build():
    # 清空旧 docs
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)

    client = app.test_client()

    # 首页
    response = try_get(client, "/")
    if response:
        save_html("index.html", response.data)

    for category in CATEGORIES:

        # 分类页
        response = try_get(client, f"/{category}/")
        if response:
            save_html(f"{category}/index.html", response.data)

        posts = get_posts(category)

        for post in posts:
            post_name = post.replace(".md", "")

            response = try_get(client, f"/{category}/{post_name}.html")
            if not response:
                response = try_get(client, f"/{category}/{post}")

            if response:
                save_html(f"{category}/{post_name}.html", response.data)
            else:
                print(f"⚠ 未生成: {category}/{post_name}")

    print("✅ Static site successfully built in /docs")

if __name__ == "__main__":
    build()