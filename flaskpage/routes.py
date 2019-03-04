from flask import render_template, url_for, flash, redirect, request, abort, make_response, render_template_string, session, Response
from flaskpage import app, db
from flaskpage.forms import RegistrationForm, LoginForm, PostForm
from flaskpage.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_table import Table, Col
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_principal import Principal, Permission, RoleNeed
import datetime
from datetime import timedelta

principals = Principal(app)
admin_permission = Permission(RoleNeed('admin'))

admin = Admin(app, name='Flask Blog', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))

@app.route("/admin")
@admin_permission.require()
def admin():
	return Response('Only accessible by admin')


@app.route("/")
@app.route("/home")
def home():
	posts = Post.query.all()
	return render_template('home.html', posts=posts)

@app.route('/query')
def query():
	person = {'name':"", 'secret':"secret_string9812309841"}
	if request.args.get('name'):
		person['name'] = request.args.get('name')
	return render_template('query.html', person=person)

@app.route("/about")
def about():
	return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, password=form.password.data, email=form.email.data)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and (form.password.data == user.password):
			login_user(user, remember=form.remember.data)
			session.permanent = True
			app.permanent_session_lifetime = timedelta(seconds=30)
			return redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
	logout_user()
	session.pop('email', None)
	return redirect(url_for('home'))

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post',
						   form=form, legend='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Your post has been updated!', 'success')
		return redirect(url_for('post', post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title='Update Post',
						   form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(url_for('home'))
