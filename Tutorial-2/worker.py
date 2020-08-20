import pika
import time

# RabbitMq bağlantısını burada gerçekleştiriyoruz. Klasik bir yapı. Localhost işlem yapılacak bilgisayarın ip'si olabilir.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Kuyruk tanımlama işlemi.
# Server kapansa bile mesajlarımızın kaybolmaması için durable parametresini kullanırız.
channel.queue_declare(queue='task_queue', durable=True)

# Body içerisinde queueye gönderilen mesajımız gelir. Sleep fonksiyonunda ise string içerisindeki nokta sayısı kadar saniye ile bizi bekletir.
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)


# RabbitMQ'ya bir çalışana aynı anda birden fazla mesaj vermemesini söylemek için basic.qos protokol yöntemini kullanır.
# Normalde test ettiğimizde mesajları işlem uzun sürsede aynı kuyruğa iletiyordu. Bu satıra yazılan kod ile bir kuyrukta bir işlem varsa öncelikle onun bitmesini bekliyoruz.
channel.basic_qos(prefetch_count=1)


channel.basic_consume(queue='task_queue', on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

## Burada işlem yaparken iki terminal kullanmak işlemin anlaşılması açısından daha sağlıklı olur.
## send.py ile mesajı gönderirken. receive.py ile mesajı canlı olarak alabiliriz.