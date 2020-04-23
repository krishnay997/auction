from flask import Flask,Blueprint, render_template,redirect,request,url_for,flash,session
from models import User,Product
from werkzeug.security import check_password_hash
from flask_login import login_user,logout_user,login_required,current_user
import os
import boto3
import botocore
import datetime


product_blueprint = Blueprint('product',
                            __name__,
                            template_folder='templates')

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("S3_SECRET_ACCESS_KEY")
)

@product_blueprint.route("/")
@login_required
def new():
    return render_template("product/new.html")

@product_blueprint.route("/create", methods=["POST"])
@login_required
def create():
    try:
        title=request.form.get("title")
        description=request.form.get("description")
        file = request.files.get("product_img")
        if file and title and description:
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
            Product.create(image_path=f"http://krishnaybucket.s3.amazonaws.com/{file.filename}",user=user,description=description,title=title)
            return redirect(url_for("home"))
        else:
            flash("Please complete every field","warning")
            return redirect(url_for("product.new"))
        
    except Exception as e:
        flash("Something went wrong.Please try again.","warning")
        print("Something Happened: ", e)
        return redirect(url_for("product.new"))
        

@product_blueprint.route("/search", methods=["POST"])
@login_required
def search():
    search=request.form.get("search")
    items= Product.select().where(Product.title.contains(search))
    if items:
        return render_template("product/show_product.html",search=search,items=items)
    else:
        flash("Product not found :(","warning")
        return redirect(url_for("home"))

@product_blueprint.route("/delete/<product_id>", methods=["POST"])
@login_required
def destroy(product_id):
    delete=Product.delete().where(Product.id==product_id)
    delete.execute()
    flash("Product deleted.","info")
    product=Product.select().where(Product.user_id==current_user.id)
    return render_template('users/product.html',product=product)

