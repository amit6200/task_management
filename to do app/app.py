from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt  # For password hashing
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Amit@1215'
app.config['MYSQL_DB'] = 'task_management_db'

mysql = MySQL(app)

# Route: Home (Login page)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user and sha256_crypt.verify(password, user['password']):
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect username or password!', 'danger')
    
    return render_template('login.html')

# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = sha256_crypt.encrypt(str(request.form['password']))
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        mysql.connection.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Route: Dashboard (Task list)
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tasks WHERE user_id = %s', (session['id'],))
        tasks = cursor.fetchall()
        return render_template('dashboard.html', tasks=tasks)
    else:
        return redirect(url_for('login'))

# Route: Add Task
@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if 'loggedin' in session:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO tasks (title, description, user_id) VALUES (%s, %s, %s)',
                           (title, description, session['id']))
            mysql.connection.commit()
            flash('Task added successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('add_task.html')
    else:
        return redirect(url_for('login'))

# Route: Update Task
@app.route('/update_task/<int:id>', methods=['GET', 'POST'])
def update_task(id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tasks WHERE id = %s AND user_id = %s', (id, session['id']))
        task = cursor.fetchone()

        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            cursor.execute('UPDATE tasks SET title = %s, description = %s WHERE id = %s AND user_id = %s',
                           (title, description, id, session['id']))
            mysql.connection.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('update.html',task=task)
    else:
        return redirect(url_for('login'))

# Route: Delete Task
@app.route('/delete_task/<int:id>', methods=['GET', 'POST'])
def delete_task(id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tasks WHERE id = %s AND user_id = %s', (id, session['id']))
        task = cursor.fetchone()

        if request.method == 'POST':
            cursor.execute('DELETE FROM tasks WHERE id = %s AND user_id = %s', (id, session['id']))
            mysql.connection.commit()
            flash('Task deleted successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('delete.html', task=task)
    else:
        return redirect(url_for('login'))


# Route: Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
