from flask import Flask, request, redirect, url_for
from controllers.controller import StudentsController, StudentsAddController

app = Flask(__name__)

students_controller = StudentsController()
students_add_controller = StudentsAddController()

@app.route('/')
def start():
    """Главная страница со списком студентов"""
    return "hello/"

@app.route('/<university>/')
def index(university):
    """Главная страница со списком студентов"""
    if university != students_controller.get_university():
        students_controller.set_university(university)
    return students_controller.show_list_students()

@app.route('/<university>/add/')
def add_student(university):
    """Форма добавления нового студена"""
    if university != students_add_controller.get_university():
        students_add_controller.set_university(university)
    return students_add_controller.show_add_student_form()

@app.route('/<university>/add/', methods=['POST'])
def add_student_submit(university):
    """Обработка добавления студента"""
    students_add_controller.set_university(university)
    try:
        students_add_controller.add_student(request.form.to_dict())
        # Редирект на список студентов после успешного добавления
        return redirect(url_for('index', university=university))
    except Exception as e:
        return f"Ошибка при добавлении: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)