# AI Research Tool

**中文** | [English](#english)

每日多源 AI 资讯聚合工具。自动抓取 GitHub Trending 热门项目与 arXiv 最新论文，支持个性化兴趣配置、AI 相关性评分和去重推送。零依赖，开箱即用。

## 功能

- 🔥 **GitHub Trending**：今日/本周/本月热门项目，含描述和 Star 增长
- 📚 **arXiv 论文**：按分类（cs.AI / cs.LG / cs.CL 等）抓取最新论文
- 🎯 **AI 相关性评分**：用 GPT 对每篇论文打分，按相关性过滤和排序（可选）
- 🔁 **增量去重**：记录已推送内容，避免重复
- ⚙️ **config.yaml**：个性化研究兴趣配置
- 🤖 **GitHub Actions**：Fork 即用，每天 UTC 00:00 自动生成并提交报告

## 快速开始

```bash
git clone https://github.com/kanosa0101/ai-research-tool.git
cd ai-research-tool
python3 ai_research.py
```

无需安装任何依赖（`pyyaml` 可选，用于读取 `config.yaml`）。

## 配置

编辑 `config.yaml` 自定义研究兴趣：

```yaml
arxiv:
  categories: [cs.AI, cs.LG, cs.CL, cs.MA]
  interests: |
    LLM agents, self-improving AI, agentic workflows, MCP
  min_score: 6      # AI 评分阈值（1-10）
  max_fetch: 30

github:
  since: daily      # daily | weekly | monthly
  language: ""      # 语言过滤，如 python
  top: 10

output:
  top_papers: 10
  top_repos: 10
  ai_scoring: false # 设为 true 并配置 OPENAI_API_KEY 启用
```

## 用法

```bash
# 默认运行（使用 config.yaml）
python3 ai_research.py

# 自定义关键词
python3 ai_research.py --keywords "MCP agent tool-use" --since weekly

# 保存为文件
python3 ai_research.py --output reports/today.md

# 增量模式（跳过已推送内容）
python3 ai_research.py --incremental --output reports/today.md

# 启用 AI 评分
OPENAI_API_KEY=sk-... python3 ai_research.py --score
```

| 参数 | 说明 |
|------|------|
| `--config` | 配置文件路径（默认：config.yaml） |
| `--keywords` | 覆盖 arXiv 搜索关键词 |
| `--since` | GitHub Trending 时间范围：`daily / weekly / monthly` |
| `--language` | GitHub Trending 语言过滤 |
| `--top` | 每个来源显示的条目数 |
| `--output` | 输出 Markdown 文件路径 |
| `--incremental` | 增量模式，跳过已推送内容 |
| `--score` | 启用 AI 相关性评分（需 `OPENAI_API_KEY`） |

## GitHub Actions 自动化

Fork 本仓库后，每天 UTC 00:00 自动运行，报告保存至 `reports/` 目录。

可选：在仓库 Settings → Secrets 中添加 `OPENAI_API_KEY` 启用 AI 评分。

也可手动触发：Actions → Daily AI Research Briefing → Run workflow。

---

<a name="english"></a>

## English

A lightweight, zero-dependency tool that aggregates AI news from GitHub Trending and arXiv papers into a daily Markdown briefing, with optional AI relevance scoring.

### Features

- 🔥 **GitHub Trending** — Top repos with descriptions and star growth
- 📚 **arXiv Papers** — Latest papers by category (cs.AI / cs.LG / cs.CL etc.)
- 🎯 **AI Relevance Scoring** — GPT-powered scoring and filtering (optional)
- 🔁 **Incremental dedup** — Tracks seen items, no repeats
- ⚙️ **config.yaml** — Personalized research interest configuration
- 🤖 **GitHub Actions** — Fork and forget; auto-runs daily at UTC 00:00

### Quick Start

```bash
git clone https://github.com/kanosa0101/ai-research-tool.git
cd ai-research-tool
python3 ai_research.py
```

No dependencies required (`pyyaml` optional for config.yaml support).

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--config` | `config.yaml` | Config file path |
| `--keywords` | — | Override arXiv search keywords |
| `--since` | `daily` | GitHub Trending window: `daily / weekly / monthly` |
| `--language` | *(any)* | Filter by programming language |
| `--top` | `5` | Results per source |
| `--output` | *(stdout)* | Save report to Markdown file |
| `--incremental` | — | Skip already-seen items |
| `--score` | — | Enable AI relevance scoring (requires `OPENAI_API_KEY`) |

### GitHub Actions

Fork the repo. Reports are automatically committed to `reports/` daily.
Optionally add `OPENAI_API_KEY` as a repository secret to enable AI scoring.

## License

MIT
