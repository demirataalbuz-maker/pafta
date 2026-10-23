---
id: p77
title: pwntools · Yerel Süreçle Konuşmak
summary: process ve tube akışını okumak; bytes ile gönderme, satır sınırı, tam uzunluk, timeout ve EOF durumlarını ayırmak.
backend: wsl
timeout: 90
---

::: anlat Hazır betikteki tube nereden gelir?
`process([...])` yerel bir program başlatır ve ona bağlı bir **tube** verir. Aynı temel okuma/yazma arayüzü başka tube türlerinde de bulunur; bu ders yalnız geçici klasörde başlattığımız küçük Python programlarını kullanır. `sys.executable` koşucunun gerçek Linux Python'unu seçer.

```setup
import os
os.environ["PWNLIB_NOTERM"] = "1"
```
```python
import sys
from subprocess import PIPE, DEVNULL
from pwnlib.context import context
from pwnlib.tubes.process import process

sunucu = "import sys; print('HAZIR', flush=True); print(sys.stdin.readline().rstrip('\\n').upper(), flush=True)"
with context.local(log_level="critical"):
    with process([sys.executable, "-u", "-c", sunucu],
                 stdout=PIPE, stderr=DEVNULL) as t:
        print(t.recvline(timeout=2))
        t.sendline(b"merhaba")
        print(t.recvline(timeout=2))
```

`sendline(b"merhaba")` veriye tube'un `newline` değerini ekler (varsayılan `b"\n"`); `send` eklemez. `bytes` gönder: UTF-8 metni gerekiyorsa açıkça encode et. Bu örnekte `recvline` satırsonunu da döndürür.

`process` varsayılan stdout'u PTY, stderr'i stdout'a birleşik açar. Burada `stdout=PIPE` ile ham bayt akışı seçiyoruz, çocuk Python'un tamponunu `-u` ile kaldırıyoruz. Oyuncak programlarda stderr'i `DEVNULL`'a yönlendiriyoruz; gerçek bir araçta tanı bilgisi gerekiyorsa ayrı dosyada veya `proc.stderr` üzerinden toplanmalı. `with` bloğu tube'u kapatır; program açık kalsa da dersin çocuk süreci kalıcı bırakılmaz.

Kaynak: [process](https://docs.pwntools.com/en/stable/tubes/processes.html), [tube send/sendline ve kapatma](https://docs.pwntools.com/en/stable/tubes.html).
:::

::: anlat Timeout, EOF ve eksik veri
| Çağrı | Başarılı sonuç | Süre dolarsa | Akış kapanırsa |
|---|---|---|---|
| `recv(n)` | En fazla n bayt, daha az olabilir | `b""` | Veri kalmamışsa `EOFError` |
| `recvn(n)` | Tam n bayt | `b""`; alınan kısım tamponda kalır | n tamamlanmadan `EOFError` |
| `recvline()` | Satırsonuna kadar (satırsonu dahil) | `b""`; alınan kısım tamponda kalır | Varsayılan ayarda kalan yarım satırı döndürür; tampon boşsa `EOFError` |

`recvn(0)` geçerli bir sıfır uzunluklu okumadır ve hemen `b""` verir; bunu zaman aşımı diye yorumlama. `recvline` için `b"\n"` **boş ama tamamlanmış bir satırdır**, `b""` ise timeout işaretidir.

`recvline`'ın EOF'ta yarım satır davranışı `context.throw_eof_on_incomplete_line` ile değiştirilebilir. Bu ders varsayılan `None` değerini açıkça kullanır. Tam satır isteyen kod, dönüşün `b"\n"` ile bittiğini ayrıca denetler. `strip()` protokol verisindeki gerçek boşlukları da siler.

Uzunluk önekli kayıtta başlık bir defa tüketilince aynı fonksiyonu baştan çağırmak kaldığın yerden devam etmek değildir. Yeniden deneme için başlık/gövde durumunu saklayan bir okuyucu gerekir. Aşağıdaki ikinci görev **tek okuma girişimini** değerlendirir; timeout sonrasında tekrar aynı fonksiyonla devam edeceğini iddia etmez.

Kaynak: [recv, recvn, recvline ve tampon davranışı](https://docs.pwntools.com/en/stable/tubes.html).
:::

::: tahmin Önce tampon, sonra kalan bayt
Çocuk program tek bayt yazıp bizden devam komutu bekliyor. Böylece ilk timeout bilgisayar hızına bağlı bir uyku yarışı değildir.

```setup
import os
os.environ["PWNLIB_NOTERM"] = "1"
```
```python
import sys
from subprocess import PIPE, DEVNULL
from pwnlib.context import context
from pwnlib.tubes.process import process

kod = "import sys; sys.stdout.buffer.write(b'A'); sys.stdout.flush(); sys.stdin.buffer.read(1); sys.stdout.buffer.write(b'B\\n'); sys.stdout.flush()"
with context.local(log_level="critical", throw_eof_on_incomplete_line=None):
    with process([sys.executable, "-u", "-c", kod],
                 stdout=PIPE, stderr=DEVNULL) as t:
        ilk = t.recvn(1, timeout=5)
        assert ilk == b"A"
        t.unrecv(ilk)  # Okuduğumuzu gerçek tube tamponuna geri koy.
        print(repr(t.recvn(3, timeout=0.1)))
        t.send(b"!")
        print(repr(t.recvn(3, timeout=5)))
        try:
            t.recvn(1, timeout=5)
        except EOFError:
            print("EOF")
```

???

```text
b''
b'AB\n'
EOF
```

İlk çağrı üç baytı tamamlayamaz; A kaybolmaz. Devam komutu gelince B ve LF yazılır, ikinci çağrı üç baytın tamamını alır. Son çağrıda akış kapalı ve boş olduğu için EOFError oluşur.
:::

::: gorev Satırı kayıpsız sınıflandır
`satir_al(t, sure)` yaz. LF kullanan gerçek bir tube alır; `sure` pozitif timeout süresidir. Sonucu aşağıdaki biçimde döndür:

| Durum | Dönen tuple |
|---|---|
| LF ile tamamlanmış satır | `("tam", satirsonu_haric_bytes)` |
| EOF'ta kalan LF'siz veri | `("eksik", kalan_bytes)` |
| Timeout | `("zaman", b"")` |
| Tampon boşken EOFError | `("eof", b"")` |

Yalnız **son bir LF** kaldırılır; ön/son boşluklar, CR ve NUL korunur. Tube'u kapatma; yaşam döngüsü çağırana ait. Çağıran varsayılan yarım satır davranışını seçer.

```setup
import os
os.environ["PWNLIB_NOTERM"] = "1"
```
```starter
def satir_al(t, sure):
    return "tam", t.recvline(timeout=sure).strip()
```
```test
import sys
from subprocess import PIPE, DEVNULL
from pwnlib.context import context
from pwnlib.tubes.process import process

f = need("satir_al")
def baslat(veri, bekle=False):
    kod = ("import sys; sys.stdout.buffer.write(bytes.fromhex(sys.argv[1])); "
           "sys.stdout.flush(); " + ("sys.stdin.buffer.read(1)" if bekle else "pass"))
    return process([sys.executable, "-u", "-c", kod, veri.hex()],
                   stdout=PIPE, stderr=DEVNULL)

with context.local(log_level="critical", throw_eof_on_incomplete_line=None):
    for veri, beklenen in ((b"\n", ("tam", b"")), (b"A\n", ("tam", b"A")),
                           (b"  A \r\n", ("tam", b"  A \r")), (b"\x00\xff\n", ("tam", b"\x00\xff")),
                           (b"A", ("eksik", b"A")), (b" ", ("eksik", b" ")),
                           (b"", ("eof", b""))):
        with baslat(veri) as t:
            eq(f(t, 5), beklenen, f"Satır: {veri!r}")
    with baslat(b"A\n\n") as t:
        eq(f(t, 5), ("tam", b"A"), "İlk satır")
        eq(f(t, 5), ("tam", b""), "İkinci boş satır kaybolmaz")
        eq(f(t, 5), ("eof", b""), "İki satırdan sonra EOF")
    with baslat(b"X", bekle=True) as t:
        eq(t.recvn(1, timeout=5), b"X", "Çocuk hazır")
        eq(f(t, 0.1), ("zaman", b""), "Boş tampon, açık süreç: timeout")
        t.unrecv(b"K")
        eq(f(t, 0.1), ("zaman", b""), "Yarım satır, açık süreç: timeout")
        t.send(b"!")
        eq(f(t, 5), ("eksik", b"K"), "Timeout sonrası tampon korunur")
```
```solution
def satir_al(t, sure):
    try:
        ham = t.recvline(timeout=sure)
    except EOFError:
        return "eof", b""
    if ham == b"":
        return "zaman", b""
    if ham.endswith(b"\n"):
        return "tam", ham[:-1]
    return "eksik", ham
```
```hint
Önce EOFError'ı ayır. Sonra boş dönüşü ve LF ile tamamlanmış satırı denetle. strip/rstrip yerine yalnız son baytı kaldır.
```
:::

::: gorev Uzunluk önekli yanıtı tam oku
Bu görevde biçim P76'dan daha küçük: **iki bayt big-endian unsigned uzunluk + o kadar gövde**. Uzunluk 0–16 dahil olmalı. `kayit_al(t, sure)` yaz:

- Önce başlığı `recvn(2)`, ardından gerekiyorsa gövdeyi `recvn(uzunluk)` ile oku.
- Tam kayıtta `("tam", govde)`, herhangi bir okumada timeout'ta `("zaman", b"")`, tamamlanmadan EOF'ta `("eof", b"")` döndür.
- Uzunluk 16'dan büyükse `ValueError` yükselt; gövdeyi bekleme.
- 0 uzunluğu geçerlidir; gövde okuması gerekmez.
- Her `recvn` çağrısına `timeout=sure` ver. Bu **okuma başına sınırdır**, bütün işlem için tek süre bütçesi değildir. Tube'u kapatma ve sonraki kaydın baytlarını tüketme.

```setup
import os
os.environ["PWNLIB_NOTERM"] = "1"
```
```starter
from pwnlib.util.packing import u16

def kayit_al(t, sure):
    n = u16(t.recv(2, timeout=sure), endian="big")
    return "tam", t.recv(n, timeout=sure)
```
```test
import sys
from subprocess import PIPE, DEVNULL
from pwnlib.context import context
from pwnlib.tubes.process import process

f = need("kayit_al")
def baslat(veri, bekle=False):
    kod = ("import sys; sys.stdout.buffer.write(bytes.fromhex(sys.argv[1])); "
           "sys.stdout.flush(); " + ("sys.stdin.buffer.read(1)" if bekle else "pass"))
    return process([sys.executable, "-u", "-c", kod, veri.hex()],
                   stdout=PIPE, stderr=DEVNULL)

with context.local(log_level="critical", signed=True, endian="little"):
    for govde in (b"", b"\0", b"AB\n\0\xff", bytes(range(15)), bytes(range(16))):
        veri = len(govde).to_bytes(2, "big") + govde
        with baslat(veri + b"\0\1Z") as t:
            eq(f(t, 5), ("tam", govde), f"Uzunluk {len(govde)}")
            eq(f(t, 5), ("tam", b"Z"), "Sonraki kayıt tüketilmez")
    for veri in (b"", b"\0", b"\0\1", b"\0\2X", b"\0\x10" + b"x" * 15):
        with baslat(veri) as t:
            eq(f(t, 5), ("eof", b""), "Eksik başlık veya gövde EOF")
    for n in (17, 32768, 65535):
        with baslat(n.to_bytes(2, "big"), bekle=True) as t:
            baslik = t.recvn(2, timeout=5)
            eq(baslik, n.to_bytes(2, "big"), "Geçersiz başlık hazır")
            t.unrecv(baslik)
            raises(ValueError, f, t, 0.1, msg=f"{n}: geçersiz uzunluk, gövde beklenmez")
    # Çocuk X sonrası okuyucudan komut bekler: timeout için uyku yarışı yok.
    with baslat(b"X", bekle=True) as t:
        eq(t.recvn(1, timeout=5), b"X", "Çocuk hazır")
        eq(f(t, 0.1), ("zaman", b""), "Boş başlık timeout")
        t.unrecv(b"\0")
        eq(f(t, 0.1), ("zaman", b""), "Yarım başlık timeout")
        eq(t.recvn(1, timeout=0.1), b"\0", "Başlığın kısmi baytı tutuldu")
        t.unrecv(b"\0\2A")
        eq(f(t, 0.1), ("zaman", b""), "Başlık tam, gövde yarım: timeout")
        eq(t.recvn(1, timeout=0.1), b"A", "Gövdenin kısmi baytı tutuldu")
```
```solution
from pwnlib.util.packing import u16

def kayit_al(t, sure):
    try:
        baslik = t.recvn(2, timeout=sure)
        if baslik == b"":
            return "zaman", b""
        n = u16(baslik, endian="big", sign=False)
        if n > 16:
            raise ValueError("Gövde en fazla 16 bayt")
        if n == 0:
            return "tam", b""
        govde = t.recvn(n, timeout=sure)
        if govde == b"":
            return "zaman", b""
        return "tam", govde
    except EOFError:
        return "eof", b""
```
```hint
recv en fazla, recvn tam miktarı ister. Başlık açılırken sign=False ver; dış context işaretli olabilir. 0 uzunluğu ile pozitif uzunlukta boş dönüş aynı durum değildir.
```
:::

::: anlat Bir betiği uyarlarken kontrol sırası
Önce yorumlayıcı/paket sürümünü, sonra tube'un yerel süreç mi başka bağlantı mı olduğunu bul. Gönderilen verinin bytes mı metin mi olduğunu, endian ve alan genişliğini izle. Her okumada ayraç veya uzunluk kuralını çıkar; timeout ve EOF dallarını ayrı değerlendir. Son olarak sürecin hangi blokta kapandığını kontrol et.

Bu iki dersin ölçtüğü alt küme packing, context ve yerel process/tube akışıdır. ELF inceleme, debugger, assembly üretme ve uzak bağlantı kurulumu bu teslimin kapsamına dahil değildir. P51/P54/P55'in yerine geçmez; o bilgileri hazır pwntools betiğini anlamaya bağlar.
:::
