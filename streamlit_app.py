"""Web version of Student Performance Analytics Dashboard.

Deploy this file with Streamlit Community Cloud. The original Tkinter app.py
is preserved as the desktop version.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import streamlit as st

from analytics import StudentManager, Student, SUBJECTS


st.set_page_config(
    page_title="Student Performance Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Student Performance Analytics Dashboard")
st.caption("Manage student marks, calculate results, and explore class performance.")
st.info(
    "This is the web version of the desktop project. It uses the same analytics logic, "
    "Pandas calculations, CSV sample data, and Matplotlib charts."
)

# Keep the manager across Streamlit reruns for this browser session.
if "manager" not in st.session_state:
    st.session_state.manager = StudentManager(str(Path(__file__).with_name("students.csv")))
manager = st.session_state.manager

with st.expander("➕ Add a student", expanded=True):
    with st.form("add_student_form", clear_on_submit=True):
        col_roll, col_name = st.columns(2)
        with col_roll:
            roll = st.text_input("Roll number", placeholder="e.g. CS116")
        with col_name:
            name = st.text_input("Student name", placeholder="e.g. Aditi Rao")

        mark_cols = st.columns(len(SUBJECTS))
        marks = {}
        for col, subject in zip(mark_cols, SUBJECTS):
            with col:
                marks[subject] = st.number_input(
                    subject,
                    min_value=0,
                    max_value=100,
                    value=0,
                    step=1,
                    key=f"new_{subject}",
                )

        submitted = st.form_submit_button("Add student", type="primary", use_container_width=True)
        if submitted:
            student = Student(roll.strip(), name.strip(), marks)
            try:
                manager.add_student(student)
                st.success(f"Added {name.strip()} successfully.")
            except ValueError as exc:
                st.error(str(exc))

results = manager.results()
summary = manager.summary()

st.subheader("Class overview")
if not summary:
    st.warning("No student records are available. Add a student to begin.")
else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", summary["Students"])
    c2.metric("Class average", f'{summary["Class average %"]:.2f}%')
    c3.metric("Pass percentage", f'{summary["Pass %"]:.2f}%')
    c4.metric("Topper", summary["Topper"])

st.subheader("Student results")
if results.empty:
    st.info("The results table will appear after student records are added.")
else:
    st.dataframe(results, use_container_width=True, hide_index=True)

    with st.expander("🗑️ Delete a student"):
        roll_values = results["Roll"].astype(str).tolist()
        name_by_roll = dict(zip(results["Roll"].astype(str), results["Name"].astype(str)))
        selected_roll = st.selectbox(
            "Select the roll number to delete",
            options=roll_values,
            format_func=lambda value: f"{value} — {name_by_roll.get(value, '')}",
        )
        if st.button("Delete selected student", type="secondary"):
            manager.delete_student(selected_roll)
            st.success(f"Deleted student {selected_roll}.")
            st.rerun()

st.subheader("Performance visualizations")
if results.empty:
    st.caption("Charts will appear when the dataset contains at least one student.")
else:
    chart1, chart2, chart3 = st.columns(3)

    with chart1:
        st.markdown("**Subject-wise average**")
        averages = manager.subject_averages()
        fig, ax = plt.subplots(figsize=(5, 3.5))
        ax.bar(averages.index, averages.values)
        ax.set_ylabel("Average marks")
        ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=35)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with chart2:
        st.markdown("**Overall student percentage**")
        fig, ax = plt.subplots(figsize=(5, 3.5))
        ax.bar(results["Name"], results["Percentage"])
        ax.set_ylabel("Percentage")
        ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=75, labelsize=7)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with chart3:
        st.markdown("**Grade distribution**")
        distribution = manager.grade_distribution()
        fig, ax = plt.subplots(figsize=(5, 3.5))
        ax.pie(distribution.values, labels=distribution.index, autopct="%1.0f%%")
        ax.axis("equal")
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

with st.expander("About this project"):
    st.write(
        "Built with Python, Streamlit (web interface), Tkinter (original desktop interface), "
        "Pandas, Matplotlib, object-oriented programming, and CSV storage. Students pass when "
        "every subject mark is at least 40; grades are assigned using the project rules."
    )
    st.warning(
        "Demo storage note: records are saved to the app's CSV file during the running session. "
        "On a hosted service, local-file changes are not guaranteed to survive app restarts or redeploys. "
        "Use a database if permanent shared storage is required."
    )
