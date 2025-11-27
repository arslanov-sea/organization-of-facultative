from flask import Flask, request, redirect, url_for
from controllers.controller import StudentsController, StudentsAddController, StudentsUpdateController, StudentsDeleteController, Controller
from appconfig import UNIVERSITIES

app = Flask(__name__)

students_controller = StudentsController()
students_add_controller = StudentsAddController()
students_update_controller = StudentsUpdateController()
students_delete_controller = StudentsDeleteController()

def is_university_exist(university):
    return university in UNIVERSITIES.keys()

@app.route('/')
def start():
    """Главная страница со списком студентов"""
    return Controller.show_start()

@app.route('/favicon.ico/')
def favicon():
    """Обработка favicon"""
    return app.send_static_file('favicon.ico')

@app.route('/<university>/')
def index(university):
    """Главная страница со списком студентов"""
    if is_university_exist(university):
        if university != students_controller.get_university():
            students_controller.set_university(university)
        return students_controller.show_list_students()
    return Controller.show_404()

@app.route('/<university>/add/')
def add_student(university):
    """Форма добавления нового студена"""
    if is_university_exist(university):
        if university != students_add_controller.get_university():
            students_add_controller.set_university(university)
        return students_add_controller.show_add_student_form()
    return Controller.show_404()

@app.route('/<university>/add/', methods=['POST'])
def add_student_submit(university):
    """Обработка добавления студента"""
    if is_university_exist(university):
        if university != students_add_controller.get_university():
            students_add_controller.set_university(university)
        return students_add_controller.add_student(request.form.to_dict())
    return Controller.show_404()

@app.route('/<university>/<int:student_id>/')
def update_student(university, student_id):
    """Форма редактирования студента"""
    if is_university_exist(university):
        if university != students_update_controller.get_university():
            students_update_controller.set_university(university)
        return students_update_controller.show_update_student_form(student_id)
    return Controller.show_404()

@app.route('/<university>/<int:student_id>/', methods=['POST'])
def update_student_submit(university, student_id):
    """Обработка редактирования студента"""
    if is_university_exist(university):
        if university != students_update_controller.get_university():
            students_update_controller.set_university(university)
        return students_update_controller.update_student(student_id, request.form.to_dict())
    return Controller.show_404()

@app.route('/<university>/<int:student_id>/delete', methods=['POST'])
def delete_student(university, student_id):
    """Удаление студента"""
    students_delete_controller.set_university(university)
    try:
        students_delete_controller.delete_student(student_id)
        return redirect(url_for('index', university=university))
    except Exception as e:
        return f"Ошибка при удалении: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)