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
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/blog', methods=['GET','POST'])
def blogs():

    if request.method =='GET':
        
        postID = request.args.get('id')
        if postID:
            single_post = Blog.query.get(postID)
            return render_template('single_post.html',blog=single_post)
        
        userID = request.args.get('userID')
        if userID:
            blogger_posts = Blog.query.filter_by(owner_id=userID).all()
            blog_owner = User.query.filter_by(id=userID).first()
            return render_template('singleuser.html', posts=blogger_posts, user=blog_owner)

    
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        
        username_error=''
        password_error=''
        
        user = User.query.filter_by(username=username).first()
        if not user:
            username_error="User does not exist"
            return render_template('login.html', username=username, username_error=username_error)
        if user and not password == user.password:
            password_error="Password is incorrect"
            return render_template('login.html', username=username,password_error=password_error)
        else:
            session['username']=username
            return redirect('newpost')

    else:
        return render_template('login.html')



@app.route('/newpost', methods=['GET','POST'])
def new_post():
    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        blog_owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(blog_title,blog_body,blog_owner)

        title_error = ''
        body_error = ''

        if blog_title == "":
            title_error = "This field can not be blank"
            return render_template('newpost.html', blog_title=blog_title, title_error=title_error, blog_body=blog_body, body_error=body_error)
        elif blog_body == "":
            body_error = "This field can not be blank"
            return render_template('newpost.html', blog_title=blog_title, title_error=title_error, blog_body=blog_body, body_error=body_error)
        
        elif not title_error and not body_error:
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog.id))
            
        
        

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
    if request.args:
        blogger_posts = Blog.query.filter_by(owner_id=id).all()
        return render_template('blog.html', blog=blogger_posts)

    blog_owners = User.query.all()
    return render_template('index.html', User=blog_owners)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ =='__main__':
    app.run()