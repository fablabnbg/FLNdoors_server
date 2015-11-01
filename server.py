#!/usr/bin/env python3
from wsgiref.simple_server import make_server
from wsgiref.util import shift_path_info
from app_index import App_index
from app_auth import App_auth
from app_status import App_status

import config

apps={
	None:App_index, #default
	"auth":App_auth,
	"status":App_status,
	}

def select_app(environ,start_response):
	active_app=apps[None]
	path=environ['PATH_INFO']
	for app in apps:
		if app is None: continue
		if path=='/'+app or path.startswith('/'+app+'/'):
			shift_path_info(environ)
			active_app=apps[app]
			break
	return active_app(environ,start_response)

if __name__=='__main__':
	s = make_server(config.listen_addr, config.listen_port, select_app)
	s.serve_forever()
