---
id: id05
title: Zeek · Tablolarla Sayım ve NOTICE
summary: Olaylar arasında durum tutmak: table[addr] of count ve &default; zeek_done ile özet; tablo üzerinde döngünün sırasız olması; Notice çatısı: redef enum Notice::Type, NOTICE(...) ve notice.log; bir eşiği tam bir kez geçmek (== ile >= farkı). Gerçek Zeek 9, sentetik trafik.
---

::: anlat Olaylar arasında hafıza
Tek bir olay işleyicisi yalnız o anki olayı görür. "Bu istemci kaç kez?" sorusu için olaylar arasında yaşayan bir **tablo** gerekir:

```zeek norun
global sayac: table[addr] of count &default=0;

event DNS::log_dns(rec: DNS::Info)
	{
	if ( rec?$rcode_name && rec$rcode_name == "NXDOMAIN" )
		++sayac[rec$id$orig_h];
	}

event zeek_done()
	{
	for ( h, n in sayac )
		print fmt("%s %d", h, n);
	}
```

- `table[addr] of count`: anahtarı adres, değeri sayı olan tablo.
- `&default=0`: olmayan anahtar 0 sayılır; `++sayac[h]` ilk görüşte de çalışır.
- `for ( h, n in sayac )`: anahtar ve değer üstünde döngü. Sıra **garanti değildir**; sıralı bir rapor istiyorsan sıralamayı kendin yap.

Bir tespiti `print` yerine **Notice** çatısıyla bildirmek, onu `notice.log`'a yazar. Bir SIEM'in toplayacağı ve bir analistin bakacağı yer orasıdır:

```zeek norun
@load base/frameworks/notice
redef enum Notice::Type += { Cok_NXDOMAIN };

# ... bir koşul sağlandığında:
NOTICE([$note=Cok_NXDOMAIN, $msg="açıklama", $src=h]);
```
:::

::: tahmin
Sayaç betiğinin `zeek_done`'ı `|sayac|` yazdırıyor: tablodaki anahtar sayısı. Sabah trafiğinde NXDOMAIN alan istemciler 10.0.2.8 (bir kez), 10.0.3.4 (yedi kez) ve 10.0.1.15 (üç kez). Ne yazar?

```zeek
global sayac: table[addr] of count &default=0;

event DNS::log_dns(rec: DNS::Info)
	{
	if ( rec?$rcode_name && rec$rcode_name == "NXDOMAIN" )
		++sayac[rec$id$orig_h];
	}

event zeek_done()
	{
	print |sayac|;
	}
```

???

**`3`.**

```
3
```

`|tablo|` öğe sayısıdır: üç farklı istemci. Sayımın kendisi (1, 7, 3) değerlerdedir; `&default=0` olmayan bir anahtarı **okumak** tabloya anahtar eklemez, yalnız `++` ile yazmak ekler.

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

::: gorev 1 · Eşiği aşan istemciler
Kayıt bittiğinde, **5 ya da daha fazla** NXDOMAIN yanıtı almış her istemci için bir satır yazdır: `<istemci> <sayı>` (ör. `10.0.3.4 7`). Daha az alanlar yazılmasın. Satırların sırası önemli değil.

```starter
event DNS::log_dns(rec: DNS::Info)
	{
	if ( rec?$rcode_name && rec$rcode_name == "NXDOMAIN" )
		print rec$id$orig_h;
	}
```

```test
eq(sorted(r[0] for r in sonuc), ["10.0.3.4 7"], "yalnız 10.0.3.4; 10.0.1.15'in üç hatası eşiğin altında")
EK = "".join(f'akis(tur="dns", zaman="2026-10-19 09:55:{i:02d}", istemci="10.0.1.80", sunucu="10.0.0.2", ad="t{i}.ornek-olmayan.test")\n'
             for i in range(5)) + \
     'akis(tur="dns", zaman="2026-10-19 09:56:00", istemci="10.0.1.15", sunucu="10.0.0.2", ad="y9.ornek-olmayan.test")\n'
eq(sorted(r[0] for r in dene(EK)), ["10.0.1.80 5", "10.0.3.4 7"], "tam beş hata eşiğe dahil; dördüncü hatayla 10.0.1.15 hâlâ altta")
```

```solution
global sayac: table[addr] of count &default=0;

event DNS::log_dns(rec: DNS::Info)
	{
	if ( rec?$rcode_name && rec$rcode_name == "NXDOMAIN" )
		++sayac[rec$id$orig_h];
	}

event zeek_done()
	{
	for ( h, n in sayac )
		if ( n >= 5 )
			print fmt("%s %d", h, n);
	}
```

```hint
`global sayac: table[addr] of count &default=0;` ile say, `zeek_done` içinde `for ( h, n in sayac )` ile dolaş ve `n >= 5` olanları yazdır.
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

::: gorev 2 · notice.log'a bildir
Aynı tespiti Notice çatısıyla yap: bir istemci **beşinci** NXDOMAIN yanıtını aldığı anda, o istemci için **bir** `Cok_NXDOMAIN` bildirimi üret (`$src` istemcinin adresi). Sonraki hatalar yeni bildirim üretmesin. Betik bir şey yazdırmak zorunda değil; test `notice.log`'a bakar.

```starter
@load base/frameworks/notice
redef enum Notice::Type += { Cok_NXDOMAIN };
global sayac: table[addr] of count &default=0;

event DNS::log_dns(rec: DNS::Info)
	{
	if ( ! rec?$rcode_name || rec$rcode_name != "NXDOMAIN" )
		return;
	local h = rec$id$orig_h;
	++sayac[h];
	if ( sayac[h] >= 5 )
		NOTICE([$note=Cok_NXDOMAIN, $msg=fmt("%s 5 NXDOMAIN", h), $src=h]);
	}
```

```test
bildirimler = [(n.get("note"), n.get("src")) for n in kayitlar.get("notice", [])]
eq(bildirimler, [("Cok_NXDOMAIN", "10.0.3.4")], "10.0.3.4 için tek bildirim; yedi hata yedi bildirim değil")
EK = "".join(f'akis(tur="dns", zaman="2026-10-19 09:57:{i:02d}", istemci="10.0.1.90", sunucu="10.0.0.2", ad="u{i}.ornek-olmayan.test")\n'
             for i in range(4))
dene(EK)
eq([(n.get("note"), n.get("src")) for n in kayitlar.get("notice", [])], [("Cok_NXDOMAIN", "10.0.3.4")],
   "dört hata bildirim üretmez")
BES = "".join(f'akis(tur="dns", zaman="2026-10-19 09:58:{i:02d}", istemci="10.0.1.91", sunucu="10.0.0.2", ad="t{i}.ornek-olmayan.test")\n'
              for i in range(5))
dene(BES)
eq(sorted((n.get("note"), n.get("src")) for n in kayitlar.get("notice", [])),
   [("Cok_NXDOMAIN", "10.0.1.91"), ("Cok_NXDOMAIN", "10.0.3.4")], "yeni istemcide tam beşinci hata bildirim üretir")
```

```solution
@load base/frameworks/notice
redef enum Notice::Type += { Cok_NXDOMAIN };
global sayac: table[addr] of count &default=0;

event DNS::log_dns(rec: DNS::Info)
	{
	if ( ! rec?$rcode_name || rec$rcode_name != "NXDOMAIN" )
		return;
	local h = rec$id$orig_h;
	if ( ++sayac[h] == 5 )
		NOTICE([$note=Cok_NXDOMAIN, $msg=fmt("%s 5 NXDOMAIN", h), $src=h]);
	}
```

```hint
`>= 5` beşinci, altıncı ve yedinci hatada da bildirim üretir. Eşiği tam bir kez geçmek için `== 5` kullan.
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
