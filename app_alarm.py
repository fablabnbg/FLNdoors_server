import database as db
import config
import json
from sms import sms

def bad_req(start_response):
	start_response("400 Bad Request",[])
	return []

def App_alarm(environ,start_response):
	try:
		_,door=environ['PATH_INFO'].split('/')
		request_length=int(environ.get('CONTENT_LENGTH',0))
		body=environ['wsgi.input'].read(request_length).decode('UTF-8')
		request_body = json.loads(body)
	except ValueError as e:
		return bad_req(start_response)
	try:
		msg=request_body['message']
	except KeyError:
		return bad_req(start_response)
	s=db.create_session(config.db)
	r=db.Alarm(type=msg,door_name=door)
	s.add(r)
	try:
		s.commit()
	except:
		return bad_req(start_response)

	m='ALARM: '+str(r)
	print(m)
	for recv in config.sms_receivers:
		sms(config.sms_device,recv,m)
	start_response("200 OK",[])
	return([])
