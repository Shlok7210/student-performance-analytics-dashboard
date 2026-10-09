"""app.py - Tkinter GUI for the Student Performance Analytics Dashboard.

Tkinter = screen, Pandas = calculations (analytics.py), Matplotlib = charts.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from analytics import StudentManager, Student, SUBJECTS


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Performance Analytics Dashboard")
        self.geometry("1100x650")
        self.manager = StudentManager()
        self.build_form()
        self.build_table()
        self.build_charts()
        self.refresh()

    # ---------- input form ----------
    def build_form(self):
        frame = ttk.LabelFrame(self, text="Add Student")
        frame.pack(fill="x", padx=10, pady=5)
        self.entries = {}
        for i, label in enumerate(["Roll", "Name"] + SUBJECTS):
            ttk.Label(frame, text=label).grid(row=0, column=i, padx=4)
            e = ttk.Entry(frame, width=10)
            e.grid(row=1, column=i, padx=4, pady=4)
            self.entries[label] = e
        ttk.Button(frame, text="Add", command=self.add_student).grid(row=1, column=8, padx=6)
        ttk.Button(frame, text="Delete Selected", command=self.delete_student).grid(row=1, column=9)

    def add_student(self):
        try:
            marks = {s: float(self.entries[s].get()) for s in SUBJECTS}
            student = Student(self.entries["Roll"].get().strip(),
                              self.entries["Name"].get().strip(), marks)
            self.manager.add_student(student)
        except ValueError as err:
            messagebox.showerror("Invalid input", str(err) if str(err) else "Enter numeric marks.")
            return
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.refresh()

    def delete_student(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Delete", "Select a student first.")
            return
        roll = self.table.item(selected[0])["values"][0]
        self.manager.delete_student(roll)
        self.refresh()

    # ---------- table + summary ----------
    def build_table(self):
        cols = ["Roll", "Name"] + SUBJECTS + ["Total", "Percentage", "Grade", "Result", "Rank"]
        self.table = ttk.Treeview(self, columns=cols, show="headings", height=7)
        for c in cols:
            self.table.heading(c, text=c)
            self.table.column(c, width=130 if c == "Name" else 75, anchor="center")
        self.table.pack(fill="x", padx=10)
        self.summary_label = ttk.Label(self, font=("Arial", 10, "bold"))
        self.summary_label.pack(pady=4)

    # ---------- charts ----------
    def build_charts(self):
        self.fig = Figure(figsize=(11, 3.6), dpi=90)
        self.ax1 = self.fig.add_subplot(131)
        self.ax2 = self.fig.add_subplot(132)
        self.ax3 = self.fig.add_subplot(133)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10)

    def refresh(self):
        results = self.manager.results()
        self.table.delete(*self.table.get_children())
        for _, row in results.iterrows():
            self.table.insert("", "end", values=list(row))
        info = self.manager.summary()
        self.summary_label.config(text="   |   ".join(f"{k}: {v}" for k, v in info.items()))
        self.draw_charts(results)

    def draw_charts(self, results):
        for ax in (self.ax1, self.ax2, self.ax3):
            ax.clear()
        if not results.empty:
            avg = self.manager.subject_averages()
            self.ax1.bar(avg.index, avg.values, color="#4C78A8")
            self.ax1.set_title("Subject-wise Average")
            self.ax1.set_ylim(0, 100)

            self.ax2.bar(results["Name"], results["Percentage"], color="#59A14F")
            self.ax2.set_title("Overall Percentage")
            self.ax2.tick_params(axis="x", rotation=60, labelsize=7)

            dist = self.manager.grade_distribution()
            self.ax3.pie(dist.values, labels=dist.index, autopct="%1.0f%%")
            self.ax3.set_title("Grade Distribution")
        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    Dashboard().mainloop()
