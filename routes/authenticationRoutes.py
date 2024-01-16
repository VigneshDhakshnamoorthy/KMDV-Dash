from sqlite3 import IntegrityError
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
import pandas as pd
from database.forms import LoginForm, SignupForm
from database.models import User, db
from routes.enumLinks import FileAssociate
from asyncio import to_thread


AuthenticationPage = Blueprint(
    "AuthenticationPage", __name__, template_folder="templates"
)


@AuthenticationPage.route("/login", methods=["GET", "POST"])
async def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = await to_thread(
            User.query.filter_by,
            email=form.email.data,
            password=form.password.data,
        )
        user = user.first()
        if user:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Login unsuccessful. Please check your email and password.", "danger")

    return render_template("accounts/login.html", form=form)


@AuthenticationPage.route("/signup", methods=["GET", "POST"])
async def signup():
    # if current_user.is_authenticated:
    #         return redirect(url_for('index'))
    choices = FileAssociate.keys()

    form = SignupForm()
    form.set_projects_choices([(project, project) for project in choices])

    if form.password.data != form.confirm_password.data:
        flash(
            "Password and confirm password do not match. Please try again.",
            "danger",
        )
        return redirect(url_for("AuthenticationPage.signup"))
    if form.validate_on_submit():
        existing_user = await to_thread(User.query.filter_by, email=form.email.data)
        existing_user = existing_user.first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("AuthenticationPage.signup"))

        try:
            new_user = User(
                email=form.email.data,
                password=form.password.data,
                projects=form.projects.data,
                user_type=form.user_type.data,
            )
            db.session.add(new_user)
            db.session.commit()

            flash("Your account has been created! You can now log in.", "success")
            return redirect(url_for("AuthenticationPage.login"))

        except IntegrityError:
            db.session.rollback()
            flash(
                "An error occurred while creating your account. Please try again.",
                "danger",
            )
            return redirect(url_for("AuthenticationPage.signup"))

    return render_template("accounts/signup.html", form=form)


@AuthenticationPage.route("/logout")
@login_required
async def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("AuthenticationPage.login"))
