"""
Модуль для работы с базой данных студентов.

Содержит классы для подключения к БД и репозиторий для работы с данными студентов.
"""

from typing import List
import psycopg2
from .student import Student
from appconfig import DB_HOST, DB_NAME, DB_PASSWORD, DB_USERNAME, DB_PORT

DB_CONFIG = {
    'db_name': DB_NAME,
    'host': DB_HOST,
    'port': DB_PORT,
    'user': DB_USERNAME,
    'password': DB_PASSWORD
}


class DatabaseConnection:
    """Класс для управления подключением к базе данных (одиночка)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        """Инициализирует подключение к базе данных."""
        if not hasattr(self, '_initialized'):
            self._db_name = DB_CONFIG['db_name']
            self._host = DB_CONFIG['host']
            self._port = DB_CONFIG['port']
            self._user = DB_CONFIG['user']
            self._password = DB_CONFIG['password']
            self._initialized = True
            self._create_table()

    def _get_connection(self):
        """Возвращает соединение с базой данных."""
        return psycopg2.connect(
            dbname=self._db_name,
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password
        )

    def _create_table(self) -> None:
        """Создает таблицу студентов, если она не существует."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        student_id SERIAL PRIMARY KEY,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        patronymic VARCHAR(100),
                        address TEXT NOT NULL,
                        phone VARCHAR(20) UNIQUE NOT NULL,
                        min_required_facultative_hours INTEGER DEFAULT 0
                    )
                """)
                conn.commit()
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """Выполняет SQL запрос и возвращает результат."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                conn.commit()
                return []
        finally:
            conn.close()

    def execute_insert(self, query: str, params: tuple = None) -> int:
        """Выполняет INSERT запрос и возвращает ID новой записи."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                if query.strip().upper().startswith('INSERT') and 'RETURNING' in query.upper():
                    return cursor.fetchone()[0]
                return cursor.rowcount
        except psycopg2.IntegrityError as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """Выполняет UPDATE запрос и возвращает количество измененных строк."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                return cursor.rowcount
        except psycopg2.IntegrityError as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def execute_delete(self, query: str, params: tuple = None) -> int:
        """Выполняет DELETE запрос и возвращает количество удаленных строк."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                return cursor.rowcount
        finally:
            conn.close()


class StudentRepDB:
    """Репозиторий для работы со студентами в базе данных."""

    def __init__(self):
        """Инициализирует репозиторий с подключением к БД."""
        self._db = DatabaseConnection()

    def get_by_id(self, student_id: int) -> Student | None:
        """Возвращает студента по ID или None если не найден."""
        rows = self._db.execute_query("""
            SELECT student_id, first_name, last_name, patronymic, 
                   address, phone, min_required_facultative_hours 
            FROM students WHERE student_id = %s
        """, (student_id,))

        if rows:
            row = rows[0]
            return Student(
                student_id=row[0],
                first_name=row[1],
                last_name=row[2],
                patronymic=row[3],
                address=row[4],
                phone=row[5],
                min_required_facultative_hours=row[6]
            )
        return None

    def get_k_n_short_list(self, k: int, n: int) -> List[Student]:
        """
        Возвращает список студентов для постраничного отображения.

        Args:
            k: Количество студентов на странице
            n: Номер страницы

        Returns:
            Список студентов для указанной страницы
        """
        offset = (n - 1) * k
        rows = self._db.execute_query("""
            SELECT student_id, first_name, last_name, patronymic, 
                   address, phone, min_required_facultative_hours 
            FROM students ORDER BY student_id LIMIT %s OFFSET %s
        """, (k, offset))

        students = []
        for row in rows:
            students.append(Student(
                student_id=row[0],
                first_name=row[1],
                last_name=row[2],
                patronymic=row[3],
                address=row[4],
                phone=row[5],
                min_required_facultative_hours=row[6]
            ))
        return students

    def add_student(self, student_data: dict) -> Student:
        """Добавляет нового студента и возвращает созданный объект."""
        Student.validate_name(student_data['first_name'])
        Student.validate_name(student_data['last_name'])
        Student.validate_name(student_data.get('patronymic'), is_patronymic=True)
        Student.validate_address(student_data['address'])
        Student.validate_phone(student_data['phone'])
        Student.validate_min_required_facultative_hours(student_data.get('min_required_facultative_hours', 0))
        try:
            new_id = self._db.execute_insert("""
                INSERT INTO students (first_name, last_name, patronymic, 
                                     address, phone, min_required_facultative_hours)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING student_id
            """, (
                student_data['first_name'],
                student_data['last_name'],
                student_data.get('patronymic'),
                student_data['address'],
                student_data['phone'],
                student_data.get('min_required_facultative_hours', 0)
            ))

            return Student(
                student_id=new_id,
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                patronymic=student_data.get('patronymic'),
                address=student_data['address'],
                phone=student_data.get('phone'),
                min_required_facultative_hours=student_data.get('min_required_facultative_hours', 0)
            )
        except psycopg2.IntegrityError as e:
            if 'phone' in str(e).lower() and 'unique' in str(e).lower():
                raise ValueError("Пользователь с данным номером телефона уже существует")
            raise e

    def update_student(self, student_id: int, student_data: dict) -> Student | None:
        """Обновляет данные студента и возвращает обновленный объект."""
        Student.validate_name(student_data['first_name'])
        Student.validate_name(student_data['last_name'])
        Student.validate_name(student_data.get('patronymic'), is_patronymic=True)
        Student.validate_address(student_data['address'])
        Student.validate_phone(student_data['phone'])
        Student.validate_min_required_facultative_hours(student_data.get('min_required_facultative_hours', 0))
        try:
            rows_affected = self._db.execute_update("""
                UPDATE students 
                SET first_name = %s, last_name = %s, patronymic = %s,
                    address = %s, phone = %s, min_required_facultative_hours = %s
                WHERE student_id = %s
            """, (
                student_data['first_name'],
                student_data['last_name'],
                student_data.get('patronymic'),
                student_data['address'],
                student_data.get('phone'),
                student_data.get('min_required_facultative_hours', 0),
                student_id
            ))

            if rows_affected > 0:
                return Student(
                    student_id=student_id,
                    first_name=student_data['first_name'],
                    last_name=student_data['last_name'],
                    patronymic=student_data.get('patronymic'),
                    address=student_data['address'],
                    phone=student_data.get('phone'),
                    min_required_facultative_hours=student_data.get('min_required_facultative_hours', 0)
                )
            return None
        except psycopg2.IntegrityError as e:
            if 'phone' in str(e).lower() and 'unique' in str(e).lower():
                raise ValueError("Пользователь с данным номером телефона уже существует")
            raise e

    def delete_student(self, student_id: int) -> bool:
        """Удаляет студента по ID и возвращает успешность операции."""
        rows_affected = self._db.execute_delete("""
            DELETE FROM students WHERE student_id = %s
        """, (student_id,))

        return rows_affected > 0

    def get_count(self) -> int:
        """Возвращает общее количество студентов в базе."""
        rows = self._db.execute_query("SELECT COUNT(*) FROM students")
        return rows[0][0] if rows else 0