from mongoengine import Document, IntField, StringField, EmailField, DateTimeField
from datetime import datetime


class User(Document):
    user_email = EmailField(required=True)
    user_name = StringField(required=True)
    user_hashed_password = StringField()
    user_salt = StringField()
    user_docs_capacity = IntField(default=5)


class PotentialUser(Document):
    user_email = EmailField(required=True)
    user_name = StringField(required=True)
    user_salt = StringField()
    user_hashed_password = StringField()
    user_otp_sent = IntField()
    user_otp_sent_at = DateTimeField(default=datetime.now())
