from models.student_repository import StudentRepJson, StudentRepYaml
from models.student_rep_db import StudentRepDB
from models.student_rep_db_adapter import StudentRepDBAdapter
import config


class UniversityFactory:
    """Фабрика для создания репозиториев студентов в зависимости от университета"""

    _repositories = dict()

    @staticmethod
    def create_repository(university_name: str):
        """
        Создает репозиторий для указанного университета
        """
        print(f"--- DEUG factory --- university_name: {university_name}")

        if university_name in UniversityFactory._repositories:
            return UniversityFactory._repositories[university_name]

        if university_name == "kubsu":
            repo = StudentRepJson(config.JSON_DATA_FILE_PATH)
        elif university_name == "kubstu":
            repo = StudentRepYaml(config.YAML_DATA_FILE_PATH)
        elif university_name == "kubsau":
            db_repo = StudentRepDB()
            repo = StudentRepDBAdapter(db_repo)
        else:
            raise ValueError(f"Неизвестный университет: {university_name}")

        UniversityFactory._repositories[university_name] = repo
        return repo