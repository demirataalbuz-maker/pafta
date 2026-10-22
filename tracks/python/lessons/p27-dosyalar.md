---
id: p27
title: Dosyalar
summary: open, with, kipler, kodlama; satır satır okumak, yazmak, eklemek ve log süzmek.
kazanim: PCAP 5.4, PCAP 5.5
---

::: anlat Aç, kullan, kapat: with
Dosya açmak bir **kaynak** almaktır; işin bitince kapatman gerekir. `with` bunu senin yerine yapar: blok bittiğinde, **hata olsa bile**, dosya kapanır.

```python
with open("notlar.txt", "w", encoding="utf-8") as f:   #! w: yaz (varsa içeriği SİLER)
    f.write("ilk satır\n")
    f.write("ikinci satır\n")
# burada dosya kapanmış durumda

with open("notlar.txt", encoding="utf-8") as f:        #! varsayılan kip: r (oku)
    icerik = f.read()
print(icerik)
```

Tezgah her çalıştırmada boş, geçici bir klasör kullanır; dosyalarını orada oluşturup okursun.

### Kipler
| Kip | Anlamı |
|---|---|
| `"r"` | oku (varsayılan); dosya yoksa `FileNotFoundError` |
| `"w"` | yaz; dosya varsa **içeriği silinir** |
| `"a"` | sona ekle (append) |
| `"x"` | sadece dosya **yoksa** oluştur; varsa `FileExistsError` |
| `"b"` | ikilik (binary): `"rb"`, `"wb"`; `str` değil `bytes` okur/yazar |

> [!TUZAK]
> **Her zaman `encoding="utf-8"` ver.** Vermezsen Python işletim sisteminin varsayılanını kullanır; Windows'ta bu genelde `cp1254`/`cp1252`'dir. "ş", "ğ" gibi karakterler bozulur ya da `UnicodeDecodeError` alırsın. Aynı kod Linux'ta çalışıp Windows'ta patlar.

### Okumanın yolları
```python
with open("notlar.txt", "w", encoding="utf-8") as f:
    f.write("a\nb\nc\n")

with open("notlar.txt", encoding="utf-8") as f:
    print(repr(f.read()))            #! hepsi tek metin
with open("notlar.txt", encoding="utf-8") as f:
    print(f.readlines())             #! satır listesi (\n'ler dahil)
with open("notlar.txt", encoding="utf-8") as f:
    for satir in f:                  #! en iyisi: satır satır, bellek dostu
        print(satir.rstrip("\n"))
```

**Dosya nesnesi kendisi bir yineleyicidir**: `for satir in f` dosyayı satır satır okur ve belleğe tamamını yüklemez. 20 GB'lık bir log dosyasını `f.read()` ile okumaya kalkarsan RAM biter, `for` ile okursan sorunsuz akar.
:::

::: tahmin
Çıktı tek satır:

```python
with open("not.txt", "w", encoding="utf-8") as f:
    f.write("bir\n")
    f.write("iki")

with open("not.txt", encoding="utf-8") as f:
    satirlar = f.readlines()
print(len(satirlar), repr(satirlar[0]))
```

???

`2 'bir\n'`. `readlines` satır sonlarını **korur**. Son satırın sonunda `\n` olmadığı için "iki" tek başına ikinci eleman olur.
:::

::: anlat Yazmak, eklemek, imleç
```python
with open("olaylar.log", "a", encoding="utf-8") as f:
    f.write("08:00 sistem başladı\n")
    print("08:05 ali girdi", file=f)          #! print'in file= parametresi
    f.writelines(["08:10 a\n", "08:11 b\n"])  #! writelines satır sonu EKLEMEZ

with open("olaylar.log", encoding="utf-8") as f:
    print(f.readline().strip())   #! tek satır
    print(f.tell())               #! imlecin bayt konumu
    f.seek(0)                     #! başa sar
    print(len(f.read().splitlines()), "satır")
```

Hatalı baytlarla karşılaşabileceğin log dosyalarında `errors="replace"` bozuk baytları `�` ile değiştirip okumaya devam eder: `open(yol, encoding="utf-8", errors="replace")`.

> [!DERİN]
> `open` aslında katmanlı bir yapı döndürür: en altta işletim sisteminin dosya tanıtıcısı (`FileIO`, ham baytlar), üstünde arabellek (`BufferedReader`, okumaları bloklar halinde toplar), en üstte kod çözücü (`TextIOWrapper`, baytları `str`'ye çevirir ve satır sonlarını `\n`'e normalleştirir). Metin kipinde Windows'un `\r\n`'i otomatik `\n` olur. İkilik kipte (`"rb"`) en üst katman yoktur ve baytları ham görürsün.
:::

::: tahmin
Çıktı tek satır:

```python
with open("log.txt", "w") as f:
    print("a", file=f)
with open("log.txt", "a") as f:
    print("b", file=f)
with open("log.txt") as f:
    print(f.read().split())
```

???

`['a', 'b']`. "a" kipi öncekini silmeden sona ekler.
:::

::: gorev Başarısız SSH denemeleri
Çalışma klasöründe bir `auth.log` dosyası var. İçinde `Failed password` geçen satırları say ve sayıyı yazdır. Dosyayı `with` ile ve satır satır oku.

```setup
satirlar = [
    "Oct 19 08:01:22 web01 sshd[811]: Accepted publickey for ali from 10.0.0.5 port 50122",
    "Oct 19 08:02:10 web01 sshd[812]: Failed password for root from 203.0.113.9 port 40022",
    "Oct 19 08:02:12 web01 sshd[812]: Failed password for root from 203.0.113.9 port 40024",
    "Oct 19 08:03:00 web01 CRON[900]: session opened for user backup",
    "Oct 19 08:04:41 web01 sshd[813]: Failed password for invalid user admin from 198.51.100.4 port 51000",
    "Oct 19 08:05:00 web01 sshd[814]: Accepted password for veli from 10.0.0.8 port 50200",
]
with open("auth.log", "w", encoding="utf-8") as f:
    f.write("\n".join(satirlar) + "\n")
```

```starter
sayi = 0

print(sayi)
```

```test
eq(out.strip(), "3", "3 başarısız deneme var")
ok(uses("with"), "dosyayı with ile aç")
```

```solution
sayi = 0
with open("auth.log", encoding="utf-8") as f:
    for satir in f:
        if "Failed password" in satir:
            sayi += 1
print(sayi)
```

```hint
`with open("auth.log", encoding="utf-8") as f:` sonra `for satir in f:`
```
:::

::: gorev wc klonu
`say(yol)` fonksiyonu bir dosyanın `(satır_sayısı, kelime_sayısı, karakter_sayısı)` demetini döndürsün (Unix `wc` gibi). Karakter sayısına satır sonları dahildir.

```setup
with open("ornek.txt", "w", encoding="utf-8", newline="") as f:
    f.write("merhaba dünya\nikinci satır burada\n\nson\n")
with open("bos.txt", "w", encoding="utf-8") as f:
    pass
```

```starter
def say(yol):
    pass
```

```test
need("say")
eq(say("ornek.txt"), (4, 6, 39), "ornek.txt → (4, 6, 39)")
eq(say("bos.txt"), (0, 0, 0), "boş dosya → (0, 0, 0)")
```

```solution
def say(yol):
    satir = kelime = karakter = 0
    with open(yol, encoding="utf-8") as f:
        for s in f:
            satir += 1
            kelime += len(s.split())
            karakter += len(s)
    return satir, kelime, karakter
```

```hint
Satır satır dolaş; her satırda `len(s.split())` kelime, `len(s)` karakter.
```
:::

::: gorev Hata satırlarını süz
`erisim.log` her satırda `IP YÖNTEM YOL DURUM` biçiminde web erişim kayıtları içeriyor. Durum kodu **400 ve üstü** olan satırları **olduğu gibi** `hatalar.log` dosyasına yaz. Sonra kaç satır yazdığını ekrana bas.

```setup
kayitlar = """10.0.0.5 GET /index.html 200
203.0.113.9 GET /admin 403
10.0.0.5 POST /login 302
198.51.100.4 GET /../../etc/passwd 400
10.0.0.8 GET /api/kullanici 500
10.0.0.5 GET /favicon.ico 404
"""
with open("erisim.log", "w", encoding="utf-8") as f:
    f.write(kayitlar)
```

```starter
# erisim.log → hatalar.log

```

```test
eq(out.strip(), "4", "4 satır yazılmalı")
with open("hatalar.log", encoding="utf-8") as f:
    yazilan = f.read().splitlines()
eq(yazilan, ["203.0.113.9 GET /admin 403", "198.51.100.4 GET /../../etc/passwd 400",
             "10.0.0.8 GET /api/kullanici 500", "10.0.0.5 GET /favicon.ico 404"], "hatalar.log içeriği")
```

```solution
yazilan = 0
with open("erisim.log", encoding="utf-8") as giris, open("hatalar.log", "w", encoding="utf-8") as cikis:
    for satir in giris:
        parcalar = satir.split()
        if parcalar and int(parcalar[-1]) >= 400:
            cikis.write(satir)
            yazilan += 1
print(yazilan)
```

```hint
Tek `with` içinde iki dosya açabilirsin: `with open(a) as g, open(b, "w") as c:`
```

```hint
Durum kodu son alan: `int(satir.split()[-1])`.
```
:::
