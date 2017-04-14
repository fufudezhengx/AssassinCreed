from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm
from .. import db
from ..models import Role, User, Permission
from ..decorators import admin_required, permission_required
from flask_login import login_required,current_user

@main.route('/',methods=['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['know'] = False
            if app.config['FLASK_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
        else:
            session['know'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('main.index'))
    return render_template('index.html',current_time=datetime.utcnow(),
                            name=session.get('name'),form=form,know=session.get('know',False))      

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
    return render_template('user_profile.html',user=user)

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
