from flask import Flask ,render_template, request, url_for , session , redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime 
import re 
#import flask_login


app = Flask(__name__)

app.secret_key = '1234'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '0000'
app.config['MYSQL_DB'] = 'data'

mysql = MySQL(app)

        

@app.route('/')
def index2():
    return render_template('index2.html')
    
@app.route('/signup', methods=['GET','POST'])
def signup():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        user = cursor.fetchone()
        if user:
            mesage = 'user already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('/signup.html', mesage = mesage)

@app.route('/login', methods=['GET','POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Logged in successfully !'
            return render_template('index2.html', mesage = mesage)
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)

        
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))
    
   
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/card')
def card():
    if 'loggedin' in session:
        email = session['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM cards WHERE email = %s", (email,))
        cards = cursor.fetchall() 
        if not cards:
            message = "No cards found!!! Please add a card..."
            return render_template("card.html", cards=cards, message=message)
        return render_template("card.html", cards=cards) 
    return redirect(url_for('login'))

@app.route('/delete', methods=['POST'])
def delete():
    if 'loggedin' in session:
        cardnumber = request.form['cardnumber']
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM cards WHERE cardnumber = %s", (cardnumber,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('card'))
    return redirect(url_for('login'))


@app.route('/value', methods=['GET','POST'])
def value():
    if 'loggedin' in session:
        if request.method == 'POST':
            cardnumber = request.form['cardnumber']
            amount = request.form['amount']
            # Perform card recharge logic here
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT amount FROM cards WHERE cardnumber = %s", (cardnumber,))
            result = cursor.fetchone()
            if result:
                    current_amount = result['amount']
                    updated_amount = current_amount + int(amount)
                    cursor.execute("UPDATE cards SET amount = %s WHERE cardnumber = %s", (updated_amount, cardnumber))
                    mysql.connection.commit()
                    message = f"Card {cardnumber} recharged with {amount}. Updated balance: {updated_amount}"
            else:
                message = "Invalid amount for the card."
                cursor.close()
            return render_template("value.html",message=message)
        else:
            message = "fill the form"

        return render_template("value.html")
    return redirect(url_for('login'))


@app.route('/balance', methods=['GET', 'POST'])
def balance():
    message = ""
    if 'loggedin' in session:
        email = session['email']
        #cardnumber = request.form['cardnumber']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM cards WHERE email = %s", (email,))
        #cursor.execute("SELECT * FROM cards WHERE cardnumber = %s", (cardnumber,))
        cards = cursor.fetchall()
        if not cards:
            message = "No cards found!!! Please add a card..."
        return render_template("balance.html", cards=cards, message=message)
    return redirect(url_for('login'))

@app.route('/balancecheck', methods=['GET', 'POST'])
def balancecheck():
    message = ""

    if request.method == 'POST':
        if 'cardnumber' in request.form:
            cardnumber = request.form['cardnumber']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM cards WHERE cardnumber = %s", (cardnumber,))
            cards = cursor.fetchall()
            return render_template("balancecheck.html", message=message,cards=cards)
        else:
            message = "Please enter a card number."

    return render_template("balancecheck.html")



@app.route('/cardhistory')
def cardhistory():
    if 'loggedin' in session:
        return render_template('cardhistory.html')
    return redirect(url_for('login'))

@app.route('/addcard', methods=['GET','POST'])
def addcard():
    if 'loggedin' in session:
        mesage = ''
        if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'cardnumber' :
            name = request.form['name']
            email = request.form['email']
            cardnumber = request.form['cardnumber']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cards WHERE cardnumber = % s', (cardnumber, ))
            cards = cursor.fetchone()
            if cards:
                mesage = ' already exists !'
            #elif not re.match(r'[^@]+@[^@]+\.[^@]+',cardnumber ):
             #mesage = 'Invalid Cardnumber !'
            elif not name or not email or not cardnumber :
                mesage = 'Please fill out the form !'
            else:
                cursor.execute('INSERT INTO cards VALUES ( % s, % s, % s,50)', (name,email,cardnumber,))
                mysql.connection.commit()
                mesage = 'You have successfully registered !'
                return render_template('addcard.html')
        elif request.method == 'POST':
            mesage = 'Please fill out the form !'
        return render_template('addcard.html', mesage = mesage)
    return redirect(url_for('login'))

@app.route('/feedback', methods=['GET','POST'])
def feedback():
    if request.method == 'POST':
        email = request.form['email']
        text = request.form['text']
        # Retrieve feedback from the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT email, text FROM feedback WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            email = result['email']
            text = result['text']
        if email is not None:
            cursor.execute('INSERT INTO feedback VALUES ( % s, % s)', (email,text))
            result = cursor.fetchone()
            mysql.connection.commit()
    # Fetch all feedback from the database  
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
    cursor.execute("SELECT email, text FROM feedback")
    feedback = cursor.fetchall()

    return render_template('feedback.html',feedback=feedback)


@app.route('/farecheck')
def farecheck():
    return render_template('farecheck.html')

@app.route('/map')
def map():
    return render_template('map.html')



    
@app.route('/admin')
def admin():
     return render_template('admin.html')

@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
        message = ''
        if request.method == 'POST' and 'userid' in request.form and 'password' in request.form:
            userid = request.form['userid']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM admin WHERE userid = % s AND password = % s', (userid, password, ))
            user = cursor.fetchone()
            if user:
                session['loggedin'] = True
                session['name'] = user['name']
                session['userid'] = user['userid']
                session['password'] = user['password']
                mesage = 'Logged in successfully !'
                return redirect(url_for('adminuser', message = message))
            else:
                mesage = 'Please enter correct userid / password !'
        return render_template('adminlogin.html')

@app.route('/adminlogout')
def adminlogout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('admin'))

@app.route('/adminadd', methods=['GET','POST'])
def adminadd():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'userid' in request.form :
        name = request.form['name']
        userid = request.form['userid']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE userid = % s', (userid, ))
        user = cursor.fetchone()
        if user:
            mesage = 'user already exists !'
        #elif not re.match(r'[^@]+@[^@]+\.[^@]+', userid):
            #mesage = 'Invalid email address !'
        elif not name or not password or not userid:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO admin VALUES (% s, % s, % s)', (name, userid, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('/adminadd.html', mesage = mesage)

@app.route('/adminfeedback', methods=['GET','POST'])
def adminfeedback():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
        cursor.execute("SELECT email, text FROM feedback")
        feedback = cursor.fetchall()
        return render_template('adminfeedback.html',feedback=feedback)
    return redirect(url_for('adminlogin'))

@app.route('/admindelete', methods=['GET','POST'])
def admindelete():
    if request.method == 'POST' and 'email' in request.form :
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM feedback WHERE email = %s", (email,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('adminfeedback'))
    return render_template('/adminfeedback.html')


@app.route('/adminuser')
def adminuser():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
        cursor.execute("SELECT * FROM user")
        user = cursor.fetchall()
        cursor.execute("SELECT * FROM cards")
        cards = cursor.fetchall()
        return render_template('adminuser.html',user=user,cards=cards)
    return redirect(url_for('adminlogin'))

@app.route('/adminuserdelete', methods=['GET','POST'])
def adminuserdelete():
    if request.method == 'POST' and 'email' in request.form :
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM user WHERE email = %s", (email,))
        mysql.connection.commit()
        cursor.execute("DELETE FROM cards WHERE email = %s", (email,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('adminuser'))
    return render_template('/adminuser.html')




if __name__ == "__main__":
    app.run(debug=True)