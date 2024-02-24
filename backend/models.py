from mongoengine import (
    Document,
    IntField,
    StringField,
    EmailField,
    DateTimeField,
    EmbeddedDocument,
    ListField,
    BooleanField,
)
from datetime import datetime
from backend.configuration import global_config


class PasswordRecoveryRequest(EmbeddedDocument):
    otp = StringField(required=True)
    otp_expirty = DateTimeField(required=True)


class UserTasks(Document):
    user_email = StringField(required=True)
    user_task_id = StringField(required=True, unique=True)
    user_read_docs = StringField(required=True)
    user_generated_summary = StringField()
    user_task_generated = DateTimeField(default=datetime.now())
    user_task_completed = DateTimeField()
    user_task_status = StringField(default="PENDING", options=["SUCCESS", "FAILED"])


class User(Document):
    user_email = EmailField(required=True, unique=True)
    user_name = StringField(required=True)
    user_hashed_password = StringField(required=True)
    user_salt = StringField(required=True)
    user_docs_capacity = IntField(
        default=global_config["Application"]["MAX_FREE_TRIAL_USAGE"]
    )
    user_password_recovery_request = PasswordRecoveryRequest()
    user_openai_key = StringField()


class PotentialUser(Document):
    user_email = EmailField(required=True, unique=True)
    user_name = StringField(required=True)
    user_salt = StringField(required=True)
    user_hashed_password = StringField(required=True)
    user_otp_sent = IntField(required=True)
    user_otp_sent_at = DateTimeField(default=datetime.now())
