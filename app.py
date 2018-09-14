from flask import Flask, render_template, redirect, request, url_for, session, logging, flash
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)
Articles = Articles()

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
   return render_template('home.html')

# About
@app.route('/about')
def about():
   return render_template('about.html')

# Articles
@app.route('/articles')
def articles():
   return render_template('articles.html', articles = Articles)

# Article
@app.route('/article/<string:id>/')
def article(id):
   return render_template('article.html', id=id)

# Articles
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

if __name__ == '__main__':
    app.secret_key='secret123'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run()