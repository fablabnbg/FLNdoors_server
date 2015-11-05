from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base=declarative_base()

class Member(Base):
	__tablename__='members'
	item_id=Column(Integer,primary_key=True)
	app_item_id=Column(Integer)
	title=Column(String(32))

class Card(Base):
	__tablename__='cards'
	uid=Column(String(14),primary_key=True)
	pin=Column(String(4))
	access_level=Column(Integer)
	owner=Column(String(32))
	member=Column(Integer,ForeignKey('members.item_id'))
	item_id=Column(Integer)
	app_item_id=Column(Integer)


def create_tables(dbengine):
	__engine=create_engine(dbengine)
	Base.metadata.create_all(__engine)

def create_session(dbengine):
	__engine=create_engine(dbengine)
	Session=sessionmaker(bind=__engine)
	return Session()
