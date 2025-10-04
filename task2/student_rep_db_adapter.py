from student_repository import *
from student_rep_db import *


class StudentRepDBAdapter(StudentRepository):
    def __init__(self, db_repo: StudentRepDB):
        self._db_repo = db_repo
        super().__init__("database")

    def _load(self) -> None:
        count = self._db_repo.get_count()
        self._students = self._db_repo.get_k_n_short_list(count, 1) if count > 0 else []

    def _save(self) -> None:
        pass

    def read_all(self) -> List[Student]:
        self._load()
        return self._students.copy()

    def write_all(self, students: List[Student]) -> None:
        current_students = self._db_repo.get_k_n_short_list(self._db_repo.get_count(), 1)
        for student in current_students:
            self._db_repo.delete_student(student.student_id)

        for student in students:
            self._db_repo.add_student({
                'first_name': student.first_name,
                'last_name': student.last_name,
                'patronymic': student.patronymic,
                'address': student.address,
                'phone': student.phone,
                'min_required_facultative_hours': student.min_required_facultative_hours
            })
        self._students = students.copy()

    def get_by_id(self, student_id: int) -> Student | None:
        return self._db_repo.get_by_id(student_id)

    def add_student(self, student_data: dict) -> Student:
        student = self._db_repo.add_student(student_data)
        self._load()
        return student

    def update_student(self, student_id: int, student_data: dict) -> Student | None:
        result = self._db_repo.update_student(student_id, student_data)
        self._load()
        return result

    def delete_student(self, student_id: int) -> bool:
        result = self._db_repo.delete_student(student_id)
        self._load()
        return result

    def get_count(self) -> int:
        return self._db_repo.get_count()

    def sort_by_name(self) -> List[Student]:
        count = self._db_repo.get_count()
        self._students = self._db_repo.get_k_n_short_list(count, 1) if count > 0 else []
        self._students.sort(key=lambda x: (
            x.last_name,
            x.first_name,
            x.patronymic if x.patronymic else ""
        ))
        return self._students.copy()
