

import os
from os.path import join, dirname, realpath

from flask import Flask, render_template, request

app = Flask(__name__)

#we want to now upload an image
#here is the code copied from https://justpasteit.it/6yr3g

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/')   #create path where the image file will be saved
# specify allowed extensions
ALLOWED_EXTENSIONS = set(['mp4', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# configure upload folder in the app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024*1024

#this function is used to check if the allowed image extensions has been met

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#make our route return
@app.route('/')
def main():
    return render_template('index.html')


#create a route called services that returns the services template
@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/knowledge')
def knowledge():
    return render_template('Knowledge.html')


@app.route('/about')
def About():
    return render_template('about.html')


#we import pymysql

import pymysql


#make route aware of methods to be received
@app.route('/add', methods=['POST', 'GET'])
def add():
    #We first have to check the methods sent either POST or Get so that we can extract the data sent. We do this by importing a module called request
    if request.method =='POST':
        p_name = request.form['p_name']
        cost = request.form['cost']
        p_desc = request.form['p_desc']
        p_type = request.form['p_type']
        contact = request.form['contact']
        file = request.files['file']  #receive file

        # check if file is present and allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # save the file with its filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #once the file is saved, save the link to the db

        #now we want to save this data in the database hence we have to import pymysql as the connector to the sql
        connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        #connection has true or false connection
        #create a cursor and use it to execute SQL --- Cursor helps to execute sql

        cursor = connection.cursor()

        sql = """INSERT INTO tbl_products1( product_name, product_type, cost, contact, product_desc, image) VALUES (%s,%s,%s,%s,%s,%s)"""
        cursor.execute(sql, (p_name, p_type, cost, contact, p_desc, filename))

        #commit/rollback -if the connection crashes before it commits, it should render back
        connection.commit()
        return render_template('add.html', msg="CONGRATS! SUCCESSFULLY SAVED")

    else:
        return render_template('add.html', msg2="Sorry, connection failed. Try again!")


@app.route('/register', methods=['POST', 'GET'])
def registration():
    #We first have to check the methods sent either POST or Get so that we can extract the data sent. We do this by importing a module called request
    if request.method =='POST':
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        email_add = request.form['email_add']
        password = request.form['password']
        c_password = request.form['c_password']


        connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        cursor = connection.cursor()

        sql = """INSERT INTO tbl_register(f_name, l_name, email_add, password) VALUES(%s, %s, %s, %s)"""
        cursor.execute(sql, (f_name, l_name, email_add, password))

        #commit/rollback -if the connection crashes before it commits, it should render back
        connection.commit()
        return render_template('index.html')

    else:
        return render_template('Registration.html')


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        f_name = request.form['f_name']
        # l_name = request.form['l_name']

        connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        cursor = connection.cursor()

        sql = """SELECT * FROM employees WHERE f_name= %s"""

        # sql="""SELECT * FROM employees WHERE f_name=%s AND l_name=%s"""

        #  you can also use OR , LIKE to help in querying    --- Research further on this

        cursor.execute(sql, (f_name))

        #fetch rows
        rows = cursor.fetchall()  # rows can contain 0,1 or more rows

        #perform a row count
        if cursor.rowcount == 0:
            return render_template('search.html', msg='No records')
        else:
            return render_template('search.html', data=rows)

    else: #shows the user the form for the first time --- for the first time it skips the POST and shows the user the template for the first time
        return render_template('search.html')

@app.route('/products')
def products():

        connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        cursor = connection.cursor()

        sql = """SELECT * FROM tbl_products1"""

        cursor.execute(sql)

        # fetch rows
        rows = cursor.fetchall()  # rows can contain 0,1 or more rows

        # perform a row count
        if cursor.rowcount == 0:
            return render_template('Products.html', msg='No records')
        else:
            return render_template('Products.html', data=rows)



if __name__ == '__main__':
    app.run()



'''

to store data in the database you have to run the xampp server

to run xampp server in linux we run the following command in linux

sudo /opt/lampp/lampp start

then go to http://localhost/dashboard/phpmyadmin  to access the database

to host your application, host it in Heruku or python anywhere

'''

