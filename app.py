from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
import bcrypt
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

# Datos de usuario
usuarios = [
    {
        "email": "dbelmares@utc.edu.mx",
        "password": bcrypt.hashpw("belmares".encode('utf-8'), bcrypt.gensalt())
    }
]

def obtener_alumno_por_id(alumno_id):
    return mongo.db.alumnos.find_one({'matricula': alumno_id})

def obtener_materias_y_profesores(alumno_id):
    asignaciones = mongo.db.materias_profes.find({'matricula': alumno_id})
    materias_profes = []

    for asignacion in asignaciones:
        materia = mongo.db.materias.find_one({'id_materia': asignacion['id_materia']})
        profesor = mongo.db.profes.find_one({'no_empleado': asignacion['no_empleado']})

        if materia and profesor:
            materias_profes.append({
                'materia': materia['nombre_materia'],
                'profesor': profesor['nombre']
            })

    return materias_profes

@app.route('/')
def index():
    if "email" in session:
        alumnos = mongo.db.alumnos.find()
        return render_template('index.html', alumnos=alumnos)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        user = next((u for u in usuarios if u["email"] == email), None)
        if user and bcrypt.checkpw(password, user["password"]):
            session['email'] = email
            return redirect(url_for('index'))
        else:
            flash("Correo o contraseña incorrectos.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/alumnos', methods=['GET', 'POST'])
def alumnos():
    if "email" in session:
        if request.method == 'POST':
            matricula = request.form['matricula']
            nombre = request.form['nombre']
            carrera = request.form['carrera']

            if not matricula or not nombre or not carrera:
                flash("Todos los campos son obligatorios.", "danger")
            else:
                mongo.db.alumnos.insert_one({
                    'matricula': matricula,
                    'nombre': nombre,
                    'carrera': carrera
                })
                flash("Alumno registrado correctamente.", "success")
                return redirect(url_for('alumnos'))

        alumnos = mongo.db.alumnos.find()
        return render_template('alumnos.html', alumnos=alumnos)
    return redirect(url_for('login'))

@app.route('/profes', methods=['GET', 'POST'])
def profes():
    if "email" in session:
        if request.method == 'POST':
            no_empleado = request.form['no_empleado']
            nombre = request.form['nombre']

            if not no_empleado or not nombre:
                flash("Todos los campos son obligatorios.", "danger")
            else:
                mongo.db.profes.insert_one({
                    'no_empleado': no_empleado,
                    'nombre': nombre
                })
                flash("Profesor registrado correctamente.", "success")
                return redirect(url_for('profes'))

        profes = mongo.db.profes.find()
        return render_template('profes.html', profes=profes)
    return redirect(url_for('login'))

@app.route('/materias', methods=['GET', 'POST'])
def materias():
    if "email" in session:
        if request.method == 'POST':
            id_materia = request.form['id_materia']
            nombre_materia = request.form['nombre_materia']

            if not id_materia or not nombre_materia:
                flash("Todos los campos son obligatorios.", "danger")
            else:
                mongo.db.materias.insert_one({
                    'id_materia': id_materia,
                    'nombre_materia': nombre_materia
                })
                flash("Materia registrada correctamente.", "success")
                return redirect(url_for('materias'))

        materias = mongo.db.materias.find()
        return render_template('materias.html', materias=materias)
    return redirect(url_for('login'))

@app.route('/asignar', methods=['GET', 'POST'])
def asignar():
    if "email" in session:
        if request.method == 'POST':
            id_materia = request.form['id_materia']
            no_empleado = request.form['no_empleado']
            matricula = request.form['matricula']

            if not id_materia or not no_empleado or not matricula:
                flash("Todos los campos son obligatorios.", "danger")
            else:
                mongo.db.materias_profes.insert_one({
                    'id_materia': id_materia,
                    'no_empleado': no_empleado,
                    'matricula': matricula
                })
                flash("Asignación realizada correctamente.", "success")
                return redirect(url_for('asignar'))

        materias = mongo.db.materias.find()
        profes = mongo.db.profes.find()
        alumnos = mongo.db.alumnos.find()
        return render_template('asignar.html', materias=materias, profes=profes, alumnos=alumnos)
    return redirect(url_for('login'))

@app.route('/alumnos_materias')
def alumnos_materias():
    if "email" in session:
        alumnos = mongo.db.alumnos.find()
        alumnos_materias = []

        for alumno in alumnos:
            materias_profes = obtener_materias_y_profesores(alumno['matricula'])
            if materias_profes:
                alumnos_materias.append({
                    'alumno': alumno,
                    'materias_profes': materias_profes
                })

        return render_template('alumnos_materias.html', alumnos_materias=alumnos_materias)
    return redirect(url_for('login'))

@app.route('/reportes')
def reportes():
    if "email" in session:
        alumnos = mongo.db.alumnos.find()
        profes = mongo.db.profes.find()
        materias = mongo.db.materias.find()
        return render_template('reportes.html', alumnos=alumnos, profes=profes, materias=materias)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
