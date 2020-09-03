"""
Bu Öğretici Neye Odaklanıyor
İkinci eğitimde, zaman alan görevleri birden çok çalışan arasında dağıtmak için İş Kuyruklarının nasıl kullanılacağını öğrendik.

Peki ya uzak bir bilgisayarda bir işlevi çalıştırmamız ve sonucu beklememiz gerekirse? Bu farklı bir hikaye. Bu model genellikle Uzaktan Prosedür Çağrısı veya RPC olarak bilinir.

Bu eğiticide, bir RPC sistemi oluşturmak için RabbitMQ kullanacağız: bir client ve ölçeklenebilir bir RPC sunucusu. Dağıtmaya değer zaman alıcı görevlerimiz olmadığından,
Fibonacci sayılarını döndüren sahte bir RPC hizmeti oluşturacağız.

İstemci arayüzü
Bir RPC hizmetinin nasıl kullanılabileceğini göstermek için basit bir client sınıfı oluşturacağız. Bir RPC isteği gönderen ve yanıt alınana kadar engelleyen call adlı bir yöntemi ortaya çıkaracak:

fibonacci_rpc = FibonacciRpcClient()
result = fibonacci_rpc.call(4)
print("fib(4) is %r" % result)

Özetle RPC sunucu ve istemci arasında çalışan programların ( yapılan işlemlerin ) iletişimi için dizayn edilmiştir.

RPC hakkında bir not
RPC, bilgi işlemde oldukça yaygın bir model olmasına rağmen, genellikle eleştirilir. Bir programcı, bir function callun yerel mi yoksa yavaş bir RPC mi olduğunun farkında olmadığında sorunlar 
ortaya çıkar. Bunun gibi kafa karışıklıkları, tahmin edilemeyen bir sistemle sonuçlanır ve hata ayıklamaya gereksiz karmaşıklık ekler. Yazılımı basitleştirmek yerine, yanlış kullanılan RPC, 
bakımı yapılamayan spagetti koduyla sonuçlanabilir.

Bunu akılda tutarak, aşağıdaki tavsiyeleri dikkate alın:
*Hangi function callun yerel ve hangisinin uzak olduğunun açık olduğundan emin olun.
*Sisteminizi belgeleyin. Bileşenler arasındaki bağımlılıkları netleştirin.
*Hata durumlarını ele alın. RPC sunucusu uzun süre kapalı kaldığında istemci nasıl tepki vermelidir?

Şüphe duyduğunuzda RPC'den kaçının. Yapabiliyorsanız, RPC benzeri engelleme yerine eşzamansız bir ardışık düzen kullanmalısınız - sonuçlar eşzamansız olarak bir sonraki hesaplama aşamasına aktarılır.

Callback queue
Genel olarak RabbitMQ üzerinden RPC yapmak kolaydır. Bir istemci bir istek mesajı gönderir ve bir sunucu bir yanıt mesajı ile yanıt verir. Bir yanıt almak için, istemcinin istekle birlikte bir 
'callback' kuyruk adresi göndermesi gerekir. Hadi deneyelim:

result = channel.queue_declare(queue='', exclusive=True)
callback_queue = result.method.queue

channel.basic_publish(exchange='',
                      routing_key='rpc_queue',
                      properties=pika.BasicProperties(
                            reply_to = callback_queue,
                            ),
                      body=request)

# ... and some code to read a response message from the callback_queue ...

Mesaj özellikleri
AMQP 0-9-1 protokolü, bir mesajla birlikte gelen 14 özellik kümesini önceden tanımlar. Aşağıdakiler dışında özelliklerin çoğu nadiren kullanılır:

delivery_mode: Bir mesajı kalıcı (2 değeriyle) veya geçici (herhangi bir başka değer) olarak işaretler. Bu özelliği ikinci öğreticiden hatırlayabilirsiniz.
content_type: Kodlamanın mime_type tanımlaması için kullanılır. Örneğin, sıklıkla kullanılan JSON kodlaması için bu özelliği şu şekilde ayarlamak iyi bir uygulamadır: application / json.
response_to: Genellikle bir geri arama kuyruğunu adlandırmak için kullanılır.
correlation_id: RPC yanıtlarını isteklerle ilişkilendirmek için kullanışlıdır.

Correlation id(İlişki kimliği)
Yukarıda sunulan yöntemde, her RPC isteği için bir callback queue oluşturmanızı öneririz. Bu oldukça verimsiz, ancak neyse ki daha iyi bir yol var - istemci başına tek bir callback queue oluşturalım.

Bu, yeni bir sorunu ortaya çıkarır, bu kuyrukta bir yanıt almış olmak, yanıtın hangi isteğe ait olduğu net değildir. Bu, correlation_id  özelliği kullanıldığı zamandır. Bunu her istek için benzersiz 
bir değere ayarlayacağız. Daha sonra, callback queue'de bir mesaj aldığımızda, bu özelliğe bakacağız ve buna dayanarak bir yanıtı bir istekle eşleştirebileceğiz. Bilinmeyen bir correlation_id  
değeri görürsek, mesajı güvenle atabiliriz - isteklerimize ait değildir.

Bir hata ile başarısız olmak yerine neden callback queue'deki bilinmeyen mesajları göz ardı etmemiz gerektiğini sorabilirsiniz. Sunucu tarafında bir yarış durumu olasılığı nedeniyle. Pek olası 
olmasa da, RPC sunucusunun bize yanıtı gönderdikten hemen sonra, ancak istek için bir onay mesajı göndermeden önce ölmesi mümkündür. Böyle bir durumda, yeniden başlatılan RPC sunucusu isteği yeniden 
işleyecektir. Bu nedenle, istemcide yinelenen yanıtları incelikle ele almalıyız ve RPC ideal olarak idempotent(etkisiz) olmalıdır.

özet

RPC'miz şu şekilde çalışacaktır:
*Müşteri başladığında, anonim bir özel callback queue oluşturur.
*Bir RPC isteği için, Client iki özelliğe sahip bir mesaj gönderir: callback queue'e ayarlanan reply_to ve her istek için benzersiz bir değere ayarlanan correlation_id.
*İstek bir rpc_queue kuyruğuna gönderilir.
*RPC işçisi (aka: sunucu) bu kuyruktaki istekleri bekliyor. Bir talep göründüğünde, işi yapar ve reply_to alanındaki sırayı kullanarak, sonucu Client'a geri gönderir.
*Client, callback queue'deki verileri bekler. Bir mesaj göründüğünde, correlation_id özelliğini kontrol eder. Requestten gelen değerle eşleşirse, yanıtı uygulamaya döndürür.
"""
