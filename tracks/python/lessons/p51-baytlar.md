---
id: p51
title: Baytlar, Bitler, Kodlamalar
summary: str ile bytes farkı, UTF-8, hex ve base64, bit işleçleri, endian ve struct ile ikilik başlıklar.
kazanim: PCEP 1.4, PCAP 3.1, PCAP 5.5
---

::: anlat Metin ve bayt iki ayrı dünyadır
Python 3'te iki ayrı tür vardır:

- **`str`**: Unicode karakterler dizisi, yani *anlam*. "ş" tek bir karakterdir.
- **`bytes`**: 0–255 arası sayılar dizisi, yani *depolama ve iletim*. Diskte ve ağda dolaşan her şey bayttır.

İkisi arasında **kodlama** (encoding) köprü kurar: `str.encode()` metni bayta, `bytes.decode()` baytı metne çevirir.

```python
s = "Şifre: 42"
b = s.encode("utf-8")                    #! str → bytes
print(b)                                 #! b'...' önekli, ASCII dışı baytlar \x.. ile
print(len(s), len(b))                    #! Ş UTF-8'de 2 bayt
print(b[0], b[:2])                       #! tek bayt = int, dilim = bytes
print(b.decode("utf-8"))                 #! bytes → str
print(list("aş".encode("utf-8")))        #! baytların sayı değerleri
```

**UTF-8** değişken uzunluklu bir kodlamadır: ASCII karakterler 1 bayt, Türkçe harfler 2 bayt, çoğu Asya karakteri 3, emojiler 4 bayt tutar. Bu yüzden `len(metin)` ile `len(metin.encode())` farklı olabilir.

> [!TUZAK]
> Yanlış kodlamayla çözmek ya hata verir (`UnicodeDecodeError`) ya da daha kötüsü, sessizce bozuk metin üretir: `"ş".encode("utf-8").decode("latin-1")` → `'Å\x9f'`. Türkçe sitelerde görülen "ÅŸ" bozulmaları budur.

### Baytları göstermenin yolları
```python
import base64

veri = bytes([0, 15, 255, 72, 105])
print(veri.hex())                         #! onaltılık metin: 000fff4869
print(bytes.fromhex("48 69"))             #! geri: b'Hi'
print(base64.b64encode(veri))             #! ikilik veriyi metin kanalında taşımak için
print(base64.b64decode(b"AA//SGk="))
d = bytearray(b"abc")                     #! değiştirilebilir bayt dizisi
d[0] = 65
print(d)
```

> [!GÜVENLİK]
> **base64 şifreleme değildir**, sadece bir gösterim biçimidir; herkes geri çevirebilir. HTTP Basic Auth başlığındaki `dXNlcjpwYXNz` düz metin parolanın base64 halidir. Bu yüzden HTTP Basic Auth ancak TLS (HTTPS) içinde güvenlidir. Log ve trafik incelerken base64'ü tanımak, analistin temel refleksidir.
:::

::: tahmin
İki satır:

```python
s = "şifre"
b = s.encode("utf-8")
print(len(s), len(b), b[:2])
print(b.decode("utf-8") == s)
```

???

`5 6 b'\xc5\x9f'`, sonra `True`. "ş" UTF-8'de iki bayttır: C5 9F. Diğer dört harf birer bayt tutar, toplam 6 bayt eder.
:::

::: anlat Bitler, endian ve struct
### Bit işleçleri
| İşleç | Anlamı | Örnek |
|---|---|---|
| `a & b` | VE: ikisinde de 1 olan bitler | `0b1100 & 0b1010 = 0b1000` |
| `a \| b` | VEYA: herhangi birinde 1 | `= 0b1110` |
| `a ^ b` | ÖZEL VEYA (XOR): sadece birinde 1 | `= 0b0110` |
| `~a` | tersi (Python'da `-a-1`) | |
| `a << n` / `a >> n` | n bit sola / sağa kaydır | `1 << 4 = 16` |

```python
izin = 0o754                              #! Unix izni: rwxr-xr--
print(bin(izin))
digerleri = izin & 0b111                  #! son 3 bit: "diğerleri"
print(digerleri, bool(digerleri & 0b010)) #! 4 (sadece oku), yazma izni yok

ip = (192 << 24) | (168 << 16) | (1 << 8) | 10   #! IP adresi aslında 32 bitlik bir sayıdır
print(ip, (ip >> 8) & 0xFF)               #! 3. okteti geri çek

a, k = 0b1011, 0b0110
print(a ^ k ^ k == a)                     #! XOR kendi kendini geri alır
```

### Endian: baytların sırası
Çok baytlı bir sayı belleğe iki sırayla yazılabilir: **big-endian** (en anlamlı bayt önce, "ağ sırası") ya da **little-endian** (en anlamsız önce; x86 işlemciler).

```python
n = 0x12345678
print(n.to_bytes(4, "big").hex(), n.to_bytes(4, "little").hex())
print(int.from_bytes(b"\x00\x50", "big"))  #! 80
```

### struct: ikilik yapıları paketle/aç
Ağ protokolleri ve dosya biçimleri sabit düzenli başlıklar kullanır. `struct` bu düzenleri tanımlar:

```python
import struct

# ! = ağ sırası (big-endian), B = 1 bayt, H = 2 bayt, I = 4 bayt
baslik = struct.pack("!BBHI", 4, 0b00000010, 512, 31337)
print(baslik.hex(), len(baslik))
surum, bayrak, uzunluk, kimlik = struct.unpack("!BBHI", baslik)
print(surum, bayrak, uzunluk, kimlik)
print(struct.calcsize("!BBHI"))
```

> [!DERİN]
> Python'un `int`'i sınırsız olduğu için `~5` gibi işlemler beklenmedik görünür (`-6`), çünkü sonsuz uzunlukta bir ikiye tümleyen gibi davranır. Sabit genişlik istiyorsan **maskele**: 8 bit için `~5 & 0xFF` → 250. C ile yazılmış protokol kodlarını Python'a çevirirken bu maskeler unutulursa sayılar sessizce bozulur.
:::

::: tahmin
İki satır:

```python
print(0b1100 & 0b1010, 0b1100 | 0b1010, 0b1100 ^ 0b1010, 1 << 4, 0xff >> 4)
print((5).to_bytes(2, "big"), int.from_bytes(b"\x01\x00", "little"))
```

???

`8 14 6 16 15`, sonra `b'\x00\x05' 1`. Little-endian'da ilk bayt en anlamsızdır: `01 00` → 1.
:::

::: gorev IP ↔ tam sayı
İki fonksiyon yaz, **bit kaydırma** ile (ipaddress modülü yok):

- `ip_int("192.168.1.10")` → 32 bitlik tam sayı `3232235786`
- `int_ip(3232235786)` → `"192.168.1.10"`

```starter
def ip_int(ip):
    pass

def int_ip(n):
    pass
```

```test
need("ip_int"); need("int_ip")
eq(ip_int("192.168.1.10"), 3232235786, "192.168.1.10 → 3232235786")
eq(ip_int("0.0.0.0"), 0, "0.0.0.0 → 0")
eq(ip_int("255.255.255.255"), 2**32 - 1, "255.255.255.255 → 2^32-1")
eq(int_ip(3232235786), "192.168.1.10", "geri çevirme")
eq(int_ip(167772161), "10.0.0.1", "167772161 → 10.0.0.1")
eq(int_ip(ip_int("172.16.254.3")), "172.16.254.3", "gidiş-dönüş")
ok("ipaddress" not in src, "ipaddress modülü kullanmadan")
ok("<<" in src and ">>" in src, "<< ve >> işleçlerini kullan")
```

```solution
def ip_int(ip):
    n = 0
    for parca in ip.split("."):
        n = (n << 8) | int(parca)
    return n

def int_ip(n):
    return ".".join(str((n >> kaydir) & 0xFF) for kaydir in (24, 16, 8, 0))
```

```hint
Her oktet için sayıyı 8 bit sola kaydırıp yeni okteti VEYA'la: `n = (n << 8) | int(parca)`.
```

```hint
Geri: `(n >> 24) & 0xFF`, `(n >> 16) & 0xFF`, ...
```
:::

::: gorev Alt ağ kontrolü
`ayni_agda(ip, ag)` fonksiyonu `ag`'ı CIDR biçiminde alsın (`"10.0.0.0/16"`) ve `ip` o ağın içindeyse `True` döndürsün. Maskeyi bit işlemleriyle hesapla: `/16` → üst 16 biti 1 olan 32 bitlik sayı.

```starter
def ayni_agda(ip, ag):
    pass
```

```test
need("ayni_agda")
eq(ayni_agda("10.0.5.7", "10.0.0.0/16"), True, "10.0.5.7 ∈ 10.0.0.0/16")
eq(ayni_agda("10.1.5.7", "10.0.0.0/16"), False, "10.1.5.7 ∉ 10.0.0.0/16")
eq(ayni_agda("192.168.1.130", "192.168.1.128/25"), True, "/25 üst yarı")
eq(ayni_agda("192.168.1.127", "192.168.1.128/25"), False, "/25 alt yarı dışarıda")
eq(ayni_agda("8.8.8.8", "0.0.0.0/0"), True, "/0 her şeyi kapsar")
eq(ayni_agda("10.0.0.1", "10.0.0.1/32"), True, "/32 tek adres")
eq(ayni_agda("10.0.0.2", "10.0.0.1/32"), False, "/32 başka adres değil")
ok("ipaddress" not in src, "ipaddress modülü kullanmadan")
```

```solution
def _ip_int(ip):
    n = 0
    for p in ip.split("."):
        n = (n << 8) | int(p)
    return n

def ayni_agda(ip, ag):
    adres, bit = ag.split("/")
    bit = int(bit)
    maske = (0xFFFFFFFF << (32 - bit)) & 0xFFFFFFFF
    return (_ip_int(ip) & maske) == (_ip_int(adres) & maske)
```

```hint
Maske: `(0xFFFFFFFF << (32 - bit)) & 0xFFFFFFFF`. Sondaki `& 0xFFFFFFFF` kaydırmayla taşan bitleri atar.
```

```hint
Aynı ağda olmak: `(ip & maske) == (ag & maske)`.
```
:::

::: gorev Başlık çözücü
Bir protokolün 8 baytlık başlığı şöyle (ağ sırası, big-endian):

| Bayt | Alan | Tür |
|---|---|---|
| 0 | surum | 1 bayt |
| 1 | bayraklar | 1 bayt |
| 2–3 | uzunluk | 2 bayt |
| 4–7 | kimlik | 4 bayt |

`baslik_coz(veri)` bu alanları bir sözlük olarak döndürsün ve ayrıca `"onemli"` anahtarına bayrakların **en düşük bitinin** (bit 0) set olup olmadığını koysun. Veri 8 bayttan kısaysa `ValueError` yükselt. `struct` kullan.

```starter
import struct

def baslik_coz(veri):
    pass
```

```test
import struct
need("baslik_coz")
v = bytes.fromhex("04030200") + (31337).to_bytes(4, "big")
eq(baslik_coz(v), {"surum": 4, "bayraklar": 3, "uzunluk": 512, "kimlik": 31337, "onemli": True}, "örnek başlık")
eq(baslik_coz(struct.pack("!BBHI", 1, 2, 7, 1) + b"govde")["onemli"], False, "bayrak 2 → bit 0 kapalı (fazla bayt yok sayılır)")
raises(ValueError, baslik_coz, b"\x01\x02", msg="kısa veri → ValueError")
ok(calls("unpack") or calls("unpack_from"), "struct.unpack kullan")
```

```solution
import struct

def baslik_coz(veri):
    if len(veri) < 8:
        raise ValueError("başlık 8 bayttan kısa")
    surum, bayraklar, uzunluk, kimlik = struct.unpack("!BBHI", veri[:8])
    return {"surum": surum, "bayraklar": bayraklar, "uzunluk": uzunluk,
            "kimlik": kimlik, "onemli": bool(bayraklar & 1)}
```

```hint
Biçim metni `"!BBHI"`: ağ sırası, iki tek bayt, bir 2 baytlık, bir 4 baytlık işaretsiz sayı. İlk 8 baytı ver: `veri[:8]`.
```
:::
