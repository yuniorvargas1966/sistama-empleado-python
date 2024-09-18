from flask import Flask, render_template
from flask import request, flash, redirect, url_for
from flask import send_from_directory
import pymysql
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Settings
app.secret_key = secret_key = os.getenv('SECRET_KEY')

# Configuración de la conexión a la base de datos
app.config['MYSQL_HOST'] = MYSQL_HOST = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = MYSQL_USER = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = MYSQL_DB = os.environ.get('MYSQL_DB')
# Función para conectarse a la base de datos
def connect_to_database():
    conn = pymysql.connect(
        host = app.config['MYSQL_HOST'],
        user = app.config['MYSQL_USER'],
        password = app.config['MYSQL_PASSWORD'],
        database = app.config['MYSQL_DB']
        ) 
    return conn    

CARPETA= os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)    

# Ruto para devolver todos los registros
@app.route('/')
def index():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados")
    empleados = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in empleados:
        insertObject.append(dict(zip(columnNames, record))) 
    cursor.close()
    conn.close()
    return render_template('/empleados/index.html', empleados=insertObject)

# Ruta para devolver u solo registro
@app.route('/<int:id>')
def edit(id):
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id))
    empleados = cursor.fetchall()
    
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in empleados:
        insertObject.append(dict(zip(columnNames, record))) 
    cursor.close()
    conn.close()
    return render_template('empleados/index.html', empleados=insertObject)

@app.route('/destroy/<int:id>')
def destroy(id):
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
     
    cursor.execute("DELETE FROM empleados WHERE id=%s",(id))
    conn.commit()
    flash('Registro eliminado exitosamente.')
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id))
    empleados = cursor.fetchall()
    
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in empleados:
        insertObject.append(dict(zip(columnNames, record))) 
    conn.commit()
    return render_template('empleados/edit.html', empleados=insertObject)
    

@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id=request.form['txtID']

    sql = "UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s ;"
    
    datos = (_nombre, _correo,id)

    conn = connect_to_database()
    cursor = conn.cursor()

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename!='':

        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
        fila=cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s", (nuevoNombreFoto,id))
        conn.commit()

    cursor.execute(sql, datos)

    conn.commit()

    flash('Registro actualizado exitosamente.')
    return redirect('/')

@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    global nuevoNombreFoto
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    if _nombre=='' or _correo=='' or _foto=='':
        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename!='':

        nuevoNombreFoto =tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
   
    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL,%s,%s,%s);"
    
    datos=(_nombre,_correo,nuevoNombreFoto)

    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    flash('Registro insertado exitosamente.')
    return redirect('/')

# Página no encontrada.     
def pagina_no_encontrada(error):
    return redirect(url_for('index'))  
      
if __name__ == '__main__':
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(host='0.0.0.0', port="4004", debug=True)
 
