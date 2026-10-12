# Student Performance Data Analysis – Summary Report

**Date:** October 12, 2026

**Dataset size:** 500 students, 16 columns

## Overview

This report summarizes the analysis of student academic performance data. The goal was to identify trends and patterns related to gender, grade level, study habits, attendance, and overall academic outcomes.

## Key Statistics

- **Average GPA:** 2.97
- **Average Attendance:** 87.0%
- **Average Study Hours per Week:** 9.7

### Average Score by Subject

| Subject | Average Score |
|---------|---------------|
| Math Score | 76.39 |
| Science Score | 74.64 |
| English Score | 73.37 |
| History Score | 72.90 |

### Averages by Gender

| gender   |   gpa |   attendance_rate |   study_hours_per_week |
|:---------|------:|------------------:|-----------------------:|
| Female   |  2.98 |             87.6  |                   9.97 |
| Male     |  2.97 |             86.44 |                   9.45 |

### Averages by Grade Level

| grade_level   |   gpa |   math_score |   science_score |   english_score |   history_score |
|:--------------|------:|-------------:|----------------:|----------------:|----------------:|
| 10th          |  3.03 |        77.81 |           75.9  |           75.04 |           74.72 |
| 11th          |  2.97 |        76.56 |           74.98 |           73.25 |           72.31 |
| 12th          |  2.89 |        73.67 |           72.36 |           71.51 |           71.41 |
| 9th           |  3    |        77.46 |           75.23 |           73.69 |           73.27 |

## Key Findings

1. **Most common performance category:** Average (234 students).
2. **Highest-performing subject:** Math Score (average 76.39).
3. **Lowest-performing subject:** History Score (average 72.90).
4. **Strongest correlation with GPA:** science score (r = 0.95).
5. Students with higher attendance and study hours tend to earn higher GPAs.

## Visualizations

The following charts are saved in the `output/visualizations/` folder:

1. Average Score by Subject
2. Average GPA by Grade Level
3. Distribution of Performance Categories
4. Distribution of GPA
5. GPA Distribution by Gender
6. Study Hours vs GPA
7. Correlation Heatmap
8. Average GPA by Attendance Bracket

## Conclusion

The analysis shows that study habits and attendance are meaningful predictors of academic performance. Educators can use these insights to design targeted interventions for students who are struggling, particularly those with low attendance or limited study time.
