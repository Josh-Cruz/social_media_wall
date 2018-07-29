from flask import Flask, request, redirect, render_template, session, flash
import re
import md5 # imports the md5 module to generate a hash
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,'the_wall')
app.secret_key = 'sooperdoopersekret'
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[a-zA-Z]+$')


@app.route('/', methods=['POST', 'GET'])
def form_valid():
    error = False
    logged_in= False
    if request.method == 'POST':        
        if len(request.form['email']) < 1:
            flash("E-mail cannot be empty!")
            error = True
        if len(request.form['first_name']) < 1 and len(request.form['last_name']) < 1:
            flash("Names cannot be empty!")
            error = True
        if len(request.form['password']) < 1 and len(request.form['confirm_password']):
            flash("Passwords cannot be empty!")   
            error = True
        if request.form['password'] != request.form['confirm_password']:
            flash("Passwords must match!")   
            error = True
        if not email.regex.match(request.form['email']):
            flash("Invalid Email Address!")
            error = True
        if not name.regex.match(request.form['first_name']):
            flash("Names can only accept a-z characters")
            error = True
        if not name.regex.match(request.form['last_name']):
            flash("Names can only accept a-z characters")
            error = True
        if len(request.form['password']) < 8 and len(request.form['confirm_password']) < 8:
            flash("Passwords must be over 8 characters long!")
            error = True
        #checking to see if user is in the database
        find_user = 'SELECT * from users'

        if error == True:
            return redirect('/')    
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    password = md5.new(request.form['password']).hexdigest()
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
    # We'll then create a dictionary of data from the POST data received.
    data = {
             'first_name': request.form['first_name'],
             'last_name':  request.form['last_name'],
             'email': request.form['email'],
             'password': password
           }
    # Run query, with dictionary values injected into the query.
    mysql.query_db(query, data)
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    password = request.form['password']
    user_query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
    query_data = {'email': request.form['email']}
    user = mysql.query_db(user_query, query_data)
    if len(user) != 0:
        encrypted_password = md5.new(password).hexdigest()
    if user[0]['password'] == encrypted_password:
        return redirect('/wall')
    else:
        flash('invalid login')
        return redirect ('/')
    
@app.route('/wall')
def success():
    if request.method =='POST':
        if request.form['submit']== 'add_message':
            query = "INSERT INTO messages (message, created_at, updated_at) VALUES (:message, NOW(), NOW())"
            data = {
                'message': request.form['message']
            }
            mysql.query_db(query, data)
            return redirect ('/wall')
        if request.form['submit']== 'add_comment':
            query = "INSERT INTO comment (comment, created_at, updated_at) VALUES (:comment, NOW(), NOW())"
            data = {
                'comment': request.form['comment']
            }
            mysql.query_db(query, data)
            return redirect ('/wall')



    return render_template('the_wall.html')


@app.route('/logout')
def logout():
   pass 
#    clr session
app.run(debug=True)