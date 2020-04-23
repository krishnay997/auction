from flask import Flask,Blueprint, render_template,redirect,request,url_for,flash,session
from models import User
from werkzeug.security import check_password_hash
from flask_login import login_user,logout_user,login_required

session_blueprint = Blueprint('session',
                            __name__,
                            template_folder='templates')



@session_blueprint.route("/")
def new():
    return render_template("session/new.html")

@session_blueprint.route("/verify", methods=["POST"])
def create():
    username=request.form.get("username")
    password=request.form.get("password")
    user=User.get_or_none(User.username==username)

    if user and check_password_hash(user.password,password):
        flash(f"Welcome back {user.username}","success")
        login_user(user)
        return redirect(url_for("home"))

    else:
        flash("Unable to log in :(", "warning")
        return redirect(url_for("home"))

@session_blueprint.route("/logout", methods=["POST"])
@login_required
def destroy():
    flash("Log out successful","success")
    logout_user()
    return redirect(url_for("home"))

