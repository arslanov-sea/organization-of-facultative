import json
from typing import List
from test import Student


class StudentRepJson:
    def __init__(self, filename: str = "students.json"):
        self._filename = filename
        self._students: List[Student] = []
        self._load_from_file()

    def _load_from_file(self) -> None:
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
                            min_required_facultative_hours=item.get('min_required_facultative_hours', 0)
                        )
                        self._students.append(student)
                    except (ValueError, KeyError) as e:
                        print(f"Ошибка при загрузке студента: {e}")
        except FileNotFoundError:
            self._students = []
        except json.JSONDecodeError:
            self._students = []

    def save_to_file(self) -> None:
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

    def get_by_id(self, student_id: int) -> Student | None:
        for student in self._students:
            if student.student_id == student_id:
                return student
        return None

    def get_k_n_short_list(self, k: int, n: int) -> List[str]:
        start_index = (n - 1) * k
        end_index = start_index + k

        if start_index >= len(self._students):
            return []

        students_slice = self._students[start_index:end_index]
        return [student.brief_info() for student in students_slice]

    def sort_by_field(self, field: str) -> None:
        valid_fields = {
            'student_id', 'first_name', 'last_name', 'patronymic',
            'address', 'phone', 'min_required_facultative_hours'
        }

        if field not in valid_fields:
            raise ValueError(f"Недопустимое поле для сортировки: {field}")

        self._students.sort(key=lambda student: getattr(student, field))

    def add_student(self, student_data: dict) -> int:
        if self._students:
            new_id = max(student.student_id for student in self._students) + 1
        else:
            new_id = 1

        student_data['student_id'] = new_id

        try:
            student = Student(**student_data)
            self._students.append(student)
            return new_id
        except ValueError as e:
            raise ValueError(f"Ошибка при создании студента: {e}")

    def update_student(self, student_id: int, student_data: dict) -> bool:
        for i, student in enumerate(self._students):
            if student.student_id == student_id:
                try:
                    # Сохраняем ID
                    student_data['student_id'] = student_id
                    updated_student = Student(**student_data)
                    self._students[i] = updated_student
                    return True
                except ValueError as e:
                    raise ValueError(f"Ошибка при обновлении студента: {e}")
        return False

    def delete_student(self, student_id: int) -> bool:
        for i, student in enumerate(self._students):
            if student.student_id == student_id:
                del self._students[i]
                return True
        return False

    def get_count(self) -> int:
        return len(self._students)

    @property
    def students(self) -> List[Student]:
        return self._students.copy()
