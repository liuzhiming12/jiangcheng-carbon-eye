# Jiangcheng Carbon Eye Pro

A lightweight, locally-calibrated carbon monitoring tool for developers.
Measures CO₂ emissions from Python processes using Hubei provincial emission factors.

## Why I Built This

Developers treat AI assistants as free labor. No one measures the electricity bill.

I couldn't find a lightweight tool that:
- Uses **Hubei-specific carbon factors** (not global averages)
- Works offline in restricted campus VMs
- Degrades gracefully when external APIs fail
- Shows emissions in real-time during development

## What It Does

- **3-mode monitoring**: code snippets, single files, or entire project folders
- Calculates CO₂ emissions using **Hubei provincial emission factor 0.4364 kgCO₂/kWh** (MEE 2022 bulletin)
- Auto-saves results to SQLite database for analysis
- Provides real-time dashboard with project-level and file-level breakdown
- Generates AI-powered ESG reports and reduction suggestions

## Architecture

```
core/
├── carbon_monitor.py    # 3-tier fallback monitoring engine
├── database.py          # SQLite persistence layer
├── data_aggregator.py   # Multi-dimension emission aggregation
└── ai_insights.py       # AI-powered ESG report generation

ui/
├── app.py               # Streamlit dashboard (6 pages)
└── locales.py           # zh/en internationalization
```

### Data Flow

```
Code Snippet / File / Folder
        │
        ▼
  carbon_monitor.py   ──►  SQLite DB
        │                      │
        ▼                      ▼
  Real-time result      Analysis / Dashboard / AI Insights
```

## 3-Tier Fallback

The core engineering decision: when CodeCarbon fails, degrade gracefully rather than crash.

1. **CodeCarbon** → most accurate, requires Intel RAPL/DSM
2. **psutil + TDP heuristic** → works everywhere, ~±15% variance (conservative estimate)
3. **Constant TDP estimate** → worst case, guaranteed output

## How the Heuristic Works

```
power_estimate = idle_watts + (tdp_watts - idle_watts) * (cpu_percent / 100)
energy_kwh = power_estimate * time_hours / 1000
co2_kg = energy_kwh * 0.4364
```

- `cpu_percent` comes from `psutil.Process().cpu_percent()`
- `tdp_watts` defaults to 65W (per-core), `idle_watts` to 10W
- `0.4364` is the Hubei provincial grid emission factor (kgCO₂/kWh), from the Ministry of Ecology and Environment 2022 bulletin (released Dec 2024). Replaces CodeCarbon's default global average 0.475 because Hubei has a higher hydro share.

## Quick Start

```bash
git clone https://github.com/liuzhiming12/jiangcheng-carbon-eye.git
cd jiangcheng-carbon-eye

pip install -r requirements.txt
streamlit run ui/app.py
```

Open `http://localhost:8501` in your browser.

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

- Static carbon factor (0.4364); synthetic data used for validation; no real-world campus deployment yet
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

## Related Project

- **`https://github.com/liuzhiming12/wenli-carbon-calc`** — Batch processing layer for institutional ESG reporting. Same carbon engine, different input.
