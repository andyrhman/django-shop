from django.core.serializers.json import DjangoJSONEncoder
from kafka import KafkaProducer
from decouple import config
import json

producer = KafkaProducer(
    bootstrap_servers=config('BOOTSTRAP_SERVERS'),
    client_id=config('PRODUCER_CLIENT_ID', default=None),
    security_protocol='SSL',
    ssl_cafile=config('SSL_CAFILE'),
    ssl_certfile=config('SSL_CERTFILE'),
    ssl_keyfile=config('SSL_KEYFILE'),
    value_serializer=lambda v: json.dumps(v, cls=DjangoJSONEncoder).encode('utf-8'),
)

topic = config('KAFKA_TOPIC', default='default')
