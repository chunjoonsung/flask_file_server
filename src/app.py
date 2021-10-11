from flask import Flask, render_template
from flask import send_file, url_for, request, redirect, session

import os
import sys
import time

import login as sql

base_dir = ""
home_dir = ""
page_show_num = 10
page_show_item = 25

if sys.platform == 'linux': base_dir = r"/home/pi/www2"
else: base_dir = r"D:\Temp"

app = Flask(__name__)

def prepare_request_process():
    global home_dir
    if session.get('logged_in'): home_dir = base_dir
    else: home_dir = os.path.join( base_dir, "pub" )

def strip_root(path):
    if len(path) == 0: return ""
    else: return path[1:] if path[0] == '/' else path

def get_path(path):
    rel_path = "" if not path else strip_root(path)
    abs_path = os.path.abspath(os.path.join( home_dir, rel_path ))
    rel_path = abs_path[ len(home_dir)+1: ]
    if len(rel_path) > 0:
        if rel_path[0] != '/':  rel_path = "/" + rel_path
        if rel_path[-1] != '/': rel_path = rel_path + "/"
    else:
        rel_path = "/"
    return rel_path, abs_path

def sort_dir_list( items, sort_by="name", sort_order=0 ):
    def sort_key_num_str(strItem):
        import re
        strList = re.split('(\d+)',strItem)
        strList = [x for x in strList if len(x) > 0]
        newList = []
        for s in strList:
            try: newList.append(int(s))
            except: newList.append(s)            
        return newList
    def sort_key(item):
        str_num_key = item.name if item.isdir else sort_key_num_str(item.name)
        if sort_order: #reverse
            if sort_by == 'name': return((item.isdir, str_num_key))
            if sort_by == 'size': return((item.isdir, item.size))
            if sort_by == 'date': return((item.isdir, item.date))
            return ((item.isdir, sort_key_num_str(item.name)))
        else:
            if sort_by == 'name': return((1-item.isdir, str_num_key))
            if sort_by == 'size': return((1-item.isdir, item.size))
            if sort_by == 'date': return((1-item.isdir, item.date))
            return ((1-item.isdir, sort_key_num_str(item.name)))
    if items:
        items = sorted( items, key=sort_key )
        if sort_order: items.reverse()
    return items
    
def get_dir_list( rel_path, abs_path, sort_by="name", sort_order=0 ):
    items = []
    count = [0,0]
    for f in os.listdir( abs_path ):
        full_name = os.path.join( abs_path, f )
        size = os.path.getsize( full_name )
        date = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime( full_name )))
        item = type("", (), {})()
        item.isdir = 1 if os.path.isdir(full_name) else 0
        item.name  = f
        item.size  = size        
        item.date  = date        
        items.append( item )
        if item.isdir: count[0] += 1 
        else: count[1] += 1
    items = sort_dir_list( items, sort_by, sort_order )
    if rel_path != "/": 
        item = type("", (), dict( isdir = 1, name = "..", size = 0, date = "") )()
        items.insert( 0, item ) 
    return items, count

def ItemList( all_items, num_items, curr_page ):
    return all_items[ curr_page*num_items : (curr_page+1)*num_items ]

def PageList( num_pages, num_items, curr_page, total_items ):
    start_page = int(curr_page / num_pages) * num_pages
    max_page   = int(total_items / num_items) + ( 1 if total_items % num_items != 0 else 0 )
    last_page  = start_page + num_pages 
    if last_page > max_page: last_page = max_page
    page = type("", (), {})()
    page.pages = [ p for p in range(start_page+1,last_page+1) ]
    page.curr_page = curr_page + 1
    page.prev_page = start_page if start_page > 1 else 1
    page.next_page = last_page + 1 if last_page < max_page else max_page
    page.last_page = max_page + 1
    return page

def get_flat_list( abs_path, sort_by="name", sort_order=0 ):
    items = []
    count = [0,0]
    for f in os.listdir( abs_path ):
        full_name = os.path.join( abs_path, f )
        size = os.path.getsize( full_name )
        date = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime( full_name )))
        if os.path.isdir(full_name):
            items.extend(get_flat_list( full_name, sort_by, sort_order ))
        else:
            item = type("", (), {})()
            item.isdir = 0
            item.name  = full_name[ len(home_dir)+1: ]
            item.size  = size        
            item.date  = date        
            items.append( item )
            if item.isdir: count[0] += 1 
            else: count[1] += 1
    items = sort_dir_list( items, sort_by, sort_order )
    return items, counts
    
def get_page_list(rel_path, abs_path, sort_by, sort_order, curr_page, num_pages, num_items):
    all_items, counts = get_dir_list(rel_path, abs_path, sort_by, sort_order)
    items = ItemList( all_items, num_items, curr_page-1 )
    pages = PageList( num_pages, num_items, curr_page-1, len(all_items) )
    return items, pages, counts
    
def get_list(rel_path, abs_path, sort_by, sort_order):
    all_items, counts = get_dir_list(rel_path, abs_path, sort_by, sort_order)
    return all_items, counts

def send_file_content(abs_path):
    import mimetype
    mime_type = mimetype.get_mime_type(abs_path)
    file_name = os.path.basename(abs_path)
    #return send_file(abs_path, as_attachment=True)
    if mime_type: 
        return send_file(abs_path, mimetype=mime_type)
    else: 
        return send_file(abs_path, attachment_filename=file_name, as_attachment=True)

def send_dir_content(*args, **kwargs):
    return render_template(*args, **kwargs)   
#
# url
#

@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('list'))

@app.route('/list', methods=['GET'])
def list():
    prepare_request_process()
    view_mode  = request.args.get('view_mode', session.get('view_mode'))
    curr_page  = request.args.get('page', 1, type=int)
    file_path  = request.args.get('path', "")
    sort_by    = request.args.get('sort_by',"name")
    sort_order = request.args.get('sort_order',0,type=int)
    
    if not session.get('view_mode'): session['view_mode'] = 'page'
    if view_mode: session['view_mode'] = view_mode
    session['sort_by'   ] = sort_by
    session['sort_order'] = sort_order
    
    print('list()', 'view_mode', view_mode, curr_page)
    
    sort = type("",(),dict(by=sort_by, order=sort_order))
    rel_path, abs_path = get_path(file_path)
    if os.path.isfile(abs_path):
        return send_file_content(abs_path)
    else:
        if not os.path.isdir(abs_path):
            rel_path, abs_path = get_path("")
        if view_mode == 'page':
            items, pages, counts = get_page_list(rel_path, abs_path, sort_by, sort_order, curr_page, page_show_num, page_show_item)
            return send_dir_content('list.html', folder=rel_path, sort=sort, items=items, pages=pages, counts=counts)    
        else:
            if view_mode == 'flat':
                items, counts = get_flat_list(abs_path, sort_by, sort_order)
            else:
                items, counts = get_list(rel_path, abs_path, sort_by, sort_order)
            return send_dir_content('list.html', folder=rel_path, sort=sort, items=items, pages=None, counts=counts)

@app.route('/upload', methods=['POST'])
def upload():
    prepare_request_process()
    if session.get('logged_in'):
        file = request.files['file']
        folder = strip_root(request.form['folder'])
        if file:
            file.save(os.path.join( home_dir, folder, file.filename))
    return redirect(url_for('list', path=folder))
    
@app.route('/create', methods=['POST'])
def create():
    prepare_request_process()
    if session.get('logged_in'):
        new_folder = strip_root(request.form['new_folder'])
        folder = strip_root(request.form['folder'])
        full_path = os.path.join( home_dir, folder, new_folder )
        if not os.path.exists(full_path):
            os.makedirs(full_path)
    return redirect(url_for('list', path=folder))

@app.route('/delete', methods=['GET'])
def delete():
    prepare_request_process()
    if session.get('logged_in'):
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
    return redirect(url_for('list', path=folder))

#
# Login
#

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('logged_in') and session.get('admin'):
        if request.method == 'GET':
            return render_template('register.html')
        username = request.form['username']
        password = request.form['password']
        if request.form.get('admin'): 
            admin = request.form['admin']
            print( admin, request.form['admin'], type(admin) )
        else: admin = 0
        sql.create_user(username,password,admin)
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not session.get('logged_in'):
        if request.method == 'GET':
            return render_template('login.html')
        username = request.form['username']
        password = request.form['password']
        admin = sql.query( username, password )
        if admin is not None:
            session['logged_in'] = True
            session['username'] = username
            session['admin'] = admin
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['username'] = None
    session['admin'] = None
    return redirect(url_for('home'))


#
# static files
#

@app.route('/css/<file>', methods=['GET'])
def file_css(file):
    full_path = os.path.join(app.instance_path, 'css', file)
    return send_file(full_path)

@app.route('/js/<file>', methods=['GET'])
def file_js(file):
    full_path = os.path.join(app.instance_path, 'js', file)
    return send_file(full_path)

@app.route('/image/<file>', methods=['GET'])
def file_image(file):
    full_path = os.path.join(app.instance_path, 'image', file)
    return send_file(full_path)

#
# app
#

if __name__ == '__main__':
    app.config["SECRET_KEY"] = "abcd" #app.secret_key = "3123"
    app.run(debug=False, host="0.0.0.0", port=8001) 
