"""analytics.py - data layer of the Student Performance Analytics Dashboard.

All record handling and calculations live here (no GUI code), so the logic
can be tested on its own. Uses OOP (CO1) and Pandas (CO4).
"""
import os
import pandas as pd

SUBJECTS = ["Maths", "Python", "DBMS", "OS", "AI"]
MAX_MARKS = 100
PASS_MARKS = 40
CSV_FILE = "students.csv"


class Student:
    """One student's record."""

    def __init__(self, roll, name, marks):
        self.roll = roll
        self.name = name
        self.marks = marks            # dict: {subject: marks}

    def to_row(self):
        row = {"Roll": self.roll, "Name": self.name}
        row.update(self.marks)
        return row


def get_grade(percentage):
    """Convert a percentage into a letter grade."""
    if percentage >= 90:
        return "A+"
    if percentage >= 75:
        return "A"
    if percentage >= 60:
        return "B"
    if percentage >= 50:
        return "C"
    if percentage >= PASS_MARKS:
        return "D"
    return "F"


class StudentManager:
    """Stores students in a Pandas DataFrame and saves them to a CSV file."""

    def __init__(self, csv_file=CSV_FILE):
        self.csv_file = csv_file
        self.df = self._load()

    def _load(self):
        if os.path.exists(self.csv_file):
            return pd.read_csv(self.csv_file)
        return pd.DataFrame(columns=["Roll", "Name"] + SUBJECTS)

    def save(self):
        self.df.to_csv(self.csv_file, index=False)

    def validate(self, student):
        """Return an error message, or None if the record is valid."""
        if not str(student.roll).strip() or not student.name.strip():
            return "Roll number and name are required."
        if (self.df["Roll"].astype(str) == str(student.roll)).any():
            return "Roll number already exists."
        for subject, m in student.marks.items():
            if not 0 <= m <= MAX_MARKS:
                return f"{subject} marks must be between 0 and {MAX_MARKS}."
        return None

    def add_student(self, student):
        error = self.validate(student)
        if error:
            raise ValueError(error)
        self.df = pd.concat([self.df, pd.DataFrame([student.to_row()])],
                            ignore_index=True)
        self.save()

    def delete_student(self, roll):
        self.df = self.df[self.df["Roll"].astype(str) != str(roll)]
        self.df = self.df.reset_index(drop=True)
        self.save()

    # ---------- analysis (Pandas) ----------
    def results(self):
        """DataFrame with Total, Percentage, Grade, Result and Rank added."""
        d = self.df.copy()
        if d.empty:
            return d
        d["Total"] = d[SUBJECTS].sum(axis=1)
        d["Percentage"] = (d["Total"] / (MAX_MARKS * len(SUBJECTS)) * 100).round(2)
        d["Grade"] = d["Percentage"].apply(get_grade)
        failed = (d[SUBJECTS] < PASS_MARKS).any(axis=1)
        d["Result"] = failed.map({True: "Fail", False: "Pass"})
        d["Rank"] = d["Total"].rank(ascending=False, method="min").astype(int)
        return d

    def subject_averages(self):
        return self.df[SUBJECTS].mean().round(2) if not self.df.empty else None

    def grade_distribution(self):
        r = self.results()
        return r["Grade"].value_counts() if not r.empty else None

    def summary(self):
        r = self.results()
        if r.empty:
            return {}
        top = r.loc[r["Total"].idxmax()]
        return {
            "Students": len(r),
            "Class average %": float(round(r["Percentage"].mean(), 2)),
            "Pass %": float(round((r["Result"] == "Pass").mean() * 100, 2)),
            "Topper": f"{top['Name']} ({top['Percentage']}%)",
        }
