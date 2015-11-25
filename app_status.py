import database as db
import config
from datetime import datetime
import json
from hmac import HMAC
from urllib.request import urlopen, HTTPError
from pytz import utc

def get_status(session):
	return session.query(db.Request_Success).order_by(db.Request_Success.date.desc()).first()

def send_status(session,msg_type='doorspush'):
	if not msg_type in ['doorspush','doorsbeat']:
		raise ValueError('msg_type must be "doorspush" or "doorsbeat" not "{}"'.format(msg_type))
	stat=get_status(session)
	is_open=None
	if stat.req_type=='open':
		is_open=True
	if stat.req_type=='close':
		is_open=False
	changed_on=stat.date.isoformat()
	payload={'type':msg_type,'open':is_open,'changed_on':changed_on}
	data=json.dumps({'client_id':config.fablab_client_id,'created_on':datetime.now(utc).isoformat(),'payload':payload}).encode('UTF-8')
	hmac=HMAC(msg=data,key=config.fablab_client_key.encode('UTF-8'))
	postdata=json.dumps({'hmac':hmac.hexdigest(),'data':data.decode('UTF-8')})
	try:
		req=urlopen(config.api_addr,data=postdata.encode('UTF-8'))
	except HTTPError as e:
		return (e)
	return req

def App_status(environ,start_response):
	s=db.create_session(config.db)
	start_response("200 OK",[])
	return [get_status(s).encode('UTF-8')]
