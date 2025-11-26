from flask import Flask, render_template
from controllers.controller import StudentsController

app = Flask(__name__)

# Создаем контроллер
students_controller = StudentsController()

@app.route('/')
def index():
    """Главная страница со списком студентов"""
    return students_controller.show_list_students()

if __name__ == '__main__':
    app.run(debug=True)