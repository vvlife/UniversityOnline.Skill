# 专业‑课程‑教材查询 Skill

一个用于 Minis (iOS) 的技能，可以根据输入的专业名称，自动查询该专业在主流高校的核心课程及对应的推荐教材。

## 功能特点

- 🎓 **专业课程查询**：支持中英文专业名称输入
- 📚 **教材推荐**：自动从 Open Library 和 Google Books 检索推荐教材
- 🏫 **多校课程**：整合 MIT、Stanford、Harvard 等知名高校课程
- 📊 **结构化输出**：生成 Markdown 表格，方便阅读和分享
- 📄 **完整报告**：自动生成详细报告文件，可在聊天中直接预览

## 支持的专业

目前预设支持以下专业（可扩展）：
- 计算机科学 (Computer Science)
- 数学 (Mathematics)
- 物理 (Physics)
- 数据科学 (Data Science)

## 安装方法

### 1. 在 Minis 中安装依赖
```bash
apk add py3-requests py3-beautifulsoup4
pip install --user googletrans==4.0.0-rc1
```

### 2. 将技能文件放入正确位置
确保以下文件结构：
```
/var/minis/skills/prof-course-books/
├── SKILL.md          # 技能说明（必需）
├── query.py          # 主查询脚本
└── README.md         # 本文件
```

## 使用方法

在 Minis 聊天中输入：
```
/skill prof-course-books <专业名称>
```

### 示例
```
/skill prof-course-books 计算机科学
/skill prof-course-books mathematics
```

## 输出格式

查询结果会以 Markdown 表格形式展示：

| 课程 | 授课高校 | 课程链接 | 推荐教材 |
|------|----------|----------|----------|
| ... | ... | ... | ... |

同时会生成一个完整的报告文件，路径类似：  
`/var/minis/workspace/prof-course-books/report-YYYYMMDD-HHMMSS.md`

## 技术实现

- **搜索源**：Open Library API、Google Books API
- **预设课程**：内置常见专业的核心课程列表
- **翻译支持**：使用 googletrans 进行中英文转换
- **数据清洗**：自动去重、格式化输出

## 扩展方法

要添加更多专业，请编辑 `query.py` 中的 `PRESET_COURSES` 字典：

```python
PRESET_COURSES = {
    "你的专业": [
        {"title": "课程名", "school": "学校", "url": "链接"},
        # 更多课程...
    ],
    # 更多专业...
}
```

## 注意事项

- 公开 API 有调用频率限制，建议合理使用
- 部分教材信息可能不完整，以实际查询结果为准
- 需要网络连接才能查询最新课程和教材信息

## 许可

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个技能！
