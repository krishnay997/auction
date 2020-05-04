from flask import Flask
from database import db
import os
from flask_wtf.csrf import CsrfProtect
from flask_mail import Mail, Message 

web_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'main')

app = Flask('auction', root_path=web_dir)
app.secret_key=os.getenv("SECRET_KEY")
csrf=CsrfProtect(app)
@app.before_request
def before_request():
   db.connect()
   

@app.after_request
def after_request(response):
   db.close()
   
   return response

