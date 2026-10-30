---
id: id04
title: Zeek · Günlükler ve Olay İşleyiciler
summary: Zeek'in trafiği kural yerine kayda çevirmesi (conn.log, dns.log, http.log, ssl.log, files.log); olay güdümlü betik dili; protokol olayları (dns_request) ile günlük olayları (DNS::log_dns, HTTP::log_http); kayıt alanına güvenli erişim (?$), fmt, starts_with ve zeek_done. Gerçek Zeek 9 (resmi imaj), sentetik trafik.
---

::: anlat Kural değil, kayıt
Suricata "bu kurala uyan bir şey oldu mu?" diye sorar. **Zeek** ise önce her şeyi kaydeder: her bağlantı `conn.log`'a, her DNS sorgusu `dns.log`'a, her HTTP isteği `http.log`'a, her TLS el sıkışması `ssl.log`'a bir satır olarak yazılır. Avcı sonra bu günlüklere bakar. Zeek günlükleri SIEM'lere (Splunk, Sentinel, Elastic) en sık gönderilen ağ verisidir.

Zeek'in kendi betik dili **olay güdümlüdür**: Zeek trafiği okurken olaylar üretir, betiğin o olaylar için işleyicileri vardır.

```zeek norun
event dns_request(c: connection, msg: dns_msg, query: string, qtype: count, qclass: count)
	{
	print fmt("%s %s", c$id$orig_h, query);
	}
```

- `dns_request`: bir DNS sorgusu görüldüğünde.
- `c$id$orig_h`: bağlantıyı başlatan adres (`orig` istemci, `resp` sunucu); `$` kayıt alanına erişir.
- `print`: çıktıya bir satır yazar. Bu yolda çıktının her satırı sonucun bir satırıdır.

Bir de **günlük olayları** vardır: Zeek bir günlük satırını yazarken `DNS::log_dns(rec: DNS::Info)` gibi bir olay üretir. `rec` o satırın kendisidir; sorgu, yanıt kodu, cevaplar tek yerdedir. Bir alan her kayıtta bulunmayabilir (yanıt gelmemiş bir sorgunun yanıt kodu yoktur); `rec?$rcode_name` alanın var olup olmadığını sorar. Var olmayan alana erişmek betiği durdurmaz ama daha sinsi bir şey yapar: o olay işleyicisi o kayıt için yarıda kesilir ve Zeek `reporter.log`'a `field value missing` hatası yazar. Çıktıda bir şey eksik görünmez; o kaydı sessizce kaçırmış olursun.

`zeek_done` olayı kayıt bittiğinde bir kez çalışır; sayımların sonucunu orada yazdırırsın.

> [!NOT] Laboratuvar
> Betik, Zeek projesinin resmi imajında (`zeek/zeek` 9.0.0), ağı kapalı ve iş bitince silinen bir konteynerde `zeek -C -r trafik.pcap betik.zeek` ile çalışır. Testler `print` çıktısını ve Zeek'in yazdığı günlükleri (`kayitlar["dns"]` gibi) okuyabilir.
:::

::: tahmin
Bu betik ne yazar? Sabah trafiğinde 14 DNS sorgusu var.

```zeek
global n = 0;

event dns_request(c: connection, msg: dns_msg, query: string, qtype: count, qclass: count)
	{
	++n;
	}

event zeek_done()
	{
	print n;
	}
```

???

**`14`.**

```
14
```

Her sorgu bir `dns_request` olayıdır; `n` global olduğu için olaylar arasında değerini korur. `print` olay işleyicisinin içinde olsaydı 14 satır yazardı; `zeek_done` içinde olduğu için kayıt bitince tek satır yazdı.

```meta
motor: zeek
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
```
:::

::: gorev 1 · Var olmayan adlar
Yanıt kodu `NXDOMAIN` olan her DNS kaydı için bir satır yazdır: `<istemci adresi> <sorgu>` (ör. `10.0.3.4 x0q7.ornek-olmayan.test`). Zeek'in DNS günlüğü olayını (`DNS::log_dns`) kullan. Yanıt kodu bulunmayan kayıtlar (yanıt gelmemiş sorgular) `reporter.log`'a hata yazdırmasın.

```starter
event dns_request(c: connection, msg: dns_msg, query: string, qtype: count, qclass: count)
	{
	print fmt("%s %s", c$id$orig_h, query);
	}
```

```test
eq(kullanir("DNS::log_dns"), True, "DNS günlük olayını kullan")
eq([r[0] for r in sonuc],
   ["10.0.2.8 yasak-site.example.ornek.test"] + [f"10.0.3.4 x{i}q7.ornek-olmayan.test" for i in range(7)]
   + [f"10.0.1.15 y{i}.ornek-olmayan.test" for i in range(3)],
   "on bir NXDOMAIN, kayıt sırasıyla; yanıt alan sorgular yazılmaz")
eq(len(kayitlar["dns"]), 14, "dns.log'da 14 kayıt var; betik yalnız NXDOMAIN olanları yazdı")
EK = ('akis(tur="dns", zaman="2026-10-19 09:49:00", istemci="10.0.1.70", sunucu="10.0.0.2", ad="cevapsiz.test", yanit=False)\n'
      'akis(tur="dns", zaman="2026-10-19 09:50:00", istemci="10.0.1.70", sunucu="10.0.0.2", ad="son.ornek-olmayan.test")\n')
eq(dene(EK)[-1], ("10.0.1.70 son.ornek-olmayan.test",), "yeni NXDOMAIN de yazılır")
eq([r.get("message") for r in kayitlar.get("reporter", []) if r.get("level") == "Reporter::ERROR"], [],
   "yanıtsız sorgunun yanıt kodu yok: alana sormadan erişmek reporter.log'a 'field value missing' yazar")
```

```solution
event DNS::log_dns(rec: DNS::Info)
	{
	if ( rec?$rcode_name && rec$rcode_name == "NXDOMAIN" )
		print fmt("%s %s", rec$id$orig_h, rec$query);
	}
```

```hint
`event DNS::log_dns(rec: DNS::Info) { ... }` içinde önce alanın varlığını sor: `rec?$rcode_name && rec$rcode_name == "NXDOMAIN"`. Adres `rec$id$orig_h`, sorgu `rec$query`.
```

```meta
motor: zeek
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
```
:::

::: gorev 2 · curl ile yapılan istekler
`User-Agent`'ı `curl/` ile başlayan her HTTP isteği için bir satır yazdır: `<istemci> <host><uri>` (ör. `10.0.1.22 yasak-site.example/guncelleme/kurulum.exe`). HTTP günlük olayını (`HTTP::log_http`) kullan; `user_agent` alanı olmayan istekler `reporter.log`'a hata yazdırmasın.

```starter
event HTTP::log_http(rec: HTTP::Info)
	{
	print fmt("%s %s%s", rec$id$orig_h, rec$host, rec$uri);
	}
```

```test
eq(kullanir("HTTP::log_http"), True, "HTTP günlük olayını kullan")
eq([r[0] for r in sonuc], ["10.0.1.22 yasak-site.example/guncelleme/kurulum.exe", "10.0.1.15 intranet.ornek.test/api/durum"],
   "iki curl isteği; tarayıcı istekleri yazılmaz")
EK = ('akis(tur="http", zaman="2026-10-19 09:51:00", istemci="10.0.1.70", sunucu="10.0.5.10", '
      'istek="GET /saglik HTTP/1.1\\r\\nHost: intranet.ornek.test\\r\\n\\r\\n", yanit="HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nok")\n'
      'akis(tur="http", zaman="2026-10-19 09:51:30", istemci="10.0.1.70", sunucu="10.0.5.10", '
      'istek="GET /x HTTP/1.1\\r\\nHost: intranet.ornek.test\\r\\nUser-Agent: Mozilla/5.0 (curl/8)\\r\\n\\r\\n", yanit="HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nok")\n')
eq(dene(EK)[2:], [], "curl/ başta değilse yazılmaz")
eq([r.get("message") for r in kayitlar.get("reporter", []) if r.get("level") == "Reporter::ERROR"], [],
   "User-Agent'sız istekte alana sormadan erişmek reporter.log'a 'field value missing' yazar")
```

```solution
event HTTP::log_http(rec: HTTP::Info)
	{
	if ( rec?$user_agent && starts_with(rec$user_agent, "curl/") )
		print fmt("%s %s%s", rec$id$orig_h, rec$host, rec$uri);
	}
```

```hint
`rec?$user_agent && starts_with(rec$user_agent, "curl/")` koşulu; ikisi `&&` ile, varlık sorusu önce.
```

```meta
motor: zeek
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
```
:::
