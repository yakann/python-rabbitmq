import pika

# RabbitMq bağlantısını burada gerçekleştiriyoruz. Klasik bir yapı. Localhost işlem yapılacak bilgisayarın ip'si olabilir.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Kuyruk tanımlama işlemi.
channel.queue_declare(queue='hello')

# Body içerisinde "Hello World" mesajımız geliyor.
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.basic_consume(queue='hello',
                      auto_ack=True,
                      on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

## Burada işlem yaparken iki terminal kullanmak işlemin anlaşılması açısından daha sağlıklı olur.
## send.py ile mesajı gönderirken. receive.py ile mesajı canlı olarak alabiliriz.