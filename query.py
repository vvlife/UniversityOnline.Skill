#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, json, time, urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------- 配置 ----------
MAX_COURSES = 12
MAX_BOOKS   = 3
REPORT_DIR  = Path("/var/minis/workspace/prof-course-books")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 专业翻译 ----------
def translate_to_en(chinese: str) -> str:
    text = chinese.strip()
    # 直接返回，依赖后续的宽泛搜索
    return text

# ---------- 宽泛教材搜索 ----------
def search_books_for_keyword(keyword: str):
    """通用教材搜索"""
    books = []
    headers = {"User-Agent": "MinisSkill/1.0"}
    
    # Open Library
    try:
        url = f"https://openlibrary.org/search.json?q={urllib.parse.quote(keyword)}&limit=10"
        data = requests.get(url, headers=headers, timeout=10).json()
        for doc in data.get("docs", [])[:MAX_BOOKS]:
            if "title" in doc and "author_name" in doc:
                books.append({
                    "title": doc["title"][:100],
                    "authors": ", ".join(doc["author_name"][:2]),
                    "publisher": (doc.get("publisher") or [""])[0][:50]
                })
        if len(books) >= MAX_BOOKS:
            return books[:MAX_BOOKS]
    except Exception:
        pass
    
    # Google Books
    if len(books) < MAX_BOOKS:
        try:
            gurl = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote(keyword)}&maxResults={MAX_BOOKS - len(books)}&printType=books&orderBy=relevance"
            data = requests.get(gurl, headers=headers, timeout=10).json()
            for item in data.get("items", [])[:MAX_BOOKS - len(books)]:
                vi = item.get("volumeInfo", {})
                if vi.get("title"):
                    books.append({
                        "title": vi["title"][:100],
                        "authors": ", ".join(vi.get("authors", [])[:2]),
                        "publisher": vi.get("publisher", "")[:50]
                    })
        except Exception:
            pass
    
    return books[:MAX_BOOKS]

def build_report(prof: str, books, keyword: str):
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = REPORT_DIR / f"report-{ts}.md"
    lines = [
        f"# {prof} 专业课程与教材推荐",
        "",
        f"> 搜索关键词：{keyword}",
        f"> 找到教材数：{len(books)}",
        f"> 数据来源：Open Library、Google Books",
        "",
        "| 序号 | 教材名称 | 作者 / 出版社 |",
        "|------|----------|----------------|",
    ]
    for i, b in enumerate(books, 1):
        lines.append(f"| {i} | {b['title']} | {b['authors']} ({b['publisher']}) |")
    lines.extend(["", f"*报告生成: {time.strftime('%Y-%m-%d %H:%M:%S')}*"])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path

def main():
    if len(sys.argv) < 2:
        print("用法: query.py <专业名称>")
        sys.exit(1)
    
    raw = " ".join(sys.argv[1:]).strip()
    print(f"🔍 查询专业: {raw}")
    kw = translate_to_en(raw)
    print(f"📚 关键词: {kw}")
    
    books = search_books_for_keyword(kw)
    print(f"✅ 找到 {len(books)} 本教材")
    
    if not books:
        print("⚠️  未找到教材，请尝试其他关键词。")
        sys.exit(0)
    
    report = build_report(raw, books, kw)
    print(f"📄 报告: {report}")
    
    print("\n" + "="*60)
    print(f"📚 {raw} - 教材推荐")
    print("="*60)
    for i, b in enumerate(books, 1):
        print(f"{i}. {b['title']}")
        print(f"   作者/出版社：{b['authors']} ({b['publisher']})")
    print("="*60)
    print(f"\n📄 [查看完整报告](minis://workspace/prof-course-books/{report.name})")

if __name__ == "__main__":
    main()
