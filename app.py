import http
from flask import Flask, render_template
from flask import request, flash, redirect, url_for
from flask import send_from_directory
from flaskext.mysql import MySQL
from datetime import datetime
import os

app = Flask(__name__)

# Settings
app.secret_key = 'mysecretkey'

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'containers-us-west-167.railway.app'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'vKYINRwWohPOUgyTTiy7'
app.config['MYSQL_DATABASE_DB'] = 'railway'
app.config['MYSQL_DATABASE_PORT'] = 7592
mysql.init_app(app)

CARPETA= os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)    

@app.route('/')
def index():

    sql = "SELECT * FROM `empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    empleados = cursor.fetchall()
    
    conn.commit()
    return render_template('empleados/index.html', empleados=empleados)

@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
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

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id))
    empleados = cursor.fetchall()
    conn.commit()
    flash('Ahora puede editar este registro...')
    return render_template('empleados/edit.html', empleados=empleados)

@app.route('/update', methods=['POST'])
def update():

    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id=request.form['txtID']

    sql = "UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s ;"
    
    datos = (_nombre, _correo,id)

    conn = mysql.connect()
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

    conn = mysql.connect()
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
    app.run()
 
