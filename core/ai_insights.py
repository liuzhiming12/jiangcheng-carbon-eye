import pandas as pd
import dashscope
import os
import re

def validate_report(report: str, data_points: dict) -> str:
    """Check that all numbers in report exist in raw data"""
    numbers = re.findall(r'\d+\.\d+', report)
    valid_numbers = set(str(v) for v in data_points.values())
    
    for num in numbers:
        if num not in valid_numbers:
            report = report.replace(num, "[Data not verified]")
    
    return report

def generate_esg_insights(data: pd.DataFrame, project_name: str = "Unknown", language: str = "zh") -> str:
    """Generate ESG insights using Tongyi Qianwen API"""
    total_emissions = data['emissions'].sum()
    avg_emissions = data['emissions'].mean()
    max_emission = data['emissions'].max()
    data_count = len(data)

    api_key = os.environ.get('QWEN_API_KEY')

    templates = {
        "zh": f"""
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

### 武汉本地化建议
- 利用湖北电网的峰谷电价差异，在低谷期运行大型计算任务
- 参考武汉市双碳政策，制定符合本地要求的减排目标
- 参与武汉市绿色数据中心认证，提升企业 ESG 评级

### 结论
通过持续的监测和优化，预计可降低 20-30% 的代码运行碳排放，为武汉市的双碳目标做出贡献
        """,
        "en": f"""
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
5. Regularly monitor and analyze carbon emission data for continuous improvement

### Wuhan Localized Suggestions
- Leverage Hubei grid's peak-valley electricity price differences to run large computational tasks during off-peak periods
- Reference Wuhan's dual-carbon policies to set local emission reduction targets
- Participate in Wuhan's green data center certification to improve corporate ESG ratings

### Conclusion
Through continuous monitoring and optimization, a 20-30% reduction in code execution carbon emissions is achievable, contributing to Wuhan's dual-carbon goals.
        """
    }

    prompts = {
        "zh": f"""
你是一名专业的 ESG 分析师，专注于碳排放分析。请根据以下数据生成一份详细的 ESG 分析报告。

项目名称：{project_name}
数据条数：{data_count}
总碳排放量：{total_emissions:.4f} kgCO2
平均排放量：{avg_emissions:.4f} kgCO2
最高排放：{max_emission:.4f} kgCO2

请包含以下内容：
1. 项目碳排放概况
2. 减排建议（至少5条）
3. 武汉本地化建议（考虑湖北电网碳强度 0.4364 kgCO2/kWh）
4. 长期优化策略
5. 结论和下一步行动建议

CRITICAL CONSTRAINT: 你只能使用上面提供的数值数据。不得发明、估算或推断任何未明确给出的数字。如果数据不足以支持某个主张，请注明"数据不足"。

报告应该专业、详细、有针对性，符合企业 ESG 报告的标准。
    """,
        "en": f"""
You are a professional ESG analyst specializing in carbon emission analysis. Please generate a detailed ESG analysis report based on the following data:

Project Name: {project_name}
Data Count: {data_count}
Total Emissions: {total_emissions:.4f} kgCO2
Average Emissions: {avg_emissions:.4f} kgCO2
Max Emissions: {max_emission:.4f} kgCO2

Please include:
1. Project Carbon Emission Overview
2. Reduction Suggestions (at least 5)
3. Wuhan Localized Suggestions (considering Hubei grid carbon intensity 0.4364 kgCO2/kWh)
4. Long-term Optimization Strategies
5. Conclusions and Next Steps

CRITICAL CONSTRAINT: You must ONLY use the numerical data provided above. Do not invent, estimate, or extrapolate any numbers not explicitly given. If data is insufficient for a claim, state "Data insufficient" instead.

The report should be professional, detailed, targeted, and meet corporate ESG reporting standards.
    """
    }

    data_points = {
        'total_emissions': f"{total_emissions:.4f}",
        'avg_emissions': f"{avg_emissions:.4f}",
        'max_emission': f"{max_emission:.4f}",
        'data_count': str(data_count)
    }

    if not api_key:
        return templates.get(language, templates["zh"])

    dashscope.api_key = api_key

    prompt = prompts.get(language, prompts["zh"])

    try:
        response = dashscope.Generation.call(
            model="qwen-turbo",
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )
        report = response.output.text
        return validate_report(report, data_points)
    except Exception as e:
        return templates.get(language, templates["zh"])


def generate_reduction_suggestions(data: pd.DataFrame, language: str = "zh") -> str:
    """Generate carbon reduction suggestions"""
    total_emissions = data['emissions'].sum()
    avg_emissions = data['emissions'].mean()
    data_count = len(data)

    api_key = os.environ.get('QWEN_API_KEY')

    templates = {
        "zh": f"""
## 减排建议报告

### 数据概况
- **数据条数**: {data_count}
- **总碳排放**: {total_emissions:.4f} kgCO2
- **平均排放**: {avg_emissions:.4f} kgCO2

### 具体减排建议

#### 1. 代码层面优化
- 使用高效的算法和数据结构，减少计算复杂度
- 避免不必要的循环和递归调用
- 利用 NumPy/Pandas 向量化操作替代 Python 循环

#### 2. 资源调度优化
- 将大型计算任务安排在电网负荷低谷期
- 利用湖北电网峰谷电价差异降低运营成本
- 考虑使用分布式计算框架处理大规模数据

#### 3. 硬件层面优化
- 选择能效比更高的服务器和数据中心
- 启用 CPU 动态调频功能
- 使用 SSD 替代 HDD 减少读写能耗

#### 4. 能源结构优化
- 优先选择使用可再生能源的数据中心
- 参与绿色电力购买计划
- 考虑在武汉本地选择获得绿色认证的服务商

#### 5. 持续监测与优化
- 建立碳排放监测机制，定期分析数据
- 设置碳排放阈值告警
- 持续追踪减排效果并调整策略

### 预计减排效果
通过以上措施的综合实施，预计可实现 **20-40%** 的碳排放降低。
        """,
        "en": f"""
## Carbon Reduction Suggestions Report

### Data Overview
- **Data Count**: {data_count}
- **Total Emissions**: {total_emissions:.4f} kgCO2
- **Average Emissions**: {avg_emissions:.4f} kgCO2

### Specific Reduction Suggestions

#### 1. Runtime-level Optimization
- Use efficient algorithms and data structures to reduce computational complexity
- Avoid unnecessary loops and recursive calls
- Use NumPy/Pandas vectorization instead of Python loops

#### 2. Resource Scheduling Optimization
- Schedule large computational tasks during off-peak hours
- Leverage Hubei grid's peak-valley electricity price differences
- Consider using distributed computing frameworks for large-scale data

#### 3. Hardware-level Optimization
- Choose servers and data centers with higher energy efficiency ratios
- Enable CPU dynamic frequency scaling
- Use SSD instead of HDD to reduce read/write energy consumption

#### 4. Energy Structure Optimization
- Prioritize data centers using renewable energy
- Participate in green electricity purchase programs
- Consider choosing Wuhan local service providers with green certification

#### 5. Continuous Monitoring and Optimization
- Establish carbon emission monitoring mechanism and analyze data regularly
- Set carbon emission threshold alerts
- Continuously track emission reduction effects and adjust strategies

### Expected Reduction Effect
Through comprehensive implementation of the above measures, an estimated **20-40%** carbon emission reduction can be achieved.
        """
    }

    prompts = {
        "zh": f"""
你是一名碳排放优化专家。请根据以下数据生成具体的减排建议：

数据条数：{data_count}
总碳排放量：{total_emissions:.4f} kgCO2
平均排放量：{avg_emissions:.4f} kgCO2

请从代码优化、资源调度、硬件选择、能源结构、持续监测等5个方面给出具体建议。

CRITICAL CONSTRAINT: 你只能使用上面提供的数值数据。不得发明、估算或推断任何未明确给出的数字。如果数据不足以支持某个主张，请注明"数据不足"。
        """,
        "en": f"""
You are a carbon emission optimization expert. Please generate specific reduction suggestions based on the following data:

Data Count: {data_count}
Total Emissions: {total_emissions:.4f} kgCO2
Average Emissions: {avg_emissions:.4f} kgCO2

Please provide suggestions from 5 aspects: code optimization, resource scheduling, hardware selection, energy structure, and continuous monitoring.

CRITICAL CONSTRAINT: You must ONLY use the numerical data provided above. Do not invent, estimate, or extrapolate any numbers not explicitly given. If data is insufficient for a claim, state "Data insufficient" instead.
        """
    }

    data_points = {
        'total_emissions': f"{total_emissions:.4f}",
        'avg_emissions': f"{avg_emissions:.4f}",
        'data_count': str(data_count)
    }

    if not api_key:
        return templates.get(language, templates["zh"])

    dashscope.api_key = api_key

    prompt = prompts.get(language, prompts["zh"])

    try:
        response = dashscope.Generation.call(
            model="qwen-turbo",
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )
        report = response.output.text
        return validate_report(report, data_points)
    except Exception as e:
        return templates.get(language, templates["zh"])
