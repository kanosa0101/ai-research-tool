# AI Research Tool

**中文** | [English](#english)

每日多源 AI 资讯聚合工具。自动抓取 GitHub Trending 热门项目与 arXiv 最新论文，生成结构化 Markdown 简报。零依赖，开箱即用。

---

## 功能

- 🔥 **GitHub Trending**：抓取今日/本周/本月热门项目，含描述和 Star 增长
- 📚 **arXiv 论文**：按关键词搜索最新论文，含摘要和作者
- 📄 **Markdown 输出**：可打印到终端或保存为文件
- ⚙️ **灵活配置**：支持关键词、时间范围、语言过滤、条目数量

## 安装

无需安装，Python 3.8+ 直接运行：

```bash
git clone https://github.com/kanosa0101/ai-research-tool.git
cd ai-research-tool
python3 ai_research.py
```

## 用法

```bash
# 默认：今日热门 + LLM Agent 相关论文
python3 ai_research.py

# 自定义关键词和时间范围
python3 ai_research.py --keywords "MCP agent tool-use" --since weekly

# 保存为文件
python3 ai_research.py --output report.md

# 只看 Python 项目，取 Top 10
python3 ai_research.py --language python --top 10
```

## 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--keywords` | `LLM agent agentic self-reflection` | arXiv 搜索关键词 |
| `--since` | `daily` | GitHub Trending 时间范围：`daily / weekly / monthly` |
| `--language` | *(不限)* | GitHub Trending 语言过滤（如 `python`） |
| `--top` | `5` | 每个数据源显示的条目数 |
| `--output` | *(终端)* | 输出 Markdown 文件路径 |

## 示例输出

```markdown
# 每日 AI 调研简报 — 2026-02-28

## 🔥 GitHub 今日热门（Top 5）
- **anthropics/claude-code** ⭐ +705 — Agentic coding tool...

## 📚 arXiv 最新论文（Top 5）
### SELAUR: Self Evolving LLM Agent via Uncertainty-aware Rewards
*2026-02-25 · Dengjia Zhang et al.*
...
```

## 定时运行

配合 cron 每日自动生成简报：

```bash
# 每天 UTC 00:00 运行
0 0 * * * python3 /path/to/ai_research.py --output /path/to/reports/daily_$(date +\%Y-\%m-\%d).md
```

---

<a name="english"></a>

## English

A lightweight, zero-dependency tool that aggregates AI news from multiple sources — GitHub Trending and arXiv papers — into a daily Markdown briefing.

### Features

- 🔥 **GitHub Trending**: Top repos with descriptions and star growth
- 📚 **arXiv Papers**: Latest papers by keyword, with abstracts
- 📄 **Markdown output**: Print to stdout or save to file
- ⚙️ **Flexible**: Filter by keyword, time range, language, and result count

### Install

No dependencies required. Python 3.8+:

```bash
git clone https://github.com/kanosa0101/ai-research-tool.git
cd ai-research-tool
python3 ai_research.py
```

### Usage

```bash
# Default: today's trending + LLM agent papers
python3 ai_research.py

# Custom keywords and time range
python3 ai_research.py --keywords "MCP agent tool-use" --since weekly

# Save to file
python3 ai_research.py --output report.md

# Python repos only, top 10
python3 ai_research.py --language python --top 10
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--keywords` | `LLM agent agentic self-reflection` | arXiv search query |
| `--since` | `daily` | GitHub Trending window: `daily / weekly / monthly` |
| `--language` | *(any)* | Filter by programming language (e.g. `python`) |
| `--top` | `5` | Results per source |
| `--output` | *(stdout)* | Save report to Markdown file |

### Scheduled runs

```bash
# Daily at UTC 00:00
0 0 * * * python3 /path/to/ai_research.py --output /path/to/reports/daily_$(date +\%Y-\%m-\%d).md
```

## License

MIT
