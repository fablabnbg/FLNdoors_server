#!/usr/bin/env python3
from pypodio2 import api
from database import Member, Card
from functools import reduce
from operator import or_
import datetime
import config

def get_cards_from_podio(client_id,client_secret,app_id,app_key):
	p=api.OAuthAppClient(client_id,client_secret,app_id,app_key)
	res=p.Item.filter(app_id,{'limit':1,'offset':0})
	count=res['total']-1
	items=res['items']
	offset=1
	while count>0:
		res=p.Item.filter(app_id,{'limit':50,'offset':offset})
		items.extend(res['items'])
		offset+=50
		count-=50
	data=dict()
	for item in items:
		i={
				'item_id':item['item_id'],
				'app_item_id':item['app_item_id'],
				'member':None,
				'owner':None,
				}
		for f in item['fields']:
			if f['field_id']==config.podio_fid_uid:i['uid']=f['values'][0]['value'].replace(' ','')
			if f['field_id']==config.podio_fid_access_level:i['access_level']=int(f['values'][0]['value']['text'])
			if f['field_id']==config.podio_fid_member:
				i['member']=Member(
						item_id=f['values'][0]['value']['item_id'],
						app_item_id=f['values'][0]['value']['app_item_id'],
						title=f['values'][0]['value']['title']
						)
			if f['field_id']==config.podio_fid_owner:i['owner']=f['values'][0]['value']
			if f['field_id']==config.podio_fid_expiry_data:i['expiry_date']=datetime.date(*map(int,f['values'][0]['start_date_utc'].split('-')))
		c=Card(
				uid=i['uid'],
				access_level=i['access_level'],
				pin='0000',
				owner=i['owner'],
				member=i['member'],
				item_id=i['item_id'],
				app_item_id=i['app_item_id'],
				expiry_date=i['expiry_date'] if 'expiry_date' in i else datetime.date(year=2100,month=12,day=31)
				)
		data[c.uid]=c
	return data

def get_cards_from_db(session):
	items=session.query(Card).all()
	data={x.uid:x for x in items}
	return data
	
def merge_dicts(*args):
	keys=reduce(or_,(set(x.keys()) for x in args))
	res=dict()
	for k in keys:
		res[k]=[]
		for a in args:
			res[k].append(a.get(k))
	return res

def remove_same(d):
	def cmp(a,b):
		if (not a) or (not b):
			return False
		res=True
		res&=a.access_level==b.access_level
		res&=a.owner==b.owner
		res&=a.expiry_date==b.expiry_date
		if a.member_o and b.member_o:
			res&=a.member_o.item_id==b.member_o.item_id
		return res
	res=dict()
	for k in d:
		r=True
		for a in d[k]:
			r&=cmp(a,d[k][0])
		if not r:
			res[k]=d[k]
	return res

def create_diff(session,client_id,client_secret,app_id,app_key):
	return remove_same(merge_dicts(get_cards_from_podio(client_id,client_secret,app_id,app_key),get_cards_from_db(session)))

def interactive_merge(session,d):
	for k in d:
		print('podio:')
		print(d[k][0])
		print('db:')
		print(d[k][1])
		r=input('write from podio to db? (y/N)')
		if r.upper()=='Y':
			print('changing db')
			if not d[k][0]: # Card is not listed in podio, remove from db
				s.delete(d[k][1])
			else:
				if d[k][1]:
					d[k][0].pin=d[k][1].pin # keep pin
				#if d[k][0].member:
					#session.merge(d[k][0].member) # add member from podio
					#d[k][0].member=d[k][0].member.item_id
				session.merge(d[k][0])
			session.commit()

if __name__=='__main__':
	from database import create_session
	s=create_session(config.db)
	d=create_diff(s,config.podio_client_id,config.podio_client_secret,config.podio_app_id_nfc,config.podio_app_key_nfc)
	interactive_merge(s,d)
