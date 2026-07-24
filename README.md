# Jiangcheng Carbon Eye Pro · 江城碳眼

> 代码级碳监测工具 — 实时监测每一行 Python 代码的碳排放

A lightweight, locally-calibrated carbon monitoring tool for developers.
Measures CO₂ emissions from Python processes using Hubei provincial emission factors.

## 🏃 快速体验

```bash
# 1. 克隆项目
git clone https://github.com/liuzhiming12/jiangcheng-carbon-eye.git
cd jiangcheng-carbon-eye

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
streamlit run ui/app.py
```

在浏览器中打开 `http://localhost:8501`，选择监测模式即可开始分析。**3 分钟跑起来！**

## 🏗️ 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit 仪表盘                         │
│  (6 pages: Monitoring / Analysis / Dashboard / AI Insights)     │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ ai_insights.py  │    │ data_aggregator │    │   database.py   │
│  (AI ESG报告)   │    │    .py          │    │  (SQLite存储)    │
│                 │    │  (多维聚合分析)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              ▲                     ▲
                              │                     │
                    ┌───────────────────────────────┘
                    ▼
            ┌───────────────────┐
            │ carbon_monitor.py │
            │   (3层降级监测)     │
            │  - CodeCarbon     │
            │  - psutil+TDP     │
            │  - Constant TDP   │
            └───────────────────┘
                    ▲
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   Code Snippet  File Path   Folder Path
```

## ✨ 功能特性

- **3 种监测模式**：代码片段、单文件、项目文件夹
- 使用 **湖北电网 OM 碳排放因子 0.4044 kgCO₂/kWh**（MEE 2025）计算碳排放
- 自动保存结果到 SQLite 数据库
- 实时仪表盘：项目级、文件级碳排放分析
- AI 智能 ESG 报告和减排建议

## 🔄 3 层降级机制

核心工程设计：当 CodeCarbon 不可用时，优雅降级而非崩溃。

1. **CodeCarbon** → 最精确，需要 Intel RAPL/DSM
2. **psutil + TDP 启发式** → 通用，~±15% 误差（保守估计）
3. **常量 TDP 估计** → 最坏情况，保证输出

## 📊 计算原理

```
power_estimate = idle_watts + (tdp_watts - idle_watts) * (cpu_percent / 100)
energy_kwh = power_estimate * time_hours / 1000
co2_kg = energy_kwh * 0.4044
```

- `cpu_percent` 来自 `psutil.Process().cpu_percent()`
- `tdp_watts` 默认 65W（单核），`idle_watts` 默认 10W
- `0.4044` 是湖北电网 OM 因子，替代 CodeCarbon 默认的全球平均 0.475

## How to Use

### Monitoring (3 modes)

| Mode | Description |
|------|-------------|
| **Code snippet** | Paste Python code directly in the text area, run & measure |
| **File path** | Point to a `.py` file on disk |
| **Folder path** | Scan all `.py` files in a directory recursively |

Results are automatically saved to the database and available in all other pages.

### Analysis
Aggregate emissions by project, file, hour, day, week, month, quarter, or year. Export results as CSV.

### Dashboard
Overview metrics, energy & emission trends, project/file comparison charts.

### AI Insights
Generate ESG analysis reports and carbon reduction suggestions (requires Qwen API key in `QWEN_API_KEY` env var; falls back to template-based reports otherwise).

## Tech Stack

- Python 3.12 + Streamlit for the dashboard
- psutil for system metrics
- CodeCarbon as primary emission calculator
- SQLite for data persistence
- Plotly for visualizations

## Current Limitations

- Static carbon factor (0.4044); synthetic data used for validation; no real-world campus deployment yet
- Application-layer estimation only; TDP model is a heuristic with unverified variance
- No kernel-level instrumentation (RAPL/eBPF) yet — reading docs, planning integration with lab access
- Tested on single Windows laptop; cross-platform validation pending
- AI insights use Tongyi Qianwen API with factual constraints (forced raw-data citation)

## Recent Updates

- **Jul 2026**: Refactored architecture — removed template upload flow, unified carbon factor, added 3-mode monitoring (snippet/file/folder), auto-save to database
- **May 2026**: Refined dashboard visualization with project/file-level carbon breakdown
- **May 2026**: Improved error handling for API failures with graceful degradation
- **Apr 2026**: Implemented 3-tier fallback system for offline VM environments

## What I'm Learning Next

- CMU 15-445 lectures on storage and indexing (lectures 1-5 completed, applying to my SQLite schema)
- Intel RAPL documentation (hardware-level power counters)
- Kepler eBPF framework (process-level energy attribution) — reading README and blog posts

## License

MIT

## 👤 关于作者

**刘志明** · 武汉文理学院

- GitHub: [@liuzhiming12](https://github.com/liuzhiming12)
- Email: liuzhiming_2005@qq.com

> 武汉本地开发者普遍不关注代码碳排放，企业 ESG 报告中 IT 部门能耗数据常为空白。
> 我通过这两个项目，尝试用轻量级工具填补这一缺口——从一行代码到一个校园，碳皆可量化。
