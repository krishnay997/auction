import peewee as pw
import os
import datetime
from playhouse.postgres_ext import PostgresqlExtDatabase
from flask_login import UserMixin,current_user
from werkzeug.security import generate_password_hash
import re
from playhouse.hybrid import hybrid_property
from models import BaseModel, User,Product


class Bid(BaseModel):
    owner = pw.ForeignKeyField(User)
    bidder = pw.ForeignKeyField(User)
    bid_amount = pw.IntegerField(null=False)
    product_id=pw.IntegerField(null=False)
    owner_username=pw.TextField(null=False)
    bidder_username=pw.TextField(null=False)
    product_title=pw.TextField(null=False)
    product_pic=pw.TextField(null=False)

    def validate(self):
        if type(self.bid_amount) != int:
            self.errors.append("Numbers only!")