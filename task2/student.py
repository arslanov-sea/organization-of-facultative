"""
Модуль для работы с сущностями Person и Student.

Содержит классы для представления человека и студента с валидацией данных.
"""

import json
import re


class Person:
    """Класс, представляющий человека."""

    def __init__(self, first_name: str, last_name: str, patronymic: str | None, address: str):
        """
        Инициализирует объект Person.

        Args:
            first_name: Имя
            last_name: Фамилия
            patronymic: Отчество (может быть None)
            address: Адрес
        """
        self._first_name = self.validate_name(first_name)
        self._last_name = self.validate_name(last_name)
        self._patronymic = self.validate_name(patronymic, True)
        self._address = self.validate_address(address)

    @staticmethod
    def validate_name(value: str | None, is_patronymic: bool = False) -> str | None:
        """
        Валидирует имя, фамилию или отчество.

        Args:
            value: Значение для валидации
            is_patronymic: Флаг, указывающий что это отчество

        Returns:
            Валидированное значение

        Raises:
            ValueError: Если значение не прошло валидацию
        """
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
        """
        Валидирует адрес.

        Args:
            address: Адрес для валидации

        Returns:
            Валидированный адрес

        Raises:
            ValueError: Если адрес не прошел валидацию
        """
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

        if not re.search(
            r'(ул\.|улица|пр\.|проспект|бульвар|б-р|переулок|пер\.|аллея|шоссе)',
            address,
            re.IGNORECASE
        ):
            raise ValueError("Адрес должен содержать указание улицы")
        if not re.search(r'(д\.|дом)\s*\d+', address, re.IGNORECASE):
            raise ValueError("Адрес должен содержать номер дома")

        return address

    @property
    def first_name(self) -> str:
        """Возвращает имя."""
        return self._first_name

    @property
    def last_name(self) -> str:
        """Возвращает фамилию."""
        return self._last_name

    @property
    def address(self) -> str:
        """Возвращает адрес."""
        return self._address

    @first_name.setter
    def first_name(self, value: str) -> None:
        """Устанавливает имя."""
        self._first_name = self.validate_name(value)

    @last_name.setter
    def last_name(self, value: str) -> None:
        """Устанавливает фамилию."""
        self._last_name = self.validate_name(value)

    @address.setter
    def address(self, value: str) -> None:
        """Устанавливает адрес."""
        self._address = self.validate_address(value)

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return f"Person({self._last_name} {self._first_name}, {self._address})"


class Student(Person):
    """Класс, представляющий студента."""

    def __init__(self, *args, **kwargs):
        """
        Инициализирует объект Student.

        Поддерживает различные форматы входных данных:
        - Строка с разделителями
        - JSON строка
        - Кортеж
        - Позиционные аргументы
        - Именованные аргументы
        """
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

        super().__init__(data['first_name'], data['last_name'],
                        data.get('patronymic'), data['address'])

        self._student_id = self.validate_id(data['student_id'])
        self._phone = self.validate_phone(data['phone'])
        self._min_required_facultative_hours = self.validate_min_required_facultative_hours(
            data.get('min_required_facultative_hours', 0)
        )

    @staticmethod
    def _parse_string(input_string: str) -> dict:
        """Парсит строку с разделителями в словарь."""
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
            raise ValueError(f"Invalid data format in string: {e}") from e

    @staticmethod
    def _parse_json(input_json: str) -> dict:
        """Парсит JSON строку в словарь."""
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
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON format") from exc
        except KeyError as e:
            raise ValueError(f"Missing required field in JSON: {e}") from e

    @staticmethod
    def _parse_tuple(input_tuple: tuple) -> dict:
        """Парсит кортеж в словарь."""
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
            raise ValueError(f"Invalid data format in tuple: {e}") from e

    @staticmethod
    def validate_id(student_id: int) -> int:
        """Валидирует ID студента."""
        if not isinstance(student_id, int) or student_id <= 0:
            raise ValueError("only positive integer")
        return student_id

    @staticmethod
    def validate_phone(phone: str | None) -> str | None:
        """Валидирует номер телефона."""
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
        """Валидирует количество обязательных факультативных часов."""
        if not isinstance(hours, int) or hours < 0:
            raise ValueError("only non-negative integer")
        return hours

    def info(self) -> str:
        """Возвращает полную информацию о студенте."""
        full_name = (f"{self._last_name} {self._first_name} {self._patronymic}"
                    if self._patronymic else f"{self._last_name} {self._first_name}")
        return (f"Полная информация о студенте:\n"
                f"ID: {self._student_id}\n"
                f"ФИО: {full_name}\n"
                f"Адрес: {self._address}\n"
                f"Телефон: {self._phone}\n"
                f"Обязательные факультативные часы: {self._min_required_facultative_hours}")

    def brief_info(self) -> str:
        """Возвращает краткую информацию о студенте."""
        return (f"{self._last_name} {self._first_name} {self._patronymic}"
                if self._patronymic else f"{self._last_name} {self._first_name}")

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return self.brief_info()

    def __eq__(self, other) -> bool:
        """Проверяет равенство двух объектов Student."""
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
        """Возвращает ID студента."""
        return self._student_id

    @student_id.setter
    def student_id(self, value: int) -> None:
        """Устанавливает ID студента."""
        self._student_id = self.validate_id(value)

    @property
    def patronymic(self) -> str | None:
        """Возвращает отчество."""
        return self._patronymic

    @patronymic.setter
    def patronymic(self, value: str | None) -> None:
        """Устанавливает отчество."""
        self._patronymic = self.validate_name(value, True)

    @property
    def phone(self) -> str | None:
        """Возвращает номер телефона."""
        return self._phone

    @phone.setter
    def phone(self, value: str | None) -> None:
        """Устанавливает номер телефона."""
        self._phone = self.validate_phone(value)

    @property
    def min_required_facultative_hours(self) -> int:
        """Возвращает количество обязательных факультативных часов."""
        return self._min_required_facultative_hours

    @min_required_facultative_hours.setter
    def min_required_facultative_hours(self, value: int) -> None:
        """Устанавливает количество обязательных факультативных часов."""
        self._min_required_facultative_hours = self.validate_min_required_facultative_hours(value)
