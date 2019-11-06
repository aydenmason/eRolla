from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'god' or request.form['password'] != 'god':
            error = 'Username or password not recognized. Try Again'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route("/")
def home():
    return render_template("home.html")
    
@app.route("/search")
def about():
    return render_template("search.html")
    
if __name__ == "__main__":
    app.run(debug=True)