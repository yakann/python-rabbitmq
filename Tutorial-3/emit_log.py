import pika
import sys

# RabbitMq bağlantısını burada gerçekleştiriyoruz. Klasik bir yapı. Localhost işlem yapılacak bilgisayarın ip'si olabilir.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Exchange dağıtıcımızı tanımlıyoruz.
channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='logs', routing_key='', body=message)
print(" [x] Sent %r" % message)

connection.close()