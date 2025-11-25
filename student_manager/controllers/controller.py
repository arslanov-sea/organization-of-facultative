from flask import render_template
from models.student_repository import StudentRepJson

DATA_FILE_PATH = 'models/data/students.json'


class Subject:
    """Субъект для паттерна Наблюдатель"""

    def __init__(self):
        self._observers = []

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

    def update(self, data):
        pass


class StudentsListView(Observer):
    """Наблюдатель, который выводит студентов через шаблон"""

    def update(self, students):
        return render_template('index.html', students=students)


class StudentsController(Subject):
    """Контроллер, связывающий репозиторий и наблюдателей"""

    def __init__(self):
        super().__init__()
        self.repo = StudentRepJson(DATA_FILE_PATH)
        # Прикрепляем представление как наблюдателя
        self.view = StudentsListView()
        self.attach(self.view)

    def show_list_students(self):
        """Получить список студентов и уведомить наблюдателей"""
        students = self.repo.get_k_n_short_list(self.repo.get_count(), 1)
        print(f"Загружено студентов: {len(students)}")

        # Уведомляем всех наблюдателей и возвращаем результат первого (шаблона)
        results = self.notify(students)
        return results[0] if results else "No observers"

    def add_student_view(self, view):
        """Добавить дополнительное представление"""
        self.attach(view)

    def get_student_count(self):
        """Получить количество студентов"""
        return self.repo.get_count()