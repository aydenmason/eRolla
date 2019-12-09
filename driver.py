#imports
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, FloatField, BooleanField, IntegerField
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import datetime, timedelta, date

#creating the application
app = Flask(__name__)

list_o_items = list()
size = 0

#configure the app to be able to interact with mySQL server
app.secret_key = "super secret key"
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='project123!'
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_DB'] ='project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)



class RegisterForm(Form):
    fname = StringField('Name', [validators.Length(min=1, max=50)])
    lname = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords dont match')
    ])

    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data        
        password = form.password.data
        fname = form.fname.data
        lname = form.lname.data
        email = form.email.data
        dob = form.dob.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO user(username, password, fname, lname, email, dob) VALUES(%s, %s, %s, %s, %s, %s)", (username, password, fname, lname, email, dob))

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
      return render_template('login.html', error=error)

    return render_template('login.html')

@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/search', methods = ['GET', 'POST'])
def search():
    if request.method == 'POST':
      itemName = request.form['name']
      
      current = mysql.connection.cursor()

      res = current.execute("SELECT * FROM item WHERE name = %s", [itemName])
      data = current.fetchall()
      current.close()
      return render_template("items.html", data=data)

    return render_template('search.html')

class ListingForm(Form):
    itemID = StringField('Item ID', [validators.Length(min=1, max=50)])
    itemPrice = FloatField('Price')
    itemColor = StringField('Color',[validators.Length(min=3,max=20)])
    itemRating = FloatField('Rating')
    seller = StringField('Seller',[validators.Length(min=4, max = 40)])
    itemName = StringField('Item Name',[validators.Length(min=4,max=40)])
    shippingAddress = StringField('Shipping Address', [validators.Length(min=5, max=100)])
    
    

@app.route("/listing", methods=['GET', 'POST'])
def listing():
  form = ListingForm(request.form)
  if request.method == 'POST' and form.validate():
    seller = form.seller.data
    itemID = form.itemID.data
    itemPrice = form.itemPrice.data
    itemName = form.itemName.data
    itemColor = form.itemColor.data
    itemRating = form.itemRating.data
    shippingAddress = form.shippingAddress.data
    been_sold = 0
    #create the cursor to guide the insertion
    cur = mysql.connection.cursor()

    #add to the table
    cur.execute("INSERT INTO item(seller_user,itemid,price,color,rating,name,Been_purchased) VALUES(%s,%s,%s,%s,%s,%s,%s)", (seller,itemID,itemPrice,itemColor,itemRating,itemName,been_sold))
    # Commit to DB
    mysql.connection.commit()
    # Close connection
    cur.close()
    flash('item has been added to eRolla', 'success')
  return render_template("listing.html",form=form)

@app.route("/items", methods=['GET', 'POST'])
def items():
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM item")
  data = cur.fetchall()
  cur.execute("SELECT AVG(price) FROM item")
  avgPrice = cur.fetchone()
  cur.execute("SELECT SUM(price) FROM item")
  sumPrice = cur.fetchone()
  cur.execute("SELECT MIN(price) FROM item")
  minPrice = cur.fetchone()
  cur.execute("SELECT MAX(price) FROM item")
  maxPrice = cur.fetchone()
#cur.execute("SELECT MIN(price) FROM item")
#minPrice = cur.fetchall()
#cur.execute("SELECT MAX(price) FROM item")
#maxPrice = cur.fetchall()
  cur.close()
  return render_template("items.html", data=data, price=round(avgPrice['AVG(price)']), sum=round(sumPrice['SUM(price)']), min=round(minPrice['MIN(price)']), max=round(maxPrice['MAX(price)']))
#also pass min=minPrice, max=maxPrice
@app.route("/delete", methods=['GET','POST'])
def delete():
  if request.method == 'POST':
      itemID = request.form['itemid']
      
      current = mysql.connection.cursor()
      res = current.execute("DELETE FROM item WHERE itemid = %s", [itemID])

      data = current.fetchone()
      mysql.connection.commit()
      current.close()
      flash("Item Deleted!", 'success')
     
  return render_template("delete.html")

class modifyForm(Form):
  itemID = StringField('Item ID', [validators.Length(min=1, max=50)])
  itemPrice = FloatField('Price')
  itemColor = StringField('Color',[validators.Length(min=3,max=20)])
  itemRating = FloatField('Rating')
  itemName = StringField('Item Name',[validators.Length(min=4,max=40)])      


@app.route("/modify", methods=['GET', 'POST'])
def modify():
   form = modifyForm(request.form)
   if request.method == 'POST':
      itemID = form.itemID.data
      itemPrice = form.itemPrice.data
      itemName = form.itemName.data
      itemColor = form.itemColor.data
      itemRating = form.itemRating.data
      current = mysql.connection.cursor()

      res = current.execute("SELECT * FROM item WHERE itemid = %s", [itemID])
      mysql.connection.commit()
      data = current.fetchall()


      current.close()
   

   return render_template("modify2.html", form=form)
#not used yet
@app.route("/shipping")
def shipping():
  return render_template("shipping.html")
#not used yet
@app.route("/DOA")
def DOA():
  return render_template("DOA.html")

@app.route("/about")
def about():
  return render_template("about.html")
class purchaseForm(Form):
    itemID = StringField('Item ID', [validators.Length(min=1, max=50)])
    buyer = StringField('Buyer',[validators.Length(min=1, max=20)])
    depState = StringField('Departing State', [validators.Length(min=1,max=20)])
    depCity = StringField('Departing City', [validators.Length(min=1,max=20)])
    depZip = StringField('Departing Zip', [validators.Length(min=1,max=20)])       
    depStreet = StringField('Departing Street', [validators.Length(min=1,max=20)])
    arrCity = StringField('Arrival City', [validators.Length(min=1,max=20)])
    arrState = StringField('Arrival State', [validators.Length(min=1,max=20)])
    arrZip = StringField('Arrival Zip', [validators.Length(min=1,max=20)])
    arrStreet = StringField('Arrival Street', [validators.Length(min=1,max=20)])
  
@app.route("/purchase", methods=['GET','POST'])
def purchase():
  form = purchaseForm(request.form)
  if request.method == 'POST' and form.validate():
    itemID = form.itemID.data
    buyer = form.buyer.data
    depStreet = form.depStreet.data
    depState = form.depState.data
    depCity = form.depCity.data
    depZip = form.depZip.data
    arrStreet = form.arrStreet.data
    arrState = form.arrState.data
    arrCity = form.arrCity.data
    arrZip = form.arrZip.data
    depDate = date.today()
    arrDate = date.today() + timedelta(days=2)
    shippingCost = 0
    #create the cursor to guide the insertion
    
    cur = mysql.connection.cursor()

    #add to the table
    cur.execute("INSERT INTO purchases(item_id,buyer,dep_st,dep_city,dep_state,dep_zip,arr_st,arr_city,arr_state,arr_zip,dep_date,arr_date,ship_cost) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(itemID,buyer,depStreet,depCity,depState,depZip,arrStreet,arrCity,arrState,arrZip,depDate,arrDate,shippingCost))
    # Commit to DB
    mysql.connection.commit()
    # Close connection
    cur.close()
    flash('Item Has been ORDERED!', 'success')
    
  return render_template("purchase.html", form=form)
#main functions
if __name__ == "__main__":
    app.run(debug=True)
