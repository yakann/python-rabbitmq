"""
Direct exchange ile istediğimiz işlemleri yapabilmemize rağmen birden fazla kritere göre işlem yapamaz.

Loglama sistemimizde, yalnızca önem derecesine göre değil, aynı zamanda logları yayınlayan kaynağa göre de loglara subscribe olmak isteyebiliriz. 
Bu kavramı, logları hem önem derecesine (info / warn / crit ...) hem de tesise (auth / cron / kern ...) göre yönlendiren syslog unix aracından öğrenebilirsiniz.

Bu bize çok fazla esneklik sağlayacaktır - sadece 'cron'dan gelen kritik hataları ve aynı zamanda' kern'den gelen tüm günlükleri dinlemek isteyebiliriz.

Bunu loglama sistemimize uygulamak için daha karmaşık bir TOPIC exchange hakkında bilgi edinmemiz gerekiyor.

Topic exchange

Bir topic exchange'e gönderilen mesajlarda rastgele bir routinG_keye sahip olamaz - bu, noktalarla ayrılmış bir kelime listesi olmalıdır. 
Kelimeler herhangi bir şey olabilir, ancak genellikle mesajla bağlantılı bazı özellikleri belirtirler. Birkaç geçerli rounting key 
örneği: 'stock.usd.nyse', 'nyse.vmw', 'quick.orange.rabbit'. Routing keyde 255 bayt sınırına kadar istediğiniz kadar kelime olabilir.

Binding key de aynı biçimde olmalıdır. Topic exchange'in ardındaki mantık, direct olana benzer - belirli bir routing key ile gönderilen bir ileti, eşleşen bir bing key ile 
bağlanan tüm kuyruklara teslim edilecektir. Bununla birlikte, binding keyler için iki önemli özel durum vardır:

*(yıldız) tam olarak bir kelimenin yerini alabilir.
#(karma) sıfır veya daha fazla kelimenin yerini alabilir.

Bunu bir örnekle açıklamak en kolay yoldur:



Bu örnekte, tümü hayvanları tanımlayan mesajlar göndereceğiz. Mesajlar, üç kelimeden (iki nokta) oluşan bir yönlendirme anahtarı ile gönderilecektir. Mesajlar, üç kelimeden 
(iki nokta) oluşan bir routing key ile gönderilecektir. Yönlendirme anahtarındaki ilk kelime bir hızı, ikincisi bir rengi ve üçüncüsü bir türü tanımlayacaktır: 'hız, renk, tür'.
Üç binding oluşturduk: Q1 binding keyi '* .orange. *' İle ve Q2 '*. *. Rabbit' ve 'lazy. #' İle bağlıdır.

Bu bindingler şu şekilde özetlenebilir:
Q1, tüm turuncu hayvanlarla ilgileniyor.
Q2, tavşanlar hakkında her şeyi ve tembel hayvanlar hakkında her şeyi duymak istiyor.

Routing keyi 'quick.orange.rabbit' olarak ayarlanmış bir mesaj, her iki kuyruğa da teslim edilecektir. 'Lazy.orange.elephant' mesajı da her ikisine de gidecek. Öte yandan, 
'quick.orange.fox' yalnızca ilk kuyruğa ve 'lazy.brown.fox' yalnızca ikinciye gidecektir. 'lazy.pink.rabbit', iki bağlamayla eşleşmesine rağmen ikinci kuyruğa yalnızca bir kez
teslim edilecektir. 'quick.brown.fox' herhangi bir bağlamayla eşleşmediğinden atılacak.

Sözleşmemizi bozarsak ve 'turuncu' veya 'hızlı.orange.male.rabbit' gibi bir veya dört kelimelik bir mesaj gönderirsek ne olur? Bu mesajlar herhangi bir bağlamayla eşleşmeyecek 
ve kaybolacak.

Öte yandan 'lazy.orange.male.rabbit', dört kelimesi olmasına rağmen, son bağlama ile eşleşecek ve ikinci kuyruğa teslim edilecektir.

Topic Exchange
Topic exhange güçlüdür ve diğer alışverişler gibi davranabilir.
Bir kuyruk '#' (karma) bağlama anahtarı ile bağlandığında - yönlendirme anahtarına bakılmaksızın tüm mesajları alır - fanout değişiminde olduğu gibi.

Bindinglerde '*' (yıldız) ve '#' (karma) özel karakterleri kullanılmadığında, topic exchange tıpkı direct bir karakter gibi davranacaktır.

Hepsini bir araya koy
Logging sistemimizde bir topic exchange kullanacağız. Logların routing keylerinin iki kelimeye sahip olacağına dair çalışan bir varsayımla başlayacağız: "<facility>.<severity>".
"""

import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

routing_key = sys.argv[1] if len(sys.argv) > 2 else 'anonymous.info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(
    exchange='topic_logs', routing_key=routing_key, body=message)
print(" [x] Sent %r:%r" % (routing_key, message))
connection.close()