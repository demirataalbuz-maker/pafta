---
id: id01
title: Suricata · İlk Kuralın
summary: Bir ağ tespit kuralının anatomisi (eylem, protokol, adresler ve portlar, yön, seçenekler, msg, sid, rev); uygulama katmanı tamponları (dns.query, http.uri) ve content; nocase ile büyük-küçük harf, endswith ile sonu sabitlemek; yalnız content yazmanın neden geniş kaldığı. Kurallar gerçek Suricata 8 ile, görevin ürettiği sentetik trafik kaydında çalışır.
---

::: anlat Bir paket akışı, bir kural
**Suricata**, ağ trafiğini okuyup kurallarla karşılaştıran açık kaynak bir ağ tespit motorudur. Bir SOC'ta ya ağın bir noktasında canlı trafiği izler ya da bir olaydan sonra kaydedilmiş bir trafik dosyasını (PCAP) tarar. Bu yolda ikincisini yapıyoruz: her görev küçük, sentetik bir ofis sabahı trafiği üretir; yazdığın kural dosyası bu kayıtta gerçek Suricata ile çalışır.

Bir kural tek satırdır:

```suricata norun
alert dns any any -> any any (msg:"Yasak site sorgusu"; dns.query; content:"yasak-site.example"; nocase; sid:1000001; rev:1;)
```

| Parça | Anlamı |
|---|---|
| `alert` | eylem: eşleşince alarm yaz |
| `dns` | protokol; `tcp`, `udp` gibi ağ katmanı ya da `http`, `dns`, `tls` gibi uygulama katmanı |
| `any any -> any any` | kaynak adres ve port, yön, hedef adres ve port |
| `( ... )` | seçenekler; her biri `;` ile biter |
| `msg` | alarmda görünen açıklama |
| `dns.query` | **tampon**: bundan sonraki `content` yalnız DNS sorgusundaki adda aranır |
| `content` | aranan bayt dizisi |
| `nocase` | önceki `content` büyük-küçük harfe duyarsız |
| `sid`, `rev` | kuralın kimliği ve sürümü; aynı dosyada iki kural aynı `sid`'i taşıyamaz |

Tampon kullanmak kuralın hem doğru hem hızlı olmasını sağlar: `http.uri; content:".exe";` yalnız isteğin adresine bakar; tampon yazmazsan Suricata bütün paket yükünde arar ve bir sayfanın içinde geçen ".exe" metni de alarm verir.

Çıktı her alarm için bir satırdır: `zaman | sid | mesaj | kaynak | hedef | hedef_port` (zaman UTC).

> [!NOT] Laboratuvar
> Trafik kayıtları Scapy ile üretilir ve zararsızdır: gerçek kişi ya da sistem yoktur, alan adları `.example` ve `.test` gibi ayrılmış adlardır. Suricata, WSL'deki Kali dağıtımında kuruludur ve yalnız bu kayıtları okur; ağını dinlemez, açılışta başlamaz.
:::

::: tahmin
Sabah trafiğinde dört DNS sorgusu bu adı içeriyor: `yasak-site.example` (09:01:00), `YASAK-SITE.example` (09:02:00), `yasak-site.example.ornek.test` (09:02:10, böyle bir ad yok) ve sabahın başka sorguları. Bu kural hangi sorgularda alarm verir?

```suricata
alert dns any any -> any any (msg:"Yasak site sorgusu"; dns.query; content:"yasak-site.example"; sid:1000001; rev:1;)
```

???

**İkisinde: 09:01:00 ve 09:02:10.**

```
2026-10-19 09:01:00|1000001|Yasak site sorgusu|10.0.1.22|10.0.0.2|53
2026-10-19 09:02:10|1000001|Yasak site sorgusu|10.0.2.8|10.0.0.2|53
```

`content` varsayılan olarak büyük-küçük harfe duyarlıdır: `YASAK-SITE.example` kaçtı. Ve `content` metnin **herhangi bir yerinde** eşleşir: yasak siteyle ilgisi olmayan `yasak-site.example.ornek.test` alarm verdi. İlki bir kaçırma (yanlış negatif), ikincisi bir yanlış alarm (yanlış pozitif).

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

::: gorev 1 · Yasak site sorgusu
`yasak-site.example` adının DNS sorgularında alarm üreten kuralı yaz (`sid:1000001`). Ad hangi harf büyüklüğüyle yazılırsa yazılsın yakalansın; adın **sonunda** olmadığı sorgular (ör. `yasak-site.example.ornek.test`) alarm vermesin.

```starter
alert dns any any -> any any (msg:"Yasak site sorgusu"; dns.query; content:"yasak-site.example"; sid:1000001; rev:1;)
```

```test
eq(sutunlar, ["zaman", "sid", "mesaj", "kaynak", "hedef", "hedef_port"], "alarm sütunları")
eq({r[1] for r in sonuc}, {1000001}, "sid:1000001")
eq([(r[0], r[3]) for r in sonuc], [("2026-10-19 09:01:00", "10.0.1.22"), ("2026-10-19 09:02:00", "10.0.2.8")],
   "küçük ve büyük harfli sorgu; sonda olmayan ad değil")
EK = ('akis(tur="dns", zaman="2026-10-19 09:30:00", istemci="10.0.1.40", sunucu="10.0.0.2", ad="cdn.Yasak-Site.Example", cevap="198.51.100.81")\n'
      'akis(tur="dns", zaman="2026-10-19 09:30:10", istemci="10.0.1.40", sunucu="10.0.0.2", ad="yasak-site.examples")\n')
eq([(r[0], r[3]) for r in dene(EK) if r[0] >= "2026-10-19 09:30"], [("2026-10-19 09:30:00", "10.0.1.40")],
   "alt alan adı yakalanır; 'examples' ile biten ad yakalanmaz")
```

```solution
alert dns any any -> any any (msg:"Yasak site sorgusu"; dns.query; content:"yasak-site.example"; nocase; endswith; sid:1000001; rev:1;)
```

```hint
`content`'ten sonra iki değiştirici: `nocase;` (harf büyüklüğü fark etmesin) ve `endswith;` (eşleşme tamponun sonunda bitsin).
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

::: gorev 2 · Çalıştırılabilir dosya indirme
HTTP isteklerinde adresi (`http.uri`) `.exe` ile **biten** istekler için alarm yaz (`sid:1000002`); `.EXE` de yakalansın. Sabah trafiğinde `/yardim/exe-dosyalari.html` gibi adında "exe" geçen sıradan sayfalar da var.

```starter
alert http any any -> any any (msg:"EXE indirme"; http.uri; content:"exe"; sid:1000002; rev:1;)
```

```test
eq({r[1] for r in sonuc}, {1000002}, "sid:1000002")
eq([(r[0], r[3], r[4]) for r in sonuc], [("2026-10-19 09:01:01", "10.0.1.22", "198.51.100.80")],
   "yalnız kurulum.exe indirmesi; exe-dosyalari.html sayfası değil")
EK = ('akis(tur="http", zaman="2026-10-19 09:31:00", istemci="10.0.1.40", sunucu="10.0.5.10", '
      'istek="GET /indir/SETUP.EXE HTTP/1.1\\r\\nHost: intranet.ornek.test\\r\\n\\r\\n", yanit="HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nMZ")\n'
      'akis(tur="http", zaman="2026-10-19 09:31:30", istemci="10.0.1.40", sunucu="10.0.5.10", '
      'istek="GET /belgeler/exe.txt HTTP/1.1\\r\\nHost: intranet.ornek.test\\r\\n\\r\\n", yanit="HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nok")\n'
      'akis(tur="http", zaman="2026-10-19 09:31:50", istemci="10.0.1.40", sunucu="10.0.5.10", '
      'istek="GET /araclar/flexe HTTP/1.1\\r\\nHost: intranet.ornek.test\\r\\n\\r\\n", yanit="HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nok")\n'
      'akis(tur="http", zaman="2026-10-19 09:31:55", istemci="10.0.1.40", sunucu="10.0.5.10", '
      'istek="GET /yedek/kurulum.exe.bak HTTP/1.1\\r\\nHost: intranet.ornek.test\\r\\n\\r\\n", yanit="HTTP/1.1 200 OK\\r\\nContent-Length: 2\\r\\n\\r\\nok")\n')
eq([r[0] for r in dene(EK) if r[0] >= "2026-10-19 09:31"], ["2026-10-19 09:31:00"],
   "SETUP.EXE yakalanır; exe.txt, noktasız biten /araclar/flexe ve ortasında .exe geçen kurulum.exe.bak yakalanmaz")
```

```solution
alert http any any -> any any (msg:"EXE indirme"; http.uri; content:".exe"; endswith; nocase; sid:1000002; rev:1;)
```

```hint
Aranan metni noktasıyla yaz (`".exe"`) ve sona sabitle (`endswith`). `nocase` büyük harfli uzantıyı da yakalar.
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
