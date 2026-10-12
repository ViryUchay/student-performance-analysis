"""
Student Performance Data Analysis Dashboard
CSE 310 - Applied Programming - Module 3 (Data Analysis)

Author: Vivian Eze
Date: October 2026

Description:
    An interactive Streamlit dashboard that visualizes student performance data.
    Run with: streamlit run dashboard.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

DATA_PATH = "data/student_performance.csv"

st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

sns.set_style("whitegrid")

# ---------------------------------------------------------------------------
# DATA LOADING AND CLEANING
# ---------------------------------------------------------------------------

@st.cache_data
def load_and_clean_data(path: str) -> pd.DataFrame:
    """Load, clean, and enrich the student performance dataset."""
    df = pd.read_csv(path)

    # Remove duplicates
    df = df.drop_duplicates(subset="student_id", keep="first")

    # Fill missing numeric scores with column means
    score_cols = ["math_score", "science_score", "english_score", "history_score"]
    for col in score_cols:
        df[col] = df[col].fillna(df[col].mean())

    # Derived columns
    df["average_score"] = df[score_cols].mean(axis=1).round(1)

    def performance_category(gpa):
        if gpa >= 3.5:
            return "Excellent"
        elif gpa >= 3.0:
            return "Good"
        elif gpa >= 2.0:
            return "Average"
        else:
            return "Needs Improvement"

    df["performance_category"] = df["gpa"].apply(performance_category)
    df["pass_fail"] = np.where(df["gpa"] >= 2.0, "Pass", "Fail")

    return df


# ---------------------------------------------------------------------------
# DASHBOARD LAYOUT
# ---------------------------------------------------------------------------

def main():
    # Header
    st.title("📊 Student Performance Data Analysis Dashboard")
    st.markdown(
        "An interactive dashboard for exploring student academic performance "
        "across subjects, grade levels, gender, and behavioral factors."
    )

    # Check that data exists
    if not os.path.exists(DATA_PATH):
        st.error(
            f"Dataset not found at `{DATA_PATH}`. "
            "Please run `student_performance_analysis.py` first to generate it."
        )
        return

    # Load data
    df = load_and_clean_data(DATA_PATH)

    # -----------------------------------------------------------------------
    # SIDEBAR FILTERS
    # -----------------------------------------------------------------------

    st.sidebar.header("🔎 Filters")

    # Gender filter
    genders = ["All"] + sorted(df["gender"].unique().tolist())
    selected_gender = st.sidebar.selectbox("Gender", genders)

    # Grade level filter
    grade_levels = ["All"] + sorted(df["grade_level"].unique().tolist())
    selected_grade = st.sidebar.selectbox("Grade Level", grade_levels)

    # Performance category filter
    categories = ["All"] + sorted(df["performance_category"].unique().tolist())
    selected_category = st.sidebar.selectbox("Performance Category", categories)

    # GPA range slider
    gpa_min, gpa_max = float(df["gpa"].min()), float(df["gpa"].max())
    gpa_range = st.sidebar.slider(
        "GPA Range",
        min_value=gpa_min,
        max_value=gpa_max,
        value=(gpa_min, gpa_max),
        step=0.1,
    )

    # Study hours slider
    study_min, study_max = float(df["study_hours_per_week"].min()), float(df["study_hours_per_week"].max())
    study_range = st.sidebar.slider(
        "Study Hours per Week",
        min_value=study_min,
        max_value=study_max,
        value=(study_min, study_max),
        step=1.0,
    )

    # Apply filters
    filtered = df.copy()
    if selected_gender != "All":
        filtered = filtered[filtered["gender"] == selected_gender]
    if selected_grade != "All":
        filtered = filtered[filtered["grade_level"] == selected_grade]
    if selected_category != "All":
        filtered = filtered[filtered["performance_category"] == selected_category]

    filtered = filtered[
        (filtered["gpa"] >= gpa_range[0]) &
        (filtered["gpa"] <= gpa_range[1]) &
        (filtered["study_hours_per_week"] >= study_range[0]) &
        (filtered["study_hours_per_week"] <= study_range[1])
    ]

    st.sidebar.markdown(f"**Students matching filters:** {len(filtered)}")

    # -----------------------------------------------------------------------
    # KPI METRICS
    # -----------------------------------------------------------------------

    st.subheader("📌 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", f"{len(filtered)}")
    col2.metric("Average GPA", f"{filtered['gpa'].mean():.2f}")
    col3.metric("Average Attendance", f"{filtered['attendance_rate'].mean():.1f}%")
    col4.metric("Average Study Hours", f"{filtered['study_hours_per_week'].mean():.1f} hrs/wk")

    st.markdown("---")

    # -----------------------------------------------------------------------
    # CHARTS
    # -----------------------------------------------------------------------

    # Row 1: Subject averages + GPA by grade level
    st.subheader("📈 Academic Performance")

    col1, col2 = st.columns(2)

    with col1:
        subject_cols = ["math_score", "science_score", "english_score", "history_score"]
        subject_means = filtered[subject_cols].mean()

        fig, ax = plt.subplots(figsize=(6, 4))
        subject_means.plot(kind="bar", color="steelblue", edgecolor="black", ax=ax)
        ax.set_title("Average Score by Subject")
        ax.set_ylabel("Average Score")
        ax.set_xticklabels([s.replace("_score", "").title() for s in subject_cols], rotation=0)
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        filtered.groupby("grade_level")["gpa"].mean().plot(
            kind="bar", color="seagreen", edgecolor="black", ax=ax
        )
        ax.set_title("Average GPA by Grade Level")
        ax.set_ylabel("Average GPA")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        st.pyplot(fig)
        plt.close(fig)

    # Row 2: GPA distribution + performance categories
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(filtered["gpa"], bins=20, kde=True, color="purple", ax=ax)
        ax.set_title("Distribution of GPA")
        ax.set_xlabel("GPA")
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        filtered["performance_category"].value_counts().plot(
            kind="pie",
            autopct="%1.1f%%",
            startangle=90,
            colors=["#66b3ff", "#99ff99", "#ffcc99", "#ff9999"],
            ax=ax,
        )
        ax.set_title("Performance Category Distribution")
        ax.set_ylabel("")
        st.pyplot(fig)
        plt.close(fig)

    # Row 3: Study hours vs GPA + correlation heatmap
    st.subheader("🔬 Relationships and Correlations")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(
            x="study_hours_per_week",
            y="gpa",
            hue="gender",
            data=filtered,
            alpha=0.7,
            ax=ax,
        )
        ax.set_title("Study Hours vs GPA")
        ax.set_xlabel("Study Hours per Week")
        ax.set_ylabel("GPA")
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        numeric_cols = [
            "math_score", "science_score", "english_score", "history_score",
            "attendance_rate", "study_hours_per_week", "gpa",
        ]
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(
            filtered[numeric_cols].corr(),
            annot=True,
            cmap="coolwarm",
            fmt=".2f",
            linewidths=0.5,
            ax=ax,
        )
        ax.set_title("Correlation Heatmap")
        st.pyplot(fig)
        plt.close(fig)

    # Row 4: GPA by gender + attendance bracket
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(x="gender", y="gpa", data=filtered, palette="Set2", ax=ax)
        ax.set_title("GPA Distribution by Gender")
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        temp = filtered.copy()
        temp["attendance_bracket"] = pd.cut(
            temp["attendance_rate"],
            bins=[50, 70, 80, 90, 100],
            labels=["50-70%", "70-80%", "80-90%", "90-100%"],
        )
        fig, ax = plt.subplots(figsize=(6, 4))
        temp.groupby("attendance_bracket", observed=True)["gpa"].mean().plot(
            kind="line", marker="o", color="darkorange", ax=ax
        )
        ax.set_title("Average GPA by Attendance Bracket")
        ax.set_xlabel("Attendance Rate")
        ax.set_ylabel("Average GPA")
        st.pyplot(fig)
        plt.close(fig)

    # -----------------------------------------------------------------------
    # DATA TABLE
    # -----------------------------------------------------------------------

    st.subheader("📋 Filtered Data Table")
    st.dataframe(filtered, use_container_width=True)

    # Download button
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_student_data.csv",
        mime="text/csv",
    )

    # -----------------------------------------------------------------------
    # FOOTER
    # -----------------------------------------------------------------------

    st.markdown("---")
    st.caption("© 2026 Vivian Eze — CSE 310 Module 3: Data Analysis")


if __name__ == "__main__":
    main()