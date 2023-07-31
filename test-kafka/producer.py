from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError
import json


def _kafka_success(response):
    '''
    Callback for successful send
    '''
    print("Sent page to Kafka")


def _kafka_failure(exception):
    '''
    Callback for failed send
    '''
    print(exception)
    print("Failed to send page to Kafka")
    

producer = KafkaProducer(bootstrap_servers='localhost:9092',
                                     retries=3,
                                     linger_ms=25,
                                     buffer_memory=4 * 1024 * 1024,
                                     value_serializer=lambda m: m.encode('utf-8'),
                                     max_request_size=1024 * 1024,
                                     api_version=(0,10))


data = {"hello": 'there'}
firehose_topic = "demo.outbound_firehose"
future = producer.send(firehose_topic, json.dumps(data))
future.add_callback(_kafka_success)
future.add_errback(_kafka_failure)

producer.flush()
producer.close(timeout=10)