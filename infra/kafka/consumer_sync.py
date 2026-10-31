from kafka import KafkaConsumer

consumer = KafkaConsumer('websocket-messages')
for msg in consumer:
    print(msg)
    key = msg.key.decode('utf-8')
    value = msg.value.decode('utf-8')
    print(f'key={key} value={value}')