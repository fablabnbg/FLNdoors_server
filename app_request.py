import database as db
import config
import json
import sqlalchemy.orm.exc as exc
from app_status import get_status, send_status
from datetime import date
import threading

def bad_req(start_response):
	start_response("400 Bad Request",[])
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
		print(body)
		request_body = json.loads(body)
	except ValueError:
		return bad_req(start_response)
	try:
		card_uid=request_body['card']
	except KeyError:
		return bad_req(start_response)
	print(card_uid)
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
		if card.access_level>=10:
			log_success(s,card_uid,'open',door)
			return ok(start_response,'open')
		if get_status(s)=='open':
			log_success(s,card_uid,'open',door)
			return ok(start_response,'open')
		log_failure(s,card_uid,'open',door)
		return ok(start_response,'deny')
	
