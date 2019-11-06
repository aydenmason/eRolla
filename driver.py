from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")
    
@app.route("/search")
def about():
    return render_template("search.html")
    
if __name__ == "__main__":
    app.run(debug=True)