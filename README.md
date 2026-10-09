# Student Performance Analytics Dashboard

Advanced Python Programming Micro-Project (E1CSA348) - Alliance University

A desktop app that stores student marks, calculates results with **Pandas**,
and shows charts with **Matplotlib** inside a **Tkinter** window.

## Features
- Add / delete student records (validated input, no duplicate roll numbers)
- Automatic Total, Percentage, Grade, Pass/Fail and Rank
- Charts: subject-wise average, overall percentage, grade distribution
- Class summary: number of students, class average, pass %, topper
- Data saved to `students.csv`

## Files
| File | Purpose |
|------|---------|
| `analytics.py` | Data layer: `Student`, `StudentManager` (OOP + Pandas) |
| `app.py` | Tkinter GUI + Matplotlib charts |
| `test_analytics.py` | 7 unit tests |
| `students.csv` | Sample data (15 students) |

## Run
```
pip install -r requirements.txt
python app.py
```
Run tests: `python -m unittest test_analytics -v`

## Author
Shlok Gupta - Alliance School of Advanced Computing, Alliance University
