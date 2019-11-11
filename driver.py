from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='project123!'
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_DB'] ='project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords dont match')
    ])
    confirm = PasswordField('Confirm Your Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data        
        password = form.password.data
        name = form.name.data
        email = form.email.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(username, password, name, email) VALUES(%s, %s, %s, %s)", (username, password, name, email))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', title ="Register", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
      username = request.form['username']
      password_to_test = request.form['password']
      
      current = mysql.connection.cursor()

      res = current.execute("SELECT * FROM users WHERE username = %s", [username])
      data = current.fetchone()
      pw = data['password']

      if password_to_test == pw:
        flash('You are now logged in', 'success')
        return redirect(url_for('home'))
      else:
        error = 'This Login is not valid'
        return render_template('login.html', error = error)
      current.close()
    else:
      error = 'Username is not detected'
      return render_template('login.html', error=error)

    return render_template('login.html')

@app.route("/home")
def home():
    return render_template("home.html")
    
@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/listing")
def listing():
  return render_template("listing.html")

@app.route("/shipping")
def shipping():
  return render_template("shipping.html")

@app.route("/DOA")
def DOA():
  return render_template("DOA.html")

@app.route("/about")
def about():
  return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)