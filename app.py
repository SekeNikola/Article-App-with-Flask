from flask import Flask, render_template, redirect, request, url_for, session, logging, flash
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
#Articles = Articles()

#Conifure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'newuser'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'flaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


# Init MySQL
mysql = MySQL(app)

# Home
@app.route('/')
def index():
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute('SELECT * FROM articles')

    articles = cur.fetchall()

    if result > 0:
        return render_template('home.html', articles=articles)
    else:
        msg = 'No articles found'
        return render_template('home.html', msg=msg)

    # Close connection
    cur.close()
    return render_template('home.html')

# About
@app.route('/about')
def about():
   return render_template('about.html')

# Articles
@app.route('/articles')
def articles():#Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute('SELECT * FROM articles')

    articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No articles found'
        return render_template('articles.html', msg=msg)

    # Close connection
    cur.close()

    return render_template('articles.html', articles = articles)

#Single Article
@app.route('/article/<string:id>/')
def article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()

    return render_template('article.html', article=article)

# Users
@app.route('/users')
def users():
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM users;")

    users = cur.fetchall()

    cur.close()

    return render_template('users.html', users = users)

# Register
class RegisterForm(Form):
    name = StringField('Name', validators=[validators.input_required(), validators.Length(min=1, max=50)])
    username = StringField('Username', validators=[validators.input_required(), validators.Length(min=4, max=25)])
    email = StringField('Email', validators=[validators.input_required(), validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match')
    ])
    confirm = PasswordField('Confirm Password')


# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('signup'))
    return render_template('signup.html', form=form)

# Sign in
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        #Get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user
        result = cur.execute('SELECT * FROM users WHERE username = %s', [username])
        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('signin.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Wrong password or username'
            return render_template('signin.html', error=error)

    return render_template('signin.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please signin', 'danger')
            return redirect(url_for('signin'))
    return wrap

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():

    #Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute('SELECT * from articles')

    articles =  cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No articles found'
        return render_template('dashboard.html', msg=msg)

    # Close connection
    cur.close()

# Article form
class ArticleForm(Form):
    title = StringField('Title', validators=[ validators.Length(min=1, max=200)])
    body = TextAreaField('Body', validators=[ validators.Length(min=30)])

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)

# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()
    cur.close()
    # Get form
    form = ArticleForm(request.form)

    # Populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(title)
        # Execute
        cur.execute ("UPDATE articles SET title=%s, body=%s WHERE id=%s",(title, body, id))
        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)

# Delete article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute cursor
    cur.execute('DELETE from articles WHERE id = %s', [id])

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('Article Deleted' 'success')
    return redirect(url_for('dashboard'))

# Signout
@app.route('/signout')
@is_logged_in
def signout():
   session.clear()
   flash('You are now signed out', 'success')
   return redirect(url_for('signin'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run()