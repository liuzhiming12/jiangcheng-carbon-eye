import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.emission_calculator import calculate_emissions
from core.data_aggregator import aggregate_emissions
from core.carbon_monitor import monitor_emissions
from ui.locales import locales

st.set_page_config(
    page_title = "Jiangcheng Carbon Eye Pro",
    page_icon = "🌍",
    layout = "wide"
)

language = st.sidebar.selectbox(
    "Language",
    options = ["zh", "en"],
    format_func = lambda x: locales[x]["chinese"] if x == "zh" else locales[x]["english"],
    key = "language"
)

current_locale = locales[language]

st.title(current_locale["app_title"])
st.markdown("---")

page = st.sidebar.radio(
    current_locale["sidebar_title"],
    [current_locale["home"],
    current_locale["monitoring"],
    current_locale["analysis"],
    current_locale["energy_carbon_dashboard"],
    current_locale["ai_insights"],
    current_locale["about"]],
    key = "page"
)

def generate_sample_data():
    """Generate sample monitoring data"""
    return pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=20, freq='h'),
        'project': ['Project A'] * 10 + ['Project B'] * 10,
        'file_path': ['file1.py', 'file2.py'] * 10,
        'duration': [1.0] * 20,
        'emissions': [0.05, 0.06, 0.04, 0.07, 0.05, 0.08, 0.06, 0.09, 0.07, 0.05,
                      0.08, 0.07, 0.09, 0.06, 0.08, 0.05, 0.07, 0.06, 0.08, 0.05]
    })

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

elif page == current_locale["monitoring"]:
    st.header(current_locale["real_time_monitoring"])

    from core.database import load_from_database
    db_data = load_from_database()

    if not db_data.empty:
        monitoring_data = db_data
        st.info("📊 Displaying real data from database")
    else:
        monitoring_data = generate_sample_data()
        st.info("📊 Displaying sample data (real data will show after upload)")

    col1, col2, col3 = st.columns(3)
    with col1:
        total_emissions = monitoring_data['emissions'].sum()
        st.metric(current_locale["total_emissions"], f"{total_emissions:.4f} kgCO2")
    with col2:
        monitor_count = len(monitoring_data)
        st.metric(current_locale["monitoring_count"], f"{monitor_count}")
    with col3:
        avg_emissions = monitoring_data["emissions"].mean()
        st.metric(current_locale["avg_emissions"],f"{avg_emissions:.4f} kgCO2")
    st.markdown("---")
    st.subheader(current_locale["emission_trend"])
    fig = px.line(monitoring_data, x='timestamp', y='emissions', title=current_locale["emission_trend"])
    st.plotly_chart(fig, width='stretch')
    st.markdown("---")
    st.subheader(current_locale["monitoring_data"])
    st.dataframe(monitoring_data)

elif page == current_locale["analysis"]:
    st.header(current_locale["data_analysis"])
    st.subheader(current_locale["data_import"])
    uploaded_file = st.file_uploader(current_locale["upload_file"], type = ["csv", "xlsx"])

    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../templates/data_template.xlsx")
    with open(template_path, "rb") as f:
        template_data = f.read()
    st.download_button(
        label=current_locale["download_template"],
        data=template_data,
        file_name="data_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    uploaded_data = None
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            uploaded_data = pd.read_csv(uploaded_file)
        else:
            uploaded_data = pd.read_excel(uploaded_file)
        st.dataframe(uploaded_data)

        if 'power' in uploaded_data.columns and 'duration' in uploaded_data.columns:
            from core.emission_calculator import calculate_emissions
            emissions = []
            energy_consumptions = []
            scopes = []
            for _, row in uploaded_data.iterrows():
                result = calculate_emissions(row['power'], row['duration'])
                emissions.append(result['emissions'])
                energy_consumptions.append(result['energy_consumption'])
                scopes.append(result['scope'])
            uploaded_data['emissions'] = emissions
            uploaded_data['energy_consumption'] = energy_consumptions
            uploaded_data['scope'] = scopes
            st.dataframe(uploaded_data)

            if st.button(current_locale["save_to_db"]):
                from core.database import save_to_database
                save_to_database(uploaded_data)
                st.success(current_locale["save_success"])

    if uploaded_data is not None and 'emissions' in uploaded_data.columns:
        analysis_data = uploaded_data
    else:
        analysis_data = generate_sample_data()

    st.subheader(current_locale["select_dimension"])
    group_by = st.selectbox(
        current_locale["select_dimension"],
        ["project", "file_path", "hour", "day", "week", "month", "quarter", "year"]
    )
    result = aggregate_emissions(analysis_data, group_by = group_by)
    st.subheader(current_locale["aggregation_result"])
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(result, x=result.columns[0], y='total_emissions', title=current_locale["total_emissions_compare"])
        st.plotly_chart(fig, width='stretch')
    with col2:
        fig = px.bar(result, x=result.columns[0], y='avg_emissions', title=current_locale["avg_emissions_compare"])
        st.plotly_chart(fig, width='stretch')
    st.markdown("---")
    st.subheader(current_locale["detailed_data"])
    st.dataframe(result)
    csv_data = result.to_csv(index = False)
    st.download_button(label = current_locale["download_csv"], data = csv_data, file_name = f"emissions_by_{group_by}.csv", mime = "text/csv")

elif page == current_locale["energy_carbon_dashboard"]:
    st.header("⚡ " + current_locale["energy_carbon_dashboard"])

    from core.database import load_from_database
    from core.data_aggregator import aggregate_emissions
    data = load_from_database()

    if not data.empty:
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
        trend_data = trend_data.resample('D').sum()

        fig = px.line(trend_data, y=['energy_consumption', 'emissions'], title=current_locale["energy_emission_trend"])
        fig.update_layout(yaxis_title="Value")
        st.plotly_chart(fig, width='stretch')

        st.subheader(current_locale["project_comparison"])
        project_data = aggregate_emissions(data, group_by="project")
        
        fig = px.pie(project_data, values='total_emissions', names='project', 
                     title=current_locale["project_comparison"],
                     hole=0.3)
        st.plotly_chart(fig, width='stretch')

        st.subheader(current_locale["file_comparison"])
        file_data = aggregate_emissions(data, group_by="file_path")
        
        fig = px.bar(file_data, x='file_path', y='total_emissions', 
                     title=current_locale["file_comparison"],
                     color='total_emissions', color_continuous_scale='Viridis')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, width='stretch')

        st.subheader(current_locale["detailed_data"])
        st.dataframe(data)

    else:
        st.warning(current_locale["upload_data_first"])

elif page == current_locale["ai_insights"]:
    st.header("🤖 " + current_locale["ai_insights"])

    from core.database import load_from_database
    data = load_from_database()

    if not data.empty:
        project_name = st.text_input(current_locale["project_name"], "Default Project")

        if st.button(current_locale["generate_esg_report"]):
            with st.spinner(current_locale["generating_report"]):
                from core.ai_insights import generate_esg_insights
                report = generate_esg_insights(data, project_name, language)
                st.markdown(report)

        if st.button(current_locale["generate_reduction_suggestions"]):
            with st.spinner(current_locale["generating_suggestions"]):
                from core.ai_insights import generate_reduction_suggestions
                suggestions = generate_reduction_suggestions(data, language)
                st.markdown(suggestions)
    else:
        st.warning(current_locale["upload_data_first"])

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
