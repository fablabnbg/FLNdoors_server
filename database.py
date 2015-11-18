from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

import json

Base=declarative_base()

class Member(Base):
	__tablename__='members'
	item_id=Column(Integer,primary_key=True)
	app_item_id=Column(Integer)
	title=Column(String(64))

	def obj(self):
		return {
				#'item_id':self.item_id,
				#'app_item_id':self.app_item_id,
				'title':self.title,
				}
	def __str__(self):
		return str(self.obj())

class Card(Base):
	__tablename__='cards'
	uid=Column(String(14),primary_key=True)
	pin=Column(String(4))
	access_level=Column(Integer)
	owner=Column(String(64),nullable=True)
	member=Column(Integer,ForeignKey('members.item_id'),nullable=True)
	member_o=relationship(Member)
	item_id=Column(Integer)
	app_item_id=Column(Integer)
	expiry_date=Column(Date)

	def obj(self):
		return {
				'uid':self.uid,
				'access_level':self.access_level,
				'owner':self.owner,
				'member':self.member_o.obj() if self.member_o else self.member.obj() if self.member else None,
				#'item_id':self.item_id,
				'app_item_id':self.app_item_id,
				'expiry_date':str(self.expiry_date),
				}

	def __str__(self):
		return str(self.obj())

def create_tables(dbengine):
	__engine=create_engine(dbengine)
	Base.metadata.create_all(__engine)

def create_session(dbengine):
	__engine=create_engine(dbengine)
	Session=sessionmaker(bind=__engine)
	return Session()
