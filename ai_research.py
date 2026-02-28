#!/usr/bin/env python3
"""
Multi-Source AI Research Tool v1.1
Daily briefing: GitHub Trending + arXiv papers with optional AI relevance scoring.

Usage:
    python3 ai_research.py
    python3 ai_research.py --config config.yaml
    python3 ai_research.py --keywords "MCP agent" --since weekly --output report.md
    python3 ai_research.py --score --incremental
"""

import argparse
import json
import os
import re
import html
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

DEFAULT_CONFIG = {
    "arxiv": {
        "categories": ["cs.AI", "cs.LG", "cs.CL"],
        "interests": "LLM agents, self-improving AI, agentic workflows, multi-agent systems",
        "min_score": 6,
        "max_fetch": 30,
    },
    "github": {"since": "daily", "language": "", "top": 10},
    "output": {"top_papers": 10, "top_repos": 10, "ai_scoring": False},
}

STATE_FILE = Path(".ai_research_state.json")


def load_config(path=None):
    cfg = {k: dict(v) for k, v in DEFAULT_CONFIG.items()}
    if path and Path(path).exists() and HAS_YAML:
        with open(path) as f:
            user = yaml.safe_load(f) or {}
        for section, values in user.items():
            if section in cfg and isinstance(values, dict):
                cfg[section].update(values)
    return cfg


def fetch(url, headers_extra=None):
    headers = {"User-Agent": "ai-research-tool/1.1 (github.com/kanosa0101/ai-research-tool)"}
    if headers_extra:
        headers.update(headers_extra)
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.read().decode(errors="replace")
        except Exception as e:
            if attempt == 2:
                print(f"  warning: fetch failed {url} — {e}")
                return ""
    return ""


def github_trending(since="daily", language=""):
    url = f"https://github.com/trending{('/' + language) if language else ''}?since={since}"
    raw = fetch(url)
    slugs, seen, clean = re.findall(r'href="/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"', raw), set(), []
    for s in slugs:
        if s not in seen and "/" in s and not any(x in s for x in ["trending","login","signup","explore","settings"]):
            seen.add(s); clean.append(s)
    stars = re.findall(r'([\d,]+)\s+stars? today', raw)
    descs = re.findall(r'<p class="col-9[^"]*">\s*(.*?)\s*</p>', raw, re.S)
    results = []
    for i, slug in enumerate(clean[:20]):
        results.append({
            "repo": slug, "url": f"https://github.com/{slug}",
            "description": html.unescape(descs[i].strip()) if i < len(descs) else "",
            "stars_today": stars[i].replace(",", "") if i < len(stars) else "?",
        })
    return results


def arxiv_by_category(categories, max_results=30):
    cat_query = " OR ".join(f"cat:{c}" for c in categories)
    q = urllib.parse.quote(cat_query)
    url = (f"https://export.arxiv.org/api/query?search_query={q}"
           f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}")
    return _parse_arxiv(fetch(url))


def arxiv_by_keyword(keywords, max_results=30):
    q = urllib.parse.quote(keywords)
    url = (f"https://export.arxiv.org/api/query?search_query=all:{q}"
           f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}")
    return _parse_arxiv(fetch(url))


def _parse_arxiv(raw):
    papers = []
    for entry in re.findall(r"<entry>(.*?)</entry>", raw, re.S):
        def tag(t):
            m = re.search(rf"<{t}[^>]*>(.*?)</{t}>", entry, re.S)
            return html.unescape(m.group(1).strip()) if m else ""
        title = tag("title").replace("\n", " ")
        summary = tag("summary").replace("\n", " ")[:400]
        published = tag("published")[:10]
        link_m = re.search(r"<id>(http[s]?://arxiv\.org/abs/[^<]+)</id>", entry)
        if not title or not link_m:
            continue
        papers.append({
            "title": title, "url": link_m.group(1).strip(),
            "published": published, "summary": summary,
            "authors": re.findall(r"<name>(.*?)</name>", entry)[:3],
            "categories": re.findall(r'term="([^"]+)"', entry)[:3],
            "score": None,
        })
    return papers


def score_papers(papers, interests, api_key, min_score=6):
    scored = []
    for p in papers:
        prompt = (f"Rate the relevance of this paper to the following research interests "
                  f"on a scale of 1-10. Reply with ONLY a single integer.\n\n"
                  f"Research interests:\n{interests}\n\n"
                  f"Paper: {p['title']}\nAbstract: {p['summary']}")
        try:
            data = json.dumps({"model": "gpt-3.5-turbo",
                               "messages": [{"role": "user", "content": prompt}],
                               "max_tokens": 5, "temperature": 0}).encode()
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions", data=data,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                resp = json.loads(r.read())
                p["score"] = int(re.search(r"\d+", resp["choices"][0]["message"]["content"]).group())
        except Exception:
            p["score"] = 5
        if p["score"] >= min_score:
            scored.append(p)
    return sorted(scored, key=lambda x: x["score"] or 0, reverse=True)


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"seen_papers": [], "seen_repos": []}


def save_state(state):
    state["seen_papers"] = state["seen_papers"][-500:]
    state["seen_repos"] = state["seen_repos"][-200:]
    STATE_FILE.write_text(json.dumps(state, indent=2))


def generate(repos, papers, cfg, since):
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    since_label = {"daily": "今日", "weekly": "本周", "monthly": "本月"}.get(since, since)
    top_r, top_p = cfg["output"]["top_repos"], cfg["output"]["top_papers"]
    cats = ", ".join(cfg["arxiv"]["categories"])
    scoring_note = " · AI 相关性评分" if cfg["output"]["ai_scoring"] else ""

    lines = [
        f"# 每日 AI 调研简报 — {date}", "",
        f"> 生成时间：{now} | 分类：`{cats}` | 数据来源：GitHub Trending · arXiv",
        "", "---", "",
        f"## 🔥 GitHub {since_label}热门（Top {min(top_r, len(repos))}）", "",
    ]
    for r in repos[:top_r]:
        stars = f"⭐ +{r['stars_today']}" if r["stars_today"] != "?" else ""
        desc = f" — {r['description']}" if r["description"] else ""
        lines.append(f"- **[{r['repo']}]({r['url']})** {stars}{desc}")

    lines += ["", f"## 📚 arXiv 最新论文（Top {min(top_p, len(papers))}）{scoring_note}", ""]
    for p in papers[:top_p]:
        authors = ", ".join(p["authors"]) + (" et al." if len(p["authors"]) >= 3 else "")
        score_badge = f" · 🎯 {p['score']}/10" if p.get("score") else ""
        cat_badge = " · ".join(f"`{c}`" for c in p["categories"][:2])
        lines += [
            f"### [{p['title']}]({p['url']})",
            f"*{p['published']} · {authors}{score_badge}*" + (f"  \n*{cat_badge}*" if cat_badge else ""),
            "", f"{p['summary']}...", "",
        ]

    lines += [
        "---", "",
        "## 💡 今日洞察", "",
        "*(由使用者或 AI 补充)*", "",
        "---",
        f"*自动生成 by [ai-research-tool](https://github.com/kanosa0101/ai-research-tool)*",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Multi-Source AI Research Tool")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--keywords", default=None)
    parser.add_argument("--since", default=None, choices=["daily", "weekly", "monthly"])
    parser.add_argument("--language", default=None)
    parser.add_argument("--top", type=int, default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--incremental", action="store_true", help="跳过已推送内容")
    parser.add_argument("--score", action="store_true", help="启用 AI 相关性评分（需 OPENAI_API_KEY）")
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.since: cfg["github"]["since"] = args.since
    if args.language is not None: cfg["github"]["language"] = args.language
    if args.top: cfg["output"]["top_papers"] = cfg["output"]["top_repos"] = args.top
    if args.score: cfg["output"]["ai_scoring"] = True
    since = cfg["github"]["since"]

    print("📡 抓取 GitHub Trending...", flush=True)
    repos = github_trending(since, cfg["github"]["language"])
    print(f"   找到 {len(repos)} 个项目")

    print("📡 抓取 arXiv 论文...", flush=True)
    papers = arxiv_by_keyword(args.keywords) if args.keywords else arxiv_by_category(
        cfg["arxiv"]["categories"], cfg["arxiv"]["max_fetch"])
    print(f"   找到 {len(papers)} 篇论文")

    state = load_state()
    if args.incremental:
        seen_p, seen_r = set(state["seen_papers"]), set(state["seen_repos"])
        papers = [p for p in papers if p["url"] not in seen_p]
        repos = [r for r in repos if r["repo"] not in seen_r]
        print(f"   去重后：{len(papers)} 篇论文，{len(repos)} 个项目")

    api_key = os.environ.get("OPENAI_API_KEY")
    if cfg["output"]["ai_scoring"]:
        if api_key:
            print("🤖 AI 相关性评分中...", flush=True)
            papers = score_papers(papers, cfg["arxiv"]["interests"], api_key, cfg["arxiv"]["min_score"])
            print(f"   评分后保留 {len(papers)} 篇")
        else:
            print("⚠  OPENAI_API_KEY 未设置，跳过 AI 评分")

    report = generate(repos, papers, cfg, since)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"✅ 报告已保存：{args.output}")
    else:
        print("\n" + report)

    state["seen_papers"].extend(p["url"] for p in papers)
    state["seen_repos"].extend(r["repo"] for r in repos)
    save_state(state)


if __name__ == "__main__":
    main()
