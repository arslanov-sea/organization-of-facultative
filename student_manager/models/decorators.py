"""
Модуль декораторов для репозитория студентов.

Содержит декораторы для фильтрации и сортировки студентов.
"""

from typing import List, Callable, Any
from .student import Student
from .student_repository import StudentRepository


class StudentRepFilterSortDecorator:
    """Декоратор для фильтрации и сортировки студентов в репозитории."""

    def __init__(self, repo: StudentRepository, filter_func: Callable[[Student], bool] = None,
                 sort_key: Callable[[Student], Any] = None):
        """
        Инициализирует декоратор.

        Args:
            repo: Репозиторий студентов
            filter_func: Функция для фильтрации студентов
            sort_key: Функция для определения ключа сортировки
        """
        self._repo = repo
        self._filter_func = filter_func
        self._sort_key = sort_key
        self._count = self._repo.get_count()

    def get_k_n_short_list(self, k: int, n: int) -> List[Student]:
        """
        Возвращает отсортированный и отфильтрованный список студентов.

        Args:
            k: Количество студентов на странице
            n: Номер страницы

        Returns:
            Список студентов для указанной страницы
        """
        try:
            students = self._repo.get_k_n_short_list(self._count, 1)  # Получаем всех

            if self._filter_func:
                students = list(filter(self._filter_func, students))

            if self._sort_key:
                students.sort(key=self._sort_key)

            start_index = (n - 1) * k
            end_index = start_index + k
            return students[start_index:end_index] if start_index < len(students) else []
        except (ValueError, TypeError, AttributeError) as e:
            raise RuntimeError(f"Error during filtering or sorting: {e}") from e

    def get_count(self) -> int:
        """
        Возвращает количество студентов после применения фильтра.

        Returns:
            Количество отфильтрованных студентов
        """
        try:
            students = self._repo.get_k_n_short_list(self._count, 1)

            if self._filter_func:
                students = list(filter(self._filter_func, students))

            return len(students)
        except (ValueError, TypeError, AttributeError) as e:
            raise RuntimeError(f"Error during filtering: {e}") from e
