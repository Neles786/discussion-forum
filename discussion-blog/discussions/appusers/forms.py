from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from discussions.models import Users

class SignupForm(FlaskForm):
    name = StringField('Name')
    username = StringField('Username', validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField('Email', validators=[DataRequired(), Email("This field requires a valid email address")])
    mobileno = StringField('Mobile', validators=[DataRequired(), Length(min=10,max=10)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username) -> bool:
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken, please choose a different one')
    
    def validate_mobileno(self, mobileno) -> bool:
        valid = True
        dl = [str(d) for d in range(10)]
        for d in mobileno.data:
            if d not in dl:
                valid = False
                break
        user = None
        if valid:
            user = Users.query.filter_by(mobileno=mobileno.data).first()
        if (not valid):
            raise ValidationError('Mobile Number contains invalid characters')
        if user:
            raise ValidationError('Mobile Number already exists, please choose a different one')
    
    def validate_email(self, email) -> bool:
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email Already exists, please choose other email ids')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email("This field requires a valid email address")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    name = StringField('Name')
    username = StringField('Username', validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField('Email', validators=[DataRequired(), Email("This field requires a valid email address")])
    mobileno = StringField('Mobile', validators=[DataRequired(), Length(min=10,max=10)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','jpeg','gif','bmp','tiff','tif','png','svg'])])
    submit = SubmitField('Update')

    def validate_username(self, username) -> bool:
        if username.data != current_user.username:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken, please choose a different one')
            
    def validate_mobileno(self, mobileno) -> bool:
        valid = True
        dl = [str(d) for d in range(10)]
        for d in mobileno.data:
            if d not in dl:
                valid = False
                break

        if (not valid):
            raise ValidationError('Mobile Number contains invalid characters')
        if mobileno.data != current_user.mobileno:
            user = Users.query.filter_by(mobileno=mobileno.data).first()
            if user:
                raise ValidationError('Mobile Number already exists, please choose a different one')
    
    def validate_email(self, email) -> bool:
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email Already exists, please choose other email ids')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email("This field requires a valid email address")])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email) -> bool:
        user = Users.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Email does not exists, do signup first!')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=5)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Reset Password')