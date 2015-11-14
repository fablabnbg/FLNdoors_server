import json
import database as db
import config

class auth_file:
	def __init__(self,filename):
		self.filename=filename

	def __call__(self,uid):
		uid=uid.replace('_','')
		with open(self.filename,encoding='latin1') as f:
			for l in f:
				try:
					lid,access_level,comment=l.strip().split(';',2)
					if lid.replace(' ','')==uid:
						return {'uid':uid,'access_level':int(access_level),'name':comment,'pin':'0000'}
				except ValueError:
					pass
			return None

class auth_db:
	def __init__(self,connection_string):
		self.session=db.create_session(connection_string)

	def __call__(self,uid):
		uid=uid.replace('_','').replace(' ','').upper()
		entry=self.session.query(db.Card).filter(db.Card.uid==uid).first()
		if not entry:
			return None
		return {'uid':entry.uid,'access_level':entry.access_level,'name':entry.owner,'pin':entry.pin}


def App_auth(environ,start_response):
	auth=auth_file('/root/door_management/door_access')
	auth=auth_db(config.db)
	uid=environ['PATH_INFO'][1:]
	res=auth(uid)
	if not res:
		start_response("404 Not Found",[])
		return []
	start_response("200 OK",[])
	body_json=json.dumps(res)
	return [body_json.encode('ascii')]
