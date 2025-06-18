# app/producer.py
import json
import threading
from kafka import KafkaProducer, errors
from django.core.serializers.json import DjangoJSONEncoder
from decouple import config
import time

_lock = threading.Lock()
_producer = None

def get_producer():
    global _producer
    if _producer:
        return _producer

    with _lock:
        if _producer:  # double‑checked locking
            return _producer

        # build it here, with some retry logic
        for attempt in range(5):
            try:
                p = KafkaProducer(
                    bootstrap_servers=config('BOOTSTRAP_SERVERS').split(','),
                    client_id=config('PRODUCER_CLIENT_ID', default=None),
                    security_protocol='SSL',
                    ssl_cafile=config('SSL_CAFILE'),
                    ssl_certfile=config('SSL_CERTFILE'),
                    ssl_keyfile=config('SSL_KEYFILE'),
                    value_serializer=lambda v: json.dumps(v, cls=DjangoJSONEncoder).encode('utf-8'),
                    # optional backoffs:
                    retries=5,
                    retry_backoff_ms=500,
                )
                _producer = p
                return _producer

            except errors.NoBrokersAvailable:
                if attempt < 4:
                    time.sleep(1)  # wait and retry
                else:
                    raise

def send_message(topic, value, key=None):
    p = get_producer()
    p.send(topic, value=value, key=key)
    p.flush()
