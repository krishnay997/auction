import peewee as pw
import os
import datetime
from playhouse.postgres_ext import PostgresqlExtDatabase
from flask_login import UserMixin,current_user
from werkzeug.security import generate_password_hash
import re
from playhouse.hybrid import hybrid_property

db = PostgresqlExtDatabase("auction")


class BaseModel(pw.Model):
    created_at = pw.DateTimeField(default=datetime.datetime.now)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.errors = []
        self.validate()
        if len(self.errors) == 0:
            self.updated_at = datetime.datetime.now()
            return super(BaseModel, self).save(*args, **kwargs)
        else:
            return "Not saved"

    class Meta:
        database = db
        legacy_table_names = False

def has_num(word):
        return re.search("[0-9]", word)
class User(UserMixin,BaseModel):
    first_name = pw.CharField(unique=False,null=False)
    last_name = pw.CharField(unique=False,null=False)
    username=pw.CharField(unique=True,null=False)
    email=pw.CharField(unique=True,null=False)
    password=pw.CharField(unique=False,null=False)
    real_password=None
    profile_pic=pw.TextField(null=True)


    def validate(self):
        same_mail=User.get_or_none(email=self.email)
        same_uname=User.get_or_none(username=self.username)

        if same_mail and self.id != same_mail.id:
            self.errors.append("Email is already taken!")

        if same_uname:
            self.errors.append("Username is already taken!")
        
        if len(self.password)<=6:
            self.errors.append("Password should be greater than 6 characters!")

        if not has_num(self.password):
            self.errors.append("Password contain atleast one number!")
        
        if self.real_password is not None:
            self.password=generate_password_hash(self.password)
    @hybrid_property
    def bid_history(self):
        from bid import Bid
        return Bid.select().join(User, on=(Bid.bidder_id==current_user.id)).where((User.id==self.id)).order_by(Bid.created_at.desc())

class Product(BaseModel):
    user = pw.ForeignKeyField(User, backref='product')
    image_path=pw.TextField(null=False)
    description=pw.TextField(null=False)
    title=pw.TextField(null=False)
    bid_end=pw.BooleanField(default=False)

    def validate(self):
        if len(self.description)==0:
            self.errors.append("Must provide description!")

        if len(self.title)==0:
            self.errors.append("Must provide title!")

        if len(self.image_path)==0:
            self.errors.append("Must upload image!")

    @hybrid_property
    def bid_history(self):
        from bid import Bid
        return Bid.select().join(Product, on=(Bid.product_id==Product.id)).where((Product.id==self.id)).order_by(Bid.created_at.desc()).limit(3)




    
    

         