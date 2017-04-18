from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash
from . import main
from .forms import PostForm,EditProfileForm,EditProfileAdminForm
from .. import db
from ..models import Role, User, Post,Permission
from ..decorators import admin_required, permission_required
from flask_login import login_required,current_user

@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
       form.validate_on_submit():
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash('You have submit the post')
        return redirect(url_for('main.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html',form=form,posts=posts,current_time=datetime.utcnow())


@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return "For administrators!"

@main.route('/user_profile/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user_profile.html',user=user,posts=posts)

@main.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.name.data :
            current_user.name = form.name.data
        if form.location.data :
            current_user.location = form.location.data
        if form.about_me.data :
            current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile have been updated')
        return redirect(url_for('main.user_profile',username=current_user.username))
    return render_template('edit_profile.html',form=form)

@main.route('/edit_profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        if form.email.data :
            user.email = form.email.data
        if form.username.data :
            user.username = form.username.data
        if form.confirmed.data :
            user.confirmed = form.confirmed.data
        if form.role.data :
            user.role = Role.query.get(form.role.data)
        if form.name.data :
            user.name = form.name.data
        if form.email.data :
            user.email = form.email.data
        if form.location.data :
            user.location = form.location.data
        if form.about_me.data :
            user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('You have been updated the user profile')
        return redirect(url_for('main.user_profile',username=user.username))
    return render_template('edit_profile_admin.html',form=form,user=user)
