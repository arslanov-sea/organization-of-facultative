from typing import List, Callable
from student import Student


class StudentRepFilterSortDecorator:
    def __init__(self, _repo, filter_func: Callable = None,
                 sort_key: Callable[[Student], any] = None):
        self._repo = _repo
        self._filter_func = filter_func
        self._sort_key = sort_key
        self._count = self._repo.get_count()

    def get_k_n_short_list(self, k: int, n: int) -> List[Student]:
        students = self._repo.get_k_n_short_list(self._count, 1)  # Получаем всех

        if self._filter_func:
            students = list(filter(self._filter_func, students))

        if self._sort_key:
            students.sort(key=self._sort_key)

        start_index = (n - 1) * k
        end_index = start_index + k
        return students[start_index:end_index] if start_index < len(students) else []

    def get_count(self) -> int:
        students = self._repo.get_k_n_short_list(self._count, 1)

        if self._filter_func:
            students = list(filter(self._filter_func, students))

        return len(students)
