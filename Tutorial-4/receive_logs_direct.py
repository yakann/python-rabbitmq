#!/usr/bin/env python
import pika
import sys

# RabbitMq bağlantısını burada gerçekleştiriyoruz. Klasik bir yapı. Localhost işlem yapılacak bilgisayarın ip'si olabilir.
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# İşlem yapılacak exchange seçilir.
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

# İşlem sonrası silinme özelliğine sahip yeni rastgele kuyruklar oluşturmak için kullanılır. 
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

severities = sys.argv[1:]
if not severities:
    sys.stderr.write("Usage: %s [info] [warning] [error]\n" % sys.argv[0])
    sys.exit(1)

# Burada ise bind etme işlemi yapılıyor. Log bilgisine göre kuyruklara bind edilir.
for severity in severities:
    channel.queue_bind(
        exchange='direct_logs', queue=queue_name, routing_key=severity)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()