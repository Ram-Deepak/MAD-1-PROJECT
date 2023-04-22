from flask_security import LoginForm, RegisterForm
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from application.models import User

class RegisterForm(FlaskForm):
    first_name = StringField("First Name",
        validators=[InputRequired()], render_kw={'placeholder':'First name'})
    last_name = StringField("Last Name", render_kw={'placeholder':'Last name'})
    email = StringField("Email",
        validators=[InputRequired(), Email()], render_kw={'placeholder':'Email'})
    username = StringField("Username",
        validators=[InputRequired(), Length(min=4, max=20)], render_kw={'placeholder':'username'})
    password = PasswordField("Password",
        validators=[InputRequired(), Length(min=4, max=20)], render_kw={'placeholder':'password'})
    submit = SubmitField('Register')

    def isUsernameValid(self, username):
        record = User.query.filter_by(username=username.data).first()
        if record:
            raise ValidationError('Username already exists. Please enter new username')

class LoginForm(FlaskForm):
    username = StringField("Username",
        validators=[InputRequired(), Length(min=4, max=20)], render_kw={'placeholder':'username'})
    password = PasswordField("Password",
        validators=[InputRequired(), Length(min=4, max=20)], render_kw={'placeholder':'password'})
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField("Title", 
                        validators=[InputRequired()], render_kw={'placeholder':'Title'})
    description = TextAreaField("Description",
                        validators=[InputRequired()], render_kw={'placeholder':'Description'})
    photo = FileField(validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Post')

class UpdatePostForm(FlaskForm):
    title = StringField("Title", render_kw={'placeholder':'Title'})
    description = TextAreaField("Description", render_kw={'placeholder':'Description'})
    photo = FileField(validators=[FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField('Update')

class UpdateInfoForm(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    submit = SubmitField('Update')