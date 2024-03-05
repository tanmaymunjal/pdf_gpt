from celery import Celery
from backend.summarise_gpt import GPTSummarisation
from backend.configuration import global_config
import requests

# there is a memory leak in celery codebase
# small thing but the reason broker pool is disabled
# https://github.com/celery/celery/discussions/7028
celery_app = Celery(
    "celery_app",
    backend="rpc://",
    broker=global_config["Celery"]["BROKER"],
    broker_pool_limit=0,
    broker_transport_options={"confirm_publish": True},
    include=["backend.celery_app"],
)


def send_task_notification(
    notification_body,
    api_gateway=global_config["Application"]["API_GATEWAY"],
):
    requests.post(
        api_gateway + "/notify/task",
        json=notification_body,
    )


class CeleryApplication:
    def __init__(
        self,
        app=celery_app,
        task_notifier=send_task_notification,
        notification_api_key=global_config["Notification"]["API_KEY"],
    ):
        self.task_notifier = task_notifier
        self.notification_api_key = notification_api_key
        self.app = app

    def enable_app(self):
        @self.app.task(bind=True, track_started=True)
        def generate_summary_celery_task(task_self, user_openai_key, read_docs):
            """
            Celery task to generate a summary using GPT and send it to an API gateway.

            Args:
                self: Reference to the task instance.
                read_docs (str): Text content to be summarized.

            Returns:
                None

            Sends a POST request to the configured API_GATEWAY endpoint with the generated summary.

            On success, sends a notification to the API gateway with the task_id, generated summary,
            and task_status as "SUCCESS".

            On failure, sends a notification to the API gateway with the task_id and task_status as "FAILED".
            """

            try:
                gpt_summariser = GPTSummarisation(user_openai_key)
                summary = gpt_summariser.summarise_doc(read_docs)
                self.task_notifier(
                    {
                        "notification_auth": self.notification_api_key,
                        "task_id": task_self.request.id,
                        "generated_summary": summary,
                        "task_status": "SUCCESS",
                    }
                )
            except:
                self.task_notifier(
                    {
                        "notification_auth": global_config["Notification"]["API_KEY"],
                        "task_id": task_self.request.id,
                        "task_status": "FAILED",
                    }
                )

        return self

    def run_generate_task(self, user_openai_key, read_docs):
        return self.app.send_task(
            "celery_app.generate_summary_celery_task",
            kwargs={"user_openai_key": user_openai_key, "read_docs": read_docs},
        ).id
celery_application = CeleryApplication(celery_app).enable_app()