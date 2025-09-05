from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FileField, SelectMultipleField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired
from flask_ckeditor import CKEditorField

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

class EditorForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    tags = StringField('Tags (comma separated)')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    tags = SelectMultipleField('Tags', coerce=int)

class TagForm(FlaskForm):
    name = StringField("Tag name", validators=[DataRequired()])

class ImageUploadForm(FlaskForm):
    file = FileField("Image", validators=[FileRequired()])
    alt_text = StringField("Alt text")
    tags = SelectMultipleField("Tags", coerce=int)