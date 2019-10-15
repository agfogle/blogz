from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:myblogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key="lmnop%$#@!" 

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.Text(120)) 
    body = db.Column(db.Text(250))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/blog')
def blogs():
    if request.args:
        post_id = request.args.get('id')
        single_post = Blog.query.get(post_id)
        return render_template('single_post.html',blog=single_post)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username)

        username_error = ''
        password_error = ''
        

        if user and User.password == password:
            session['username'] = username
            return redirect('/newpost')

        elif user == username and password != User.password:
            password_error="Password is incorrect"

        elif username not in user:
            username_error = "Username does not exist"
        
        return render_template('login.html', username=username, username_error=username_error, password_error=password_error)

@app.route('/newpost', methods=['GET','POST'])
def new_post():
    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        blog_owner = User.query.filter_by(session=username)
        new_blog = Blog(blog_title,blog_body,blog_owner)

        title_error = ''
        body_error = ''

        if blog_title == "":
            title_error = "This field can not be blank"
        elif blog_body == "":
            body_error = "This field can not be blank"

        if not title_error and not body_error:
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog.id))
            
        
        return render_template('newpost.html', blog_title=blog_title, title_error=title_error, blog_body=blog_body, body_error=body_error)


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        verify_error = ''
        password_error =''
        username_error = ''
        

        if " " in username:
            username_error = "username can not include spaces"
            return render_template('signup.html', username_error=username_error)
        elif len(username) < 3:
            username_error = "Must be greater than 3 characters"
            return render_template('signup.html', username_error=username_error)


        if " " in password:
            password_error = "Password can not include spaces"
            return render_template('signup.html', password_error=password_error)
        elif len(password) < 3:
            password_error = "Must be greater than 3 characters"  
            return render_template('signup.html', password_error=password_error)  
           

        if not verify == password:
            verify_error = "Passwords must match"
            return render_template('signup.html', verify_error=verify_error)
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            username_error = "Username already exists"
            return render_template('signup.html', username=username, username_error=username_error)
    
    else:
        return render_template('signup.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    blog_owners = User.query.all()
    return render_template('index.html', User=blog_owners)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ =='__main__':
    app.run()