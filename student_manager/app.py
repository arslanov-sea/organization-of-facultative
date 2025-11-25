from flask import Flask
from controllers.controller import StudentsController

app = Flask(__name__)
controller = StudentsController

@app.route('/')
def index():
    return controller.show_list_students()

if __name__ == '__main__':
    app.run(debug=True)