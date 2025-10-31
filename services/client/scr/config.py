from decouple import config 

RABBIT_URL = config("RABBIT_URL", default="amqp://Cg7pyYf5PcIMk0yl:sJYYgR298JNVf3rspmGSG2LdjXuO18al@trolley.proxy.rlwy.net:55643")
REQUEST_QUEUE = config("REQUEST_QUEUE", default="translate_requests")
RESPONSE_QUEUE = config("RESPONSE_QUEUE", default="translate_responses")