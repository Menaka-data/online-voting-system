from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="menaka22",
    database="voting_system"
)

cursor = db.cursor(dictionary=True)

# REGISTER
@app.route('/', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            flash("Username already exists!", "error")
            return redirect('/')

        cursor.execute("INSERT INTO users (username,password) VALUES (%s,%s)", (username,password))
        db.commit()

        flash("Registered successfully!", "success")
        return redirect('/login')

    return render_template('register.html')


# LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect('/admin')

        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s",(username,password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['has_voted'] = user['has_voted']
            return redirect('/dashboard')
        else:
            flash("Invalid login!", "error")

    return render_template('login.html')


# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    return render_template('dashboard.html', candidates=candidates, voted=session.get('has_voted'))


# VOTE
@app.route('/vote/<int:id>')
def vote(id):
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('has_voted'):
        flash("You already voted!", "info")
        return redirect('/dashboard')

    cursor.execute("UPDATE candidates SET votes=votes+1 WHERE id=%s",(id,))
    cursor.execute("UPDATE users SET has_voted=TRUE WHERE id=%s",(session['user_id'],))
    db.commit()

    session['has_voted'] = True
    flash("Vote successful!", "success")

    return redirect('/dashboard')


# ADMIN
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')

    cursor.execute("SELECT * FROM candidates")
    data = cursor.fetchall()

    return render_template('admin.html', data=data)


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)