from app import app
from flask import render_template,flash
from main.blueprints.users.views import users_blueprint
from main.blueprints.session.views import session_blueprint
from main.blueprints.product.views import product_blueprint
from main.blueprints.bid.views import bid_blueprint
from flask_login import LoginManager,UserMixin,current_user
from models import User,Product
from bid import Bid



login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.get_or_none(User.id==user_id)


app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(session_blueprint, url_prefix="/login")
app.register_blueprint(product_blueprint, url_prefix="/product")
app.register_blueprint(bid_blueprint, url_prefix="/bid")


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def no_url(e):
    return render_template('404.html'), 404

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(405)
def not_allowed(e):
    return render_template('405.html'), 405


@app.route("/")
def home():
    product=Product.select()
    return render_template('home.html',product=product)
