import database as db
import config
from datetime import datetime
import json
from hmac import HMAC
from urllib.request import urlopen, HTTPError

def get_status(session):
	return session.query(db.Request_Success).order_by(db.Request_Success.date.desc()).first().req_type

def send_status(session):
	stat=get_status(session)
	payload=json.dumps({'client':config.fablab_client_id,'date':datetime.now().isoformat(),'status':stat})
	hmac=HMAC(msg=payload.encode('UTF-8'),key=config.fablab_client_key.encode('UTF-8'))
	data=json.dumps({'hmac':hmac.hexdigest(),'payload':payload})
	try:
		req=urlopen(config.api_addr,data=data.encode('UTF-8'))
	except HTTPError as e:
		print(e)

def App_status(environ,start_response):
	s=db.create_session(config.db)
	start_response("200 OK",[])
	return [get_status(s).encode('UTF-8')]
