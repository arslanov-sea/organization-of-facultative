"""
Модуль для работы с репозиторием студентов.
Поддерживает сохранение и загрузку данных в форматах JSON и YAML.
"""

import json
from typing import List
import yaml
from student import Student


class StudentRepository:
    """Базовый класс репозитория для управления данными студентов."""

    def __init__(self, filename: str):
        """Инициализирует репозиторий с указанным именем файла."""
        self._filename = filename
        self._students = []
        self._load()

    def _load(self) -> None:
        """Загружает данные из файла."""
        raise NotImplementedError

    def _save(self) -> None:
        """Сохраняет данные в файл."""
        raise NotImplementedError

    def get_by_id(self, student_id: int) -> Student | None:
        """Находит студента по ID."""
        for student in self._students:
            if student.student_id == student_id:
                return student
        return None

    def get_k_n_short_list(self, k: int, n: int) -> List[Student]:
        """Возвращает короткий список из k элементов на n-й странице."""
        start_index = (n - 1) * k
        end_index = start_index + k
        return self._students[start_index:end_index] if start_index < len(self._students) else []

    def sort_by_name(self) -> List[Student]:
        """Сортирует студентов по ФИО и сохраняет изменения."""
        self._students.sort(key=lambda x: (
            x.last_name,
            x.first_name,
            x.patronymic if x.patronymic else ""
        ))
        self._save()
        return self._students.copy()

    def _is_student_unique(self, new_student: Student) -> bool:
        """Проверяет на уникальность студента (только по номеру телефона)"""
        for student in self._students:
            if new_student.phone == student.phone:
                return False
        return True

    def add_student(self, student_data: dict) -> Student:
        """Добавляет нового студента."""
        new_id = max([s.student_id for s in self._students] or [0]) + 1
        student = Student(
            student_id=new_id,
            first_name=student_data['first_name'],
            last_name=student_data['last_name'],
            patronymic=student_data.get('patronymic'),
            address=student_data['address'],
            phone=student_data['phone'],
            min_required_facultative_hours=student_data.get(
                'min_required_facultative_hours', 0
            )
        )

        if self._is_student_unique(student):
            self._students.append(student)
        else:
            raise ValueError("Пользователь с данным номером телефона уже существует")
        self._save()
        return student

    def update_student(self, student_id: int, student_data: dict) -> Student | None:
        """Обновляет данные студента по ID."""

        student_index = None
        current_student = None

        # Находим студента и его индекс
        for i, student in enumerate(self._students):
            if student.student_id == student_id:
                student_index = i
                current_student = student
                break

        # Если студент не найден
        if student_index is None:
            return None

        # Создаем обновленного студента
        updated_student = Student(
            student_id=student_id,
            first_name=student_data['first_name'],
            last_name=student_data['last_name'],
            patronymic=student_data.get('patronymic'),
            address=student_data['address'],
            phone=student_data['phone'],  # убрал .get(), так как phone обязателен
            min_required_facultative_hours=student_data.get(
                'min_required_facultative_hours', 0
            )
        )

        # Проверяем уникальность номера телефона, только если он изменился
        if updated_student.phone != current_student.phone:
            if not self._is_student_unique(updated_student):
                raise ValueError("Пользователь с данным номером телефона уже существует")

        # Обновляем студента
        self._students[student_index] = updated_student
        self._save()
        return updated_student

    def delete_student(self, student_id: int) -> bool:
        """Удаляет студента по ID."""
        for i, student in enumerate(self._students):
            if student.student_id == student_id:
                del self._students[i]
                self._save()
                return True
        return False

    def get_count(self) -> int:
        """Возвращает количество студентов."""
        return len(self._students)


class StudentRepJson(StudentRepository):
    """Реализация репозитория для работы с JSON файлами."""

    def _load(self) -> None:
        """Загружает данные из JSON файла."""
        try:
            with open(self._filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self._students = []
                for item in data:
                    try:
                        student = Student(
                            student_id=item['student_id'],
                            first_name=item['first_name'],
                            last_name=item['last_name'],
                            patronymic=item.get('patronymic'),
                            address=item['address'],
                            phone=item['phone'],
                            min_required_facultative_hours=item.get(
                                'min_required_facultative_hours', 0
                            )
                        )
                        self._students.append(student)
                    except (ValueError, KeyError) as e:
                        print(f"Ошибка при загрузке студента: {e}")
        except FileNotFoundError:
            self._students = []
        except json.JSONDecodeError:
            self._students = []

    def _save(self) -> None:
        """Сохраняет данные в JSON файл."""
        data = []
        for student in self._students:
            student_data = {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'patronymic': student.patronymic,
                'address': student.address,
                'phone': student.phone,
                'min_required_facultative_hours': student.min_required_facultative_hours
            }
            data.append(student_data)

        with open(self._filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


class StudentRepYaml(StudentRepository):
    """Реализация репозитория для работы с YAML файлами."""

    def _load(self) -> None:
        """Загружает данные из YAML файла."""
        try:
            with open(self._filename, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file) or []
                self._students = []
                for item in data:
                    try:
                        student = Student(
                            student_id=item['student_id'],
                            first_name=item['first_name'],
                            last_name=item['last_name'],
                            patronymic=item.get('patronymic'),
                            address=item['address'],
                            phone=item['phone'],
                            min_required_facultative_hours=item.get(
                                'min_required_facultative_hours', 0
                            )
                        )
                        self._students.append(student)
                    except (ValueError, KeyError) as e:
                        print(f"Ошибка при загрузке студента: {e}")
        except FileNotFoundError:
            self._students = []

    def _save(self) -> None:
        """Сохраняет данные в YAML файл."""
        data = []
        for student in self._students:
            student_data = {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'patronymic': student.patronymic,
                'address': student.address,
                'phone': student.phone,
                'min_required_facultative_hours': student.min_required_facultative_hours
            }
            data.append(student_data)

        with open(self._filename, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, allow_unicode=True, default_flow_style=False)
