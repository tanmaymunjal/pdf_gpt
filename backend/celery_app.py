from celery import Celery
from backend.summarise_gpt import GPTSummarisation
from backend.configuration import global_config
import requests

# there is a memory leak in celery codebase
# small thing but the reason broker pool is disabled
# https://github.com/celery/celery/discussions/7028
app = Celery(
    "celery_app",
    backend="rpc://",
    broker="amqp://myuser:mypassword@localhost:5672/myvhost",
    broker_pool_limit=0,
    broker_transport_options={"confirm_publish": True},
    ignore_result=True,
    include=["backend.celery_app"],
)


@app.task(bind=True, track_started=True)
def generate_summary_celery_task(self, user_openai_key, read_docs):
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
        requests.post(
            global_config["Application"]["API_GATEWAY"],
            json={
                "notification_auth": global_config["Notification"]["API_KEY"],
                "task_id": self.request.id,
                "generated_summary": summary,
                "task_status": "SUCCESS",
            },
        )
    except:
        requests.post(
            global_config["Application"]["API_GATEWAY"],
            json={
                "notification_auth": global_config["Notification"]["API_KEY"],
                "task_id": self.request.id,
                "task_status": "FAILED",
            },
        )
