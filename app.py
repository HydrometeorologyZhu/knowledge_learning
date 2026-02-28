import os
from flask import Flask, render_template, abort
import markdown

app = Flask(__name__)

CONTENT_DIR = "content"
CATEGORIES = ["hydrology", "meteorology", "codes", "culture", "movies"]

def get_posts(category):
    path = os.path.join(CONTENT_DIR, category)
    if not os.path.exists(path):
        return []
    files = [f for f in os.listdir(path) if f.endswith(".md")]
    return sorted(files)

def read_markdown(category, filename):
    filepath = os.path.join(CONTENT_DIR, category, filename)
    if not os.path.exists(filepath):
        abort(404)
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
        html = markdown.markdown(text, extensions=["fenced_code", "tables"])
    return html

@app.route("/")
def index():
    return render_template("index.html", categories=CATEGORIES)

@app.route("/<category>/")
def category(category):
    if category not in CATEGORIES:
        abort(404)
    posts = get_posts(category)
    return render_template("category.html", category=category, posts=posts)

@app.route("/<category>/<post>.html")
def post(category, post):
    if category not in CATEGORIES:
        abort(404)
    content = read_markdown(category, post + ".md")
    return render_template("post.html", content=content, category=category)

if __name__ == "__main__":
    app.run(debug=True)