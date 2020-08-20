import pika

# RabbitMq bağlantısını burada gerçekleştiriyoruz. Klasik bir yapı. Localhost işlem yapılacak bilgisayarın ip'si olabilir.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Kuyruk tanımlama işlemi.
channel.queue_declare(queue='hello')

# Oluşturduğumuz queue'ye mesajımızı publish ediyoruz.
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')

print(" [x] Sent 'Hello World!'")

# Gereksiz yer işgal etmemesi için kapatıyoruz.
connection.close()