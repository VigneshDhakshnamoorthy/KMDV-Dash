from wtforms import PasswordField, SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class SignupForm(FlaskForm):
    
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )

    projects = SelectMultipleField('Select Projects')
    submit = SubmitField("Sign Up")
    
    def set_projects_choices(self, choices):
        self.projects.choices = choices
    
