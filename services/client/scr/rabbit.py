import aio_pika 
from .config import RABBIT_URL, REQUEST_QUEUE
from typing import Optional

_connection: aio_pika.RobustConnection | None = None
_channel: aio_pika.RobustChannel | None = None
_default_exchange: aio_pika.Exchange | None = None

async def connect():
    global _connection, _channel, _default_exchange
    _connection = await aio_pika.connect_robust(RABBIT_URL)
    _channel = await _connection.channel()
    _default_exchange = _channel.default_exchange 
    
    await _channel.declare_queue(REQUEST_QUEUE, durable=True)
    print("Connected to RabbitMQ")
    
async def disconnect():
    global _connection
    if _connection:
        await _connection.close()
        print("RabbitMQ connection closed")
        
def get_channel() -> aio_pika.RobustChannel:
    if _channel is None:
        raise RuntimeError("RabbitMQ channel not initialized")
    return _channel

async def publish_request(body_bytes: bytes, routing_key: str = REQUEST_QUEUE, correlation_id: Optional[str] = None, reply_to: Optional[str] = None):
    if _default_exchange is None:
        raise RuntimeError("RabbitMQ exchange not initialized")
    msg = aio_pika.Message (
        body=body_bytes,
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        correlation_id=correlation_id,
        reply_to=reply_to,
    )
    await _default_exchange.publish(msg, routing_key=routing_key)