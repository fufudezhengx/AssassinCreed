from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email',validators = [Required(),Length(1,64),Email()])
    
    password = PasswordField('Password',validators = [Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
    
class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    
    username = StringField('Username',validators=[Required(),Length(1,64),
                                        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters, ''numbers, dots or underscores')])
                                        
    password = PasswordField('Password',validators=[Required(),EqualTo('password2',message='Password must match')])
    password2 = PasswordField('Confirm password',validators=[Required()])
    submit = SubmitField('Register')
    
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered!')
            
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already used')
            
class ChangePasswordForm(FlaskForm):
    old_password    = PasswordField('Old password',validators=[Required()])
    new_password = PasswordField('Password',validators=[Required(),EqualTo('new_password2',message='Password must match')])
    new_password2 = PasswordField('Confirm password',validators=[Required()])

    submit = SubmitField('Change Password')
 
class RequestResetPasswordForm(FlaskForm):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    submit = SubmitField('Reset')
    
class ResetPasswordForm(FlaskForm):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('Password',validators=[Required(),EqualTo('password2',message='Password must match')])
    password2 = PasswordField('Confirm password',validators=[Required()])
    submit = SubmitField('Reset')
    
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unregistered email address!')
            
class RequestChangEmailForm(FlaskForm):
    email = StringField('New Email Address',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('password',validators=[Required()])
    submit = SubmitField('Change')
    
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('Registered email address!')