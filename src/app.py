from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from dominate.tags import img, span

from flask import send_file, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

import time
import os
import sys
from datetime import timedelta

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
MIME_TYPE = { 'txt' : 'text/plane', 
              'pdf' : 'application/pdf', 
              'png' : 'image/png', 
              'jpg' : 'image/jpg', 
              'jpeg': 'image/jpg', 
              'gif' : 'image/gif',
            }

if sys.platform == 'linux': home_dir = r"/home/pi/www"
else: home_dir = r"D:\Temp"

#
# Menu
#

logo = img(src='./static/img/logo.png', height="32", width="32", style="margin-top:-4px")
title = span(logo," Simple File Server")
topbar = Navbar( 
    View( title, 'home'),
    View('Download', 'home'),
    Subgroup('Admin',
        View('Register', 'register'),
        View('User', 'user'),
    ),
    Subgroup( "Help", 
        View('Pagination', 'pagination'),
        View('About', 'about'),
    )
)

nav = Nav()
nav.register_element('top', topbar)

app = Flask(__name__)
db = SQLAlchemy(app)
Bootstrap(app)

@app.route('/about', methods=["GET"])
def about():
    return(render_template('about.html'))

#
# File List
#

        
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_mime_type(filename):
    if '.' in filename:
        return MIME_TYPE.get(filename.rsplit('.', 1)[1])

def strip_root(filename):
    if len(filename) == 0: return ""
    else: return filename[1:] if filename[0] == '/' else filename

def sort_file_list(files,sort_by="name",sort_order=0):
    def sort_key(item):
        if sort_by == 'name': return(item[0])
        if sort_by == 'size': return(item[1])
        if sort_by == 'date': return(item[2])
        return (item[0])
    if files is not None:
        files = sorted( files, key=sort_key )
        if sort_order: files.reverse()
    return files
    
def send_list_directory(file_path,sort_by="name", sort_order=0):
    dirs  = []
    files = []
    abs_path = os.path.abspath(os.path.join(home_dir,file_path))
    if len(file_path) > 0:
        if file_path[0] != '/':  file_path = "/" + file_path
        if file_path[-1] != '/': file_path = file_path + "/"
    else:
        file_path = "/"
    for f in os.listdir( abs_path ):
        full_name = os.path.join( abs_path, f )
        size = os.path.getsize( full_name )
        date = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime( full_name )))
        if os.path.isdir(full_name): dirs.append( (f, size, date) )
        else: files.append( (f, size, date) )
    if dirs and len(dirs) > 1: dirs  = sort_file_list(dirs, sort_by, sort_order)
    if files and len(files) > 1: files = sort_file_list(files, sort_by, sort_order)
    if file_path != "/": dirs.insert( 0, ("..", 0, "") ) 
    if session['admin']:
        return render_template("browser.html", folder=file_path, dirs=dirs, files=files, sort_order=sort_order)
    else:
        return render_template("download.html", folder=file_path, dirs=dirs, files=files, sort_order=sort_order)


@app.route('/', methods=['GET'])
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return send_list_directory("")

@app.route('/user', methods=['GET'])
def user():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if session['admin']:
            users = User.query.all() 
            return render_template('user.html', users=users)
        else: return redirect(url_for('home'))

@app.route('/download', methods=['GET'])
def download():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        filePath = request.args.get('path')
        filePath = "" if filePath is None else strip_root(filePath)
        fullPath = os.path.abspath(os.path.join( home_dir, filePath ))
        print( 'download()', fullPath, home_dir, filePath )
        filePath = fullPath[ len(home_dir)+1: ]
        if os.path.isdir(fullPath):
            sort_by    = request.args.get('sort_by')
            sort_order = request.args.get('sort_order')
            sort_order = 0 if sort_order is None else 1 - int(sort_order)
            return send_list_directory(filePath, sort_by, sort_order )
        else:
            mime_type = get_mime_type(fullPath)
            if mime_type:
                return send_file(fullPath, mimetype=mime_type)
            else:
                return send_file(fullPath, as_attachment=True)

@app.route('/upload', methods=['POST'])
def Upload():
    if not session.get('logged_in'):
        return render_template('login.html')
    file = request.files['file']
    folder = strip_root(request.form['folder'])
    if file: # and allowed_file(file.filename):
        file.save(os.path.join( home_dir, folder, file.filename))
    return send_list_directory(folder)

@app.route('/create', methods=['POST'])
def Create():
    if not session.get('logged_in'):
        return render_template('login.html')
    new_folder = strip_root(request.form['new_folder'])
    folder = strip_root(request.form['folder'])
    full_path = os.path.join( home_dir, folder, new_folder )
    print('create()', full_path )
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return send_list_directory(folder)

@app.route('/delete', methods=['GET'])
def Delete():
    if not session.get('logged_in'):
        return render_template('login.html')
    file = strip_root(request.args['file'])
    folder = strip_root(os.path.dirname(file))
    full_path = os.path.join( home_dir, file)
    if os.path.isdir(full_path):
        if len(os.listdir(full_path)) == 0:
            os.rmdir(full_path)
    elif os.path.isfile(full_path):
        os.remove(full_path)
    else:
        print(f"permission error : delete {full_path}")
    return send_list_directory(folder)

@app.route('/image/<image>', methods=['GET'])
def File(image):
    full_path = os.path.join(app.instance_path, 'image', image)
    return send_file(full_path)


#
# SESSION
#

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Integer)
    def __init__(self, username, password, admin):
        self.username = username
        self.password = password
        self.admin    = admin

def create_user(username,password,admin=0):
    new_user = User(username=username, password=password, admin=admin)
    db.session.add(new_user)
    db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not session.get('logged_in'):
        if request.method == 'GET':
            return render_template('login.html')
        username = request.form['username']
        password = request.form['password']
        print( '/login', username, password )
        try:
            data = User.query.filter_by(username=username, password=password).first()
            if data is not None:
                session['logged_in'] = True
                session['username'] = username
                session['admin'] = data.admin
                return redirect(url_for('home'))
            else:
                return render_template('login.html', message="Login Fail [1] !")
        except:
            return  render_template('login.html', message="Login Fail [2] !")
    else:
        return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if not session.get('logged_in'):
        return render_template('login.html')
    if not session.get('admin'):
        return render_template('login.html') 
    if request.method == 'POST':
        admin = 1 if request.form.get("admin") else 0
        new_user = User(username=request.form['username'], password=request.form['password'], admin=admin)
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('register.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))

#
# Pagination
#


class Item():
    def __init__(self,i):
        self.name = "black" + str(i)
        self.created_at = str(i*1000)

class Pages():
    def __init__(self):
        pass
        
class Items():
    def __init__(self,num_items):
        self.items = [ Item(i) for i in range(num_items) ]
        self.num_items = num_items
    def get_items(self,page,num_items,num_pages):
        page = page - 1
        start_page = int(page / num_pages) * num_pages
        last_page  = start_page + num_pages
        max_page   = int(self.num_items / num_items) + ( 1 if self.num_items % num_items != 0 else 0 )
        #print( 'get_items()', start_page, last_page, max_page )
        if last_page > max_page: last_page = max_page
        items = self.items[ page*num_items : (page+1)*num_items ]
        pages = Pages()
        pages.pages = [ p for p in range(start_page+1,last_page+1) ]
        pages.curr_page = page + 1
        pages.prev_page = start_page if start_page > 1 else 1
        pages.next_page = last_page + 1 if last_page < max_page else max_page
        pages.last_page = max_page + 1
        return items, pages
        

list_items = Items(94)

@app.route('/pagination')
def pagination():
    global list_items
    page = request.args.get('page', 1, type=int)
    items, pages = list_items.get_items(page,10,5)
    return render_template('pagination.html', items=items, pages=pages)


#
# Application
#

if __name__ == '__main__':
    #app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30) 
    app.config["SECRET_KEY"] = "abcd" #app.secret_key = "3123"
    db.create_all()
    nav.init_app(app)
    app.run(debug=True, host="0.0.0.0", port=8000) #, ssl_context='adhoc')
