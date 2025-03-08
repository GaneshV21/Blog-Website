from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash,request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text,ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm,RegisterForm,LoginForm,CommentForm
from typing import List
import os

'''
Make sure the required packages are installed:
Open the Terminal in PyCharm (bottom left).

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CONFIGURE TABLES

# TODO: Create a User table for all your registered users.
class User(UserMixin,db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(100))
    posts: Mapped["BlogPost"] = relationship(back_populates="author")
    comments: Mapped["Comment"] = relationship(back_populates="comment_author")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped["User"] = relationship(back_populates="posts")
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    comments: Mapped["Comment"] = relationship(back_populates="parent_post")


class Comment(UserMixin,db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    comment_author: Mapped["User"] = relationship(back_populates="comments")
    parent_post: Mapped["BlogPost"] = relationship(back_populates="comments")
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    post_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))

with app.app_context():
    db.create_all()

@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts,authenticated=current_user.is_authenticated)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function
# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register',methods=['POST','GET'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        hash_password = generate_password_hash(password, method='pbkdf2:sha256',salt_length=8)
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        user = User(email=email,password=hash_password,name=name)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html",form=form,authenticated=current_user.is_authenticated)


# TODO: Retrieve a user from the database based on their email.
@app.route('/login',methods=['POST','GET'])
def login():
    form = LoginForm()
    if request.method =='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_get = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user_get:
            if check_password_hash(user_get.password, password):
                login_user(user_get)
                return redirect(url_for('get_all_posts'))
            else:
                flash('Password incorrect,please try again.')
                return render_template("login.html", form=form,authenticated=current_user.is_authenticated)
        else:
            flash('That email does not exist,please try again.')
            return render_template("login.html", form=form,authenticated=current_user.is_authenticated)

    return render_template("login.html",form=form,authenticated=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))



# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>",methods=['POST', 'GET'])
def show_post(post_id):
    form = CommentForm()
    login_form = LoginForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    comments = db.session.execute(db.select(Comment).where(Comment.post_id == requested_post.id)).scalars()
    gravatar = Gravatar(app,
                        size=100,
                        rating='g',
                        default='retro',
                        force_default=False,
                        force_lower=False,
                        use_ssl=False,
                        base_url=None)
    if request.method == 'POST':
        if current_user.is_authenticated:
            text = form.comment.data
            comment = Comment(text=text, post_id=requested_post.id, author_id=current_user.id)
            db.session.add(comment)
            db.session.commit()
            return redirect(f'/post/{post_id}')

        else:
            flash('You need to login or register to comment.')
            return render_template("login.html", form=login_form, authenticated=current_user.is_authenticated)

    return render_template("post.html", post=requested_post,authenticated=current_user.is_authenticated,form=form,comments=comments,gravatar=gravatar)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form,authenticated=current_user.is_authenticated)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id,authenticated=current_user.is_authenticated))
    return render_template("make-post.html", form=edit_form, is_edit=True,authenticated=current_user.is_authenticated)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html",authenticated=current_user.is_authenticated)


@app.route("/contact")
def contact():
    return render_template("contact.html",authenticated=current_user.is_authenticated)

if __name__ == "__main__":
    app.run(debug=True, port=5002)

