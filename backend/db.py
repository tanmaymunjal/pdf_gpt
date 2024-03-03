from backend.configuration import global_config
import mongoengine


def connect_to_db(db_uri=global_config["Application"]["DB"]):
    mongoengine.connect(db_uri)
