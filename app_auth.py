import json

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

def App_auth(environ,start_response):
	auth=auth_file('door_access')
	uid=environ['PATH_INFO'][1:]
	res=auth(uid)
	if not res:
		start_response("404 Not Found",[])
		return []
	start_response("200 OK",[])
	body_json=json.dumps(res)
	return [body_json.encode('ascii')]
