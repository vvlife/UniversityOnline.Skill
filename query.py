#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, json, time, urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------- 配置 ----------
MAX_COURSES = 10            # 每个专业返回的课程上限
MAX_BOOKS   = 2             # 每门课程推荐的教材数量
REPORT_DIR  = Path("/var/minis/workspace/prof-course-books")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 预设课程库 ----------
PRESET_COURSES = {
    "计算机科学": [
        {"title": "Introduction to Computer Science", "school": "Harvard", "url": "https://cs50.harvard.edu/"},
        {"title": "Data Structures and Algorithms", "school": "MIT", "url": "https://ocw.mit.edu/courses/6-006-intro-algorithms/"},
        {"title": "Operating Systems", "school": "Stanford", "url": "https://os.stanford.edu/"},
        {"title": "Database Systems", "school": "CMU", "url": "https://15445.courses.cs.cmu.edu/"},
        {"title": "Computer Networks", "school": "MIT", "url": "https://ocw.mit.edu/courses/6-829-computer-networks/"},
        {"title": "Artificial Intelligence", "school": "UC Berkeley", "url": "https://ai.berkeley.edu/"},
    ],
    "数学": [
        {"title": "Calculus I", "school": "MIT", "url": "https://ocw.mit.edu/courses/18-01sc-single-variable-calculus/"},
        {"title": "Linear Algebra", "school": "MIT", "url": "https://ocw.mit.edu/courses/18-06-linear-algebra/"},
        {"title": "Probability & Statistics", "school": "Stanford", "url": "https://online.stanford.edu/courses/stats116-theory-statistics/"},
        {"title": "Differential Equations", "school": "MIT", "url": "https://ocw.mit.edu/courses/18-03sc-differential-equations/"},
        {"title": "Real Analysis", "school": "Harvard", "url": "https://math.harvard.edu/"},
    ],
    "物理": [
        {"title": "Classical Mechanics", "school": "MIT", "url": "https://ocw.mit.edu/courses/8-01sc-classical-mechanics/"},
        {"title": "Quantum Mechanics", "school": "MIT", "url": "https://ocw.mit.edu/courses/8-04-quantum-physics/"},
        {"title": "Thermodynamics", "school": "Caltech", "url": "https://www.its.caltech.edu/courses/thermodynamics"},
        {"title": "Electromagnetism", "school": "MIT", "url": "https://ocw.mit.edu/courses/8-02-electricity-and-magnetism/"},
        {"title": "Astrophysics", "school": "Yale", "url": "https://oyc.yale.edu/astronomy/astr-160"},
    ],
    "数据科学": [
        {"title": "Data Science Specialization", "school": "JHU", "url": "https://www.coursera.org/specializations/jhu-data-science"},
        {"title": "Statistical Learning", "school": "Stanford", "url": "https://online.stanford.edu/courses/stats216-statistical-learning"},
        {"title": "Data Mining", "school": "Stanford", "url": "https://online.stanford.edu/courses/soe-ycsdatamining-2014"},
    ],
}

# ---------- 辅助函数 ----------
def translate_to_en(chinese: str) -> str:
    """中文转英文关键词"""
    map_zh_en = {
        "计算机科学": "computer science",
        "数学": "mathematics",
        "物理": "physics",
        "数据科学": "data science",
        "人工智能": "artificial intelligence",
        "机器学习": "machine learning",
    }
    return map_zh_en.get(chinese.strip(), chinese)

def search_courses(keyword: str):
    """根据关键词返回预设或公开课程"""
    results = []
    lower_kw = keyword.lower()
    
    # 先查预设库
    if lower_kw in PRESET_COURSES:
        results.extend(PRESET_COURSES[lower_kw][:MAX_COURSES])
    else:
        # 如果没有预设，回退到逐字匹配部分关键词
        for prof, courses in PRESET_COURSES.items():
            if lower_kw in prof.lower() or any(keyword in c["title"].lower() for c in courses):
                results.extend(courses[:MAX_COURSES - len(results)])
                if len(results) >= MAX_COURSES:
                    break
    
    # 补充搜索（如果未达到上限）
    if len(results) < MAX_COURSES:
        try:
            headers = {"User-Agent": "MinisSkill/1.0"}
            # 模拟 Open Syllabus 查询
            query_url = f"https://api.opensyllabus.org/search?q={urllib.parse.quote(keyword)}&limit={MAX_COURSES - len(results)}"
            resp = requests.get(query_url, headers=headers, timeout=8)
            if resp.ok:
                data = resp.json()
                if isinstance(data, dict) and "results" in data:
                    for item in data["results"]:
                        if len(results) >= MAX_COURSES:
                            break
                        results.append({
                            "title": item.get("title", f"Course: {keyword}"),
                            "school": item.get("school", "Various"),
                            "url": item.get("url", "#")
                        })
        except Exception as e:
            print(f"[提示] 公开课程搜索未命中: {e}", file=sys.stderr)
    
    # 去重
    seen = set()
    uniq = []
    for r in results:
        k = (r["title"], r["school"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    return uniq[:MAX_COURSES]

def search_books(course_title: str):
    """在 Open Library 和 Google Books 中检索教材"""
    books = []
    
    # Open Library
    try:
        ol_url = f"https://openlibrary.org/search.json?title={urllib.parse.quote(course_title)}&limit=5"
        data = requests.get(ol_url, timeout=8).json()
        for doc in data.get("docs", [])[:MAX_BOOKS]:
            if "title" in doc and "author_name" in doc:
                books.append({
                    "title": doc["title"],
                    "authors": ", ".join(doc["author_name"]),
                    "publisher": (doc.get("publisher") or [""])[0]
                })
    except Exception:
        pass
    
    # Google Books fallback
    if len(books) < MAX_BOOKS:
        try:
            gb_url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote(course_title)}&maxResults={MAX_BOOKS - len(books)}"
            data = requests.get(gb_url, timeout=8).json()
            for item in data.get("items", []):
                vol = item.get("volumeInfo", {})
                books.append({
                    "title": vol.get("title", ""),
                    "authors": ", ".join(vol.get("authors", [])),
                    "publisher": vol.get("publisher", "")
                })
        except Exception:
            pass
    
    return books[:MAX_BOOKS]

def build_report(prof: str, courses):
    """生成 Markdown 报告"""
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = REPORT_DIR / f"report-{ts}.md"
    lines = [f"# {prof} 专业课程与教材推荐", ""]
    lines.append("| 课程 | 授课高校 | 课程链接 | 推荐教材 |")
    lines.append("|---|---|---|---|")
    for c in courses:
        books = c.get("books", [])
        book_str = "<br/>".join(
            f"**{b['title']}** – {b['authors']} ({b['publisher']})"
            for b in books
        ) if books else "暂无教材信息"
        lines.append(f"| {c['title']} | {c['school']} | [Link]({c['url']}) | {book_str} |")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path

def main():
    if len(sys.argv) < 2:
        print("用法: query.py <专业名称>")
        sys.exit(1)
    
    raw_prof = " ".join(sys.argv[1:]).strip()
    print(f"正在查询专业: {raw_prof}")
    kw = translate_to_en(raw_prof)
    print(f"搜索关键词: {kw}")
    
    courses = search_courses(kw)
    print(f"找到 {len(courses)} 门课程")
    
    for c in courses:
        print(f"  - 正在搜索教材: {c['title']}")
        c["books"] = search_books(c["title"])
    
    report = build_report(raw_prof, courses)
    print(f"\n报告: {report}")
    
    # 输出表格
    print("\n| 课程 | 授课高校 | 课程链接 | 推荐教材 |")
    print("|---|---|---|---|")
    for c in courses:
        books = c["books"]
        book_str = " | ".join(
            f"**{b['title']}** – {b['authors']} ({b['publisher']})"
            for b in books
        ) if books else "暂无教材信息"
        print(f"| {c['title']} | {c['school']} | [Link]({c['url']}) | {book_str} |")
    
    print(f"\n[查看完整报告](minis://workspace/prof-course-books/{report.name})")

if __name__ == "__main__":
    main()
