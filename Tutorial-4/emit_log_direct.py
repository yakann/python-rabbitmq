"""
Bu eğiticide ona bir özellik ekleyeceğiz - mesajların yalnızca bir alt kümesine subscribe olmayı mümkün kılacağız. 
Örneğin, konsoldaki tüm günlük mesajlarını yazdırmaya devam ederken, yalnızca kritik hata mesajlarını log dosyasına 
(disk alanından tasarruf etmek için) yönlendirebileceğiz.

Bindingsler, fazladan bir routing_key parametresi alabilir. Bir basic_publish parametresiyle karışıklığı önlemek için, 
ona bir 'binding key' diyeceğiz. Anahtarla bir binding nasıl oluşturabiliriz:

channel.queue_bind(exchange=exchange_name,
                   queue=queue_name,
                   routing_key='black')

Binding keyin anlamı, exchange türüne bağlıdır. Daha önce kullandığımız fanout exchange, değerini basitçe görmezden geldi.

Direct exchange
Önceki eğitimden alınan loglama sistemimiz tüm mesajları tüm consumerlara yayınlar. Mesajların önem derecelerine göre 
filtrelenmesine izin vermek için bunu genişletmek istiyoruz. Örneğin, diske log mesajlarını yazan komut dosyasının 
yalnızca kritik hataları almasını ve uyarı veya bilgi günlüğü mesajlarında disk alanını boşa harcamamasını isteyebiliriz

Bize çok fazla esneklik sağlamayan bir fanout exchange kullanıyorduk - sadece akılsız yayın yapabiliyor.


Bunun yerine direct exchange kullanacağız. Direct exchangein arkasındaki yönlendirme algoritması basittir - bir mesaj, 
binding key mesajın routing_keyiyle tam olarak eşleşen sıralara gider.

Multiple bindings
Birden çok kuyruğu aynı binding key ile bağlamak tamamen yasaldır. Örneğimizde, X ve Q1 arasına siyah bağlama anahtarı 
ile bir bağlama ekleyebiliriz. Bu durumda, doğrudan değişim fanout gibi davranacak ve mesajı tüm eşleşen kuyruklara yayınlayacaktır. 
Siyah yönlendirme anahtarına sahip bir mesaj hem Q1 hem de Q2'ye gönderilecektir.


Logları yaymak
Bu modeli log sistemimiz için kullanacağız. Fanout yerine direct exchange'e mesaj göndereceğiz. Logların önem 
derecesini yönlendirme anahtarı olarak sağlayacağız. Bu şekilde, consumer komut dosyası almak istediği şiddeti seçebilecektir. 
Önce logları yaymaya odaklanalım.


İşleri basitleştirmek için 'önem derecesinin' 'bilgi', 'uyarı', 'hata' olabileceğini varsayacağız.

Subscribing
Mesaj almak, bir istisna dışında, önceki eğitimde olduğu gibi çalışacaktır - ilgilendiğimiz her önem derecesi için yeni bir bağlantı oluşturacağız.

Yalnızca 'uyarı' ve 'hata' ('bilgi' değil) günlük mesajlarını bir dosyaya kaydetmek istiyorsanız, bir konsol açın ve şunu yazın:
python receive_logs_direct.py warning error > logs_from_rabbit.log
Tüm günlük mesajlarını ekranınızda görmek isterseniz, yeni bir terminal açın ve şunları yapın:
python receive_logs_direct.py info warning error
"""
import pika
import sys

# RabbitMq bağlantısını burada gerçekleştiriyoruz. Klasik bir yapı. Localhost işlem yapılacak bilgisayarın ip'si olabilir.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
# Direct tipli exchangeimizi tanımlıyoruz.
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

# Severity değişkeni mesajın önemini belirten bir değişkendir. Publish kısmında routing_key ile ilişkilendirilmektedir.
severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(exchange='direct_logs', routing_key=severity, body=message)
print(" [x] Sent %r:%r" % (severity, message))
connection.close()