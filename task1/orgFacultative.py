class Student:
    def __init__(self, student_id, first_name, last_name, patronymic, address, phone, min_required_facultative_hours=0):
        self._student_id = self.validate_id(student_id)
        self._first_name = self.validate_first_name(first_name)
        self._last_name = self.validate_last_name(last_name)
        self._patronymic = self.validate_patronymic(patronymic)
        self._address = self.validate_address(address)
        self._phone = self.validate_phone(phone)
        self._min_required_facultative_hours = self.validate_min_required_facultative_hours(min_required_facultative_hours)

    @staticmethod
    def validate_id(student_id):
        if not isinstance(student_id, int) or student_id <= 0:
            raise ValueError("only positive integer")
        return student_id

    @staticmethod
    def validate_last_name(last_name):
        if not isinstance(last_name, str) or len(last_name.strip()) == 0:
            raise ValueError("only non-empty string")
        return last_name.strip()

    @staticmethod
    def validate_first_name(first_name):
        if not isinstance(first_name, str) or len(first_name.strip()) == 0:
            raise ValueError("only non-empty string")
        return first_name.strip()

    @staticmethod
    def validate_patronymic(patronymic):
        if patronymic is None:
            return None
        if not isinstance(patronymic, str):
            raise ValueError("only None or a string")
        if len(patronymic.strip()) == 0:
            return None
        return patronymic.strip()

    @staticmethod
    def validate_address(address):
        if not isinstance(address, str):
            raise ValueError("Address must be a string")
        address = address.strip()
        if len(address) == 0:
            raise ValueError("Address cannot be empty")
        if len(address) < 10:
            raise ValueError("Address is too short to be valid")
        address_lower = address.lower()
        address_keywords = ['ул.', 'улица', 'д.', 'дом', 'кв.', 'квартира', 'пр.', 'проспект']
        if not any(keyword in address_lower for keyword in address_keywords):
            raise ValueError("Address should contain typical address components (ул., д., кв., etc.)")
        return address

    @staticmethod
    def validate_phone(phone):
        if not isinstance(phone, str):
            raise ValueError("Phone must be a string")

        phone = phone.strip()

        if not phone.startswith('+'):
            raise ValueError("Phone number must start with '+'")

        if len(phone) != 12:
            raise ValueError("Phone number must contain '+' followed by exactly 11 digits")

        digits_part = phone[1:]
        if not digits_part.isdigit():
            raise ValueError("Phone number must contain only digits after '+'")

        return phone

    @staticmethod
    def validate_min_required_facultative_hours(hours):
        if not isinstance(hours, int) or hours < 0:
            raise ValueError("only non-negative integer")
        return hours

    @property
    def student_id(self):
        return self._student_id

    @student_id.setter
    def student_id(self, value):
        self.student_id = self.validate_id(value)

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = self.validate_first_name(value)

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = self.validate_last_name(value)

    @property
    def patronymic(self):
        return self._patronymic

    @patronymic.setter
    def patronymic(self, value):
        self._patronymic = self.validate_patronymic(value)

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = self.validate_address(value)

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        self._phone = self.validate_phone(value)

    @property
    def min_required_facultative_hours(self):
        return self._min_required_facultative_hours

    @min_required_facultative_hours.setter
    def min_required_facultative_hours(self, value):
        self._min_required_facultative_hours = self.validate_min_required_facultative_hours(value)
