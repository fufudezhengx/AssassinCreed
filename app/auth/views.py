from flask import render_template,redirect,request,url_for,flash
from . import auth
from .forms import LoginForm,RegistrationForm,ChangePasswordForm,ResetPasswordForm,RequestResetPasswordForm,RequestChangEmailForm
from ..models import User
from flask_login import login_user,logout_user,login_required,current_user
from .. import db
from ..email import send_email

@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html',form=form)
    
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
    
@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,
                            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,'Confirm You Count','auth/email/confirm',user=user,token=token)
        flash('A confirmation email has been sent to your email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)
    
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account.Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))
    
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
          and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))
        
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
    
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
                        'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))
    
@auth.route('/change_password',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash('Your password has been changed!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid Password')
    return render_template('auth/change_password.html',form=form)
    
@auth.route('/request_reset_password',methods=['GET','POST'])
def request_reset_password():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_confirmation_token()
            send_email(user.email, 'Reset Your Password',
                            'auth/email/reset_password', user=user, token=token)
            flash('An email with instructions to reset your password has been '
                      'sent to you.')
            return redirect(url_for('auth.login'))
        else:
            flash('This email has not register yet.')
    return render_template('auth/request_reset_password.html',form=form)

@auth.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.confirm(token):
            user.password = form.password.data
            db.session.add(user)
            flash('Your password has been reset')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid email')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)
    
@auth.route('/requeset_change_email',methods=['GET','POST'])
@login_required
def request_change_email():
    form = RequestChangEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            token = current_user.generate_new_email_confirmation_token(form.email.data)
            send_email(form.email.data, 'Change Your Email Address',
                                'auth/email/change_email', user=current_user, token=token)
            flash('An email with instructions to change your email has been '
                          'sent to you.')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or password')
    return render_template('auth/request_change_email.html',form=form)
    
@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.confirm_new_email(token):
        flash('You have change your email')
        logout_user()
        return redirect(url_for('auth.login'))
    flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('/auth.requeset_change_email'))