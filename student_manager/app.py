from flask import Flask, render_template
from controllers.controller import StudentsController

app = Flask(__name__)

# Создаем контроллер
students_controller = StudentsController()

@app.route('/')
def start():
    """Главная страница со списком студентов"""
    return "hello/"

@app.route('/<university>')
def index(university):
    """Главная страница со списком студентов"""
    if university != students_controller.get_university():
        students_controller.set_university(university)
    return students_controller.show_list_students()

if __name__ == '__main__':
    app.run(debug=True)