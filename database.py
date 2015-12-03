from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Date, func, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from pytz import utc

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

class Door(Base):
	__tablename__='doors'
	name=Column(String(16),primary_key=True)

class Request_Success(Base):
	__tablename__='requests_success'
	id=Column(Integer,primary_key=True)
	date=Column(DateTime, default=func.now())
	card_uid=Column(String(14))
	req_type=Column(Enum('open','close'))
	door_name=Column(String(16),ForeignKey('doors.name'))
	door=relationship(Door)

class Request_Failure(Base):
	__tablename__='requests_failure'
	id=Column(Integer,primary_key=True)
	date=Column(DateTime, default=func.now())
	card_uid=Column(String(14))
	req_type=Column(Enum('open','close'))
	door_name=Column(String(16),ForeignKey('doors.name'))
	door=relationship(Door)

class Alarm(Base):
	__tablename__='alarms'
	id=Column(Integer,primary_key=True)
	date=Column(DateTime, default=func.now())
	type=Column(String(32))
	door_name=Column(String(16),ForeignKey('doors.name'))
	door=relationship(Door)

	def __str__(self):
		return '"{}" from "{}" on "{}"'.format(self.type,self.door.name,utc.localize(self.date))

def create_tables(dbengine):
	__engine=create_engine(dbengine)
	Base.metadata.create_all(__engine)

def create_session(dbengine):
	__engine=create_engine(dbengine)
	Session=sessionmaker(bind=__engine)
	return Session()
