---
id: id03
title: Suricata · Değişkenler, Yön ve Eşikler
summary: $HOME_NET ve $EXTERNAL_NET değişkenleri; yanıt paketinde kaynağın sunucu olması; dns.rcode ile NXDOMAIN; detection_filter ile "N olaydan sonra" ve threshold type both ile "pencerede bir kez" alarm; track by_src ile by_dst farkı ve yanlış yönde sayan eşik. Gerçek Suricata 8, sentetik trafik.
---

::: anlat Bir olay değil, bir örüntü
Tek bir başarısız DNS sorgusu (NXDOMAIN: "böyle bir ad yok") olağandır. Bir istemcinin bir dakikada onlarca yok olan ad sorması ise başka bir şeydir: yanlış yapılandırılmış bir uygulama ya da rastgele ad üreten bir yazılım. Böyle örüntüler için Suricata'nın iki aracı vardır:

| Seçenek | Ne yapar |
|---|---|
| `detection_filter:track by_dst, count 5, seconds 60;` | aynı izleme anahtarı için 60 saniyede **5'i aşan** her eşleşmede alarm (6., 7. ...) |
| `threshold:type both, track by_dst, count 5, seconds 60;` | 60 saniyede 5. eşleşmede **bir kez** alarm, pencere bitene kadar susar |

`track` neyin sayılacağını söyler: `by_src` paketin **kaynak** adresine, `by_dst` **hedef** adresine göre ayrı sayaç.

`$HOME_NET` ve `$EXTERNAL_NET`, Suricata yapılandırmasındaki adres değişkenleridir. Varsayılanda `$HOME_NET` özel adres aralıklarıdır (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16); `$EXTERNAL_NET` onların dışı.

DNS yanıt koduna `dns.rcode:3;` ile bakılır (3 = NXDOMAIN).

> [!TUZAK] Yanıtın kaynağı sunucudur
> NXDOMAIN bir **yanıttır**: paketi DNS sunucusu istemciye gönderir. Bu pakette kaynak sunucu, hedef istemcidir. "İstemci başına" saymak istiyorsan `track by_dst` yazmalısın. `by_src` bütün istemcilerin hatalarını sunucunun tek sayacında toplar.
:::

::: tahmin
09:10'da 10.0.3.4 yedi yok olan ad soruyor. 09:20'de iki ayrı istemci (10.0.1.15 ve 10.0.2.8) üçer tane soruyor. Bu kural kaç alarm üretir?

```suricata
alert dns any any -> $HOME_NET any (msg:"Cok sayida NXDOMAIN"; dns.rcode:3; detection_filter:track by_src, count 5, seconds 60; sid:1000013; rev:1;)
```

???

**Üç: ikisi 10.0.3.4 için, biri 09:20'de.**

```
2026-10-19 09:10:25|1000013|Cok sayida NXDOMAIN|10.0.0.2|10.0.3.4|59057
2026-10-19 09:10:30|1000013|Cok sayida NXDOMAIN|10.0.0.2|10.0.3.4|46156
2026-10-19 09:20:10|1000013|Cok sayida NXDOMAIN|10.0.0.2|10.0.2.8|49822
```

Sayaç yanıtın kaynağına, yani DNS sunucusu 10.0.0.2'ye göre tutuldu. 09:20'de iki istemcinin üçer hatası tek sayaçta toplanınca altıncı yanıtta alarm çıktı. Hiçbir istemci eşiği aşmadı; alarm yanlış. Kaynak ve hedef sütunlarına bak: kaynak her satırda sunucudur.

```setup
akis(tur="dns", zaman="2026-10-19 09:00:01", istemci="10.0.1.15", sunucu="10.0.0.2", ad="intranet.ornek.test", cevap="10.0.5.10")
akis(tur="http", zaman="2026-10-19 09:00:02", istemci="10.0.1.15", sunucu="10.0.5.10", istek="GET /indir/rapor.pdf HTTP/1.1\r\nHost: intranet.ornek.test\r\nUser-Agent: Mozilla/5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
akis(tur="dns", zaman="2026-10-19 09:01:00", istemci="10.0.1.22", sunucu="10.0.0.2", ad="yasak-site.example", cevap="198.51.100.80")
akis(tur="http", zaman="2026-10-19 09:01:01", istemci="10.0.1.22", sunucu="198.51.100.80", istek="GET /guncelleme/kurulum.exe HTTP/1.1\r\nHost: yasak-site.example\r\nUser-Agent: curl/8.5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nMZ")
akis(tur="dns", zaman="2026-10-19 09:02:00", istemci="10.0.2.8", sunucu="10.0.0.2", ad="YASAK-SITE.example", cevap="198.51.100.80")
akis(tur="dns", zaman="2026-10-19 09:02:10", istemci="10.0.2.8", sunucu="10.0.0.2", ad="yasak-site.example.ornek.test")
akis(tur="http", zaman="2026-10-19 09:03:00", istemci="10.0.2.8", sunucu="10.0.5.10", istek="GET /yardim/exe-dosyalari.html HTTP/1.1\r\nHost: intranet.ornek.test\r\nUser-Agent: Mozilla/5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
akis(tur="tls", zaman="2026-10-19 09:04:00", istemci="10.0.1.15", sunucu="203.0.113.20", sni="guncelle.example")
akis(tur="tcp", zaman="2026-10-19 09:05:00", istemci="10.0.1.22", sunucu="198.51.100.7", port=22, veri="SSH-2.0-OpenSSH_9.6\r\n", yanit="SSH-2.0-OpenSSH_9.2\r\n")
akis(tur="tcp", zaman="2026-10-19 09:05:30", istemci="10.0.1.15", sunucu="10.0.5.20", port=22, veri="SSH-2.0-OpenSSH_9.6\r\n", yanit="SSH-2.0-OpenSSH_9.2\r\n")
akis(tur="tls", zaman="2026-10-19 09:04:10", istemci="10.0.1.15", sunucu="203.0.113.21", sni="cdn.guncelle.example")
akis(tur="tls", zaman="2026-10-19 09:04:20", istemci="10.0.1.15", sunucu="203.0.113.22", sni="kotuguncelle.example")
akis(tur="http", zaman="2026-10-19 09:06:00", istemci="10.0.1.15", sunucu="10.0.5.10", istek="GET /api/durum HTTP/1.1\r\nHost: intranet.ornek.test\r\nUser-Agent: curl/8.5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
for i in range(7):
    akis(tur="dns", zaman=f"2026-10-19 09:10:{i*5:02d}", istemci="10.0.3.4", sunucu="10.0.0.2", ad=f"x{i}q7.ornek-olmayan.test")
for i in range(3):
    akis(tur="dns", zaman=f"2026-10-19 09:12:{i*5:02d}", istemci="10.0.1.15", sunucu="10.0.0.2", ad=f"y{i}.ornek-olmayan.test")
for i in range(3):
    akis(tur="dns", zaman=f"2026-10-19 09:20:{i*4:02d}", istemci="10.0.1.15", sunucu="10.0.0.2", ad=f"a{i}.ornek-olmayan.test")
    akis(tur="dns", zaman=f"2026-10-19 09:20:{i*4+2:02d}", istemci="10.0.2.8", sunucu="10.0.0.2", ad=f"b{i}.ornek-olmayan.test")
```
:::

::: gorev 1 · İstemci başına NXDOMAIN
Aynı **istemci** 60 saniye içinde 5'ten fazla NXDOMAIN yanıtı aldığında, 5'i aşan her yanıt için alarm üret (`sid:1000013`). Kural yalnız `$HOME_NET`'e giden yanıtlara baksın.

```starter
alert dns any any -> $HOME_NET any (msg:"Cok sayida NXDOMAIN"; dns.rcode:3; detection_filter:track by_src, count 5, seconds 60; sid:1000013; rev:1;)
```

```test
eq({r[1] for r in sonuc}, {1000013}, "sid:1000013")
eq([(r[0], r[4]) for r in sonuc], [("2026-10-19 09:10:25", "10.0.3.4"), ("2026-10-19 09:10:30", "10.0.3.4")],
   "yalnız 10.0.3.4'ün 6. ve 7. hatası; 09:20'deki iki istemcinin üçer hatası değil")
EK5 = "".join(f'akis(tur="dns", zaman="2026-10-19 09:40:{i * 10:02d}", istemci="10.0.1.50", sunucu="10.0.0.2", ad="z{i}.ornek-olmayan.test")\n'
              for i in range(5))
eq([r for r in dene(EK5) if r[0] >= "2026-10-19 09:40"], [], "60 saniyede tam beş hata eşiği aşmaz")
EK6 = EK5 + 'akis(tur="dns", zaman="2026-10-19 09:40:50", istemci="10.0.1.50", sunucu="10.0.0.2", ad="z5.ornek-olmayan.test")\n'
eq([(r[0], r[4]) for r in dene(EK6) if r[0] >= "2026-10-19 09:40"], [("2026-10-19 09:40:50", "10.0.1.50")],
   "altıncı hata alarm verir")
```

```solution
alert dns any any -> $HOME_NET any (msg:"Cok sayida NXDOMAIN"; dns.rcode:3; detection_filter:track by_dst, count 5, seconds 60; sid:1000013; rev:1;)
```

```hint
NXDOMAIN paketinin hedefi istemcidir: `track by_dst`.
```

```setup
akis(tur="dns", zaman="2026-10-19 09:00:01", istemci="10.0.1.15", sunucu="10.0.0.2", ad="intranet.ornek.test", cevap="10.0.5.10")
akis(tur="http", zaman="2026-10-19 09:00:02", istemci="10.0.1.15", sunucu="10.0.5.10", istek="GET /indir/rapor.pdf HTTP/1.1\r\nHost: intranet.ornek.test\r\nUser-Agent: Mozilla/5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
akis(tur="dns", zaman="2026-10-19 09:01:00", istemci="10.0.1.22", sunucu="10.0.0.2", ad="yasak-site.example", cevap="198.51.100.80")
akis(tur="http", zaman="2026-10-19 09:01:01", istemci="10.0.1.22", sunucu="198.51.100.80", istek="GET /guncelleme/kurulum.exe HTTP/1.1\r\nHost: yasak-site.example\r\nUser-Agent: curl/8.5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nMZ")
akis(tur="dns", zaman="2026-10-19 09:02:00", istemci="10.0.2.8", sunucu="10.0.0.2", ad="YASAK-SITE.example", cevap="198.51.100.80")
akis(tur="dns", zaman="2026-10-19 09:02:10", istemci="10.0.2.8", sunucu="10.0.0.2", ad="yasak-site.example.ornek.test")
akis(tur="http", zaman="2026-10-19 09:03:00", istemci="10.0.2.8", sunucu="10.0.5.10", istek="GET /yardim/exe-dosyalari.html HTTP/1.1\r\nHost: intranet.ornek.test\r\nUser-Agent: Mozilla/5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
akis(tur="tls", zaman="2026-10-19 09:04:00", istemci="10.0.1.15", sunucu="203.0.113.20", sni="guncelle.example")
akis(tur="tcp", zaman="2026-10-19 09:05:00", istemci="10.0.1.22", sunucu="198.51.100.7", port=22, veri="SSH-2.0-OpenSSH_9.6\r\n", yanit="SSH-2.0-OpenSSH_9.2\r\n")
akis(tur="tcp", zaman="2026-10-19 09:05:30", istemci="10.0.1.15", sunucu="10.0.5.20", port=22, veri="SSH-2.0-OpenSSH_9.6\r\n", yanit="SSH-2.0-OpenSSH_9.2\r\n")
akis(tur="tls", zaman="2026-10-19 09:04:10", istemci="10.0.1.15", sunucu="203.0.113.21", sni="cdn.guncelle.example")
akis(tur="tls", zaman="2026-10-19 09:04:20", istemci="10.0.1.15", sunucu="203.0.113.22", sni="kotuguncelle.example")
akis(tur="http", zaman="2026-10-19 09:06:00", istemci="10.0.1.15", sunucu="10.0.5.10", istek="GET /api/durum HTTP/1.1\r\nHost: intranet.ornek.test\r\nUser-Agent: curl/8.5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
for i in range(7):
    akis(tur="dns", zaman=f"2026-10-19 09:10:{i*5:02d}", istemci="10.0.3.4", sunucu="10.0.0.2", ad=f"x{i}q7.ornek-olmayan.test")
for i in range(3):
    akis(tur="dns", zaman=f"2026-10-19 09:12:{i*5:02d}", istemci="10.0.1.15", sunucu="10.0.0.2", ad=f"y{i}.ornek-olmayan.test")
for i in range(3):
    akis(tur="dns", zaman=f"2026-10-19 09:20:{i*4:02d}", istemci="10.0.1.15", sunucu="10.0.0.2", ad=f"a{i}.ornek-olmayan.test")
    akis(tur="dns", zaman=f"2026-10-19 09:20:{i*4+2:02d}", istemci="10.0.2.8", sunucu="10.0.0.2", ad=f"b{i}.ornek-olmayan.test")
```
:::

::: gorev 2 · Pencerede bir kez
Aynı kuralı nöbetçiyi yormayacak biçimde yaz: bir istemci 60 saniyede 5 NXDOMAIN yanıtına ulaştığında **bir kez** alarm (`sid:1000014`), pencere bitene kadar o istemci için susulsun.

```starter
alert dns any any -> $HOME_NET any (msg:"NXDOMAIN esigi"; dns.rcode:3; detection_filter:track by_dst, count 5, seconds 60; sid:1000014; rev:1;)
```

```test
eq({r[1] for r in sonuc}, {1000014}, "sid:1000014")
eq([(r[0], r[4]) for r in sonuc], [("2026-10-19 09:10:20", "10.0.3.4")], "10.0.3.4 için tek alarm, beşinci yanıtta")
EK = "".join(f'akis(tur="dns", zaman="2026-10-19 09:45:{i * 2:02d}", istemci="10.0.1.60", sunucu="10.0.0.2", ad="v{i}.ornek-olmayan.test")\n'
             for i in range(12))
eq([(r[0], r[4]) for r in dene(EK) if r[0] >= "2026-10-19 09:45"], [("2026-10-19 09:45:08", "10.0.1.60")],
   "12 hatada bile pencere başına tek alarm")
```

```solution
alert dns any any -> $HOME_NET any (msg:"NXDOMAIN esigi"; dns.rcode:3; threshold:type both, track by_dst, count 5, seconds 60; sid:1000014; rev:1;)
```

```hint
`detection_filter` eşiği aşan her eşleşmede alarm verir; tek alarm için `threshold:type both, track by_dst, count 5, seconds 60;`.
```

```setup
akis(tur="dns", zaman="2026-10-19 09:00:01", istemci="10.0.1.15", sunucu="10.0.0.2", ad="intranet.ornek.test", cevap="10.0.5.10")
akis(tur="http", zaman="2026-10-19 09:00:02", istemci="10.0.1.15", sunucu="10.0.5.10", istek="GET /indir/rapor.pdf HTTP/1.1\r\nHost: intranet.ornek.test\r\nUser-Agent: Mozilla/5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
akis(tur="dns", zaman="2026-10-19 09:01:00", istemci="10.0.1.22", sunucu="10.0.0.2", ad="yasak-site.example", cevap="198.51.100.80")
akis(tur="http", zaman="2026-10-19 09:01:01", istemci="10.0.1.22", sunucu="198.51.100.80", istek="GET /guncelleme/kurulum.exe HTTP/1.1\r\nHost: yasak-site.example\r\nUser-Agent: curl/8.5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nMZ")
akis(tur="dns", zaman="2026-10-19 09:02:00", istemci="10.0.2.8", sunucu="10.0.0.2", ad="YASAK-SITE.example", cevap="198.51.100.80")
akis(tur="dns", zaman="2026-10-19 09:02:10", istemci="10.0.2.8", sunucu="10.0.0.2", ad="yasak-site.example.ornek.test")
akis(tur="http", zaman="2026-10-19 09:03:00", istemci="10.0.2.8", sunucu="10.0.5.10", istek="GET /yardim/exe-dosyalari.html HTTP/1.1\r\nHost: intranet.ornek.test\r\nUser-Agent: Mozilla/5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
akis(tur="tls", zaman="2026-10-19 09:04:00", istemci="10.0.1.15", sunucu="203.0.113.20", sni="guncelle.example")
akis(tur="tcp", zaman="2026-10-19 09:05:00", istemci="10.0.1.22", sunucu="198.51.100.7", port=22, veri="SSH-2.0-OpenSSH_9.6\r\n", yanit="SSH-2.0-OpenSSH_9.2\r\n")
akis(tur="tcp", zaman="2026-10-19 09:05:30", istemci="10.0.1.15", sunucu="10.0.5.20", port=22, veri="SSH-2.0-OpenSSH_9.6\r\n", yanit="SSH-2.0-OpenSSH_9.2\r\n")
akis(tur="tls", zaman="2026-10-19 09:04:10", istemci="10.0.1.15", sunucu="203.0.113.21", sni="cdn.guncelle.example")
akis(tur="tls", zaman="2026-10-19 09:04:20", istemci="10.0.1.15", sunucu="203.0.113.22", sni="kotuguncelle.example")
akis(tur="http", zaman="2026-10-19 09:06:00", istemci="10.0.1.15", sunucu="10.0.5.10", istek="GET /api/durum HTTP/1.1\r\nHost: intranet.ornek.test\r\nUser-Agent: curl/8.5.0\r\n\r\n", yanit="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
for i in range(7):
    akis(tur="dns", zaman=f"2026-10-19 09:10:{i*5:02d}", istemci="10.0.3.4", sunucu="10.0.0.2", ad=f"x{i}q7.ornek-olmayan.test")
for i in range(3):
    akis(tur="dns", zaman=f"2026-10-19 09:12:{i*5:02d}", istemci="10.0.1.15", sunucu="10.0.0.2", ad=f"y{i}.ornek-olmayan.test")
for i in range(3):
    akis(tur="dns", zaman=f"2026-10-19 09:20:{i*4:02d}", istemci="10.0.1.15", sunucu="10.0.0.2", ad=f"a{i}.ornek-olmayan.test")
    akis(tur="dns", zaman=f"2026-10-19 09:20:{i*4+2:02d}", istemci="10.0.2.8", sunucu="10.0.0.2", ad=f"b{i}.ornek-olmayan.test")
```
:::
