import io
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Data Analytics Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Custom UI Styling (Preserved original gradient theme)
st.markdown(
    """
    <style>
    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Header Styling */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 700;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Main Titles
st.markdown(
    '<h1 class="main-title">🚀 Simple Data Analytics Hub</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Upload your CSV or Excel file to clean data, view basic charts, and export to Power BI</p>',
    unsafe_allow_html=True,
)

# Centered File Uploader
col_center1, col_center2, col_center3 = st.columns([1, 2, 1])
with col_center2:
    uploaded_file = st.file_uploader(
        "📁 Drag and drop or browse file",
        type=["csv", "xlsx"],
        help="Upload CSV or Excel file to get started",
    )

st.markdown("---")


# Helper function to convert dataframe to CSV download
def convert_df_to_csv(data_frame):
    return data_frame.to_csv(index=False).encode("utf-8")


# Helper function to convert dataframe to Power BI Excel download
def convert_df_to_powerbi_excel(data_frame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data_frame.to_excel(writer, index=False, sheet_name="PowerBI_Data")
    return output.getvalue()


# Main Dashboard Logic
if uploaded_file is not None:
    try:
        # Load File into Session State so clean actions persist
        if (
            "df" not in st.session_state
            or st.session_state.get("file_name") != uploaded_file.name
        ):
            raw_df = (
                pd.read_csv(uploaded_file)
                if uploaded_file.name.endswith(".csv")
                else pd.read_excel(uploaded_file)
            )
            st.session_state["df"] = raw_df
            st.session_state["file_name"] = uploaded_file.name

        df = st.session_state["df"]

        st.success(f"Successfully loaded `{uploaded_file.name}`")

        # Key Metrics Summary Row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rows", f"{df.shape[0]:,}")
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Missing Values", df.isnull().sum().sum())
        col4.metric(
            "Duplicates",
            df.duplicated().sum(),
            delta="-Clean up" if df.duplicated().sum() > 0 else "Clean",
        )

        st.markdown("---")

        # Simplified Tab Structure
        tab1, tab2, tab3 = st.tabs(
            [
                "📊 Easy Charts",
                "📋 Data Cleaning & Inspection",
                "🟡 Power BI Export",
            ]
        )

        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        cat_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        # TAB 1: Beginner Visual Charts
        with tab1:
            st.subheader("Simple Visualizations")
            col_left, col_right = st.columns([1, 2])

            with col_left:
                chart_type = st.selectbox(
                    "Select Chart Type",
                    ["Bar Chart", "Donut Chart", "Histogram (Count)"],
                )

                if chart_type in ["Bar Chart", "Donut Chart"] and cat_cols:
                    selected_cat = st.selectbox(
                        "Category Column (Labels)", cat_cols
                    )
                    selected_num = st.selectbox(
                        "Value Column (Optional)", [None] + num_cols
                    )
                elif chart_type == "Histogram (Count)" and num_cols:
                    selected_num = st.selectbox(
                        "Select Numeric Variable", num_cols
                    )
                    selected_cat = None
                else:
                    selected_cat, selected_num = None, None

            with col_right:
                if chart_type == "Bar Chart" and selected_cat:
                    if selected_num:
                        fig = px.bar(
                            df,
                            x=selected_cat,
                            y=selected_num,
                            color=selected_cat,
                            title=f"{selected_num} by {selected_cat}",
                        )
                    else:
                        counts = df[selected_cat].value_counts().reset_index()
                        counts.columns = [selected_cat, "Count"]
                        fig = px.bar(
                            counts,
                            x=selected_cat,
                            y="Count",
                            color=selected_cat,
                            title=f"Total Count by {selected_cat}",
                        )

                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Donut Chart" and selected_cat:
                    if selected_num:
                        fig = px.pie(
                            df,
                            names=selected_cat,
                            values=selected_num,
                            hole=0.4,
                            title=f"{selected_num} Breakdown by {selected_cat}",
                        )
                    else:
                        counts = df[selected_cat].value_counts().reset_index()
                        counts.columns = [selected_cat, "Count"]
                        fig = px.pie(
                            counts,
                            names=selected_cat,
                            values="Count",
                            hole=0.4,
                            title=f"Distribution of {selected_cat}",
                        )

                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Histogram (Count)" and selected_num:
                    fig = px.histogram(
                        df,
                        x=selected_num,
                        title=f"Distribution of {selected_num}",
                        color_discrete_sequence=["#38bdf8"],
                    )
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(
                        "Please ensure your dataset contains compatible text or numerical columns for the selected chart."
                    )

        # TAB 2: Data Cleaning & Download
        with tab2:
            st.subheader("Clean & Download Dataset")
            st.markdown(
                "Click the button below to **remove duplicate rows** and automatically fill missing values."
            )

            col_clean_act1, col_clean_act2 = st.columns([1, 2])

            with col_clean_act1:
                if st.button("🧹 Clean Data & Remove Duplicates"):
                    initial_dup_count = df.duplicated().sum()

                    # Drop Duplicate Rows
                    cleaned_df = df.drop_duplicates()

                    # Fill Missing Values
                    for col in cleaned_df.columns:
                        if cleaned_df[col].dtype in ["int64", "float64"]:
                            cleaned_df[col] = cleaned_df[col].fillna(
                                cleaned_df[col].median()
                            )
                        else:
                            cleaned_df[col] = cleaned_df[col].fillna("Unknown")

                    # Save cleaned dataset to state and refresh view
                    st.session_state["df"] = cleaned_df
                    st.success(
                        f"Removed {initial_dup_count} duplicate row(s) and handled missing values!"
                    )
                    st.rerun()

            cleaned_csv = convert_df_to_csv(df)
            st.download_button(
                label="📥 Download Cleaned CSV Data",
                data=cleaned_csv,
                file_name="Cleaned_Dataset.csv",
                mime="text/csv",
            )

            st.markdown("#### Dataset Preview")
            st.dataframe(df, use_container_width=True)

        # TAB 3: Power BI Export
        with tab3:
            st.subheader("🟡 Export Dataset for Power BI Dashboard")
            st.markdown(
                "Download your dataset as an Excel file and use these simple DAX formulas inside Power BI Desktop."
            )

            col_pbi1, col_pbi2 = st.columns(2)

            with col_pbi1:
                st.markdown("### 1. Simple DAX Measures")
                st.markdown(
                    "Copy and paste these beginner DAX measures into Power BI:"
                )

                first_num = num_cols[0] if num_cols else "Value"
                table_name = (
                    uploaded_file.name.split(".")[0]
                    .replace(" ", "_")
                    .replace("-", "_")
                )

                dax_code = f"""
// 1. Total Rows Measure
Total Records = COUNTROWS('{table_name}')

// 2. Sum Aggregation Measure
Total {first_num} = SUM('{table_name}'[{first_num}])

// 3. Average Aggregation Measure
Average {first_num} = AVERAGE('{table_name}'[{first_num}])
                """
                st.code(dax_code, language="dax")

            with col_pbi2:
                st.markdown("### 2. Download & Import Steps")

                pbi_excel_data = convert_df_to_powerbi_excel(df)
                st.download_button(
                    label="⚡ Download Power BI Excel File",
                    data=pbi_excel_data,
                    file_name="PowerBI_Dataset.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

                st.markdown("""
                **Quick Steps:**
                1. Click the button above to download `PowerBI_Dataset.xlsx`.
                2. Open **Power BI Desktop**.
                3. Click **Get Data > Excel Workbook** and select the downloaded file.
                4. Select the `PowerBI_Data` sheet and click **Load**.
                5. Add visual cards and charts using the dataset columns.
                """)

    except Exception as e:
        st.error(f"Error reading dataset: {e}")
else:
    st.info(
        "👈 Please upload a CSV or Excel file using the box above to get started."
    )
