from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Length

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    employee_number = StringField('employee_number', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])

class PunchForm(Form):
	notes = StringField('notes', validators=[DataRequired()])
	timestamp = DateTimeField('timestamp', format="%Y-%m-%d %H:%M")
