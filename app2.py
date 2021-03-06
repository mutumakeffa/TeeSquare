import os
from os.path import join, dirname, realpath

from flask import Flask, render_template, request, redirect, session, send_file

# we create a flask application parsing its name
app2 = Flask(__name__)

# We now want to create a session to identify each user
# We first generate a secret key used for encrypting the session. You can also import random  and use x= random.randit(0,5)
app2.secret_key = "sssss34567890hgffghjk(*&^%$#@#$%^&"

# we want to now upload Images and files
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/')  # create path where the image file will be saved
# specify allowed extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc'}

# configure upload folder in the app
app2.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app2.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024


# this function is used to check if the allowed image extensions has been met

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# we import pymysql
# this is a connector to our database
import pymysql

# make a connection to the database only once
connection = pymysql.connect("localhost", "root", "", "datasuit_db")


# make route aware of methods to be received
# this route is for uploading files to the file system then saving the file path to the database
@app2.route('/addSheets', methods=['POST', 'GET'])
def addsheet():
    # We first have to check the methods sent either POST or Get so that we can extract the data sent. We do this by importing a module called request

    if request.method == 'POST':
        file = request.files['file']  # receive file
        title = request.form['title']
        sheet_number = request.form['sheetNumber']
        desc = request.form['description']
        tag = request.form['tag']

        # check if file is present and allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # save the file with its filename
            file.save(os.path.join(app2.config['UPLOAD_FOLDER'], filename))

        # once the file is saved, save the link to the db
        # now we want to save this data in the database hence we have to import pymysql as the connector to the sql -top
        # connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        # connection has true or false connection
        # create a cursor and use it to execute SQL --- Cursor helps to execute sql

        cursor = connection.cursor()

        sql = """INSERT INTO tbl_sheets(file,title,sheet_number,sheet_desc,tag) VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (filename, title, sheet_number, desc, tag))

        # commit/rollback -if the connection crashes before it commits, it should render back
        try:
            connection.commit()
            return redirect('/sheetsDashboard')
        except:
            connection.commit()
            return render_template('SheetsDashboard.html', msg="Error Occurred during transmission")

    else:
        return render_template('SheetsDashboard.html', msg2="Sorry, connection failed. Try again!")


@app2.route('/sheetsDashboard')
def sheets_dashboard():
    # first connect to the database using pymysql
    # connection = pymysql.connect("localhost", "root", "", "datasuit_db")

    # we now use the cursor function to execute on the database
    cursor = connection.cursor()

    sql = """SELECT * FROM tbl_sheets ORDER BY edited_when DESC """  # shows records in descending order or use ASC
    # sql = """SELECT * FROM tbl_projects WHERE project_code = %s """

    cursor.execute(sql)

    rows = cursor.fetchall()  # rows can contain 0,1 or more rows

    # perform a row count
    if cursor.rowcount == 0:
        return render_template('SheetsDashboard.html', msg='No records')
    else:
        return render_template('SheetsDashboard.html', data=rows)


@app2.route('/viewSheets')
def view_sheets():
    return render_template('view_sheets.html')


# this route will enable us to download the file
@app2.route('/file_download')
def file_download():
    return send_file('../static/uploads/')  # specify the file path here


# make our routes return
@app2.route('/')
def main():
    return render_template('main_testing_components.html')


@app2.route('/register', methods=['POST', 'GET'])
def register():
    # We first have to check the methods sent either POST or Get so that we can extract the data sent. We do this by importing a module called request
    if request.method == 'POST':
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        company_name = request.form['company_name']
        email_add = request.form['email_add']
        password1 = request.form['password1']
        password2 = request.form['password2']
        role = request.form['role']

        if password1 == "":
            return render_template('Registration_template.html', msg1="Empty password")
        elif password1 != password2:
            return render_template('Registration_template.html', msg2="!Passwords do not match")
        elif email_add == "":
            return render_template('Registration_template.html', msg3="Please enter a Valid email address")
        else:
            connection = pymysql.connect("localhost", "root", "", "datasuit_db")

            cursor = connection.cursor()

            sql = """INSERT INTO tbl_register(f_name, l_name, company_name, email_add, password, role) VALUES(%s, %s, %s, %s, %s, %s)"""

            # cursor() method is used to execute on sql
            # commit/rollback -if the connection crashes before it commits, it should render back

            # lets try and catch errors during commit and execution
            try:
                cursor.execute(sql, (f_name, l_name, company_name, email_add, password1, role))
                connection.commit()
                return redirect('/login')
            except:
                connection.commit()
                return render_template('Registration_template.html', msg5="Error Occurred during transmission")

    else:
        return render_template('Registration_template.html')


@app2.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email_add = request.form['email_add']
        password = request.form['password']

        # connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        cursor = connection.cursor()

        sql = """SELECT * FROM tbl_register WHERE email_add=%s AND password=%s """
        cursor.execute(sql, (email_add, password))

        if cursor.rowcount == 0:
            return render_template('login_template.html', msg6="unsuccessful Login. Check if you are registered")
        elif cursor.rowcount == 1:
            session['key'] = email_add
            # rows = cursor.fetchall()
            # session['key1'] = rows[0]
            # session['key2'] = rows[3]
            # print(rows[3])
            return redirect('/projects')

        else:
            return render_template('login_template.html', msg6='Something went Wrong. sorry for the inconvinience '
                                                               'Contact support at +254716681166')
    else:
        return render_template('login_template.html')


# @app2.route('/Dashboard/<code>')       #to give that route its own unique route
# def dashboard(code):
#     print(code)
#     return render_template('Dashboard2.html')


@app2.route('/Dashboard')
def dashboard():
    return render_template('Dashboard2.html')


@app2.route('/add_projects', methods=['POST', 'GET'])
def add_projects():
    # we want to protect the Projects templates with a session
    if 'key' in session:
        # pull out the key and get back your email and store that email in a variable called email
        # This helps you track who was in session when a certain activity was executed
        # you can render this email to the database to monitor various aspects
        # We use the email from the session to track what a specific user does.
        # i.e we can track individual products or projects and use that to make specific user profiles
        # also don't forget to add a column to cater for the email session in the database.
        email = session['key']

        if request.method == 'POST':
            project_name = request.form['project_name']
            project_code = request.form['project_code']
            project_status = request.form['project_status']
            project_location = request.form['project_location']

            # connection = pymysql.connect("localhost", "root", "", "datasuit_db")

            cursor = connection.cursor()
            sql = """INSERT INTO tbl_projects (project_name, project_code, project_status, project_location, email_add) VALUES (%s, %s, %s, %s, %s)"""

            try:
                cursor.execute(sql, (project_name, project_code, project_status, project_location, email))
                connection.commit()
                return redirect("/Dashboard")
            except:
                connection.commit()
                return render_template('Projects.html', msg="Error during transimmission")

        else:
            return render_template('Projects.html', msg10=email)


    elif 'key' not in session:
        return redirect('/login')
    else:
        return redirect('/login')


@app2.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        project_name = request.form['search']
        project_code = request.form['search']

        # Validate your passwords
        # if project_name=="":

        # connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        cursor = connection.cursor()

        sql = """SELECT * FROM tbl_projects WHERE project_name=%s or project_code=%s"""

        # sql="""SELECT * FROM employees WHERE f_name=%s AND l_name=%s"""
        #  you can also use OR , LIKE to help in querying    --- Research further on this

        cursor.execute(sql, (project_name, project_code))

        # fetch rows
        rows = cursor.fetchall()  # rows can contain 0,1 or more rows

        # perform a row count
        if cursor.rowcount == 0:
            return render_template('search_results.html', msg='No records')
        else:
            return render_template('search_results.html', data=rows)

    else:  # shows the user the form for the first time --- for the first time it skips the POST and shows the user the template for the first time
        return render_template('Projects.html')


@app2.route('/projects')
def projects():
    if 'key' in session:

        # you can check the session roles here
        # if not
        # check algorithms to encrypt passwords Bcrypt

        # connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        cursor = connection.cursor()

        sql = """SELECT * FROM tbl_projects WHERE email_add = %s ORDER BY time_created DESC """  # shows records in descending order / ASC
        email = session['key']
        cursor.execute(sql, email)

        # define a session key that tracks each individual project key to separate the projects

        # fetch rows
        rows = cursor.fetchall()  # rows can contain 0,1 or more rows

        # perform a row count
        if cursor.rowcount == 0:
            return render_template('Projects.html', msg='No update in Projects')
        else:
            return render_template('Projects.html', data=rows)

    elif 'key' not in session:
        return redirect('/login')
    else:
        return redirect('/login')


@app2.route('/add_team', methods=['POST', 'GET'])
def add_team():
    if request.method == 'POST':
        email = request.form['email']
        tag = request.form['tag']
        access = request.form['access']

        # connect to the database, insert into Database and execute
        cursor = connection.cursor()

        sql = """INSERT INTO tbl_team (email, tag, access) VALUES (%s, %s, %s)"""

        try:
            cursor.execute(sql, (email, tag, access))
            connection.commit()
            return redirect('/teams')
        except:
            connection.commit()
            return render_template('Teams.html')

    else:
        return render_template('Teams.html')


@app2.route('/teams')
# make sure to protect this with a project session
# the session will only specify what project you are currently in.
# All team mates invited are only invited in this particular session
def teams():
    # connect to the database and select the required fields
    cursor = connection.cursor()

    sql = """SELECT * FROM tbl_team ORDER BY date_posted DESC """

    cursor.execute(sql)

    rows = cursor.fetchall()

    # perform a row count
    if cursor.rowcount == 0:
        return render_template('Teams.html', msg='No records')
    else:
        return render_template('Teams.html', data=rows)


# path to upload images
UPLOAD_FOLDER2 = join(dirname(realpath(__file__)),
                      'static/uploads/images')  # create path where the image file will be saved

# configure upload folder in the app
app2.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2


@app2.route('/add_image', methods=['POST', 'GET'])
def add_image():
    if request.method == 'POST':
        image_file = request.files['image_file']
        image_name = request.form['image_name']
        image_desc = request.form['image_desc']
        tag = request.form['tag']

        # check if file is present and allowed
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            # save the file with its filename
            image_file.save(os.path.join(app2.config['UPLOAD_FOLDER2'], filename))

        # connect to the db and insert into it
        cursor = connection.cursor()
        sql = """INSERT INTO tbl_images (img_file, img_name, img_desc, tag) VALUES (%s, %s, %s, %s)"""

        try:
            cursor.execute(sql, (filename, image_name, image_desc, tag))
            connection.commit()
            return redirect('/images')
        except:
            connection.commit()
            return render_template('Images.html', msg="Error during transmission..try again")

    else:
        return render_template('Images.html')


@app2.route('/images')
def images():
    # since we already have a connection to the database, we execute using the cursor fxn
    cursor = connection.cursor()

    sql = """SELECT * FROM tbl_images ORDER BY date_posted DESC """  # shows records in descending order or use ASC

    cursor.execute(sql)

    rows = cursor.fetchall()  # rows can contain 0,1 or more rows

    # perform a row count
    if cursor.rowcount == 0:
        return render_template('Images.html', msg='No records')
    else:
        return render_template('Images.html', data=rows)


@app2.route('/add_document', methods=['POST', 'GET'])
def add_document():
    if request.method == 'POST':
        file = request.files['file']
        title = request.form['doc_title']
        desc = request.form['doc_desc']
        tag = request.form['tag']

        # check if file is present and allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # save the file with its filename
            file.save(os.path.join(app2.config['UPLOAD_FOLDER'], filename))

        # connect to the database, insert and execute
        cursor = connection.cursor()

        sql = """INSERT INTO tbl_documents (file, doc_title, doc_desc, tag) VALUES (%s,%s,%s,%s)"""

        try:
            cursor.execute(sql, (filename, title, desc, tag))
            connection.commit()
            return redirect('/Document')
        except:
            connection.commit()
            return render_template('Documents.html', msg="Error during transmission..try again")
    else:
        return render_template('Documents.html')


@app2.route('/Document')
def documents():
    # Firstly connect to the database
    cursor = connection.cursor()

    # select from the db
    sql = """SELECT * FROM tbl_documents ORDER BY date_posted DESC """

    cursor.execute(sql)

    rows = cursor.fetchall()  # rows can contain 0,1 or more rows

    # perform a row count
    if cursor.rowcount == 0:
        return render_template('Documents.html', msg='No records')
    else:
        return render_template('Documents.html', data=rows)


@app2.route('/add_issue', methods=['POST', 'GET'])
def add_issue():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        file = request.files['file']
        tag = request.form['tag']

        # check if file is present and allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # save the file with its filename
            file.save(os.path.join(app2.config['UPLOAD_FOLDER'], filename))

        # since we already have a connection to the database, we execute using the cursor fxn
        cursor = connection.cursor()
        sql = """INSERT INTO tbl_issues(title, description, file, tag) VALUES (%s,%s,%s,%s) """

        try:
            cursor.execute(sql, (title, desc, filename, tag))
            connection.commit()
            return redirect('/issue')
        except:
            connection.commit()
            return render_template('Issues.html', msg="Error during transmission..try again")

    else:
        return render_template('Issues.html')


@app2.route('/issue')
def issue():
    # first connect to the database
    cursor = connection.cursor()

    # then select and execute
    sql = """SELECT * FROM tbl_issues ORDER BY date_posted DESC """

    cursor.execute(sql)

    rows = cursor.fetchall()  # rows can contain 0,1 or more rows

    # perform a row count
    if cursor.rowcount == 0:
        return render_template('Issues.html', msg='No records')
    else:
        return render_template('Issues.html', data=rows)


@app2.route('/add_field', methods=['POST', 'GET'])
def add_field():
    if request.method == 'POST':
        title = request.form['title']
        frequency = request.form['frequency']
        description = request.form['description']
        file = request.files['file']
        tag = request.form['tag']

        # check if file is present and allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # save the file with its filename
            file.save(os.path.join(app2.config['UPLOAD_FOLDER'], filename))

        # connect to the database, insert into the database and execute
        cursor = connection.cursor()

        sql = """INSERT INTO tbl_fields (title, frequency, description, file, tag) VALUES (%s,%s,%s,%s,%s)"""

        try:
            cursor.execute(sql, (title, frequency, description, filename, tag))
            connection.commit()
            return redirect('/Field')
        except:
            connection.commit()
            return render_template('Field.html')
    else:
        return render_template('Field.html')


@app2.route('/Field')
def field():
    # connect to the database and select the rows
    cursor = connection.cursor()

    sql = """SELECT * FROM tbl_fields ORDER BY date_posted DESC"""

    cursor.execute(sql)

    rows = cursor.fetchall()

    # perform a row count
    if cursor.rowcount == 0:
        return render_template('Field.html', msg='No records')
    else:
        return render_template('Field.html', data=rows)


@app2.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


# make sure to add a logout link to the website to clear sessions
@app2.route('/logout')
def logout():
    # remove the key from the session
    session.pop('key', None)
    return redirect('/login')


if __name__ == '__main__':
    app2.run(debug=True)

'''

to store data in the database you have to run the xampp server

to run xampp server in linux we run the following command in linux

sudo /opt/lampp/lampp start

then go to http://localhost/dashboard/phpmyadmin  to access the database

to host your application, host it in Heroku or python anywhere

'''
