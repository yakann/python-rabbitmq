import sys
import pika

# RabbitMq bağlantısını burada gerçekleştiriyoruz. Klasik bir yapı. Localhost işlem yapılacak bilgisayarın ip'si olabilir.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Kuyruk tanımlama işlemi.
# Server kapansa bile mesajlarımızın kaybolmaması için durable parametresini kullanırız.
channel.queue_declare(queue='task_queue', durable=True)

# Oluşturduğumuz queue'ye parametre olarak girilen mesaj gönderilir. Hiçbirşey yazılmamışsa eğer 'Hello World!' yazar. 
message = ' '.join(sys.argv[1:]) or "Hello World!"
# delivery_mode özelliği sağlayarak mesajlarımızı kalıcı olarak işaretlememiz gerekiyor.
channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
print(" [x] Sent %r" % message)

# Gereksiz yer işgal etmemesi için kapatıyoruz.
connection.close()


