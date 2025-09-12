class Student:
    def __init__(self, student_id, first_name, last_name, patronymic, address, min_required_facultative_hours):
        self._student_id = student_id
        self._first_name = first_name
        self._last_name = last_name
        self._patronymic = patronymic
        self._address = address
        self._min_required_facultative_hours = min_required_facultative_hours

    @property
    def student_id(self):
        return self._student_id

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def patronymic(self):
        return self._patronymic

    @property
    def address(self):
        return self._address

    @property
    def min_required_facultative_hours(self):
        return self._min_required_facultative_hours

    @student_id.setter
    def student_id(self, value):
        self._student_id = value

    @first_name.setter
    def first_name(self, value):
        self._first_name = value

    @last_name.setter
    def last_name(self, value):
        self._last_name = value

    @patronymic.setter
    def patronymic(self, value):
        self._patronymic = value

    @address.setter
    def address(self, value):
        self._address = value

    @min_required_facultative_hours.setter
    def min_required_facultative_hours(self, value):
        self._min_required_facultative_hours = value
