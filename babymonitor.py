# PART 4
# Build a Streamlit App

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
from collections import Counter

# Set page configuration
st.set_page_config(
    page_title="Medical Monitoring Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('monitoringdata.csv')
        return df
    except FileNotFoundError:
        st.error("File 'monitoringdata.csv' not found. Please make sure it's in the same directory.")
        return pd.DataFrame()

# Main app
def main():
    # Title and description
    st.title("🏥 Medical Monitoring Data Dashboard")
    st.markdown("""
    This interactive dashboard allows you to explore and visualize medical monitoring data.
    Use the sidebar controls to filter data and generate insights.
    """)

    # Load data
    df = load_data()

    if df.empty:
        st.stop()

    # Sidebar
    st.sidebar.header("📊 Control Panel")

    # Display basic info
    st.sidebar.subheader("Dataset Info")
    st.sidebar.write(f"**Total records:** {len(df)}")
    st.sidebar.write(f"**Total columns:** {len(df.columns)}")
    st.sidebar.write(f"**Data types:**")
    for dtype, count in df.dtypes.value_counts().items():
        st.sidebar.write(f"  - {dtype}: {count}")

    # Interactive filters
    st.sidebar.subheader("🔍 Data Filters")

    # Numeric column filters
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        selected_numeric = st.sidebar.selectbox("Select numeric column to filter:", numeric_cols)
        if selected_numeric:
            min_val = float(df[selected_numeric].min())
            max_val = float(df[selected_numeric].max())
            selected_range = st.sidebar.slider(
                f"Filter {selected_numeric}:",
                min_val, max_val, (min_val, max_val)
            )
            df = df[(df[selected_numeric] >= selected_range[0]) &
                (df[selected_numeric] <= selected_range[1])]

    # Categorical filters
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    if categorical_cols:
        selected_cat = st.sidebar.selectbox("Select categorical column to filter:", categorical_cols)
        if selected_cat:
            unique_vals = df[selected_cat].unique()
            selected_vals = st.sidebar.multiselect(
                f"Select {selected_cat}:",
                options=unique_vals,
                default=unique_vals
            )
            df = df[df[selected_cat].isin(selected_vals)]

    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", "🌡️ Temperature Analysis", "👶 Baby Data",
        "📋 Data Sample", "📊 Advanced Visualizations"
    ])

    with tab1:
        st.header("Data Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Basic Statistics")
            st.dataframe(df.describe(), use_container_width=True)

        with col2:
            st.subheader("Missing Values")
            missing_data = df.isnull().sum()
            missing_df = pd.DataFrame({
                'Column': missing_data.index,
                'Missing Values': missing_data.values,
                'Percentage': (missing_data.values / len(df)) * 100
            })
            st.dataframe(missing_df[missing_df['Missing Values'] > 0], use_container_width=True)

            if missing_df['Missing Values'].sum() == 0:
                st.success("No missing values found!")

    with tab2:
        st.header("Temperature Analysis")

        if 'temperature_c' in df.columns:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Temperature Distribution")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.histplot(df['temperature_c'].dropna(), kde=True, ax=ax)
                ax.set_xlabel('Temperature (°C)')
                ax.set_ylabel('Frequency')
                ax.set_title('Temperature Distribution')
                st.pyplot(fig)

            with col2:
                st.subheader("Temperature Stats")
                temp_stats = df['temperature_c'].describe()
                st.metric("Mean Temperature", f"{temp_stats['mean']:.2f}°C")
                st.metric("Standard Deviation", f"{temp_stats['std']:.2f}°C")
                st.metric("Minimum", f"{temp_stats['min']:.2f}°C")
                st.metric("Maximum", f"{temp_stats['max']:.2f}°C")

        else:
            st.warning("Temperature data not available")

    with tab3:
        st.header("Baby Data Analysis")

        # Check for baby-related columns
        baby_cols = [col for col in df.columns if 'baby' in col.lower() or 'birth' in col.lower()]

        if baby_cols:
            st.subheader("Baby-related Data")

            for col in baby_cols:
                if df[col].dtype in ['object', 'string']:
                    st.write(f"**{col}** value counts:")
                    st.bar_chart(df[col].value_counts())
                else:
                    st.write(f"**{col}** distribution:")
                    st.line_chart(df[col].value_counts())

        else:
            st.info("No baby-specific columns found")

    with tab4:
        st.header("Data Sample")

        st.subheader("Raw Data Preview")
        rows_to_show = st.slider("Number of rows to show:", 5, 100, 10)
        st.dataframe(df.head(rows_to_show), use_container_width=True)

        st.subheader("Column Information")
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.values,
            'Non-Null Count': df.notnull().sum().values,
            'Unique Values': df.nunique().values
        })
        st.dataframe(col_info, use_container_width=True)

    with tab5:
        st.header("Advanced Visualizations")

        viz_type = st.selectbox(
            "Select visualization type:",
            ["Scatter Plot", "Heatmap", "Box Plot", "Correlation Matrix"]
        )

        if viz_type == "Scatter Plot":
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(num_cols) >= 2:
                x_col = st.selectbox("X-axis:", num_cols)
                y_col = st.selectbox("Y-axis:", num_cols)

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.scatter(df[x_col], df[y_col], alpha=0.6)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f'{y_col} vs {x_col}')
                st.pyplot(fig)

        elif viz_type == "Correlation Matrix":
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(num_cols) > 1:
                corr_matrix = df[num_cols].corr()
                fig, ax = plt.subplots(figsize=(12, 8))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
                ax.set_title('Correlation Matrix')
                st.pyplot(fig)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 Tip: Use the filters in the sidebar to explore specific subsets of your data. "
        "The visualizations will update automatically."
    )

if __name__ == "__main__":
    main()