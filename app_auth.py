def App_auth(environ,start_response):
	users={
			"04_F6_AB_AA_16_3C_80":(10,"Himmelmann, Patrick","1234"),
			}
	uid=environ['PATH_INFO'][1:]
	try:
		userdata=userd[uid]
	except KeyError:
		start_response("404 Not Found",[])
	return [b'Auth',str(environ).encode('ascii')]
