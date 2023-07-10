"""Blogly application."""

from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'somesecret'

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

#APP ROUTE FOR BLOGLY HOMEPAGE
@app.route('/')
def homepage():
    """Render homepage of recent posts"""
    posts=Post.query.order_by(Post.created_at.desc()).limit(5).all()
    users = [post.user for post in posts]
    return render_template('posts/homepage.html', posts=posts, users=users)

@app.route('/posts/<int:post_id>', methods=['GET'])
def show_feed_post(post_id):
    """Display post with corresponding post id"""
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.user_id)
    return render_template('posts/show.html', post=post, user=user)


#APP ROUTES FOR BLOGLY USERS

@app.route('/users')
def all_users():
    """Display all Blogly users"""
    users = User.query.all()
    return render_template('users/index.html', users=users)

@app.route('/users/new', methods=["GET"])
def new_users_form():
    """Display form for creating new user"""
    return render_template('users/new.html')


@app.route("/users/new", methods=["POST"])
def add_new_users():
    """Handle new user form submission"""
    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Render user specific info"""

    user = User.query.get_or_404(user_id)
    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    """Show a form to edit an existing user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def update_users(user_id):
    """Handle existing user profile update via form submission"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_users(user_id):
    """Handle deleting a user via form submission"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")


#APP ROUTES FOR BLOGLY POSTS
@app.route('/users/<int:user_id>/posts/new', methods=["GET"])
def post_form(user_id):
    """Render form template for adding new posts"""
    get_user = User.query.get_or_404(user_id)
    return render_template('posts/new.html', user=get_user)


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def handle_post(user_id):
    """Handle post submission form, update posts, and redirect to user detail page"""
    user = User.query.get_or_404(user_id)
    new_post = Post(title=request.form['title'],
                    content=request.form['content'],
                    user_id=user.id)
    
    db.session.add(new_post)
    db.session.commit()
    
    return redirect(f"/users/{user_id}")


@app.route('/users/posts/<int:post_id>', methods=['GET'])
def show_post(post_id):
    """Display post with corresponding post id"""
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.user_id)
    return render_template('posts/show.html', post=post, user=user)


@app.route('/posts/<int:post_id>/edit', methods=['GET'])
def edit_post_form(post_id):
    """Render form template for editing existing posts"""
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.user_id)
    return render_template('posts/edit.html', post=post, user=user)


@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def handle_edit_post(post_id):
    """Handle post edit form submission, update post, and redirect to post display"""
    post = Post.query.get_or_404(post_id)

    post.title = request.form['title']
    post.content = request.form['content']

    db.session.commit()

    return redirect(f"/users/{post.user_id}")


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Delete post with corresponding post id"""
    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{post.user_id}")