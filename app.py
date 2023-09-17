from flask import Flask
from flask import render_template,request,redirect,url_for,flash,jsonify
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
import os 



app = Flask(__name__)
app.secret_key="Panaderia"

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='panaderiav'
mysql.init_app(app)

CARPETA= os.path.join('uploads') #hace una referencia para entrar a la carpeta uploads
app.config['CARPETA']=CARPETA #crear ruta para almacenar en CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route('/')
def index():

    sql ="SELECT * FROM `producto`;"
    conn=mysql.connect() #Para ejecutar la coneccion mysql
    cursor=conn.cursor() #lamacena la informacion sql
    cursor.execute(sql) 
    producto= cursor.fetchall() #Para regeresar toda la informacion obtenida
    #print(producto)
    conn.commit() #commit para cerrar la instruccion

    return render_template('producto/index.html',producto= producto) #Para enviar la infoamrcion recuparada de la base de datos

@app.route('/live')
def live():
    return render_template('producto/live.html')

@app.route('/lvsearch', methods=['POST'])
def lvsearch():
    conn=mysql.connect() #Para ejecutar la coneccion mysql
    cursor=conn.cursor() #lamacena la informacion sql
    
    
    if request.method == 'POST':
        search_word = request.form['sql']
        print(search_word)
        if search_word == '':
            sql = "SELECT * FROM `producto` ORDER BY id;"
            cursor.execute(sql) 
            producto= cursor.fetchall()
            conn.commit() 
            cursor.close()
        else:
            sql = "SELECT * FROM producto WHERE nombre LIKE '%{}%' OR precio LIKE '%{}%' ORDER BY id DESC LIMIT 20".format(search_word,search_word,search_word)
            cursor.execute(sql)
            numrows = int(cursor.rowcount)
            producto= cursor.fetchall()
            conn.commit() 
            cursor.close()
            print(numrows)
    return jsonify({'htmlresponse': render_template('producto/response.html',producto=producto)})             


@app.route('/destroy/<int:id>')
def destroy(id):

    conn=mysql.connect() #Para ejecutar la coneccion mysql
    cursor=conn.cursor() #lamacena la informacion sql
    
    cursor.execute("SELECT foto FROM producto WHERE id=%s", id)
    fila= cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

    cursor.execute("DELETE FROM producto WHERE id=%s",(id))
    conn.commit()

    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):

    
    conn=mysql.connect() #Para ejecutar la coneccion mysql
    cursor=conn.cursor() #lamacena la informacion sql
    cursor.execute("SELECT * FROM producto WHERE id=%s",(id)) 
    producto= cursor.fetchall() #Para regeresar toda la informacion obtenida
   # print(producto)
    conn.commit() #commit para cerrar la instruccion

    return render_template('producto/edit.html',producto=producto)

@app.route('/update', methods=['POST'])
def update():
    
    _nombre=request.form['txtNombre'] #En esta parte se reciben todos los datos
    _precio=request.form['txtPrecio'] 
    _cat=request.form['txtCat']
    _foto=request.files['txtFoto']
    id=request.form['txtID']

    sql="UPDATE producto SET nombre=%s,precio=%s,categoria=%s  WHERE id=%s ;" 
    datos = (_nombre,_precio,_cat,id)

    conn=mysql.connect() #Para ejecutar la coneccion mysql
    cursor=conn.cursor() #lamacena la informacion sql
    
    now= datetime.now()
    tiempo= now.strftime("%Y%H%M%S")

    if _foto.filename!= '':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT foto FROM producto WHERE id=%s", id)
        fila= cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE producto SET foto=%s WHERE id=%s",(nuevoNombreFoto,id))
        conn.commit()

    cursor.execute(sql,datos) #sentencia de actualizacion
    conn.commit() #commit para cerrar la instruccion

    return redirect('/')

@app.route('/crear')
def crear():
    
    return render_template('producto/crear.html')

@app.route('/store', methods=['POST'])
def storage():
    
    _nombre=request.form['txtNombre']
    _precio=request.form['txtPrecio']
    _categoria=request.form['txtCat']
    _foto=request.files['txtFoto']

    if _nombre == '' or _precio == '' or _foto== '' or _categoria== '':
        flash('Recuerda llenar los campos')
        return redirect(url_for('crear'))

    now= datetime.now()
    tiempo= now.strftime("%Y%H%M%S")

    if _foto.filename!= '':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)




    sql ="INSERT INTO `producto` (`id`, `nombre`, `precio`, `foto`,`categoria`) VALUES (NULL,%s,%s,%s,%s);"
 
    datos = (_nombre,_precio,nuevoNombreFoto,_categoria)

    conn=mysql.connect() #Para ejecutar la coneccion mysql
    cursor=conn.cursor() #lamacena la informacion sql
    cursor.execute(sql,datos) 
    conn.commit() #commit para cerrar la instruccion

    return render_template('producto/crear.html')


if __name__== '__main__':
    app.run(debug=True)