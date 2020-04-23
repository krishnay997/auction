from flask import Flask,Blueprint, render_template,redirect,request,url_for,flash,session
from models import User,Product
from bid import Bid
from werkzeug.security import check_password_hash
from flask_login import login_user,logout_user,login_required,current_user
from peewee import fn
from app import app
import os
import smtplib



bid_blueprint = Blueprint('bid',
                            __name__,
                            template_folder='templates')



@bid_blueprint.route("/<product_id>")
@login_required
def new(product_id):
    product=Product.get_or_none(Product.id==product_id)
    # bid=product.bid_history.limit(1)

    # print("************************************************************************")
    # print(bid.bid_amount)
    # print("************************************************************************")
    return render_template("bid/new.html",product_id=product_id,product=product)

@bid_blueprint.route("/create/<product_id>", methods=["POST"])
@login_required
def create(product_id):
    product=Product.get_or_none(Product.id==product_id)
    bid=request.form.get("bid_num")
    if bid=="":
        flash("Please enter a bidding amount!","warning")
        return redirect(url_for("bid.new",product_id=product_id,product=product))
    else:
        bid_num=int(bid)
        
        owner=User.get_or_none(User.id==product.user_id)
        bidder=User.get_or_none(User.id==current_user.id)
        
        check_bid=Bid.select(fn.MAX(Bid.bid_amount)).where(Bid.product_id==product_id)
        highest_bid=check_bid.scalar()

        if highest_bid is None or bid_num > highest_bid:
            Bid.create(owner=owner.id,owner_username=owner.username,bidder=bidder.id,bidder_username=bidder.username,product_title=product.title,product_pic=product.image_path,bid_amount=bid_num,product_id=product.id)
            flash("Bid successful!","success")
            return redirect(url_for("bid.new",product_id=product_id,product=product))
        
        else:
            flash("Must bid higher than the current highest bid!","warning")
            return redirect(url_for("bid.new",product_id=product_id,product=product))

@bid_blueprint.route("/sold/<product_id>", methods=["POST"])
@login_required
def destroy(product_id):
    product=Product.get_or_none(Product.id==product_id)
    owner=User.get_or_none(User.id==product.user_id)

    subq=Bid.select(fn.MAX(Bid.bid_amount)).where(Bid.product_id==product_id)
    query=Bid.select(Bid.bidder_id).where(Bid.bid_amount==subq)

    bidder=User.get_or_none(User.id==query.scalar())
    check_bid=Bid.select(fn.MAX(Bid.bid_amount)).where(Bid.product_id==product_id)
    highest_bid=check_bid.scalar()
    update=Product.update(bid_end=True).where(Product.id==product_id)
    update.execute()
    server=smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(os.getenv("MAIL"),os.getenv("PASS"))
    
    subject = f"Sold!"
    body = f"{owner.username} has ended the bid for {product.title} at ${highest_bid}.\nHighest bid by {bidder.username}(You).\nContact the owner via {owner.email} to discuss further :)\nSign in to view the product at http://127.0.0.1:5000/bid/{product_id}?"

    msg = f"Subject: {subject}\n\n{body}"

    server.sendmail(os.getenv("MAIL"),bidder.email,msg)
    flash("Email has been sent to bidder!", "success")
    print("Email has been sent!")
    server.quit()
    return redirect(url_for("bid.new",product_id=product_id,product=product))
    

    


