from hmac import HMAC
from datetime import datetime
from urllib.request import urlopen

class FLN_api:
	def __init__(self,endpoint,clientid,psk):
		self.endpoint=endpoint
		self.clientid=clientid
		self.psk=psk

	def send(self,msg_type,msg):
		data=json.dumps({
				'created_on':datetime.now(),
				'type':msg_type,
				'body':msg,
				}).encode('ascii')
		body=json.dumps({
				'clientid':self.clientid,
				'hmac':HMAC(key=self.psk,msg=data),
				'data':data,
				}).encode('ascii')

		try:
			r=urlopen(self.endpoint,data=body)
		except HTTPError as e:
			return e
		return r


