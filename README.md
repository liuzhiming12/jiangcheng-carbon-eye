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

- Monitors CPU usage and estimates power consumption
- Calculates CO₂ emissions using **Hubei provincial emission factor 0.4364 kgCO₂/kWh** (MEE 2022 bulletin)
- Provides real-time dashboard with process-level breakdown
- Exports reports in ESG disclosure format

## 3-Tier Fallback

The core engineering decision: when CodeCarbon fails, degrade gracefully rather than crash.

1. **CodeCarbon** → most accurate, requires network access
2. **psutil + TDP heuristic** → works everywhere, ~±15% variance (conservative estimate)
3. **Constant TDP estimate** → worst case, guaranteed output

## How the Heuristic Works

```
power_estimate = tdp_watts * (cpu_utilization_percent / 100)
energy_kwh = power_estimate * time_hours / 1000
co2_kg = energy_kwh * 0.4364
```

- `cpu_utilization_percent` comes from `psutil.cpu_percent(interval=1)`
- `tdp_watts` is read from a user-configurable lookup table (default 15W for laptops)
- `0.4364` is the Hubei provincial grid emission factor (kgCO₂/kWh), from the Ministry of Ecology and Environment 2022 bulletin (released Dec 2024). Replaces CodeCarbon's default global average 0.475 because Hubei has a higher hydro share.

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

- **May 2026**: Refined dashboard visualization with project/file-level carbon breakdown
- **May 2026**: Improved error handling for API failures with graceful degradation
- **May 2026**: Updated aggregation logic to focus on Scope 2 emissions (code-level monitoring)
- **May 2026**: Added unit tests for carbon estimation calculations
- **Apr 2026**: Implemented 3-tier fallback system for offline VM environments

## What I'm Learning Next

- CMU 15-445 lectures on storage and indexing (lectures 1-5 completed, applying to my SQLite schema)
- Intel RAPL documentation (hardware-level power counters)
- Kepler eBPF framework (process-level energy attribution) — reading README and blog posts

## License

MIT

## Related Project

- **`https://github.com/liuzhiming12/wenli-carbon-calc`** — Batch processing layer for institutional ESG reporting. Same carbon engine, different input.