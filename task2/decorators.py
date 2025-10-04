from typing import List, Callable
from student import Student
from student_repository import *
from student_rep_db import StudentRepDB


class StudentRepDBDecorator:
    def __init__(self, db_repo, filter_func: Callable[[Student], bool] = None,
                 sort_key: Callable[[Student], any] = None):
        self._db_repo = db_repo
        self._filter_func = filter_func
        self._sort_key = sort_key

    def get_k_n_short_list(self, k: int, n: int) -> List[Student]:
        students = self._db_repo.get_k_n_short_list(1000, 1)  # Получаем всех

        if self._filter_func:
            students = list(filter(self._filter_func, students))

        if self._sort_key:
            students.sort(key=self._sort_key)

        start_index = (n - 1) * k
        end_index = start_index + k
        return students[start_index:end_index] if start_index < len(students) else []

    def get_count(self) -> int:
        students = self._db_repo.get_k_n_short_list(1000, 1)

        if self._filter_func:
            students = list(filter(self._filter_func, students))

        return len(students)
