import peeweedbevolve
from database import db
from bid import Bid

if __name__ == '__main__':
   db.evolve(ignore_tables={'base_model'})