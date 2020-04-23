from flask import Blueprint, render_template,redirect,request,url_for,flash
from models import User,Product
from flask_login import login_user,logout_user,login_required,current_user
import os
import boto3
import botocore
import datetime
from bid import Bid

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')

@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/create', methods=['POST'])
def create():
    mail=request.form.get("email")
    uname=request.form.get("username")
    password=request.form.get("password")
    
    user=User(first_name=request.form.get("first_name"),last_name=request.form.get("last_name"),email=mail,username=uname,password=password, real_password=password)

    if user.save():
        flash(f"Welcome to Bid Bud {user.username}!","success")
        return redirect(url_for("users.new"))
    
    else:
        for e in user.errors:
            flash(e,"warning")
        return redirect(url_for("users.new"))

@users_blueprint.route('/profile', methods=['GET'])
@login_required
def show():
    return render_template('users/profile.html')

@users_blueprint.route('/profile/product', methods=['GET'])
@login_required
def show_product():
    product=Product.select().where(Product.user_id==current_user.id)
    return render_template('users/product.html',product=product)

@users_blueprint.route('/profile/bid', methods=['GET'])
@login_required
def show_bid():
    return render_template('users/bid.html')

@users_blueprint.route('/<id>/edit', methods=['GET'])
@login_required
def edit(id):
    id_num=int(id)
    if id_num==current_user.id:
        return render_template("users/edit.html")

    else:
        flash("Unauthorized to make changes.","danger")
        return redirect(url_for("home"))


@users_blueprint.route('/update/<id>', methods=['POST'])
@login_required
def update(id):
    uname=request.form.get("username")
    password=request.form.get("password")
    check=User.get_or_none(User.username==uname)
 
    if not check :
        user =User.get_or_none(User.id==current_user.id)
        user.username=uname
        user.password=password
        user.real_password=password
        user.save()
        print("test------------------------------------------------------")
        print(user.username)
        print("test------------------------------------------------------")
        flash("Saved changes","success")
        return redirect(url_for("home"))
    
    else:
        flash("Username already exists","warning")
        return redirect(url_for("home"))

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("S3_SECRET_ACCESS_KEY")
)

@users_blueprint.route("/profpic", methods=["GET"])
@login_required
def profpic():
    return render_template("users/upload_profpic.html")

@users_blueprint.route("/upload", methods=["POST"])
@login_required
def upload():
    try:
        file = request.files.get("img")
        s3.upload_fileobj(
            file,
            "krishnaybucket",
            file.filename,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type
            }
        )
        user=User.get_or_none(User.id==current_user.id)
        user.update(updated_at=datetime.datetime.now(),profile_pic=f"http://krishnaybucket.s3.amazonaws.com/{file.filename}").where(User.id==current_user.id).execute()
        
        return redirect(url_for("home"))
        
    except Exception as e:

        print("Something Happened: ", e)
        flash("Cannot upload nothing","warning")
        return redirect(url_for("home"))