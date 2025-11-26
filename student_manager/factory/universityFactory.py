from models.student_repository import StudentRepJson, StudentRepYaml
from models.student_rep_db import StudentRepDB
from models.student_rep_db_adapter import StudentRepDBAdapter
import config


class UniversityFactory:
    """Фабрика для создания репозиториев студентов в зависимости от университета"""

    @staticmethod
    def create_repository(university_name: str):
        """
        Создает репозиторий для указанного университета
        """
        if university_name == "kubsu":
            return StudentRepJson(config.JSON_DATA_FILE_PATH)
        elif university_name == "kubstu":
            return StudentRepYaml(config.YAML_DATA_FILE_PATH)
        elif university_name == "kubsau":
            db_repo = StudentRepDB()
            return StudentRepDBAdapter(db_repo)
        else:
            raise ValueError(f"Неизвестный университет: {university_name}")