import database as db
import config
import podio_sync as ps

db.create_tables(config.db)
data=ps.get_cards_from_podio(config.podio_client_id,config.podio_client_secret,config.podio_app_id_nfc,config.podio_app_key_nfc)
s=db.create_session(config.db)
for d in data:
	s.merge(data[d])
	s.commit()
