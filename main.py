#!/usr/bin/env python3
import os
import random
import pickle
from base64 import b64decode,b64encode
from binascii import hexlify, unhexlify
from os import popen
from lxml import etree
import html
from Crypto.Cipher import AES
from Crypto import Random
import argparse
import sys
import sqlite3, hashlib

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, jsonify, g, flash, redirect, url_for, session, request, make_response, render_template_string,render_template



DATABASE_NAME = 'game'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/game"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or \
    'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'


db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())

# Main index
@app.route('/')
def index():
    return render_template("main.html")

#XXE needs more development
@app.route('/xxe', methods = ['POST', 'GET'])
def xml():
    parsed_xml = None
    if request.method == 'POST':
        xml = request.form['xml']
        parser = etree.XMLParser(no_network=False, dtd_validation=False, load_dtd=True, huge_tree=True)
        #try:
        doc = etree.fromstring(xml.encode(), parser)
        parsed_xml = etree.tostring(doc).decode('utf8')
        #except:
            #pass
    return render_template('xxe.html',parsed_xml=parsed_xml)




@app.route('/BrokenAuth', methods = [ 'GET'])
def iss():
    return render_template("BrokenAuth.html")
  
@app.route('/ssti', methods = ['POST', 'GET'])
def ssti():
   name = ''
   if request.method == 'POST':
      name = 'From %s' %(request.form['name'])

   template = """
   <html>
    <head>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <link rel="stylesheet" href="/static/style2.css">
        
    </head>
    <body class="w-100">
       
      <div class="signin w-30" style="background-color: white;">
         <form class="text-center" action="/ssti" method="POST">
             <img class="w-30" src="/static/images/farewell.jpg">
             <h5 id="sign" class="text-dark mt-4 font-weight-bold" > %s</h5>
             <h3 class="mt-5 text-dark">Sign the Farewell Card</h3>
             <h3 class="mt-3 text-dark">Your Name</h3>
             <input type="text" class="mt-3 mx-auto text-dark w-100" name="name"  >
             <button class="btn w-100">Submit</button>
         </form>
      </div>
    
    </body>
</html>
   """ %(name)
   return render_template_string(template)


@app.errorhandler(404)
def pnf(e):
    template = '''<html>
    <head>
    <title>Error</title>
    </head>
    <body>
    <h1>Oops that page doesn't exist!!</h1>
    <h3>%s</h3>
    </body>
    </html>
    ''' % request.url

    return render_template_string(template, dir = dir, help = help, locals = locals),404


@app.route('/guess_home')
def guess_home():
    # the "answer" value cannot be stored in the user session as done below
    # since the session is sent to the client in a cookie that is not encrypted!
    session['OTP'] = random.randint(10000, 99999)
    return redirect(url_for('guess'))

@app.route('/guess')
def guess():
    guess = int(request.args['guess']) if 'guess' in request.args else None
    print(guess, session['answer'])
    if request.args.get('guess'):
        if guess == session['answer']:
            return render_template('win.html')
        else:
            session['try_number'] += 1
            if session['try_number'] > 3:
                return render_template('lose.html', guess=guess)
    return render_template('guess.html', try_number=session['try_number'],
                           guess=guess)


@app.route('/cookie_home')
def cookie_home():
    if 'super-member' not in session:
        session['super-member'] = False

    if session['super-member']:
        return render_template('logged-in.html')
    else:
        return render_template('not-user.html')


@app.route('/1', methods=['GET', 'POST'])
def login1():
    if request.method == 'POST':
        uname, pword = (request.form['username'],request.form['password'])
        result = db.engine.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" %(uname,pword))
        if result.fetchone():
            return redirect('/2')
        else:
            result = {'status': 'fail'}
        return jsonify(result)
        
    return render_template('login1.html')

@app.route('/2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        uname, pword = (request.form['username'],request.form['password'])
        for letter in uname:
            if letter in ['=', '<', '>']:
                flash('''The following characters are banned: =, >, <''')
                return render_template('login2.html')
        for letter in pword:
            if letter in ['=', '<', '>']:
                flash('''The following characters are banned: =, >, <''')
                return render_template('login2.html')
        
        result = db.engine.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" %(uname,pword))
        if result.fetchone():
            return redirect('/3')
        else:
            result = {'status': 'fail'}
        return jsonify(result)
        
    return render_template('login2.html')

@app.route('/3', methods=['GET', 'POST'])
def login3():
    if request.method == 'POST':
        uname, pword = (request.form['username'],request.form['password'])
        for letter in uname:
            if letter in ['--', '/*']:
                flash('''The following characters are banned: --, /*''')
                return render_template('login3.html')
        for letter in pword:
            if letter in ['--', '/*']:
                flash('''The following characters are banned: --, /*''')
                return render_template('login3.html')
        
        result = db.engine.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" %(uname,pword))
        if result.fetchone():
            return redirect('/4')
        else:
            result = {'status': 'fail'}
        return jsonify(result)
        
    return render_template('login3.html')


@app.route('/4', methods=['GET', 'POST'])
def login4():
    if request.method == 'POST':
        uname, pword = (request.form['username'],request.form['password'])
        for letter in uname:
            if letter in ['OR']:
                flash('''The following characters are banned: OR''')
                return render_template('login4.html')
        for letter in pword:
            if letter in ['OR']:
                flash('''The following characters are banned: OR''')
                return render_template('login4.html')
        
        result = db.engine.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" %(uname,pword))
        if result.fetchone():
            return redirect('/5')
        else:
            result = {'status': 'fail'}
        return jsonify(result)
        
    return render_template('login4.html')




@app.route('/5', methods=['GET', 'POST'])
def login5():
    if request.method == 'POST':
        uname, pword = (request.form['username'],request.form['password'])
        for letter in uname:
            if letter in ['Admin', 'OR']:
                flash('''The following characters are banned: Admin, OR''')
                return render_template('login5.html')
        for letter in pword:
            if letter in ['Admin', 'OR']:
                flash('''The following characters are banned: Admin, OR''')
                return render_template('login5.html')
        
        result = db.engine.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" %(uname,pword))
        if result.fetchone():
            return redirect('/6')
        else:
            result = {'status': 'fail'}
        return jsonify(result)
        
    return render_template('login5.html')





@app.route('/6', methods=['GET', 'POST'])
def login6():
    if request.method == 'POST':
        uname, pword = (request.form['username'],request.form['password'])
        for letter in uname:
            if letter in ['UNION', 'Admin', 'OR']:
                flash('''The following characters are banned: UNION, Admin, OR''')
                return render_template('login6.html')
        for letter in pword:
            if letter in ['UNION', 'Admin', 'OR']:
                flash('''The following characters are banned: UNION, Admin, OR''')
                return render_template('login6.html')
        
        result = db.engine.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" %(uname,pword))
        if result.fetchone():
            return redirect('/7')
        else:
            result = {'status': 'fail'}
        return jsonify(result)
        
    return render_template('login6.html')



@app.route('/7', methods=['GET', 'POST'])
def login7():
    if request.method == 'POST':
        uname, pword = (request.form['username'],request.form['password'])
        for letter in uname:
            if letter in ['']:
                flash('''The following characters are banned: Whitespaces''')
                return render_template('login7.html')
        for letter in pword:
            if letter in ['']:
                flash('''The following characters are banned: Whitespaces''')
                return render_template('login7.html')
        
        result = db.engine.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" %(uname,pword))
        if result.fetchone():
            return redirect('/8')
        else:
            result = {'status': 'fail'}
        return jsonify(result)
        
    return render_template('login7.html')


@app.route('/8', methods=['GET', 'POST'])
def login8():
    if request.method == 'POST':
        uname, pword = (request.form['username'],request.form['password'])
        for letter in uname:
            if letter in ["'", '`']:
                flash('''The following characters are banned: ' , `''')
                return render_template('login8.html')
        for letter in pword:
            if letter in ["'", "`"]:
                flash("The following characters are banned: ', `")
                return render_template('login8.html')
        
        result = db.engine.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" %(uname,pword))
        if result.fetchone():
            result = {'status': 'success'}
        else:
            result = {'status': 'fail'}
        return jsonify(result)
        
    return render_template('login8.html')

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, help='Listen port. Default: 4000', default=4000)
    parser.add_argument('-a', '--address', type=str, help='Listen address. Default: 127.0.0.1', default='127.0.0.1')
    parser.add_argument('-d', help='Debug level', action="count", default=0)
    parser.add_argument('--database_type', help='Database type. Default: postgres', default='postgres', choices=['postgres'])
    parser.add_argument('--database_user', type=str, help='Database username. Default: None', default='postgres')
    parser.add_argument('--database_password', type=str, help='Database username.  Default: None', default='postgres')
    parser.add_argument('--database_host', type=str, help='Database hostname. Default: None', default='127.0.0.1')
    parser.add_argument('--database_port', type=int, help='Database port. Default: 5432', default=5432)
    # parser.add_argument('--database_filename', type=str, help='Database filename (sqlite only). Default: :memory:', default=':memory:')
    # parser.add_argument('--oracle_lib_dir', type=str, help='Location of Oracle client libraries, needed for Oracle database connectivity', default='/opt/local/lib/oracle')


    args = parser.parse_args()

    
    if args.database_type == 'postgres':
        import psycopg2 as dbmodule
        def autocommit(x):
            x.autocommit = True
        list_databases_query = 'SELECT datname FROM pg_database;'
        list_tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
 

    try:
        if args.database_type not in ['sqlite', 'oracle']:
            connection_params = {a.replace('database_', ''): getattr(args, a) for a in dir(args) if a in ['database_user', 'database_host', 'database_password', 'database_port']}
            connection = dbmodule.connect(**connection_params)
            autocommit(connection)
            cursor = connection.cursor()
            cursor.execute(list_databases_query)
            r = [a[0] for a in cursor.fetchall() if a[0] == DATABASE_NAME]
            if not r: # create database if it doesnt exist
                cursor.execute("CREATE DATABASE {};".format(DATABASE_NAME))
            cursor.close()
            connection.close()
            connection_params['database'] = DATABASE_NAME
            connection = dbmodule.connect(**connection_params) # reconnect in new database context
            autocommit(connection)
       
        else: # shouldnt happen
            print('Invalid database type selected: {}'.format(args.database_type))
            sys.exit(1)

        cursor = connection.cursor()
        cursor.execute(list_tables_query)
        existing_tables = [a[0].lower() for a in cursor.fetchall()]
        
    except Exception as e:
        print('An error ocured during database connection/setup: {}'.format(e))
        sys.exit(1)
    
    app.run(host=args.address, port=args.port)
