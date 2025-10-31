from decouple import config 

RABBIT_URL = config("RABBIT_URL", default="amqp://guest:guest@rabbitmq:5672/")
REQUEST_QUEUE = config("REQUEST_QUEUE", default="translate_requests")
RESPONSE_QUEUE = config("RESPONSE_QUEUE", default="translate_responses")