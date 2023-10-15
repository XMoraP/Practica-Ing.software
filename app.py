from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_mysqldb import MySQL, MySQLdb
from PIL import Image
import bcrypt
import os
import io
import base64


app = Flask(__name__, template_folder="templates")

app.config['UPLOAD_FOLDER'] = './files'
ALLOWED_EXTENSIONS= {'pdf', 'txt'}
# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'uni-connect.mysql.database.azure.com'  # Cambia esto si tu servidor MySQL no está en localhost
app.config['MYSQL_USER'] = 'XMoraP'
app.config['MYSQL_PASSWORD'] = '12345678u$'
app.config['MYSQL_DB'] = 'uniconnect'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_SSL_CA'] = './DigiCertGlobalRootCA.crt.pem'

mysql = MySQL(app)

# Ruta para mostrar datos de la base de datos
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user")
    data = cur.fetchall()
    cur.close()
    return render_template('index2.html', data=data)



# Ruta para agregar un nuevo registro a la base de datos
@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    error = None
    if request.method == 'POST':
        nombre = request.form['name']
        apellido = request.form['last_name']
        email = request.form['email']
        contrasenna = request.form['password']

        if not nombre or not apellido or not email or not contrasenna:
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('mostrar_notificacion'))
            #return redirect(url_for('registrarse'))

        cur0 = mysql.connection.cursor()
        cur0.execute("SELECT eMail from user WHERE eMail = %s", [email])
        result = cur0.fetchone()

        if result and result['eMail'] == email:

            flash('Este email ya esta en uso', 'error')
            return redirect(url_for('registrarse'))
            
        else:
            # Realiza la inserción en la base de datos aquí
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO user (nombre, apellido, email, contrasenna) VALUES (%s, %s, %s, %s)",
                        (nombre, apellido, email, contrasenna))
            mysql.connection.commit()
            cur.close()
            
            return redirect(url_for('index2'))     

    return render_template('index2.html', error=error)
 
@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None
    result = None

    if request.method == 'POST':
        # Obtén los datos del formulario de inicio de sesión
        email = request.form['email']
        contrasenna = request.form['password']

        # Crea un cursor para interactuar con la base de datos
        cur = mysql.connection.cursor()

        # Obtiene la contraseña almacenada para el usuario
        cur.execute("SELECT id_user, contrasenna, nombre, apellido, status, nombre_grado FROM user WHERE eMail = %s", [email])
        result = cur.fetchone()

        if not email or not contrasenna:
            #flash('Debe ingresar email y contraseña para iniciar sesion', 'error')
            return redirect(url_for('login'))    

    if result:
    # Comprueba si la contraseña ingresada coincide con la almacenada
        if contrasenna == result['contrasenna']:

        # Inicio de sesión exitoso, establece una sesión
            session['logged_in'] = True
            session['email'] = email
            session['id_user'] = result['id_user']
            session['name'] = result['nombre']
            session['last_name'] = result['apellido']
            session['status'] = result['status']
            session['nombre_grado'] = result['nombre_grado']

            return redirect(url_for('dashboard'))
        else:
        # Contraseña incorrecta
            flash('Email o contraseña incorrectos', 'error')

    return render_template('login.html', error=error)

#DashBoard
@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        user_profile = {
            'name': session['name'],
            'last_name': session['last_name'],
            'status' : session['status']
        }
    else:
        user_profile = None


    return render_template('dashboard.html', user_profile=user_profile)
#Tables

@app.route('/tables')
def tables():
    if 'logged_in' in session:
        user_profile = {
            'name': session['name'],
            'last_name': session['last_name']
        }
    else:
        user_profile = None
    subject = None
    id_user= None
    session['id_user'] = id_user
    if request.method == 'POST':
         cur = mysql.connection.cursor()
         cur.execute("SELECT course_title FROM courses WHERE user_id = %s", [id_user])
         cur.fetchall()
         cur.close()

    return render_template('tables.html', user_profile=user_profile, subject = subject)

    
#Asignaturas
@app.route('/asignaturas')
def asignaturas():
    if 'logged_in' in session:
        user_profile = {
            'name': session['name'],
            'last_name': session['last_name']
        }
    else:
        user_profile = None

    return render_template('asignaturas.html', user_profile=user_profile)

#Elements
@app.route('/general_elements')
def general_elements():
    return render_template('general_elements.html')

@app.route('/media_gallery')
def media_gallery():
    return render_template('media_gallery.html')

@app.route('/invoice')
def invoice():
    return render_template('invoice.html')

@app.route('/icons')
def icons():
    return render_template('icons.html')


#Apps
@app.route('/email')
def email():
    return render_template('email.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

#Pricing_Tables
@app.route('/price')
def price():
    return render_template('price.html')

#Contact
@app.route('/contact')
def contact():
    cur = mysql.connection.cursor()
    cur.execute("SELECT CONCAT(user.nombre, ' ', user.apellido) AS nombre_apellido, user.email, tutor.asignaturas_tutor FROM user INNER JOIN tutor ON user.id_user = tutor.id_tutor;")
    contacts = cur.fetchall()
    cur.close()
    return render_template('contact.html', contacts=contacts)


#Additional_Pages

@app.route('/profile')
def profile():
    # Fetch user's profile information from your data source (e.g., session, database)
    user_profile = None
    user_profile = {
        'name': session.get('name'),
        'last_name': session['last_name'],
        'email': session['email'],
        'status': session['status'],
        'nombre_grado': session['nombre_grado'],
        'photo_url': 'static/images/userPhoto.png',  # Replace with the actual URL of the user's photo
        'role': 'Estudiante',  # Replace with the actual user's role
    }
    mensaje = session.pop('mensaje', None)
    

    return render_template('profile.html', user_profile=user_profile, mensaje=mensaje)

# Perfil Tutor
@app.route('/profileTutor')
def profileTutor():
    user_profile = None
    user_profile = {
        'name': session.get('name'),
        'last_name': session['last_name'],
        'email': session['email'],
        'status': session['status'],
        'nombre_grado': session['nombre_grado'],
        'photo_url': 'static/images/userPhoto.png',  # Replace with the actual URL of the user's photo
        'role': 'Estudiante',  # Replace with the actual user's role
    }
    mensaje = session.pop('mensaje', None)

    return render_template('profileTutor.html', user_profile=user_profile, mensaje=mensaje)

# Dashboard Tutor
@app.route('/dashboardTutor')
def dashboardTutor():
    user_profile = None
    if 'logged_in' in session:
        user_profile = {
            'name': session['name'],
            'last_name': session['last_name'],
            'email': session['email'],
            'status': session['status']
        }
        mensaje = session.pop('mensaje', None)
 
    return render_template('dashboardTutor.html', user_profile=user_profile, mensaje = mensaje)

# Guardar cambios del Perfil
@app.route('/guardar_perfil', methods=['POST'])
def guardar_perfil():
    
    user_profile = None
    mensaje = None
    error = None

    if request.method == 'POST':

        nombre = request.form['name']
        apellido = request.form['last_name']
        email = request.form['email']
        contrasenna = request.form['password']
        grado = request.form['grado']

        user_profile = {
            'name': session['name'],
            'last_name': session['last_name'],
            'status': session['status'],
            'email': session['email'],
            'nombre_grado': session['nombre_grado']
           
        }

        email_from_session = session["email"]
        cursor = mysql.connection.cursor()
        cursor2 = mysql.connection.cursor()

        # Obtener la contraseña almacenada asociada con el correo electrónico proporcionado
        cursor.execute("SELECT contrasenna, eMail FROM user WHERE eMail = %s", [email_from_session])
        cursor2.execute("SELECT eMail from user WHERE eMail <> %s", [email_from_session])
        resultado = cursor.fetchone()
        emails_existentes = cursor2.fetchone()

            # Comparar la contraseña proporcionada con la almacenada en la base de datos
        if contrasenna == resultado['contrasenna'] and not (emails_existentes['eMail'] == email):
                # Las contraseñas coinciden, actualizar el perfil
                cursor.execute("UPDATE user SET nombre = %s, apellido = %s, eMail = %s, nombre_grado= %s WHERE contrasenna = %s", [nombre, apellido, email, grado, contrasenna])
                mysql.connection.commit()
                cursor.close()

                session['name'] = nombre
                session['last_name'] = apellido
                session['email'] = email
                session['nombre_grado'] = grado

                session['mensaje'] = {'tipo': 'successUpdate', 'contenido': 'Perfil actualizado exitosamente'}
                return redirect(url_for('profile'))
        if emails_existentes['eMail'] == email:
                session['mensaje'] = {'tipo': 'errorEmail', 'contenido': 'Este correo electrónico ya esta en uso.'}
                return redirect(url_for('profile'))
        else:
             if not (contrasenna == resultado['contrasenna']):
                session['mensaje'] = {'tipo': 'errorPassword', 'contenido': 'La contraseña proporcionada es incorrecta. Por favor, inténtalo de nuevo.'}
                return redirect(url_for('profile'))

    return render_template('profile.html', user_profile=user_profile, mensaje=mensaje)

# Codigos para subir imagenes de perfil.
@app.route('/subir_imagen', methods=['POST'])
def subir_imagen():
    id_user = session['id_user'] 
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT image from image WHERE id_user = %s", (id_user,))
        result = cursor.fetchall()
        mysql.connection.commit()

        if result:
            data = base64.b64encode(imagen.read())
            cursor.execute("UPDATE image SET image = %s WHERE id_user = %s", (data, id_user,))
            mysql.connection.commit()
            cursor.close()
            session['mensaje'] = {'tipo':'successUpdate','contenido':'imagen actualizada'}
            return redirect(url_for('profile'))
        else:
            data = base64.b64encode(imagen.read())
            cursor.execute("INSERT INTO image (id_user, image) VALUES (%s,%s)", (id_user, data,))
            mysql.connection.commit()
            cursor.close()
            session['mensaje'] = {'tipo':'successUpdate','contenido':'imagen actualizada Nuevo'}
            return redirect(url_for('profile'))
        
@app.route('/cargar_imagen')
def cargar_imagen():
    id_user = session['id_user']
    cur = mysql.connection.cursor()
    cur.execute("SELECT image FROM image WHERE id_user = %s", (id_user,))
    image_data = cur.fetchone()
    cur.close()
    if image_data is not None:
        # Decodifica la imagen en formato base64 para mostrarla
        image_bytes = base64.b64decode(image_data['image'])
        return send_file(io.BytesIO(image_bytes), mimetype='image/*')
    else:
        return "Imagen no encontrada", 404

@app.route('/project')
def project():
    return render_template('project.html')

#Maps
@app.route('/map')
def map():
    return render_template('map.html')

#Charts
@app.route('/charts')
def charts():
    return render_template('charts.html')

#Settings
@app.route('/settings')
def settings():
    return render_template('settings.html')

#Boton Salir
@app.route('/salir', methods=['GET'])
def salir():
    session.clear()
    return render_template('index2.html')

@app.route('/registrarse',  methods=['GET', 'POST'])
def registrarse():
    return render_template('register.html')

@app.route('/index2',  methods=['GET', 'POST'])
def index2():
    return render_template('index2.html')

# Cambiar contraseña de usuario
@app.route('/cambiarContrasenna',  methods=['GET', 'POST'])
def cambiarContrasenna():
    user_profile = None
    mensaje = None
    
    if request.method == 'POST':
    
        email_from_session = session["email"]
        contrasenna = request.form['password']
        newPassword = request.form['newPassword']
        confirmPassword = request.form['confirmPassword']


        cur = mysql.connection.cursor()
        cur.execute("SELECT contrasenna FROM user WHERE eMail = %s", [email_from_session])
        result = cur.fetchone()

        if result['contrasenna'] == contrasenna: 
            if newPassword == confirmPassword:
                cursor = mysql.connection.cursor()
                cursor.execute("UPDATE user SET contrasenna = %s WHERE contrasenna = %s", [newPassword, contrasenna])
                result = cur.fetchone()
                mysql.connection.commit()
                cursor.close()

                session['contrasenna']: newPassword
                session['mensaje'] = {'tipo':'successUpdate','contenido':'Contraseña actualizada'}
                return redirect(url_for('profile'))
            else:
                session['mensaje'] = {'tipo': 'errorPassword', 'contenido': 'Los campos Nueva contraseña y Confirmar contraseña no coinciden. Por favor, inténtalo de nuevo.'}
                return redirect(url_for('profile'))
        else:
            session['mensaje'] = {'tipo': 'errorPassword', 'contenido': 'La contraseña proporcionada es incorrecta. Por favor, inténtalo de nuevo.'}
            return redirect(url_for('profile')) 
        
    return render_template('profile.html', user_profile=user_profile, mensaje=mensaje)

#Darse de alta de tutor
@app.route('/altaTutor',  methods=['GET', 'POST'])
def altaTutor():
     
     user_profile = None
     mensaje = None
     
     if request.method == 'POST':
    
        email_from_session = session["email"]
        contrasenna = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT contrasenna FROM user WHERE eMail = %s", [email_from_session])
        result = cur.fetchone()

        if result['contrasenna'] == contrasenna:
                cursor = mysql.connection.cursor()
                cursor.execute("UPDATE user SET status = 'Tutor' WHERE contrasenna = %s", [contrasenna])
                result = cursor.fetchone()
                mysql.connection.commit()

            
                session['mensaje'] = {'tipo':'successUpdate','contenido':'Te has dado de alta de Tutor'}

                cursor2 = mysql.connection.cursor()
                cursor2.execute("SELECT status FROM user WHERE eMail = %s", [email_from_session])
                resultado = cursor2.fetchone()
                mysql.connection.commit()
                session['status'] = resultado['status']

                return redirect(url_for('dashboardTutor'))
        

        else:
            session['mensaje'] = {'tipo': 'errorPassword', 'contenido': 'La contraseña proporcionada es incorrecta. Por favor, inténtalo de nuevo.'}
            return redirect(url_for('profile')) 
        
     return render_template('profile.html', user_profile=user_profile, mensaje=mensaje)




        


    

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)

