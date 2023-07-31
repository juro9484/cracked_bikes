from kafka import KafkaClient,KafkaConsumer
from kafka.common import NoBrokersAvailable, KafkaUnavailableError

topic = "quickstart-events"

consumer = KafkaConsumer(
                topic,
                group_id=None,
                bootstrap_servers='localhost:9092',
                value_deserializer=lambda m: m.decode('utf-8'),
                consumer_timeout_ms=-1,
                auto_offset_reset='latest',
                auto_commit_interval_ms=5000,
                enable_auto_commit=True,
                max_partition_fetch_bytes=10 * 1024 * 1024)


while True:
    for message in consumer:
        print(message)
        # message = message.value
        # print('{} added to {}'.format(message, 'hi'))
    # try:
    #     print(consumer)
    #     for message in consumer:
    #         if message is None:
    #             print("no message")
    #             break
    #         print("Received message")
    #         print(message)
    #             # val = message.value
    #             # Get the encoding. If it's not a key of item, return utf-8.
    #     print('sup')
    # except KeyboardInterrupt:
    #     print("Keyboard interrupt received")
    #     break
    # print("Closing Kafka connection")
    # try:
    #     consumer.close()
    # except:
    #     # Exception is thrown when group_id is None.
    #     # See https://github.com/dpkp/kafka-python/issues/619
    #     pass
