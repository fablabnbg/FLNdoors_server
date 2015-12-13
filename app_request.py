import database as db
import config
import json
import sqlalchemy.orm.exc as exc
from app_status import get_status, send_status
from datetime import date
import threading

def bad_req(start_response,data=None):
	start_response("400 Bad Request",[])
	if data:
		return [json.dumps(data).encode('UTF-8')]
	else:
		return []

def ok(start_response,data):
	start_response("200 OK",[])
	return [json.dumps(data).encode('UTF-8')]

def log_success(session,card_uid,req_type,door):
		r=db.Request_Success(card_uid=card_uid,req_type=req_type,door_name=door)
		session.add(r)
		session.commit()
		threading.Thread(target=lambda:send_status(session)).start()
		return True

def log_failure(session,card_uid,req_type,door):
		r=db.Request_Failure(card_uid=card_uid,req_type=req_type,door_name=door)
		session.add(r)
		session.commit()
		return True

def App_request(environ,start_response):
	try:
		_,door,req=environ['PATH_INFO'].split('/')
		request_length=int(environ.get('CONTENT_LENGTH',0))
		body=environ['wsgi.input'].read(request_length).decode('UTF-8')
		request_body = json.loads(body)
	except ValueError as e:
		return bad_req(start_response)
	try:
		card_uid=request_body['card']
	except KeyError:
		return bad_req(start_response)
	pin=request_body.get('pin','')
	new_pin=request_body.get('new_pin','')
	s=db.create_session(config.db)
	if req=='close':
		if request_body.get('write_log',False):
			log_success(s,card_uid,'close',door)
		return ok(start_response,'close')

	if req=='open':
		try:
			card=s.query(db.Card).filter(db.Card.uid==card_uid.upper()).one()
		except exc.NoResultFound:
			log_failure(s,card_uid,'open',door)
			return ok(start_response,'deny')
		if card.access_level<5 or card.expiry_date<date.today():
			log_failure(s,card_uid,'open',door)
			return ok(start_response,'deny')
		if get_status(s).req_type=='open':
			log_success(s,card_uid,'open',door)
			return ok(start_response,'open')
		if card.access_level>=10:
			if card.pin==pin:
				log_success(s,card_uid,'open',door)
				return ok(start_response,'open')
			else:
				return ok(start_response,'require_pin')
		log_failure(s,card_uid,'open',door)
		return ok(start_response,'deny')

	if req=='change_pin':
		try:
			card=s.query(db.Card).filter(db.Card.uid==card_uid.upper()).one()
		except exc.NoResultFound:
			return bad_req(start_response,{'message':'Unknown uid','uid':card_uid.upper()})
		if card.pin!=pin:
			return bad_req(start_response,{'message':'wrong pin','uid':card_uid.upper()})
		if len(new_pin)!=len(pin):
			return bad_req(start_response,{'message':'wrong new pin length','uid':card_uid.upper()})
		card.pin=new_pin
		s.merge(card)
		s.commit()
		card=s.query(db.Card).filter(db.Card.uid==card_uid.upper()).one()
		return ok(start_response,'ack')
	return bad_req(start_response,{'message':'unknown request'})

