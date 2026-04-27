# 专业‑课程‑教材查询 Skill

## 目标
输入任意专业名称，返回该专业在中国/美国主流高校常见核心课程及每门课程的推荐教材信息。

## 工作流程
1. **专业 → 关键词**
   - 将用户输入的专业名称统一转为英文关键词（使用 `googletrans` 简单翻译，或直接使用英文）。
2. **检索课程列表**
   - 通过公开的 OpenCourseWare、MIT OCW、Stanford Online、Coursera、edX 等平台的 API（或页面抓取）获取与关键词匹配的前 **10** 门核心课程。
   - 只保留课程标题、授课学校、课程链接。
3. **检索教材**
   - 对每个课程标题在 **Open Library**（`openlibrary.org/search.json`）和 **Google Books**（`books.googleapis.com/v1/volumes`）进行搜索。
   - 选取出版时间最近、评分最高的前 **2** 本书作为推荐教材。
4. **组织结果**
   - 以 Markdown 表格返回：
     | 课程 | 授课高校 | 课程链接 | 推荐教材 |。
   - 同时提供一个 **minis://** 链接指向生成的完整报告（`/var/minis/workspace/prof-course-books/report-<timestamp>.md`），用户可点击查看全部细节。

## 输入格式
```bash
/skill prof-course-books <专业名称>
```
示例：
```
/skill prof-course-books 计算机科学
```

## 输出示例
```
以下是「计算机科学」专业的核心课程及对应教材：

| 课程 | 授课高校 | 课程链接 | 推荐教材 |
|------|----------|----------|----------|
| … | … | … | … |
```

## 依赖
- `requests`（已在 Alpine 中通过 `apk add py3-requests` 提供）
- `beautifulsoup4`（`apk add py3-beautifulsoup4`）
- `googletrans==4.0.0‑rc1`（纯 Python，可 `pip install`）

## 运行方式
```bash
python3 /var/minis/skills/prof-course-books/query.py "<专业名称>"
```

## 注意事项
- 本 Skill 采用公开 API，调用频率受限。如需大量查询请自行申请对应 API Key（如 Google Books）。
- 若搜索不到教材，返回 "暂无教材信息"。
- 仅返回公开可访问的教材信息，不涉及付费链接。
