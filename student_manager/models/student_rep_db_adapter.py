"""
Модуль адаптера для репозитория базы данных.

Содержит адаптер для интеграции StudentRepDB с интерфейсом StudentRepository.
"""

from typing import List
from student_repository import StudentRepository
from student_rep_db import StudentRepDB
from student import Student


class StudentRepDBAdapter(StudentRepository):
    """Адаптер для использования StudentRepDB через интерфейс StudentRepository."""

    def __init__(self, db_repository: StudentRepDB):
        """
        Инициализирует адаптер.

        Args:
            db_repository: Репозиторий базы данных для адаптации
        """
        self._db_repo = db_repository
        super().__init__("database")

    def _load(self) -> None:
        """Загружает студентов из базы данных во внутренний кеш."""
        count = self._db_repo.get_count()
        self._students = self._db_repo.get_k_n_short_list(count, 1) if count > 0 else []

    def _save(self) -> None:
        """Сохраняет данные (не используется, так как сохранение происходит напрямую в БД)."""


    def get_by_id(self, student_id: int) -> Student | None:
        """
        Возвращает студента по ID.

        Args:
            student_id: ID студента

        Returns:
            Студент или None если не найден
        """
        return self._db_repo.get_by_id(student_id)

    def add_student(self, student_data: dict) -> Student:
        """
        Добавляет нового студента.

        Args:
            student_data: Данные студента

        Returns:
            Созданный студент
        """
        student = self._db_repo.add_student(student_data)
        self._load()
        return student

    def update_student(self, student_id: int, student_data: dict) -> Student | None:
        """
        Обновляет данные студента.

        Args:
            student_id: ID студента
            student_data: Новые данные студента

        Returns:
            Обновленный студент или None если не найден
        """
        result = self._db_repo.update_student(student_id, student_data)
        self._load()
        return result

    def delete_student(self, student_id: int) -> bool:
        """
        Удаляет студента по ID.

        Args:
            student_id: ID студента

        Returns:
            True если удален, False если не найден
        """
        result = self._db_repo.delete_student(student_id)
        self._load()
        return result

    def get_count(self) -> int:
        """
        Возвращает количество студентов в базе.

        Returns:
            Количество студентов
        """
        return self._db_repo.get_count()

    def sort_by_name(self) -> List[Student]:
        """
        Возвращает студентов, отсортированных по ФИО.

        Returns:
            Отсортированный список студентов
        """
        count = self._db_repo.get_count()
        self._students = self._db_repo.get_k_n_short_list(count, 1) if count > 0 else []
        self._students.sort(key=lambda x: (
            x.last_name,
            x.first_name,
            x.patronymic if x.patronymic else ""
        ))
        return self._students.copy()
