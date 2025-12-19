from flask import render_template
from models.student_repository import StudentRepository, Student
from models.decorators import StudentRepFilterSortDecorator
from factory.universityFactory import UniversityFactory
from typing import List
from flask import request, redirect, url_for
from appconfig import UNIVERSITIES, DEFAULT_PAGE_SIZE
from math import ceil


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

    def __init__(self, university=None):
        self.university = university

    def update(self, data):
        if isinstance(data, tuple) and len(data) == 3:
            students, university, page_cnt = data
            self.university = university
        else:
            # ...
            return 'error'

        return render_template('index.html',
                               students=students,
                               university=self.university,
                               page_cnt=page_cnt)

class Controller:
    def __init__(self, university: str | None):
        self._university = university
        self._repo: StudentRepository = UniversityFactory.create_repository(university) if university else None

    @staticmethod
    def show_404():
        return render_template('not_found.html')

    @staticmethod
    def show_start():
        universities = UNIVERSITIES
        return render_template('start.html', universities=universities)

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
            filter_type = request.args.get('filter_type', '')
            filter_value = request.args.get('filter_value', '')
            sort_by = request.args.get('sort_by', '')
            sort_order = request.args.get('sort_order', 'asc')

            decorated_repo = StudentRepFilterSortDecorator(self._repo)

            if filter_type and filter_value:
                if filter_type == 'name':
                    filter_func = lambda \
                        s: filter_value.lower() in f"{s.last_name} {s.first_name} {s.patronymic or ''}".lower()
                elif filter_type == 'phone':
                    filter_func = lambda s: filter_value in s.phone
                elif filter_type == 'address':
                    filter_func = lambda s: filter_value.lower() in s.address.lower()
                elif filter_type == 'hours':
                    try:
                        hours = int(filter_value)
                        filter_func = lambda s: s.min_required_facultative_hours >= hours
                    except ValueError:
                        filter_func = None
                else:
                    filter_func = None

                if filter_func:
                    decorated_repo.filter_func = filter_func

            if sort_by:
                if sort_by == 'name':
                    sort_key = lambda s: (s.last_name, s.first_name, s.patronymic or '')
                elif sort_by == 'phone':
                    sort_key = lambda s: s.phone
                elif sort_by == 'address':
                    sort_key = lambda s: s.address
                elif sort_by == 'hours':
                    sort_key = lambda s: s.min_required_facultative_hours
                elif sort_by == 'id':
                    sort_key = lambda s: s.student_id
                else:
                    sort_key = None

                if sort_key:
                    decorated_repo.sort_key = sort_key
                    decorated_repo.reverse = (sort_order == 'desc')

            # count = decorated_repo.get_count()
            count = DEFAULT_PAGE_SIZE
            page_cnt = ceil(decorated_repo.get_count() / DEFAULT_PAGE_SIZE)

            if request.args.get('page'):
                page = int(request.args.get('page'))
            else:
                page = 1
            students = decorated_repo.get_k_n_short_list(count, page)
            print(f"Загружено студентов после фильтрации: {len(students)}")

            data = (students, self._university, page_cnt)
            results = self.notify(data)
            return results[0] if results else "No observers"
        else:
            raise ValueError("Университет не существует")


class StudentsAddController(Controller):
    def __init__(self, university: str | None = None):
        super().__init__(university)

    def show_add_student_form(self):

        return render_template('student_add_form.html', university=self._university)

    def add_student(self, request_data: dict):
        try:
            request_min_req_hours = request_data.get('min_required_facultative_hours')
            request_data['min_required_facultative_hours'] = int(request_min_req_hours)
            self._repo.add_student(request_data)
            return redirect(url_for('index', university=self._university))
        except Exception as e:
            return render_template('student_add_form.html',
                                   university=self._university,
                                   form_data=request.form.to_dict(),
                                   error=str(e))


class StudentsUpdateController(Controller):
    def __init__(self, university: str | None = None):
        super().__init__(university)

    def show_update_student_form(self, student_id: int):
        student = self._repo.get_by_id(student_id)
        if student:
            form_data = {
                'last_name': student.last_name,
                'first_name': student.first_name,
                'patronymic': student.patronymic,
                'address': student.address,
                'phone': student.phone,
                'min_required_facultative_hours': student.min_required_facultative_hours,
            }
            return render_template(
                'student_update_form.html',
                university=self._university,
                student=self._repo.get_by_id(student_id),
                form_data=form_data)
        return Controller.show_404()

    def update_student(self, student_id: int, request_data: dict):
        request_min_req_hours = request_data.get('min_required_facultative_hours')
        request_data['min_required_facultative_hours'] = int(request_min_req_hours)
        try:
            self._repo.update_student(student_id, request_data)
            return redirect(url_for('index', university=self._university))
        except Exception as e:
            return render_template(
                'student_update_form.html',
                university=self._university,
                student=self._repo.get_by_id(student_id),
                form_data=request_data,
                error=str(e))

class StudentsDeleteController(Controller):
    def __init__(self, university: str | None = None):
        super().__init__(university)

    def delete_student(self, student_id: int):
        self._repo.delete_student(student_id)