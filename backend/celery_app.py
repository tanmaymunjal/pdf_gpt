from celery import Celery
from celery.result import AsyncResult
import time
from parser import ParserFactory
from summarise_gpt import GPTSummarisation

# there is a memory leak in celery codebase
# small thing but the reason broker pool is disabled
# https://github.com/celery/celery/discussions/7028
app = Celery(
    "celery_app",
    backend="rpc://",
    broker="amqp://myuser:mypassword@localhost:5672/myvhost",
    broker_pool_limit=0,
    broker_transport_options={"confirm_publish": True},
    ignore_result=False,
)


@app.task(track_started=True)
def generate_summary(source_stream, file_extension):
    parser = ParserFactory(source_stream, file_extension).build()
    read_docs = parser.read()
    return {"summary": gpt_summariser.summarise_doc(read_docs)}
