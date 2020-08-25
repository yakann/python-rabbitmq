import pika
import sys

# RabbitMq bağlantısını burada gerçekleştiriyoruz. Klasik bir yapı. Localhost işlem yapılacak bilgisayarın ip'si olabilir.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Exchange dağıtıcımızı tanımlıyoruz.
channel.exchange_declare(exchange='logs', exchange_type='fanout')

# Rabbite bağlandığımızda boş bir kuyruğa ihtiyacımız var. Bunu rabbitin bizim için yapmasını isteyebiliriz. 
# queue parametresine boş bir değer girersek rabbitmq bizim için rastgele bir kuyruk oluşturacaktır. Consumer kapandığı zaman kuyruğun silinmesi için 'exclusive' parametresini kullanıyoruz.
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Şimdi Exchangeimize kuyruğa mesaj göndermesini söylememiz gerekiyor. Exchange ve kuyruk arasındaki bu ilişkiye binding(bağlama) denir.
# result.method.queue bize amq.gen-JzTY20BRgKO-HjmUJj0wLg bu değeri verecektir. Kuyruğun adı diyebiliriz.
# logs isimli exchangeimiz artık mesajları kuyruğa ekleyecek
channel.queue_bind(exchange='logs', queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r" % body)

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()