---
id: id02
title: Suricata · Tamponlar ve Değiştiriciler
summary: http.host, http.user_agent ve tls.sni tamponları; aynı kuralda birden çok tampon ve her content'in kendinden önceki tampona bağlı olması; startswith, endswith ve dotprefix ile alan adını ve alt alan adlarını doğru yakalamak; content:! ile olumsuz eşleşme. Gerçek Suricata 8, sentetik trafik.
---

::: anlat Doğru tampon, dar eşleşme
Uygulama katmanı protokollerinde Suricata trafiği ayrıştırır ve alanlarını ayrı **tamponlara** koyar. Sık kullanılanlar:

| Tampon | İçinde ne var |
|---|---|
| `http.uri` | istek adresi (yol ve sorgu) |
| `http.host` | `Host:` başlığının değeri |
| `http.user_agent` | `User-Agent:` başlığının değeri |
| `dns.query` | DNS sorgusundaki ad |
| `tls.sni` | TLS el sıkışmasında istemcinin istediği sunucu adı (şifreleme başlamadan önce görünür) |

Bir kuralda birden çok tampon olabilir; her `content` kendisinden önce gelen **son** tampona bağlıdır:

```suricata norun
alert http any any -> any any (msg:"Dis sunucuya curl"; http.user_agent; content:"curl/"; startswith; http.host; content:!".ornek.test"; endswith; sid:1000011; rev:1;)
```

Burada `curl/` istemci adında başta, `!".ornek.test"` ise sunucu adında aranır: `content:!` "bu metin **yoksa**" demektir. Kural, kurum içi olmayan bir sunucuya curl ile yapılan istekleri yakalar.

Alan adlarında `endswith` tek başına yetmez: `content:"guncelle.example"; endswith;` hem `guncelle.example`'ı hem `cdn.guncelle.example`'ı yakalar, ama `kotuguncelle.example`'ı da yakalar. **`dotprefix`** tamponun başına bir nokta ekler; içeriği de noktayla yazarsan (`".guncelle.example"`) yalnız alan adının kendisi ve alt alanları eşleşir.
:::

::: tahmin
Sabah trafiğinde üç TLS el sıkışması var: SNI `guncelle.example` (09:04:00), `cdn.guncelle.example` (09:04:10) ve `kotuguncelle.example` (09:04:20). Bu kural kaç alarm üretir?

```suricata
alert tls any any -> any any (msg:"Guncelleme alani"; tls.sni; content:"guncelle.example"; endswith; nocase; sid:1000010; rev:1;)
```

???

**Üç; `kotuguncelle.example` de.**

```
2026-10-19 09:04:00|1000010|Guncelleme alani|10.0.1.15|203.0.113.20|443
2026-10-19 09:04:10|1000010|Guncelleme alani|10.0.1.15|203.0.113.21|443
2026-10-19 09:04:20|1000010|Guncelleme alani|10.0.1.15|203.0.113.22|443
```

`endswith` yalnız sonu sabitler; `kotuguncelle.example` de `guncelle.example` ile biter. Alan adı sınırını nokta belirler: `dotprefix` ile `".guncelle.example"` yazmak gerekir.

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

::: gorev 1 · Güncelleme alanı ve alt alanları
`guncelle.example` ve onun alt alan adlarına (ör. `cdn.guncelle.example`) yapılan TLS bağlantılarında alarm üret (`sid:1000010`); `kotuguncelle.example` gibi yalnız benzeyen adlar alarm vermesin. Harf büyüklüğü fark etmesin.

```starter
alert tls any any -> any any (msg:"Guncelleme alani"; tls.sni; content:"guncelle.example"; endswith; nocase; sid:1000010; rev:1;)
```

```test
eq({r[1] for r in sonuc}, {1000010}, "sid:1000010")
eq([(r[0], r[4]) for r in sonuc], [("2026-10-19 09:04:00", "203.0.113.20"), ("2026-10-19 09:04:10", "203.0.113.21")],
   "alan adı ve alt alanı; kotuguncelle.example değil")
EK = ('akis(tur="tls", zaman="2026-10-19 09:32:00", istemci="10.0.1.40", sunucu="203.0.113.30", sni="GUNCELLE.EXAMPLE")\n'
      'akis(tur="tls", zaman="2026-10-19 09:32:10", istemci="10.0.1.40", sunucu="203.0.113.31", sni="guncelle.example.kotu.test")\n')
eq([r[0] for r in dene(EK) if r[0] >= "2026-10-19 09:32"], ["2026-10-19 09:32:00"],
   "büyük harfli ad yakalanır; guncelle.example ile başlayıp başka yerde biten ad yakalanmaz")
```

```solution
alert tls any any -> any any (msg:"Guncelleme alani"; tls.sni; dotprefix; content:".guncelle.example"; endswith; nocase; sid:1000010; rev:1;)
```

```hint
`tls.sni;`'den hemen sonra `dotprefix;` yaz ve içeriği noktayla başlat: `content:".guncelle.example"; endswith; nocase;`.
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

::: gorev 2 · Kurum dışına curl
`User-Agent`'ı `curl/` ile **başlayan** ve `Host`'u `.ornek.test` ile **bitmeyen** HTTP istekleri için alarm yaz (`sid:1000011`). Sabah trafiğinde kurum içi bir sunucuya (`intranet.ornek.test`) yapılan bir curl isteği de var; o alarm vermesin.

```starter
alert http any any -> any any (msg:"Dis sunucuya curl"; http.user_agent; content:"curl/"; startswith; sid:1000011; rev:1;)
```

```test
eq({r[1] for r in sonuc}, {1000011}, "sid:1000011")
eq([(r[0], r[3], r[4]) for r in sonuc], [("2026-10-19 09:01:01", "10.0.1.22", "198.51.100.80")],
   "yalnız dış sunucuya curl; intranet'e curl değil")
EK = ('akis(tur="http", zaman="2026-10-19 09:33:00", istemci="10.0.1.40", sunucu="198.51.100.90", '
      'istek="GET / HTTP/1.1\\r\\nHost: dosya.example\\r\\nUser-Agent: curl/7.88\\r\\n\\r\\n", yanit="HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nok")\n'
      'akis(tur="http", zaman="2026-10-19 09:33:20", istemci="10.0.1.40", sunucu="198.51.100.90", '
      'istek="GET / HTTP/1.1\\r\\nHost: dosya.example\\r\\nUser-Agent: Mozilla/5.0 curl/7.88\\r\\n\\r\\n", yanit="HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nok")\n'
      'akis(tur="http", zaman="2026-10-19 09:33:40", istemci="10.0.1.40", sunucu="10.0.5.11", '
      'istek="GET / HTTP/1.1\\r\\nHost: portal.ornek.test\\r\\nUser-Agent: curl/7.88\\r\\n\\r\\n", yanit="HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nok")\n'
      'akis(tur="http", zaman="2026-10-19 09:33:50", istemci="10.0.1.40", sunucu="198.51.100.91", '
      'istek="GET / HTTP/1.1\\r\\nHost: x.ornek.test.dis.example\\r\\nUser-Agent: curl/7.88\\r\\n\\r\\n", yanit="HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nok")\n')
eq([r[0] for r in dene(EK) if r[0] >= "2026-10-19 09:33"], ["2026-10-19 09:33:00", "2026-10-19 09:33:50"],
   "dış sunucuya curl yakalanır (adında .ornek.test geçen dış ad da); curl/ başta değilse ya da sunucu kurum içiyse yakalanmaz")
```

```solution
alert http any any -> any any (msg:"Dis sunucuya curl"; http.user_agent; content:"curl/"; startswith; http.host; content:!".ornek.test"; endswith; sid:1000011; rev:1;)
```

```hint
İkinci tampon `http.host;` ve ardından olumsuz içerik: `content:!".ornek.test"; endswith;`.
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
