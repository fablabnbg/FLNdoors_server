import database as db
import config

def get_status(session):
	return session.query(db.Request_Success).order_by(db.Request_Success.date.desc()).first().req_type


def App_status(environ,start_response):
	s=db.create_session(config.db)
	start_response("200 OK",[])
	return [get_status(s).encode('UTF-8')]
