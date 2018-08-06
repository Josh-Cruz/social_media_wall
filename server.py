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
    

        if error == True:
            return redirect('/')    
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    password = md5.new(request.form['password']).hexdigest()
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
    data = {
             'first_name': request.form['first_name'],
             'last_name':  request.form['last_name'],
             'email': request.form['email'],
             'password': password
           }
    mysql.query_db(query, data)
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    password = request.form['password']
    user_query = "select * from users where users.email = :email LIMIT 1;"
    query_data = {'email': request.form['email']}
    user = mysql.query_db(user_query, query_data)
    session['user'] = user
    session['name'] = user[0]['first_name'] + " " + user[0]['last_name']
    session['user_id']= user[0]['id']
    if len(user) != 0:
        encrypted_password = md5.new(password).hexdigest()
    if user[0]['password'] == encrypted_password:
        return redirect('/wall')
    else:
        flash('invalid login')
        return redirect ('/')
        
@app.route('/posts/create', methods=['POST'])
def create_post():
  if len(request.form['content']) < 2:
    flash('post must be at least 2 characters')
    return redirect('/wall')

  post_query = 'INSERT INTO messages (message, user_id, created_at, updated_at) VALUES (:content, :user_id, NOW(), NOW())'
  data = {
    'content': request.form['content'],
    'user_id': session['user_id']
  }
  mysql.query_db(post_query, data)
  return redirect('/wall')

@app.route('/comments/create/<message_id>', methods=['POST'])
def create_comment(post_id):
  if len(request.form['content']) < 2:
    flash('comment must be at least 2 characters')
    return redirect('/')

  comment_query = 'INSERT INTO comments (comment, user_id, message_id, created_at, updated_at) VALUES (:content, :user_id, :post_id, NOW(), NOW())'
  data = {
    'content': request.form['content'],
    'user_id': session['user_id'],
    'post_id': message_id
  }
  mysql.query_db(comment_query, data)
  return redirect('/wall')
    
@app.route('/wall', methods=['POST', 'GET'])
def wall():
  if not 'user_id' in session:
    return redirect('/')

  post_query = 'SELECT users.first_name AS first, users.last_name AS last, messages.message AS content, messages.created_at AS created_at, messages.id AS id FROM messages JOIN users ON users.id = messages.user_id'
  messages = mysql.query_db(post_query)

  comment_query = 'SELECT comments.comment AS content, comments.message_id AS post_id, users.first_name AS first, users.last_name AS last, comments.created_at AS created_at FROM comments JOIN users ON users.id = comments.user_id'
  comments = mysql.query_db(comment_query)

  data = {
    'title': 'The Wall',
    'posts': messages,
    'comments': comments
  }
  return render_template('the_wall.html', data=data)



@app.route('/logout')
def logout():
   session.clear()
   return redirect('/')

   
app.run(debug=True)