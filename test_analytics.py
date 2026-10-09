"""Unit tests - run with: python -m unittest test_analytics -v"""
import os, tempfile, unittest
from analytics import StudentManager, Student, get_grade, SUBJECTS


def make(roll="R1", name="Test", m=(80, 70, 60, 90, 85)):
    return Student(roll, name, dict(zip(SUBJECTS, m)))


class TestAnalytics(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), "t.csv")
        self.m = StudentManager(self.path)

    def test_grade_boundaries(self):
        self.assertEqual(get_grade(95), "A+")
        self.assertEqual(get_grade(75), "A")
        self.assertEqual(get_grade(40), "D")
        self.assertEqual(get_grade(39.9), "F")

    def test_add_and_calculate(self):
        self.m.add_student(make())
        r = self.m.results().iloc[0]
        self.assertEqual(r["Total"], 385)
        self.assertEqual(r["Percentage"], 77.0)
        self.assertEqual(r["Grade"], "A")
        self.assertEqual(r["Result"], "Pass")

    def test_fail_if_any_subject_below_40(self):
        self.m.add_student(make("R2", "Low", (90, 90, 30, 90, 90)))
        self.assertEqual(self.m.results().iloc[0]["Result"], "Fail")

    def test_duplicate_roll_rejected(self):
        self.m.add_student(make())
        with self.assertRaises(ValueError):
            self.m.add_student(make())

    def test_invalid_marks_rejected(self):
        with self.assertRaises(ValueError):
            self.m.add_student(make("R3", "Bad", (101, 0, 0, 0, 0)))

    def test_rank_and_delete(self):
        self.m.add_student(make("A", "A", (90,90,90,90,90)))
        self.m.add_student(make("B", "B", (50,50,50,50,50)))
        res = self.m.results().set_index("Roll")
        self.assertEqual(res.loc["A", "Rank"], 1)
        self.m.delete_student("A")
        self.assertEqual(len(self.m.df), 1)

    def test_persistence(self):
        self.m.add_student(make())
        self.assertEqual(len(StudentManager(self.path).df), 1)


if __name__ == "__main__":
    unittest.main()
