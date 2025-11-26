from flask import render_template
from models.student_repository import StudentRepository, Student
from factory.universityFactory import UniversityFactory
from typing import List
from flask import request, redirect, url_for


class Subject:
    """Субъект для паттерна Наблюдатель"""

    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer):
        """Добавить наблюдателя"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """Удалить наблюдателя"""
        self._observers.remove(observer)

    def notify(self, data):
        """Уведомить всех наблюдателей"""
        results = []
        for observer in self._observers:
            result = observer.update(data)
            if result is not None:
                results.append(result)
        return results


class Observer:
    """Базовый класс Наблюдателя"""

    def update(self, data: List[Student]):
        pass


class StudentsListView(Observer):
    """Наблюдатель, который выводит студентов через шаблон"""

    def update(self, students):
        return render_template('index.html', students=students)

class Controller:
    def __init__(self, university: str | None):
        self._university = university
        self._repo: StudentRepository = UniversityFactory.create_repository(university) if university else None

    def get_university(self) -> str | None:
        return self._university

    def set_university(self, university: str | None):
        self._university = university
        self._repo: StudentRepository | None = UniversityFactory.create_repository(university) if university else None


class StudentsController(Subject, Controller):
    """Контроллер, связывающий репозиторий и наблюдателей"""

    def __init__(self, university: str | None = None):
        Subject.__init__(self)
        Controller.__init__(self, university)
        self._view: Observer = StudentsListView()
        self.attach(self._view)

    def show_list_students(self):
        if self._repo:
            """Получить список студентов и уведомить наблюдателей"""
            students = self._repo.get_k_n_short_list(self._repo.get_count(), 1)
            print(f"Загружено студентов: {len(students)}")

            results = self.notify(students)
            return results[0] if results else "No observers"
        else:
            raise ValueError("Университет не существует (репозиторий не найден)")


class StudentsAddController(Controller):
    def __init__(self, university: str | None = None):
        super().__init__(university)

    def show_add_student_form(self):

        return render_template('add_form.html', university=self._university)

    def add_student(self, request_data: dict):
        request_min_req_hours = request_data.get('min_required_facultative_hours')
        request_data['min_required_facultative_hours'] = int(request_min_req_hours) if request_min_req_hours else None
        self._repo.add_student(request_data)

