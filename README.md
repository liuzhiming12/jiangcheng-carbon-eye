# Jiangcheng Carbon Eye Pro

A lightweight carbon emission monitoring tool for code-level energy attribution, 
built for developers and small IT teams in Wuhan, China.

## Why I Built This

At Wuhan College of Arts and Sciences, I noticed campus IT departments had no way 
to measure the carbon footprint of running software. After struggling with Database 
Principles (53), I decided to rebuild my understanding of data systems by building 
something real.

## What It Does

- Monitors real-time CPU/memory usage via `psutil`
- Estimates power consumption using a TDP-based model when CodeCarbon fails
- Calculates CO₂ emissions using **Hubei Grid OM factor 0.562 kgCO₂/kWh**
- Stores time-series data in SQLite
- Visualizes trends via Streamlit

## 3-Tier Fallback

The core engineering decision: when CodeCarbon fails (offline/restricted VM), 
degrade gracefully rather than crash.

1. **CodeCarbon** — most accurate, requires network access
2. **psutil + TDP formula** — works everywhere, ±15% variance
3. **Constant TDP estimate** — worst case, guaranteed output

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

- Application-layer estimation only; TDP model has ±15% variance
- No kernel-level instrumentation (RAPL/eBPF) yet
- Tested on single Windows laptop; cross-platform validation pending
- AI insights use Tongyi Qianwen API with factual constraints

## What's Next

- Auditing CMU 15-445 (database systems concepts; C++ labs planned Fall 2026)
- Investigating Intel RAPL for hardware-level power measurement
- Exploring eBPF for process-level energy attribution (reading Kepler framework)

## License

MIT