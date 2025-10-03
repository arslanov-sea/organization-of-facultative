import json
import re

class Person:
    def __init__(self, first_name: str, last_name: str, patronymic: str | None, address: str):
        self._first_name = self.validate_name(first_name)
        self._last_name = self.validate_name(last_name)
        self._patronymic = self.validate_name(patronymic, True)
        self._address = self.validate_address(address)

    @staticmethod
    def validate_name(value: str | None, is_patronymic: bool = False) -> str | None:
        if is_patronymic:
            if value is None:
                return None
            if not isinstance(value, str):
                raise ValueError("Patronymic must be None or a string")
            if len(value.strip()) == 0:
                return None
            value = value.strip()
        else:
            if not isinstance(value, str) or len(value.strip()) == 0:
                raise ValueError("name must be a non-empty string")
            value = value.strip()

        if value is not None:
            if not re.match(r'^[A-Za-zА-Яа-я]+(?:-[A-Za-zА-Яа-я]+)*$', value):
                raise ValueError("Invalid name format")
            value = value.title()

        return value

    @staticmethod
    def validate_address(address: str) -> str:
        if not isinstance(address, str) or not address.strip():
            raise ValueError("Address must be a non-empty string")

        address = address.strip()
        region_types = [r'Респ\.', r'Край', r'Обл\.']
        location_types = [r'г\.', r'с\.', r'ст-ца', r'а\.']

        found_regions = [r for r in region_types if re.search(r, address, re.IGNORECASE)]
        found_locations = [l for l in location_types if re.search(l, address, re.IGNORECASE)]

        if len(found_regions) > 1:
            raise ValueError(f"Адрес не может содержать одновременно {', '.join(found_regions)}")
        if len(found_locations) > 1:
            raise ValueError(f"Адрес не может содержать одновременно {', '.join(found_locations)}")

        if not re.search(r'(ул\.|улица|пр\.|проспект|бульвар|б-р|переулок|пер\.|аллея|шоссе)', address, re.IGNORECASE):
            raise ValueError("Адрес должен содержать указание улицы")
        if not re.search(r'(д\.|дом)\s*\d+', address, re.IGNORECASE):
            raise ValueError("Адрес должен содержать номер дома")

        return address

    @property
    def first_name(self) -> str:
        return self._first_name

    @property
    def last_name(self) -> str:
        return self._last_name

    @property
    def address(self) -> str:
        return self._address

    @first_name.setter
    def first_name(self, value: str) -> None:
        self._first_name = self.validate_name(value)

    @last_name.setter
    def last_name(self, value: str) -> None:
        self._last_name = self.validate_name(value)

    @address.setter
    def address(self, value: str) -> None:
        self._address = self.validate_address(value)

    def __str__(self) -> str:
        return f"Person({self._last_name} {self._first_name}, {self._address})"


class Student(Person):
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                if arg.startswith('{') and arg.endswith('}'):
                    data = self._parse_json(arg)
                else:
                    data = self._parse_string(arg)
            elif isinstance(arg, tuple):
                data = self._parse_tuple(arg)
            else:
                raise ValueError("Unsupported argument type")
        elif len(args) == 7:
            data = {
                'student_id': args[0],
                'first_name': args[1],
                'last_name': args[2],
                'patronymic': args[3],
                'address': args[4],
                'phone': args[5],
                'min_required_facultative_hours': args[6]
            }
        elif kwargs:
            data = kwargs
        else:
            raise ValueError("Invalid arguments")

        super().__init__(data['first_name'], data['last_name'], data.get('patronymic'), data['address'])

        self._student_id = self.validate_id(data['student_id'])
        self._phone = self.validate_phone(data['phone'])
        self._min_required_facultative_hours = self.validate_min_required_facultative_hours(
            data.get('min_required_facultative_hours', 0)
        )

    @staticmethod
    def _parse_string(input_string: str) -> dict:
        parts = input_string.split(';')
        if len(parts) != 7:
            raise ValueError("String must contain exactly 7 parts separated by ';'")

        try:
            return {
                'student_id': int(parts[0]),
                'first_name': parts[1],
                'last_name': parts[2],
                'patronymic': parts[3],
                'address': parts[4],
                'phone': parts[5],
                'min_required_facultative_hours': int(parts[6])
            }
        except ValueError as e:
            raise ValueError(f"Invalid data format in string: {e}")

    @staticmethod
    def _parse_json(input_json: str) -> dict:
        try:
            data = json.loads(input_json)
            return {
                'student_id': data['student_id'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'patronymic': data.get('patronymic'),
                'address': data['address'],
                'phone': data['phone'],
                'min_required_facultative_hours': data.get('min_required_facultative_hours', 0)
            }
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
        except KeyError as e:
            raise ValueError(f"Missing required field in JSON: {e}")

    @staticmethod
    def _parse_tuple(input_tuple: tuple) -> dict:
        if len(input_tuple) != 7:
            raise ValueError("Tuple must contain exactly 7 elements")

        try:
            return {
                'student_id': int(input_tuple[0]),
                'first_name': input_tuple[1],
                'last_name': input_tuple[2],
                'patronymic': input_tuple[3],
                'address': input_tuple[4],
                'phone': input_tuple[5],
                'min_required_facultative_hours': int(input_tuple[6])
            }
        except ValueError as e:
            raise ValueError(f"Invalid data format in tuple: {e}")

    @staticmethod
    def validate_id(student_id: int) -> int:
        if not isinstance(student_id, int) or student_id <= 0:
            raise ValueError("only positive integer")
        return student_id

    @staticmethod
    def validate_phone(phone: str | None) -> str | None:
        if phone is None:
            return None

        if not isinstance(phone, str):
            raise ValueError("Phone must be a string")

        phone = phone.strip()

        if not re.match(r'^\+7\d{10}$', phone):
            raise ValueError("Phone must start with +7 followed by exactly 10 digits")

        return phone

    @staticmethod
    def validate_min_required_facultative_hours(hours: int) -> int:
        if not isinstance(hours, int) or hours < 0:
            raise ValueError("only non-negative integer")
        return hours

    def info(self) -> str:
        full_name = f"{self._last_name} {self._first_name} {self._patronymic}" if self._patronymic else f"{self._last_name} {self._first_name}"
        return (f"Полная информация о студенте:\n"
                f"ID: {self._student_id}\n"
                f"ФИО: {full_name}\n"
                f"Адрес: {self._address}\n"
                f"Телефон: {self._phone}\n"
                f"Обязательные факультативные часы: {self._min_required_facultative_hours}")

    def brief_info(self) -> str:
        return f"{self._last_name} {self._first_name} {self._patronymic}" if self._patronymic else f"{self._last_name} {self._first_name}"

    def __str__(self) -> str:
        return self.brief_info()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Student):
            return False
        return (self._student_id == other._student_id and
                self._first_name == other._first_name and
                self._last_name == other._last_name and
                self._patronymic == other._patronymic and
                self._address == other._address and
                self._phone == other._phone and
                self._min_required_facultative_hours == other._min_required_facultative_hours)

    @property
    def student_id(self) -> int:
        return self._student_id

    @student_id.setter
    def student_id(self, value: int) -> None:
        self._student_id = self.validate_id(value)

    @property
    def patronymic(self) -> str | None:
        return self._patronymic

    @patronymic.setter
    def patronymic(self, value: str | None) -> None:
        self._patronymic = self.validate_name(value, True)

    @property
    def phone(self) -> str | None:
        return self._phone

    @phone.setter
    def phone(self, value: str | None) -> None:
        self._phone = self.validate_phone(value)

    @property
    def min_required_facultative_hours(self) -> int:
        return self._min_required_facultative_hours

    @min_required_facultative_hours.setter
    def min_required_facultative_hours(self, value: int) -> None:
        self._min_required_facultative_hours = self.validate_min_required_facultative_hours(value)
