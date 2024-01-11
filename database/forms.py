from wtforms import (
    EmailField,
    PasswordField,
    RadioField,
    SelectMultipleField,
    SubmitField,
)
from wtforms.validators import DataRequired, EqualTo, Email
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class SignupForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )

    projects = SelectMultipleField("Select Projects")

    user_type = RadioField(
        "User Type",
        choices=[("admin", "Admin"), ("master", "Master"), ("normal", "Normal")]
    )

    submit = SubmitField("Sign Up")

    def set_projects_choices(self, choices):
        self.projects.choices = choices
