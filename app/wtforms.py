from wtforms import BooleanField, StringField, PasswordField, EmailField, SelectField, FileField, TextAreaField
from wtforms.validators import Length, InputRequired, Optional
from flask_wtf import FlaskForm

class RegistrationForm(FlaskForm):
    username = StringField('Username',[Length(min=4, max=35), InputRequired()])
    password = PasswordField('Password',[Length(min=6, max=35), InputRequired()])
    confirm = PasswordField('Confirm password', [Length(min=6, max=35), InputRequired()])
    accept_rules = BooleanField('I accept the site rules',[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username',[Length(min=4, max=25), InputRequired()])
    password = PasswordField('Password',[Length(min=6, max=35), InputRequired()])

class InfoForm(FlaskForm):
    twitter_username = StringField("Twitter Username", [Length(min=2, max=100), InputRequired()])
    demographic = SelectField("Demographic", choices=[("","Select"), ("asian","Asian"), ("black","Black"), ("white","White"), ("aa","African American")])
    first_language = SelectField("First language", choices=[("","Select"), ("zh","Chinese - 中文"), ("es","Spanish - español"), ("en","English"), ("hi","Hindi - हिन्दी"), ("ar","Arabic - العربية"), ("pt","Portuguese - português"), ("bn","Bengali - বাংলা"), ("ru","Russian - русский"), ("ja","Japanese - 日本語"), ("pa","Punjabi - ਪੰਜਾਬੀ<")])
    gender = SelectField("Gender", choices=[("","Select"), ("male","Male"), ("female","Female"), ("other","Other"), ("n/a","Do not with to response")])
    work_status = SelectField("Current work status", choices=[("","Select"), ("student","Student"), ("employed","Employed"),("self-employed","Self-employed"), ("unemployed","Unemployed")])
    email = EmailField("Email address", [Length(min=4, max=100), InputRequired()])
    number = StringField("Mobile number", [Length(min=7, max=15), InputRequired()])

class ViewForm(FlaskForm):
    post_content = TextAreaField("",[Length(min=4, max=500), Optional()])
    post_image = FileField("", [InputRequired()])
    post_anonymously = BooleanField("Post anonymously", [Optional()])

class RegisterForm(FlaskForm):
    register_name = StringField("Full Name", [Length(min=2, max=100), InputRequired()])
    cost = StringField("Fee per hour", [Length(min=1, max=10), InputRequired()])
    language_preferred = SelectField("Language preferred", choices=[("","Select"), ("zh","Chinese - 中文"), ("es","Spanish - español"), ("en","English"), ("hi","Hindi - हिन्दी"), ("ar","Arabic - العربية"), ("pt","Portuguese - português"), ("bn","Bengali - বাংলা"), ("ru","Russian - русский"), ("ja","Japanese - 日本語"), ("pa","Punjabi - ਪੰਜਾਬੀ<")])
    register_gender = SelectField("Gender", choices=[("","Select"), ("male","Male"), ("female","Female"), ("other","Other"), ("n/a","Do not with to response")])
    work_experience = StringField("Current work status", [Length(min=2, max=5000), InputRequired()])
    register_email = EmailField("Email address", [Length(min=4, max=100), InputRequired()])
    register_number = StringField("Mobile number", [Length(min=7, max=15), InputRequired()])
    register_image = FileField("Add your profile picture here", [InputRequired()])