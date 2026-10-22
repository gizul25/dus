from kafka import KafkaProducer

print('connecting...')
producer = KafkaProducer(bootstrap_servers='kafka:9092')
print('ready')
key = b'1234'
while True:
    text = input()
    data = text.encode('utf-8')
    producer.send('websocket-messages', key=key, value=data)