#!/usr/bin/env python3
import config
import app_status
import database as db

s=db.create_session(config.db)
r=app_status.send_status(s,'doorsbeat')
