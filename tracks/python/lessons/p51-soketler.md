---
id: p51
title: Soketler · TCP'nin Temeli
summary: Yerel bir sunucu ve istemci; bind, listen, accept, connect, sendall, recv ve mesaj çerçeveleme.
---

::: anlat İki uç, bir akış
Ağ üzerinden konuşan her program (tarayıcı, SSH, veritabanı istemcisi) en altta **soket** kullanır. TCP soketi iki program arasında **güvenilir, sıralı bir bayt akışıdır**. Bir taraf **sunucu** (dinler), diğeri **istemci** (bağlanır) olur.

Bu paftadaki her şey **kendi makinende** (`127.0.0.1`, loopback) çalışır: aynı programın içinde bir sunucu iş parçacığı ve bir istemci konuşturacağız.

```python
import socket, threading

def sunucu(dinleyici):
    baglanti, adres = dinleyici.accept()          #! bir istemci gelene kadar bekle
    with baglanti:
        veri = baglanti.recv(1024)                #! en fazla 1024 bayt oku
        baglanti.sendall(veri.upper())            #! hepsini gönder

dinleyici = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #! IPv4 + TCP
dinleyici.bind(("127.0.0.1", 0))                  #! port 0: işletim sistemi boş bir port seçsin
dinleyici.listen()
port = dinleyici.getsockname()[1]
threading.Thread(target=sunucu, args=(dinleyici,), daemon=True).start()

with socket.create_connection(("127.0.0.1", port), timeout=3) as istemci:
    istemci.sendall(b"merhaba soket")
    print(istemci.recv(1024))
dinleyici.close()
print("port", port, "kullanıldı")
```

| Adım | Sunucu | İstemci |
|---|---|---|
| 1 | `socket()` | `socket()` |
| 2 | `bind((ip, port))`: adrese bağlan | |
| 3 | `listen()`: dinlemeye başla | |
| 4 | `accept()`: bağlantı bekle, yeni soket al | `connect((ip, port))` |
| 5 | `recv` / `sendall` | `sendall` / `recv` |
| 6 | `close()` | `close()` |

`accept()` **yeni** bir soket döndürür: dinleyici soket kapıda beklemeye devam eder, konuşma o yeni sokette olur. Gerçek sunucular her bağlantıyı ayrı bir iş parçacığında (P54) ya da asyncio ile (P56) işler.

> [!NOT]
> Soketler **bayt** taşır, metin değil: göndermeden önce `encode()`, aldıktan sonra `decode()`. `send` verinin sadece bir kısmını gönderebilir; bu yüzden hep **`sendall`** kullan.

> [!GÜVENLİK]
> `bind(("0.0.0.0", port))` makinenin **bütün** ağ arayüzlerinden bağlantı kabul eder; `127.0.0.1` sadece aynı makineden. Geliştirme sırasında açtığın bir hata ayıklama sunucusunu yanlışlıkla `0.0.0.0`'a bağlamak, onu kafedeki ağın tamamına açmak demektir. Pafta'nın kendi sunucusu bu yüzden sadece 127.0.0.1'i dinler ve ayrıca her isteği bir belirteçle doğrular.
:::

::: tahmin
İki satır:

```python
import socket
a, b = socket.socketpair()
a.sendall(b"ping")
print(b.recv(1024))
b.sendall("ş".encode())
print(len(a.recv(10)))
a.close()
b.close()
```

???

`b'ping'`, sonra `2`. `socketpair` birbirine bağlı iki soket üretir; testler için çok kullanışlıdır. "ş" UTF-8'de 2 bayttır ve soket karakter değil bayt sayar.
:::

::: anlat TCP bir akıştır, mesaj değil
Yeni başlayanların en sık hatası: "karşı taraf `sendall(b"merhaba")` dedi, ben de `recv(1024)` ile `b"merhaba"` alırım" sanmak. TCP **mesaj sınırlarını korumaz**:

- İki ayrı `sendall` tek bir `recv`'de birleşebilir
- Tek bir büyük `sendall` birden çok `recv`'e bölünebilir
- `recv` boş `b""` döndürüyorsa karşı taraf bağlantıyı **kapatmıştır**

Bu yüzden protokoller **çerçeveleme** (framing) yapar. İki yaygın yol var: **ayraç** (her mesaj `\n` ile biter, satır tabanlı protokoller gibi) ya da **uzunluk öneki** (önce mesajın uzunluğu sabit 4 bayt olarak, sonra mesajın kendisi):

```python
import socket, struct

def tam_oku(sock, n):
    tampon = b""
    while len(tampon) < n:
        parca = sock.recv(n - len(tampon))
        if not parca:
            raise ConnectionError("bağlantı erken kapandı")
        tampon += parca
    return tampon

a, b = socket.socketpair()
for metin in ["kısa", "biraz daha uzun bir mesaj"]:
    veri = metin.encode()
    a.sendall(struct.pack("!I", len(veri)) + veri)    #! 4 bayt uzunluk + gövde

for _ in range(2):
    uzunluk = struct.unpack("!I", tam_oku(b, 4))[0]
    print(tam_oku(b, uzunluk).decode())
a.close(); b.close()
```

İki mesaj aynı anda gönderildiği halde doğru ayrıldı, çünkü alıcı her seferinde **tam olarak ne kadar okuyacağını** biliyor.

> [!DERİN]
> `recv`'in ne kadar veri döndüreceğini işletim sisteminin TCP yığını belirler: alım tamponu, Nagle algoritması (küçük paketleri biriktirme, `TCP_NODELAY` ile kapatılır) ve ağdaki parçalanma. Loopback'te test ederken her şey tek parça gelir ve hata görünmez; aynı kod gerçek ağda rastgele bozulur. Çerçeveleme hatasız protokol yazmanın ön koşuludur.
:::

::: tahmin
Çıktı tek satır:

```python
import struct
mesaj = "selam".encode()
paket = struct.pack("!I", len(mesaj)) + mesaj
print(len(paket), struct.unpack("!I", paket[:4])[0], paket[4:].decode())
```

???

`9 5 selam`. 4 baytlık uzunluk öneki + 5 baytlık gövde = 9 bayt.
:::

::: gorev Büyük harf sunucusu
`buyuk_harf_sunucusu(dinleyici)` fonksiyonunu yaz. Hazır dinleyen bir soket alacak:

1. **Bir** bağlantı kabul et
2. İstemci yazma yönünü kapatana kadar (`recv` boş dönene kadar) gelen bütün veriyi oku
3. Veriyi UTF-8 olarak çöz, büyük harfe çevir ve geri gönder
4. Bağlantıyı kapat

Testler fonksiyonunu ayrı bir iş parçacığında çalıştırıp bir istemciyle bağlanacak.

```starter
import socket

def buyuk_harf_sunucusu(dinleyici):
    pass
```

```test
import socket, threading
need("buyuk_harf_sunucusu")
def dene(gonderilecek):
    d = socket.socket()
    d.bind(("127.0.0.1", 0))
    d.listen(1)
    t = threading.Thread(target=buyuk_harf_sunucusu, args=(d,), daemon=True)
    t.start()
    c = socket.create_connection(d.getsockname(), timeout=3)
    for parca in gonderilecek:
        c.sendall(parca)
    c.shutdown(socket.SHUT_WR)
    alinan = b""
    while True:
        p = c.recv(4096)
        if not p:
            break
        alinan += p
    c.close(); t.join(3); d.close()
    return alinan.decode()
eq(dene(["merhaba dünya".encode()]), "MERHABA DÜNYA", "tek parça")
eq(dene([b"parca ", b"parca ", b"geldi"]), "PARCA PARCA GELDI", "parça parça gelen veri birleştirilmeli")
eq(dene([("x" * 5000).encode()]), "X" * 5000, "1024 bayttan büyük veri")
```

```meta
timeout: 15
```

```solution
import socket

def buyuk_harf_sunucusu(dinleyici):
    baglanti, _ = dinleyici.accept()
    with baglanti:
        veri = b""
        while True:
            parca = baglanti.recv(4096)
            if not parca:
                break
            veri += parca
        baglanti.sendall(veri.decode("utf-8").upper().encode("utf-8"))
```

```hint
`baglanti, _ = dinleyici.accept()`. Döngüde `recv`; boş bayt gelince istemci yazmayı bitirmiştir.
```

```hint
Çözmeyi verinin **tamamı** gelince yap: UTF-8'de bir harf iki parçaya bölünebilir ve yarım baytları çözmek hata verir.
```
:::

::: gorev Tam oku
`tam_oku(sock, n)` fonksiyonu soketten **tam olarak n bayt** okuyup döndürsün; veri parça parça gelse de birleştirsin. n bayt gelmeden bağlantı kapanırsa `ConnectionError` yükseltsin.

```starter
def tam_oku(sock, n):
    return sock.recv(n)
```

```meta
timeout: 15
```

```test
import socket, threading, time
need("tam_oku")
a, b = socket.socketpair()
def yavas_gonder():
    for p in [b"ab", b"cde", b"fghij"]:
        a.sendall(p)
        time.sleep(0.05)
threading.Thread(target=yavas_gonder, daemon=True).start()
eq(tam_oku(b, 10), b"abcdefghij", "parça parça gelen 10 bayt birleşmeli")
a.sendall(b"xyz")
eq(tam_oku(b, 2), b"xy", "sadece istenen kadar okumalı")
eq(tam_oku(b, 1), b"z", "kalan sonraki okumada")
a.sendall(b"12")
a.close()
raises(ConnectionError, tam_oku, b, 5, msg="erken kapanış → ConnectionError")
b.close()
```

```solution
def tam_oku(sock, n):
    tampon = b""
    while len(tampon) < n:
        parca = sock.recv(n - len(tampon))
        if not parca:
            raise ConnectionError("bağlantı erken kapandı")
        tampon += parca
    return tampon
```

```hint
Döngü: `while len(tampon) < n:` içinde `sock.recv(n - len(tampon))`. Boş parça = karşı taraf kapattı.
```
:::

::: gorev Uzunluk önekli mesajlar
İki fonksiyon yaz:

- `mesaj_gonder(sock, metin)`: metni UTF-8'e çevir, önüne 4 baytlık **big-endian** uzunluk koy ve gönder
- `mesaj_al(sock)`: önce 4 bayt uzunluğu, sonra tam o kadar gövdeyi oku ve metne çevirip döndür. Bağlantı mesajlar **arasında** temiz kapandıysa (hiç bayt gelmediyse) `None` döndür

```starter
import struct

def mesaj_gonder(sock, metin):
    pass

def mesaj_al(sock):
    pass
```

```meta
timeout: 15
```

```test
import socket, struct
need("mesaj_gonder"); need("mesaj_al")
a, b = socket.socketpair()
for m in ["selam", "", "ğüşıöç " * 100]:
    mesaj_gonder(a, m)
eq(mesaj_al(b), "selam", "1. mesaj")
eq(mesaj_al(b), "", "boş mesaj da iletilebilmeli")
eq(mesaj_al(b), "ğüşıöç " * 100, "uzun Türkçe mesaj")
a.sendall(struct.pack("!I", 3) + b"abc" + struct.pack("!I", 2) + b"de")
eq((mesaj_al(b), mesaj_al(b)), ("abc", "de"), "tek seferde gelen iki çerçeve ayrılmalı")
a.close()
eq(mesaj_al(b), None, "temiz kapanış → None")
b.close()
```

```solution
import struct

def _tam_oku(sock, n):
    tampon = b""
    while len(tampon) < n:
        parca = sock.recv(n - len(tampon))
        if not parca:
            return tampon
        tampon += parca
    return tampon

def mesaj_gonder(sock, metin):
    veri = metin.encode("utf-8")
    sock.sendall(struct.pack("!I", len(veri)) + veri)

def mesaj_al(sock):
    bas = _tam_oku(sock, 4)
    if not bas:
        return None
    if len(bas) < 4:
        raise ConnectionError("yarım başlık")
    n = struct.unpack("!I", bas)[0]
    govde = _tam_oku(sock, n)
    if len(govde) < n:
        raise ConnectionError("yarım gövde")
    return govde.decode("utf-8")
```

```hint
Başlık: `struct.pack("!I", len(veri))`. Alırken önce 4 bayt oku; hiç bayt gelmediyse `None` döndür.
```
:::
