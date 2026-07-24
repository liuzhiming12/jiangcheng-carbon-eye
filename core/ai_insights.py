"""AI-powered ESG insights and carbon reduction suggestions.

Uses ZhipuAI (智谱) OpenAI-compatible API for report generation.
Falls back to template-based reports when API is unavailable.
"""

import pandas as pd
import os
import re
import json
from openai import OpenAI


# ── ZhipuAI client (OpenAI-compatible) ──────────────────────────────
# Uses the same API key as the vision MCP server
ZHIPU_API_KEY = os.environ.get('ZHIPU_API_KEY', '')
ZHIPU_BASE_URL = 'https://open.bigmodel.cn/api/paas/v4'
AI_MODEL = 'glm-4-flash'  # 智谱免费模型，够用


def _get_client() -> OpenAI | None:
    """Create an OpenAI client pointing to ZhipuAI."""
    try:
        return OpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL)
    except Exception:
        return None


def _call_llm(prompt: str, system_prompt: str = "") -> str | None:
    """Call ZhipuAI LLM and return text response."""
    client = _get_client()
    if client is None:
        return None

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[AI] LLM call failed: {e}")
        return None


def validate_report(report: str, data_points: dict) -> str:
    """Check that all numbers in report exist in raw data."""
    numbers = re.findall(r'\d+\.\d+', report)
    valid_numbers = set(str(v) for v in data_points.values())

    for num in numbers:
        if num not in valid_numbers:
            report = report.replace(num, "[Data not verified]")

    return report


# ── Template reports ────────────────────────────────────────────────

ESG_TEMPLATE_ZH = """
## ESG 分析报告

### 项目信息
- **项目名称**: {project_name}
- **数据条数**: {data_count}
- **总碳排放**: {total_emissions:.4f} kgCO2
- **平均排放**: {avg_emissions:.4f} kgCO2
- **最高排放**: {max_emission:.4f} kgCO2

### 减排建议
1. 优化代码结构，减少不必要的计算
2. 使用更高效的算法和数据结构
3. 合理安排计算任务，避开用电高峰期
4. 考虑使用可再生能源供电的服务器
5. 定期监测和分析碳排放数据，持续优化

### 本地化建议
- 利用湖北电网峰谷电价差异，低谷期运行大型计算任务
- 参考本地双碳政策，制定符合要求的减排目标

### 结论
通过持续的监测和优化，预计可降低 20-30% 的碳排放。
"""

ESG_TEMPLATE_EN = """
## ESG Analysis Report

### Project Information
- **Project Name**: {project_name}
- **Data Count**: {data_count}
- **Total Emissions**: {total_emissions:.4f} kgCO2
- **Average Emissions**: {avg_emissions:.4f} kgCO2
- **Max Emissions**: {max_emission:.4f} kgCO2

### Reduction Suggestions
1. Optimize code structure and reduce unnecessary computations
2. Use more efficient algorithms and data structures
3. Schedule computational tasks during off-peak hours
4. Consider using renewable energy powered servers
5. Regularly monitor and analyze carbon emission data

### Conclusion
Through continuous monitoring and optimization, a 20-30% reduction in carbon emissions is achievable.
"""

SUGGEST_TEMPLATE_ZH = """
## 减排建议报告

### 数据概况
- **数据条数**: {data_count}
- **总碳排放**: {total_emissions:.4f} kgCO2
- **平均排放**: {avg_emissions:.4f} kgCO2

### 具体减排建议

#### 1. 代码层面优化
- 使用高效的算法和数据结构，减少计算复杂度
- 利用 NumPy/Pandas 向量化操作替代 Python 循环

#### 2. 资源调度优化
- 将大型计算任务安排在电网负荷低谷期
- 利用湖北电网峰谷电价差异降低运营成本

#### 3. 硬件层面优化
- 选择能效比更高的服务器和数据中心
- 启用 CPU 动态调频功能

#### 4. 能源结构优化
- 优先选择使用可再生能源的数据中心
- 参与绿色电力购买计划

#### 5. 持续监测与优化
- 建立碳排放监测机制，定期分析数据
- 设置碳排放阈值告警

### 预计减排效果
通过以上措施的综合实施，预计可实现 **20-40%** 的碳排放降低。
"""

SUGGEST_TEMPLATE_EN = """
## Carbon Reduction Suggestions Report

### Data Overview
- **Data Count**: {data_count}
- **Total Emissions**: {total_emissions:.4f} kgCO2
- **Average Emissions**: {avg_emissions:.4f} kgCO2

### Specific Reduction Suggestions

#### 1. Code Optimization
- Use efficient algorithms to reduce computational complexity
- Use NumPy/Pandas vectorization instead of Python loops

#### 2. Resource Scheduling
- Schedule large tasks during off-peak hours
- Leverage peak-valley electricity price differences

#### 3. Hardware Optimization
- Choose servers with higher energy efficiency ratios
- Enable CPU dynamic frequency scaling

#### 4. Energy Structure
- Prioritize data centers using renewable energy
- Participate in green electricity purchase programs

#### 5. Continuous Monitoring
- Establish carbon emission monitoring mechanisms
- Set carbon emission threshold alerts

### Expected Effect
Through comprehensive implementation, an estimated **20-40%** reduction can be achieved.
"""


# ── Main functions ──────────────────────────────────────────────────

def generate_esg_insights(
    data: pd.DataFrame,
    project_name: str = "Unknown",
    language: str = "zh"
) -> str:
    """Generate ESG insights using ZhipuAI API, fallback to template."""
    total_emissions = float(data['emissions'].sum())
    avg_emissions = float(data['emissions'].mean())
    max_emission = float(data['emissions'].max())
    data_count = int(len(data))

    data_points = {
        'total_emissions': f"{total_emissions:.4f}",
        'avg_emissions': f"{avg_emissions:.4f}",
        'max_emission': f"{max_emission:.4f}",
        'data_count': str(data_count)
    }

    if language == "en":
        prompt = f"""You are a professional ESG analyst. Generate a detailed ESG analysis report.

Project: {project_name}
Data Records: {data_count}
Total Emissions: {total_emissions:.4f} kgCO2
Average Emissions: {avg_emissions:.4f} kgCO2
Max Emissions: {max_emission:.4f} kgCO2

Include:
1. Carbon emission overview
2. At least 5 reduction suggestions
3. Localized suggestions (Hubei grid factor: 0.4044 kgCO2/kWh)
4. Long-term optimization strategies
5. Conclusion

CRITICAL: Only use the numbers provided above. Do NOT invent any data."""
        template = ESG_TEMPLATE_EN.format(
            project_name=project_name, data_count=data_count,
            total_emissions=total_emissions, avg_emissions=avg_emissions,
            max_emission=max_emission
        )
    else:
        prompt = f"""你是一名专业 ESG 分析师。根据以下数据生成详细的分析报告。

项目：{project_name}
数据条数：{data_count}
总碳排放：{total_emissions:.4f} kgCO2
平均排放：{avg_emissions:.4f} kgCO2
最高排放：{max_emission:.4f} kgCO2

请包含：
1. 碳排放概况
2. 至少5条减排建议
3. 本地化建议（湖北电网碳强度 0.4044 kgCO2/kWh）
4. 长期优化策略
5. 结论

重要约束：只能使用上面提供的数值，不得编造任何数据。"""
        template = ESG_TEMPLATE_ZH.format(
            project_name=project_name, data_count=data_count,
            total_emissions=total_emissions, avg_emissions=avg_emissions,
            max_emission=max_emission
        )

    report = _call_llm(prompt)
    if report is None:
        return template
    return validate_report(report, data_points)


def generate_reduction_suggestions(
    data: pd.DataFrame,
    language: str = "zh"
) -> str:
    """Generate carbon reduction suggestions using ZhipuAI, fallback to template."""
    total_emissions = float(data['emissions'].sum())
    avg_emissions = float(data['emissions'].mean())
    data_count = int(len(data))

    data_points = {
        'total_emissions': f"{total_emissions:.4f}",
        'avg_emissions': f"{avg_emissions:.4f}",
        'data_count': str(data_count)
    }

    if language == "en":
        prompt = f"""You are a carbon reduction expert. Provide specific suggestions based on:

Data Records: {data_count}
Total Emissions: {total_emissions:.4f} kgCO2
Average Emissions: {avg_emissions:.4f} kgCO2

Cover: code optimization, resource scheduling, hardware, energy, monitoring.

CRITICAL: Only use numbers provided above. Do NOT invent data."""
        template = SUGGEST_TEMPLATE_EN.format(
            data_count=data_count,
            total_emissions=total_emissions,
            avg_emissions=avg_emissions
        )
    else:
        prompt = f"""你是一名碳排放优化专家。根据以下数据生成具体减排建议：

数据条数：{data_count}
总碳排放：{total_emissions:.4f} kgCO2
平均排放：{avg_emissions:.4f} kgCO2

从代码优化、资源调度、硬件选择、能源结构、持续监测5方面给出建议。

重要约束：只能使用上面提供的数值，不得编造任何数据。"""
        template = SUGGEST_TEMPLATE_ZH.format(
            data_count=data_count,
            total_emissions=total_emissions,
            avg_emissions=avg_emissions
        )

    report = _call_llm(prompt)
    if report is None:
        return template
    return validate_report(report, data_points)
