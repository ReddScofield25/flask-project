from flask import Flask, render_template, url_for, request, flash, current_app
from flaskext.mysql import MySQL
import pymysql
import json
import os

app = Flask(__name__)

app.secret_key = 'secret'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Passwordless'
app.config['MYSQL_DATABASE_DB'] = 'dictionary'

mysql = MySQL(app, cursorclass=pymysql.cursors.DictCursor)

@app.route('/', methods=['GET', 'POST'])
def index():
    user_response = ''
    if request.method == 'POST':
        user_input = request.form['word']
        if not user_input:
            flash('You did not enter a valid word, please try again', 'flash_error')
        else:
            conn = mysql.get_db()
            cur = conn.cursor()
            cur.execute("SELECT meaning FROM word WHERE word = %s", (user_input,))
            rv = cur.fetchall()
            user_response = rv[0]['meaning'] if rv \
                else 'The word cannot be found in this dictionary, please try again with another word'
    return render_template('index.html', user_response=user_response)

@app.route('/dashboard')
def dashboard():
    conn = mysql.get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM word")
    rv = cur.fetchall()
    
    return render_template('dashboard.html', words=rv)

@app.route('/word', methods=['POST'])
def add_word():
    req = request.get_json()
    word = req['word']
    meaning = req['meaning']
    
    if not word or not meaning:
        flash('Please fill in all fields, to add a new word', 'flash_error')
    else:
        conn = mysql.get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO word (word, meaning) VALUES (%s, %s)", (word, meaning))
        
        conn.commit()
        cur.close()

        flash('Word successfully added!', 'flash_success')

    return json.dumps('success')

@app.route('/word/<id>/delete', methods=['POST'])
def delete_word(id):
    conn = mysql.get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM word WHERE id = %s", (id,))

    conn.commit()
    cur.close()

    flash('Word successfully deleted!', 'flash_success')

    return json.dumps('success')

@app.route('/word/<id>/edit', methods=['POST'])
def edit_word(id):
    req = request.get_json()
    word = req['word']
    meaning = req['meaning']

    if not word or not meaning:
        flash('Please fill in all fields, to update a word', 'flash_error')
    else:
        conn = mysql.get_db()
        cur = conn.cursor()
        cur.execute("UPDATE word SET word = %s, meaning = %s WHERE id = %s", (word, meaning, id))

        conn.commit()
        cur.close()

        flash('Word successfully updated!', 'flash_success')

    return json.dumps('success')

@app.route('/add_logo', methods=['POST'])
def add_logo():
    image = request.files['file']

    if image:
        filepath = os.path.join(current_app.root_path, 'static/images/logo.png')
        image.save(filepath)
        flash('Success!', 'flash_success')
    else:
        flash('Error!','flash_error')
    
    return 'success'

@app.route('/<f_name>/<l_name>')
def greet(f_name, l_name):
    full_name = f'{f_name} {l_name}'
    return render_template('greetings.html', name=full_name)    

if __name__ == "__main__":
    app.run(debug=True)