"""Jiangcheng Carbon Eye Pro — Streamlit UI."""

import pandas as pd
# pandas 3.0 uses PyArrow strings by default, which Streamlit doesn't support
pd.options.future.infer_string = False

import streamlit as st
import sys
import os
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.carbon_monitor import monitor_emissions, monitor_file, monitor_folder
from core.data_aggregator import aggregate_emissions
from core.database import save_to_database, load_from_database, sanitize_dataframe
from ui.locales import locales

st.set_page_config(
    page_title="Jiangcheng Carbon Eye Pro",
    page_icon="🌍",
    layout="wide",
)

# ── Sidebar ─────────────────────────────────────────────────────────

language = st.sidebar.selectbox(
    "Language",
    options=["zh", "en"],
    format_func=lambda x: locales[x]["chinese"] if x == "zh" else locales[x]["english"],
    key="language",
)

current_locale = locales[language]

st.title(current_locale["app_title"])
st.markdown("---")

page = st.sidebar.radio(
    current_locale["sidebar_title"],
    [
        current_locale["home"],
        current_locale["monitoring"],
        current_locale["analysis"],
        current_locale["energy_carbon_dashboard"],
        current_locale["ai_insights"],
        current_locale["about"],
    ],
    key="page",
)


# ── Helpers ─────────────────────────────────────────────────────────

def _get_data() -> pd.DataFrame:
    """Load real data from database, fall back to sample if empty."""
    data = load_from_database()
    if data.empty:
        return _generate_sample_data()
    return sanitize_dataframe(data)


def _generate_sample_data() -> pd.DataFrame:
    """Generate demo data for first-run experience."""
    now = pd.Timestamp.now()
    records = []
    for i in range(20):
        records.append({
            'timestamp': (now - pd.Timedelta(hours=i)).isoformat(),
            'project': 'Project A' if i < 10 else 'Project B',
            'file_path': 'file1.py' if i % 2 == 0 else 'file2.py',
            'duration': 1.0,
            'energy_consumption': 0.01 + i * 0.002,
            'emissions': 0.05 + i * 0.004,
            'scope': 2,
        })
    return pd.DataFrame(records)


# ── Page: Home ──────────────────────────────────────────────────────

if page == current_locale["home"]:
    st.header(current_locale["project_intro"])
    st.markdown(f"""
    ### {current_locale["project_desc"]}

    ### {current_locale["core_features"]}
    - {current_locale["feature_1"]}
    - {current_locale["feature_2"]}
    - {current_locale["feature_3"]}
    - {current_locale["feature_4"]}

    ### {current_locale["tech_stack"]}
    - Python 3.12 + Pandas 2.2.0
    - Streamlit visualization interface
    - CodeCarbon carbon emission monitoring
    - SQLite3 data persistence
    """)

    st.markdown("---")
    st.info(current_locale["carbon_intensity"])


# ── Page: Monitoring ────────────────────────────────────────────────

elif page == current_locale["monitoring"]:
    st.header(current_locale["real_time_monitoring"])

    st.subheader("🔧 Code Monitoring")
    mode = st.radio(
        "Monitoring mode",
        ["Single code snippet", "File path", "Folder path"],
        index=0,
        horizontal=True,
    )

    project_name = st.text_input("Project Name", "default_project")

    if mode == "Single code snippet":
        test_code = st.text_area(
            "Enter Python code to monitor",
            """import time
import math

result = 0
for i in range(10000000):
    result += math.sin(i) * math.cos(i)
""",
            height=200,
        )

        if st.button("▶ Start Monitoring", key="btn_snippet"):
            with st.spinner("Running and monitoring emissions..."):
                def run_code():
                    exec(test_code)

                result_df = monitor_emissions(run_code, project_name, "snippet.py")
                st.success(
                    f"✅ Monitoring complete! "
                    f"Emissions: {result_df['emissions'].iloc[0]:.6f} kgCO2"
                )
                st.info("💾 Result automatically saved to database")

    elif mode == "File path":
        file_path = st.text_input(
            "Enter Python file path",
            os.path.join(os.path.dirname(__file__), "app.py"),
        )

        if st.button("▶ Monitor File", key="btn_file"):
            if os.path.exists(file_path) and file_path.endswith('.py'):
                with st.spinner(f"Monitoring {os.path.basename(file_path)}..."):
                    result_df = monitor_file(file_path, project_name)
                    st.success(
                        f"✅ Monitoring complete! "
                        f"Emissions: {result_df['emissions'].iloc[0]:.6f} kgCO2"
                    )
                    st.info("💾 Result automatically saved to database")
            else:
                st.error("❌ File not found or not a .py file")

    elif mode == "Folder path":
        folder_path = st.text_input(
            "Enter folder path",
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )

        if st.button("▶ Monitor Folder", key="btn_folder"):
            if os.path.isdir(folder_path):
                with st.spinner(f"Monitoring all .py files in {folder_path}..."):
                    result_df = monitor_folder(folder_path, project_name)
                    if not result_df.empty:
                        total = result_df['emissions'].sum()
                        st.success(
                            f"✅ Monitoring complete! "
                            f"Total emissions: {total:.6f} kgCO2 "
                            f"({len(result_df)} files)"
                        )
                        st.table(result_df[['file_path', 'duration', 'emissions']])
                        st.info("💾 Results automatically saved to database")
                    else:
                        st.warning("⚠️ No Python files found")
            else:
                st.error("❌ Folder not found")

    # ── Monitoring dashboard ──
    st.markdown("---")
    monitoring_data = _get_data()

    col1, col2, col3 = st.columns(3)
    with col1:
        total_emissions = monitoring_data['emissions'].sum()
        st.metric(current_locale["total_emissions"], f"{total_emissions:.4f} kgCO2")
    with col2:
        monitor_count = len(monitoring_data)
        st.metric(current_locale["monitoring_count"], str(monitor_count))
    with col3:
        avg_emissions = monitoring_data["emissions"].mean()
        st.metric(current_locale["avg_emissions"], f"{avg_emissions:.4f} kgCO2")

    st.markdown("---")
    st.subheader(current_locale["emission_trend"])

    trend_data = monitoring_data.copy()
    trend_data['timestamp'] = pd.to_datetime(trend_data['timestamp'])

    fig = px.line(
        trend_data, x='timestamp', y='emissions',
        title=current_locale["emission_trend"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader(current_locale["monitoring_data"])
    st.dataframe(monitoring_data, use_container_width=True)


# ── Page: Analysis ──────────────────────────────────────────────────

elif page == current_locale["analysis"]:
    st.header(current_locale["data_analysis"])

    analysis_data = _get_data()

    st.subheader(current_locale["select_dimension"])
    group_by = st.selectbox(
        current_locale["select_dimension"],
        ["project", "file_path", "hour", "day", "week", "month", "quarter", "year"],
    )

    result = aggregate_emissions(analysis_data, group_by=group_by)

    st.subheader(current_locale["aggregation_result"])
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            result, x=result.columns[0], y='total_emissions',
            title=current_locale["total_emissions_compare"],
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(
            result, x=result.columns[0], y='avg_emissions',
            title=current_locale["avg_emissions_compare"],
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader(current_locale["detailed_data"])
    st.dataframe(result, use_container_width=True)

    csv_data = result.to_csv(index=False)
    st.download_button(
        label=current_locale["download_csv"],
        data=csv_data,
        file_name=f"emissions_by_{group_by}.csv",
        mime="text/csv",
    )


# ── Page: Dashboard ─────────────────────────────────────────────────

elif page == current_locale["energy_carbon_dashboard"]:
    st.header("⚡ " + current_locale["energy_carbon_dashboard"])

    data = load_from_database()

    if data.empty:
        st.warning(current_locale["upload_data_first"])
        st.info("💡 Run a monitoring task first to collect real data.")
    else:
        st.subheader(current_locale["overview"])
        col1, col2, col3, col4 = st.columns(4)

        total_emissions = data['emissions'].sum()
        total_energy = data['energy_consumption'].sum()
        avg_emissions = data['emissions'].mean()
        avg_energy = data['energy_consumption'].mean()

        with col1:
            st.metric(current_locale["total_emissions"], f"{total_emissions:.4f} kgCO2")
        with col2:
            st.metric(current_locale["energy_consumption"], f"{total_energy:.4f} kWh")
        with col3:
            st.metric(current_locale["avg_emissions"], f"{avg_emissions:.4f} kgCO2")
        with col4:
            st.metric(current_locale["avg_energy_consumption"], f"{avg_energy:.4f} kWh")

        st.subheader(current_locale["energy_emission_trend"])
        trend_data = data.copy()
        trend_data['timestamp'] = pd.to_datetime(trend_data['timestamp'])
        trend_data = trend_data.set_index('timestamp')
        trend_data = trend_data.resample('D').sum(numeric_only=True)

        fig = px.line(
            trend_data, y=['energy_consumption', 'emissions'],
            title=current_locale["energy_emission_trend"],
        )
        fig.update_layout(yaxis_title="Value")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(current_locale["project_comparison"])
        project_data = aggregate_emissions(data, group_by="project")

        fig = px.pie(
            project_data, values='total_emissions', names='project',
            title=current_locale["project_comparison"], hole=0.3,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(current_locale["file_comparison"])
        file_data = aggregate_emissions(data, group_by="file_path")

        fig = px.bar(
            file_data, x='file_path', y='total_emissions',
            title=current_locale["file_comparison"],
            color='total_emissions', color_continuous_scale='Viridis',
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(current_locale["detailed_data"])
        st.dataframe(data, use_container_width=True)


# ── Page: AI Insights ───────────────────────────────────────────────

elif page == current_locale["ai_insights"]:
    st.header("🤖 " + current_locale["ai_insights"])

    data = load_from_database()

    if data.empty:
        st.warning(current_locale["upload_data_first"])
        st.info("💡 Run a monitoring task first to collect real data.")
    else:
        project_name = st.text_input(
            current_locale["project_name"], "Default Project",
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button(current_locale["generate_esg_report"]):
                with st.spinner(current_locale["generating_report"]):
                    from core.ai_insights import generate_esg_insights
                    report = generate_esg_insights(data, project_name, language)
                    st.markdown(report)

        with col2:
            if st.button(current_locale["generate_reduction_suggestions"]):
                with st.spinner(current_locale["generating_suggestions"]):
                    from core.ai_insights import generate_reduction_suggestions
                    suggestions = generate_reduction_suggestions(data, language)
                    st.markdown(suggestions)


# ── Page: About ─────────────────────────────────────────────────────

elif page == current_locale["about"]:
    st.header(current_locale["about_project"])
    st.markdown(f"""
    ### Jiangcheng Carbon Eye Pro

    **{current_locale["version"]}**: v1.0.0

    **{current_locale["developer"]}**: Liu Zhiming

    **{current_locale["tech_stack_list"]}**:
    - {current_locale["python"]}
    - {current_locale["pandas"]}
    - {current_locale["streamlit"]}
    - {current_locale["codecarbon"]}
    - SQLite3

    **{current_locale["local_adaptation_section"]}**:
    - {current_locale["hubei_carbon_intensity"]}

    **{current_locale["project_background"]}**:
    {current_locale["background_desc"]}

    **{current_locale["contact"]}**:
    - {current_locale["email"]} liuzhiming_2005@qq.com
    """)

st.markdown("---")
st.markdown(current_locale["footer"])
