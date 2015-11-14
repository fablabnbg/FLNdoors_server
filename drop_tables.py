import database as db
import config
from sqlalchemy import create_engine

e=create_engine(config.db)
db.Card.__table__.drop(e)
db.Member.__table__.drop(e)
