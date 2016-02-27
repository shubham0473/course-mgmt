import json
from flask import Flask, make_response, request, url_for, jsonify, render_template, request, redirect, session
import MySQLdb
from flask.ext.httpauth import HTTPBasicAuth
import os
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from functools import wraps
from Models import db



UPLOAD_FOLDER = '/home/shubham/Desktop/web_development/tutplus/data/user_dp/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "shubham12345"
auth = HTTPBasicAuth()
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://13CS30030:cse12@10.5.18.68/13CS30030"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
with app.app_context():
    db.create_all()

def template_or_json(template=None):
    """"Return a dict from your view and this will either
    pass it to a template or render json. Use like:

    @template_or_json('template.html')

    """
    def decorated(f):
        @wraps(f)
        def decorated_fn(*args, **kwargs):
            ctx = f(*args, **kwargs)
            if request.is_xhr or not template:
                return jsonify(ctx)
            else:
                return render_template(template, **ctx)
        return decorated_fn
    return decorated

# @auth.get_password
# def get_password(username):
#     user = User.query.filter_by(name = username)
#     if not user:
#         return user.get(password)
#     else:
#         return None

# @auth.error_handler
# def unauthorized():
#     return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
#     # return 403 instead of 401 to prevent browsers from displaying the default auth dialog

# @app.errorhandler(400)
# def not_found(error):
#     return make_response(jsonify( { 'error': 'Bad request' } ), 400)

# @app.errorhandler(404)
# def not_found(error):
#     return make_response(jsonify( { 'error': 'Not found' } ), 404)


@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')






@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        json_data = request.get_json(force=True)
        if not json_data:
            print("error")
            return redirect(url_for('login'))
        email_ = json_data['email']
        pwd = json_data['password']

        user = User.query.filter_by(email = email_).first()

        if user and user.check_password(pwd):
            session['email'] = email_
            session['user_id'] = user.user_id
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('login'))
            # session['email'] = email

    if request.method == 'GET':
        return render_template('login.html')


@app.route('/signUp', methods = ['GET','POST'])
def add_user():
    if request.method == 'POST':
        json_data = request.get_json(force=True)

        if not json_data:
            print("error")
            return redirect(url_for('add_user'))
        name = json_data['name']
        email = json_data['email']
        pwd = json_data['password']
        link = "link"
        print json_data['photo']
        # file = request.files['file']
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
            #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     link = url_for('uploaded_file',filename=filename)
        # print link
        flag = json_data['flag']
        newuser = User(name, email, pwd, link, flag)
        db.session.add(newuser)
        db.session.commit()
        return redirect(url_for('profile'), 302)

    if request.method == 'GET':
        return render_template('signup.html')

@app.route('/parentPortal', methods = ['GET' , 'POST'])
def parentPortal():
    if request.method == 'POST' :
        json_data = request.get_json(force = True)
        if not json_data :
            print ("Error !! No credentials Given !! ")
            return redirect(url_for('parentPortal'))
        rollno = json_data['RollNo']
        dob = json_data['DOB']



# @view(app, '/profile', render_html('profile.html'))
# @view(app, '/profile', render_json)
@app.route('/profile', methods=['GET'])
@template_or_json('profile.html')
def profile():

    user = User.query.filter_by(email = (session['email'])).first()

    if user is None:
        return redirect(url_for('signup'))
    else:
        return { 'username' : user.name, 'link' : '/profile', 'dp_link': user.link_to_dp, 'flag' : user.type_flag }

@app.route('/logout')
def logout():

    if 'email' not in session:
        return redirect(url_for('login'))

    session.pop('email', None)
    return redirect(url_for('home'))
# @app.route('/user/<int:user_id>' methods = ['GET'])
# @auth.login_required
# def get_profile(user_id):


# API for searching a course
@app.route('/searchresults', methods = ['GET','POST'])
def search_course():
    if request.method == 'POST':
        json_data = request.get_json(force=True)
        if not json_data:
            print("error")
            return redirect(url_for('search_course'))
        cid = json_data['course_id']

        course = Course.query.filter_by(course_id = cid).first()

        if course:
            session['course_id'] = cid
            return redirect(url_for('course_home'))
        else:
            return redirect(url_for('search_course'))
            # session['email'] = email

    if request.method == 'GET':
        return render_template('student_home.html')


# API for enrolling a student in a course
@app.route('/enroll')
def enroll():
    newenroll = Enrolls(session['user_id'],session['course_id'])
    db.session.add(newenroll)
    db.session.commit()
    return redirect(url_for('course_home'), 302)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
