"""
Student Performance Data Analysis Tool
CSE 310 - Applied Programming - Module 3 (Data Analysis)

Author: Vivian Eze
Date: October 2026

Description:
    This script loads, cleans, analyzes, and visualizes student performance data.
    It produces charts and a summary report that identify trends and patterns
    in academic performance based on gender, grade level, study habits, and attendance.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

DATA_PATH = "data/student_performance.csv"
OUTPUT_DIR = "output"
VIZ_DIR = os.path.join(OUTPUT_DIR, "visualizations")
REPORT_PATH = os.path.join(OUTPUT_DIR, "summary_report.md")

# Create output directories if they don't exist
os.makedirs(VIZ_DIR, exist_ok=True)

# Set a clean visual style for all charts
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["figure.dpi"] = 100


# ---------------------------------------------------------------------------
# 1. GENERATE DATASET (only if one does not already exist)
# ---------------------------------------------------------------------------

def generate_dataset(path: str, n_students: int = 500) -> pd.DataFrame:
    """
    Generate a realistic synthetic student performance dataset and save it as CSV.
    This is used if no real dataset is available.
    """
    np.random.seed(42)

    genders = ["Male", "Female"]
    grade_levels = ["9th", "10th", "11th", "12th"]
    extracurriculars = ["Yes", "No"]

    records = []
    for i in range(1, n_students + 1):
        gender = np.random.choice(genders)
        grade = np.random.choice(grade_levels)
        age = {"9th": 14, "10th": 15, "11th": 16, "12th": 17}[grade] + np.random.randint(0, 2)

        # Base ability influences all scores
        base_ability = np.random.normal(70, 12)

        # Study hours influence scores
        study_hours = max(0, np.random.normal(10, 5))

        # Attendance rate (percentage)
        attendance = np.clip(np.random.normal(88, 8), 50, 100)

        # Subject scores influenced by ability, study hours, and attendance
        math = np.clip(base_ability + study_hours * 0.4 + (attendance - 80) * 0.3 + np.random.normal(0, 5), 0, 100)
        science = np.clip(base_ability + study_hours * 0.3 + (attendance - 80) * 0.3 + np.random.normal(0, 5), 0, 100)
        english = np.clip(base_ability + study_hours * 0.2 + (attendance - 80) * 0.2 + np.random.normal(0, 5), 0, 100)
        history = np.clip(base_ability + study_hours * 0.2 + (attendance - 80) * 0.2 + np.random.normal(0, 5), 0, 100)

        avg_score = np.mean([math, science, english, history])
        gpa = round(np.clip(avg_score / 25, 0.0, 4.0), 2)

        extracurricular = np.random.choice(extracurriculars, p=[0.6, 0.4])

        records.append({
            "student_id": f"S{i:04d}",
            "gender": gender,
            "age": age,
            "grade_level": grade,
            "math_score": round(math, 1),
            "science_score": round(science, 1),
            "english_score": round(english, 1),
            "history_score": round(history, 1),
            "attendance_rate": round(attendance, 1),
            "study_hours_per_week": round(study_hours, 1),
            "extracurricular": extracurricular,
            "gpa": gpa,
        })

    df = pd.DataFrame(records)

    # Introduce some missing values and duplicates to make cleaning meaningful
    for col in ["math_score", "science_score", "english_score", "history_score"]:
        missing_indices = np.random.choice(df.index, size=8, replace=False)
        df.loc[missing_indices, col] = np.nan

    # Add a few duplicate rows
    duplicates = df.sample(5, random_state=1)
    df = pd.concat([df, duplicates], ignore_index=True)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[INFO] Synthetic dataset generated and saved to {path}")
    return df


# ---------------------------------------------------------------------------
# 2. LOAD AND INSPECT DATA
# ---------------------------------------------------------------------------

def load_data(path: str) -> pd.DataFrame:
    """Load the student performance CSV into a pandas DataFrame."""
    if not os.path.exists(path):
        print("[INFO] Dataset not found. Generating a new one...")
        return generate_dataset(path)

    df = pd.read_csv(path)
    print(f"[INFO] Dataset loaded from {path}")
    return df


def inspect_data(df: pd.DataFrame) -> None:
    """Print basic information about the dataset."""
    print("\n" + "=" * 60)
    print("DATA INSPECTION")
    print("=" * 60)
    print(f"\nShape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nData types and non-null counts:")
    print(df.info())
    print("\nSummary statistics:")
    print(df.describe(include="all"))


# ---------------------------------------------------------------------------
# 3. CLEAN AND PREPARE DATA
# ---------------------------------------------------------------------------

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the dataset: handle missing values, duplicates, and derived columns."""
    print("\n" + "=" * 60)
    print("DATA CLEANING")
    print("=" * 60)

    original_shape = df.shape

    # Remove duplicates
    df = df.drop_duplicates(subset="student_id", keep="first")
    print(f"[INFO] Removed {original_shape[0] - df.shape[0]} duplicate rows.")

    # Fill missing numeric scores with the column mean
    score_cols = ["math_score", "science_score", "english_score", "history_score"]
    for col in score_cols:
        missing = df[col].isnull().sum()
        if missing > 0:
            df[col] = df[col].fillna(df[col].mean())
            print(f"[INFO] Filled {missing} missing values in '{col}' with the column mean.")

    # Ensure correct data types
    df["attendance_rate"] = df["attendance_rate"].astype(float)
    df["study_hours_per_week"] = df["study_hours_per_week"].astype(float)
    df["gpa"] = df["gpa"].astype(float)

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

    print(f"[INFO] Final dataset shape after cleaning: {df.shape}")
    return df


# ---------------------------------------------------------------------------
# 4. EXPLORATORY DATA ANALYSIS
# ---------------------------------------------------------------------------

def exploratory_analysis(df: pd.DataFrame) -> dict:
    """Compute summary statistics and grouped aggregates."""
    print("\n" + "=" * 60)
    print("EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    results = {}

    # Overall averages
    results["avg_gpa"] = df["gpa"].mean()
    results["avg_attendance"] = df["attendance_rate"].mean()
    results["avg_study_hours"] = df["study_hours_per_week"].mean()

    print(f"\nAverage GPA: {results['avg_gpa']:.2f}")
    print(f"Average Attendance: {results['avg_attendance']:.1f}%")
    print(f"Average Study Hours/Week: {results['avg_study_hours']:.1f}")

    # Subject averages
    subject_cols = ["math_score", "science_score", "english_score", "history_score"]
    results["subject_means"] = df[subject_cols].mean().round(2)
    print("\nAverage score by subject:")
    print(results["subject_means"])

    # Group by gender
    results["by_gender"] = df.groupby("gender")[["gpa", "attendance_rate", "study_hours_per_week"]].mean().round(2)
    print("\nAverages by gender:")
    print(results["by_gender"])

    # Group by grade level
    results["by_grade"] = df.groupby("grade_level")[["gpa", "math_score", "science_score", "english_score", "history_score"]].mean().round(2)
    print("\nAverages by grade level:")
    print(results["by_grade"])

    # Group by performance category
    results["by_category"] = df["performance_category"].value_counts()
    print("\nStudents per performance category:")
    print(results["by_category"])

    # Correlation matrix
    numeric_cols = ["math_score", "science_score", "english_score", "history_score",
                    "attendance_rate", "study_hours_per_week", "gpa"]
    results["correlation"] = df[numeric_cols].corr().round(2)
    print("\nCorrelation matrix:")
    print(results["correlation"])

    return results


# ---------------------------------------------------------------------------
# 5. VISUALIZATIONS
# ---------------------------------------------------------------------------

def create_visualizations(df: pd.DataFrame) -> None:
    """Create and save a variety of charts to the output folder."""
    print("\n" + "=" * 60)
    print("CREATING VISUALIZATIONS")
    print("=" * 60)

    subject_cols = ["math_score", "science_score", "english_score", "history_score"]

    # 1. Bar chart: Average score per subject
    plt.figure()
    df[subject_cols].mean().plot(kind="bar", color="steelblue", edgecolor="black")
    plt.title("Average Score by Subject")
    plt.ylabel("Average Score")
    plt.xlabel("Subject")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, "01_avg_score_by_subject.png"))
    plt.close()
    print("[INFO] Saved 01_avg_score_by_subject.png")

    # 2. Bar chart: Average GPA by grade level
    plt.figure()
    df.groupby("grade_level")["gpa"].mean().plot(kind="bar", color="seagreen", edgecolor="black")
    plt.title("Average GPA by Grade Level")
    plt.ylabel("Average GPA")
    plt.xlabel("Grade Level")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, "02_avg_gpa_by_grade.png"))
    plt.close()
    print("[INFO] Saved 02_avg_gpa_by_grade.png")

    # 3. Pie chart: Performance category distribution
    plt.figure()
    df["performance_category"].value_counts().plot(
        kind="pie", autopct="%1.1f%%", startangle=90,
        colors=["#66b3ff", "#99ff99", "#ffcc99", "#ff9999"]
    )
    plt.title("Distribution of Performance Categories")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, "03_performance_categories.png"))
    plt.close()
    print("[INFO] Saved 03_performance_categories.png")

    # 4. Histogram: GPA distribution
    plt.figure()
    sns.histplot(df["gpa"], bins=20, kde=True, color="purple")
    plt.title("Distribution of GPA")
    plt.xlabel("GPA")
    plt.ylabel("Number of Students")
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, "04_gpa_distribution.png"))
    plt.close()
    print("[INFO] Saved 04_gpa_distribution.png")

    # 5. Box plot: GPA by gender
    plt.figure()
    sns.boxplot(x="gender", y="gpa", data=df, palette="Set2")
    plt.title("GPA Distribution by Gender")
    plt.xlabel("Gender")
    plt.ylabel("GPA")
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, "05_gpa_by_gender.png"))
    plt.close()
    print("[INFO] Saved 05_gpa_by_gender.png")

    # 6. Scatter plot: Study hours vs GPA
    plt.figure()
    sns.scatterplot(x="study_hours_per_week", y="gpa", hue="gender", data=df, alpha=0.7)
    plt.title("Study Hours vs GPA")
    plt.xlabel("Study Hours per Week")
    plt.ylabel("GPA")
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, "06_study_hours_vs_gpa.png"))
    plt.close()
    print("[INFO] Saved 06_study_hours_vs_gpa.png")

    # 7. Heatmap: Correlation matrix
    plt.figure(figsize=(10, 8))
    numeric_cols = ["math_score", "science_score", "english_score", "history_score",
                    "attendance_rate", "study_hours_per_week", "gpa"]
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Correlation Heatmap of Numerical Variables")
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, "07_correlation_heatmap.png"))
    plt.close()
    print("[INFO] Saved 07_correlation_heatmap.png")

    # 8. Line chart: Average GPA by attendance bracket
    plt.figure()
    df["attendance_bracket"] = pd.cut(df["attendance_rate"],
                                      bins=[50, 70, 80, 90, 100],
                                      labels=["50-70%", "70-80%", "80-90%", "90-100%"])
    df.groupby("attendance_bracket", observed=True)["gpa"].mean().plot(kind="line", marker="o", color="darkorange")
    plt.title("Average GPA by Attendance Bracket")
    plt.xlabel("Attendance Rate")
    plt.ylabel("Average GPA")
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, "08_gpa_by_attendance.png"))
    plt.close()
    print("[INFO] Saved 08_gpa_by_attendance.png")

    print(f"\n[INFO] All visualizations saved to {VIZ_DIR}/")


# ---------------------------------------------------------------------------
# 6. SUMMARY REPORT
# ---------------------------------------------------------------------------

def generate_report(df: pd.DataFrame, results: dict) -> None:
    """Write a markdown summary report of key findings."""
    print("\n" + "=" * 60)
    print("GENERATING SUMMARY REPORT")
    print("=" * 60)

    top_category = results["by_category"].idxmax()
    top_category_count = results["by_category"].max()
    best_subject = results["subject_means"].idxmax()
    worst_subject = results["subject_means"].idxmin()

    # Strongest correlation with GPA (excluding GPA itself)
    corr = results["correlation"]["gpa"].drop("gpa")
    strongest_corr_var = corr.abs().idxmax()
    strongest_corr_val = corr[strongest_corr_var]

    with open(REPORT_PATH, "w") as f:
        f.write("# Student Performance Data Analysis – Summary Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%B %d, %Y')}\n\n")
        f.write(f"**Dataset size:** {df.shape[0]} students, {df.shape[1]} columns\n\n")

        f.write("## Overview\n\n")
        f.write("This report summarizes the analysis of student academic performance data. "
                "The goal was to identify trends and patterns related to gender, grade level, "
                "study habits, attendance, and overall academic outcomes.\n\n")

        f.write("## Key Statistics\n\n")
        f.write(f"- **Average GPA:** {results['avg_gpa']:.2f}\n")
        f.write(f"- **Average Attendance:** {results['avg_attendance']:.1f}%\n")
        f.write(f"- **Average Study Hours per Week:** {results['avg_study_hours']:.1f}\n\n")

        f.write("### Average Score by Subject\n\n")
        f.write("| Subject | Average Score |\n")
        f.write("|---------|---------------|\n")
        for subject, score in results["subject_means"].items():
            f.write(f"| {subject.replace('_', ' ').title()} | {score:.2f} |\n")
        f.write("\n")

        f.write("### Averages by Gender\n\n")
        f.write(results["by_gender"].to_markdown())
        f.write("\n\n")

        f.write("### Averages by Grade Level\n\n")
        f.write(results["by_grade"].to_markdown())
        f.write("\n\n")

        f.write("## Key Findings\n\n")
        f.write(f"1. **Most common performance category:** {top_category} "
                f"({top_category_count} students).\n")
        f.write(f"2. **Highest-performing subject:** {best_subject.replace('_', ' ').title()} "
                f"(average {results['subject_means'][best_subject]:.2f}).\n")
        f.write(f"3. **Lowest-performing subject:** {worst_subject.replace('_', ' ').title()} "
                f"(average {results['subject_means'][worst_subject]:.2f}).\n")
        f.write(f"4. **Strongest correlation with GPA:** {strongest_corr_var.replace('_', ' ')} "
                f"(r = {strongest_corr_val:.2f}).\n")
        f.write("5. Students with higher attendance and study hours tend to earn higher GPAs.\n\n")

        f.write("## Visualizations\n\n")
        f.write("The following charts are saved in the `output/visualizations/` folder:\n\n")
        f.write("1. Average Score by Subject\n")
        f.write("2. Average GPA by Grade Level\n")
        f.write("3. Distribution of Performance Categories\n")
        f.write("4. Distribution of GPA\n")
        f.write("5. GPA Distribution by Gender\n")
        f.write("6. Study Hours vs GPA\n")
        f.write("7. Correlation Heatmap\n")
        f.write("8. Average GPA by Attendance Bracket\n\n")

        f.write("## Conclusion\n\n")
        f.write("The analysis shows that study habits and attendance are meaningful predictors "
                "of academic performance. Educators can use these insights to design targeted "
                "interventions for students who are struggling, particularly those with low "
                "attendance or limited study time.\n")

    print(f"[INFO] Summary report saved to {REPORT_PATH}")


# ---------------------------------------------------------------------------
# 7. MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("STUDENT PERFORMANCE DATA ANALYSIS TOOL")
    print("=" * 60)

    # Load (or generate) data
    df = load_data(DATA_PATH)

    # Inspect
    inspect_data(df)

    # Clean
    df = clean_data(df)

    # Analyze
    results = exploratory_analysis(df)

    # Visualize
    create_visualizations(df)

    # Report
    generate_report(df, results)

    # Save cleaned data for reference
    cleaned_path = os.path.join(OUTPUT_DIR, "cleaned_student_performance.csv")
    df.to_csv(cleaned_path, index=False)
    print(f"[INFO] Cleaned dataset saved to {cleaned_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()