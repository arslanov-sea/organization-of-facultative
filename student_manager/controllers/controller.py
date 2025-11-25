from flask import render_template
from models.student_repository import StudentRepository

class Observer:
    def update(self, data):
        pass


class StudentsListView(Observer):
    """Наблюдатель, который выводит студентов через шаблон"""

    def update(self, students):
        return render_template('index.html', students=students)


class StudentsController:
    """Контроллер, связывающий репозиторий и наблюдателя"""

    def __init__(self):
        self.repo = StudentRepository("data/students.json")
        self.view = StudentsListView()

    def show_list_students(self):
        students = self.repo.get_k_n_short_list(self.repo.get_count(), 1)
        return self.view.update(students)
