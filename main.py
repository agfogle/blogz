from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:testblog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app) 

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.Text(120)) 
    body = db.Column(db.Text(250)) 
    
    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog')
def blogs():
    if request.args:
        post_id = request.args.get('id')
        single_post = Blog.query.get(post_id)
        return render_template('single_post.html',blog=single_post)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['GET','POST'])
def new_post():
    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog = Blog(blog_title,blog_body)

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
            
        else:
            return render_template('newpost.html', blog_title=blog_title, title_error=title_error, blog_body=blog_body, body_error=body_error)



if __name__ =='__main__':
    app.run()