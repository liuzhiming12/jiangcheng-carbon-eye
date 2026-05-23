# Jiangcheng Carbon Eye

A lightweight carbon emission monitoring tool for code-level energy attribution,
built for developers and small IT teams in Wuhan, China.

## Why I Built This

At Wuhan College of Arts and Sciences, campus IT departments had no way to 
measure the carbon footprint of running software. After scoring 53 in Database 
Principles, I decided to rebuild my learning by building something real.

## What It Does

- Monitors real-time CPU/memory usage via `psutil`
- Estimates power consumption using a TDP-based heuristic when CodeCarbon fails 
  (offline/restricted VM)
- Calculates CO₂ emissions using **Hubei Grid OM factor 0.562 kgCO₂/kWh** 
  (2022 provincial bulletin)
- Stores time-series data in SQLite
- Visualizes trends via Streamlit

## 3-Tier Fallback

The core engineering decision: when CodeCarbon fails, degrade gracefully rather 
than crash.

1. **CodeCarbon** — most accurate, requires network access
2. **psutil + TDP heuristic** — works everywhere, ~±15% variance (conservative 
   estimate from community benchmarks, not a statistical bound)
3. **Constant TDP estimate** — worst case, guaranteed output

## How the Heuristic Works

```
power_estimate = tdp_watts * (cpu_utilization_percent / 100)
energy_kwh = power_estimate * time_hours / 1000
co2_kg = energy_kwh * 0.562
```

- `cpu_utilization_percent` comes from `psutil.cpu_percent(interval=1)`
- `tdp_watts` is read from a user-configurable lookup table (default 15W for my laptop)
- `0.562` is the Hubei Grid Operating Margin factor (kgCO₂/kWh), replacing the 
  national default 0.5556 because Hubei has a higher hydro share

## Tech Stack

Python 3.12, Streamlit, SQLite, psutil, Pandas, Plotly

## Run Locally

```bash
git clone https://github.com/liuzhiming12/jiangcheng-carbon-eye.git
cd jiangcheng-carbon-eye
pip install -r requirements.txt
streamlit run ui/app.py
```

## Current Limitations

- Application-layer estimation only; TDP model is a heuristic with unverified variance
- No kernel-level instrumentation (RAPL/eBPF) yet — reading docs, planning integration with lab access
- Tested on single Windows laptop; cross-platform validation pending
- AI insights use Tongyi Qianwen API with factual constraints (forced raw-data citation)

## What I'm Learning Next

- CMU 15-445 lectures on storage and indexing (lectures 1–5 completed, applying to my SQLite schema)
- Intel RAPL documentation (hardware-level power counters)
- Kepler eBPF framework (process-level energy attribution) — reading README and blog posts

## License

MIT