---
id: p79
title: Impacket · SMB Başlığını İzlemek
summary: SMB2Packet ve SMB2Echo ile yerel kayıt üretmek; yanıt başlığında komut, bayrak, MessageID ve Status alanlarını okuyarak hazır betiğin veri akışını çözmek.
backend: wsl
timeout: 60
---

::: anlat Yapı nesnesi ile bağlantı nesnesi farklıdır
Bir Impacket betiğinde `SMB2Packet` başlık/veri yapısını temsil eder. Nesne kurmak veya `getData()` çağırmak sunucuya bağlanmaz. Bağlantı, oturum açma ve veri gönderme ayrıca gerçekleşir. Bu derste yalnız kurulu **Impacket 0.14.0.dev0** ile bellekteki kayıtlar üretilir ve okunur.

```python
from impacket.smb3structs import SMB2Packet, SMB2Echo, SMB2_ECHO

p = SMB2Packet()
p["Command"] = SMB2_ECHO
p["MessageID"] = 7
p["Data"] = SMB2Echo().getData()
ham = p.getData()
print(ham[:4].hex())
print(len(ham), ham[64:].hex())
```

SMB2'nin senkron başlığı 64 bayt; ECHO gövdesi 4 bayttır. Burada gösterilen 68 bayt, taşıma katmanının uzunluk öneki olmadan SMB2 kaydıdır. Sunucunun bunu kabul edeceği iddia edilmez: oturum, lehçe, kredi, imzalama ve bağlantının durumu ayrıca gerekir.

Kaynak: [Fortra SMB yapıları](https://github.com/fortra/impacket/blob/master/impacket/smb3structs.py), [Microsoft ECHO isteği](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/d939504d-57e2-4c0e-8ad5-1678b6fccca1).
:::

::: anlat Başlık okurken anlamı koşula bağla
| Alan | Okurken sorulacak şey |
|---|---|
| ProtocolID / StructureSize | Başlık gerçekten FE 53 4D 42 ile başlıyor ve boyu 64 mü? |
| Command | Hangi işlem? ECHO = 13 |
| Flags bit 0 | Sunucudan gelen bir yanıt mı? |
| Flags bit 1 | ASYNC düzeni mi? Bu derste desteklenmez. |
| Flags bit 3 | SIGNED işaretlenmiş mi? İşaretin varlığı imzanın doğrulandığı anlamına gelmez. |
| NextCommand | Başlık zincirinde sonraki kaydın ofseti; burada yalnız 0 desteklenir. |
| MessageID | Bu bağlantıdaki hangi istekle eşleşiyor? |
| SessionID | Hangi oturum alanı taşınıyor? |
| Status | Yanıtta NTSTATUS değeri; sıfır başarılı sonuçtur, diğer değer korunur. |

İsteklerde Status konumunun anlamı lehçeye göre değişebilir; “8. bayttaki sayı her zaman hata kodudur” diye okuma. Bu dersteki özetleyici yalnız **yanıt başlığı** kabul eder. ASYNC düzenini SYNC gibi okumak farklı alanları aynı sanmaya yol açar.

Kaynak: [Microsoft SMB2 SYNC başlığı](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/fb188936-5050-48d3-b350-dc43059638a4).

Kurulu Impacket, sabit ProtocolID alanını nesnede `str` olarak saklar; tel üzerindeki veri ise bytes'tır. Görevde ilk dört ham baytı **nesneyi kurmadan önce** kontrol ediyoruz. Böylece yanlış sabit için kütüphanenin genel exception'ı yerine görev sözleşmesindeki ValueError verilir.
:::

::: tahmin Bayrak eşitliği mi, bit testi mi?
```python
from impacket.smb3structs import SMB2Packet

p = SMB2Packet()
p["Command"] = 13
p["MessageID"] = 256
p["Flags"] = 9
p["Status"] = 0xC0000022
q = SMB2Packet(data=p.getData())
print(q["MessageID"], q["Flags"] == 1, bool(q["Flags"] & 1))
print(bool(q["Flags"] & 8), hex(q["Status"]))
```

???

```text
256 False True
True 0xc0000022
```

9 = 1 | 8: yanıt ve SIGNED bitleri birlikte işaretli. `Flags == 1` doğru yanıtı kaçırır. Buradaki imza alanı sıfırdır; bu yapay başlık **geçerli imzalı bir mesaj değildir**. Derste bitleri okumak ile kriptografik doğrulama özellikle ayrılır.
:::

::: gorev Hazır ECHO kayıt üreticisini uyarla
`echo_yaz(ileti, oturum)` fonksiyonunu tamamla. Her iki giriş bool olmayan int ve 0–`2**64 - 1` dahil aralığında olmalı; uygunsuz girişte `ValueError`.

`SMB2Packet` içinde Command=13, MessageID=ileti, SessionID=oturum olsun. Data olarak `SMB2Echo().getData()` kullan; diğer alanlar bu sınıfların varsayılanı kalsın. **68 baytlık bytes** döndür. Bu görev alanların kodlanabilir aralığını ölçer; her değerin gerçek bir bağlantıda geçerli mesaj/oturum kimliği olduğunu söylemez.

```starter
from impacket.smb3structs import SMB2Packet, SMB2Echo, SMB2_ECHO

def echo_yaz(ileti, oturum):
    p = SMB2Packet()
    p["Command"] = SMB2_ECHO
    p["MessageID"] = ileti
    return p.getData()
```
```test
f = need("echo_yaz")
for ileti in (0, 1, 255, 256, 2**32, 2**64 - 1):
    for oturum in (0, 1, 0x123456789ABCDEF0, 2**64 - 1):
        beklenen = bytearray(68)
        beklenen[:4] = b"\xfeSMB"
        beklenen[4:6] = (64).to_bytes(2, "little")
        beklenen[12:14] = (13).to_bytes(2, "little")
        beklenen[24:32] = ileti.to_bytes(8, "little")
        beklenen[40:48] = oturum.to_bytes(8, "little")
        beklenen[64:66] = (4).to_bytes(2, "little")
        eq(f(ileti, oturum), bytes(beklenen), f"ileti={ileti}, oturum={oturum}")
for yanlis in (-1, 2**64, True, "7", 7.0, None):
    raises(ValueError, f, yanlis, 0, msg="MessageID tür/sınırı")
    raises(ValueError, f, 0, yanlis, msg="SessionID tür/sınırı")

for invalid in (2**64+1,2**65-1):
    raises(ValueError,f,invalid,0,msg='MessageID üst taşma komşuları')
    raises(ValueError,f,0,invalid,msg='SessionID üst taşma komşuları')
```
```solution
from impacket.smb3structs import SMB2Packet, SMB2Echo, SMB2_ECHO

def echo_yaz(ileti, oturum):
    if any(type(x) is not int or not 0 <= x <= 2**64 - 1 for x in (ileti, oturum)):
        raise ValueError("64 bit unsigned kimlik gerekli")
    p = SMB2Packet()
    p["Command"] = SMB2_ECHO
    p["MessageID"] = ileti
    p["SessionID"] = oturum
    p["Data"] = SMB2Echo().getData()
    return p.getData()
```
```hint
Hazır kodun yalnız MessageID doldurduğuna dikkat et. Gövde ve oturum alanı da gerekir; sayının Python int olması protokol alanına sığdığını kanıtlamaz.
```
:::

::: gorev Kaydedilmiş yanıt başlığını özetle
`yanit_oku(ham, beklenen_id)` yaz. Girdi, tam paketten önceden ayrılmış **yalnız 64 baytlık başlıktır**; taşıma öneki/gövde burada yoktur.

Şunlardan biri sağlanmıyorsa `ValueError`:
- `ham` bytes ve uzunluğu tam 64; ProtocolID `b"\xfeSMB"`, StructureSize 64.
- Yanıt biti 1 açık; ASYNC biti 2 kapalı; NextCommand 0; Command 13.
- `beklenen_id` bool olmayan, unsigned 64 bit aralığında int; MessageID bununla aynı.

Gerçek `SMB2Packet(data=ham)` alanlarından `(Status, SessionID, signed_biti_bool)` döndür. Status'u bool'a indirgeme; örneğin 1, `0xC0000022` ve `0xFFFFFFFF` ayrı değerlerdir. signed sonucu yalnız bayrağı raporlar, imza doğrulamaz. Bilinen bu alt küme dışındaki ASYNC/compound kayıtlar sessizce yorumlanmaz.

```starter
from impacket.smb3structs import SMB2Packet

def yanit_oku(ham, beklenen_id):
    p = SMB2Packet(data=ham)
    return p["Status"] == 0
```
```test
f = need("yanit_oku")
def baslik(mid=0, sid=0, status=0, flags=1, command=13, size=64, nxt=0):
    # Bağımsız bayt tanığı; Impacket serializer'ı beklenen sonucu üretmiyor.
    b = bytearray(64)
    b[:4] = b"\xfeSMB"
    for start, count, value in ((4, 2, size), (8, 4, status), (12, 2, command),
                               (16, 4, flags), (20, 4, nxt), (24, 8, mid), (40, 8, sid)):
        b[start:start+count] = value.to_bytes(count, "little")
    return bytes(b)
for mid in (0, 1, 256, 2**32, 2**64 - 1):
    for flags in (1, 9):
        for status in (0, 1, 0xC0000022, 0xFFFFFFFF):
            eq(f(baslik(mid, 2**64 - 1, status, flags), mid),
               (status, 2**64 - 1, bool(flags & 8)), "Ham NTSTATUS, 64 bit kimlik ve bit testi")
eq(f(baslik(sid=0), 0), (0, 0, False), "Sıfır oturum alanı korunur")
good = baslik()
for ham in (b"", good[:-1], good+b"\0", b"\xffSMB"+good[4:], b"\xfeBAD"+good[4:],
            baslik(size=63), baslik(size=65), baslik(flags=0), baslik(flags=8),
            baslik(flags=3), baslik(flags=11), baslik(nxt=64),
            baslik(command=12), baslik(command=14), baslik(mid=1), "", bytearray(good), None):
    raises(ValueError, f, ham, 0, msg="Başlık biçimi, alt küme ve MessageID doğrulanır")
for mid in (-1, 2**64, False, True, "0", 0.0, None):
    raises(ValueError, f, good, mid, msg="Beklenen kimlik tür/sınırı")
raises(ValueError, f, baslik(mid=1), True, msg="True eşleşen MessageID olsa da int kabul edilmez")

for invalid in (2**64+1,2**65-1):
    raises(ValueError,f,good,invalid,msg='beklenen MessageID üst taşma komşuları')
```
```solution
from impacket.smb3structs import SMB2Packet

def yanit_oku(ham, beklenen_id):
    if type(beklenen_id) is not int or not 0 <= beklenen_id <= 2**64 - 1:
        raise ValueError("64 bit kimlik gerekli")
    if not isinstance(ham, bytes) or len(ham) != 64:
        raise ValueError("Yalnız 64 baytlık başlık gerekli")
    if ham[:4] != b"\xfeSMB":
        raise ValueError("SMB2 başlığı değil")
    p = SMB2Packet(data=ham)
    if p["StructureSize"] != 64:
        raise ValueError("SMB2 başlığı değil")
    flags = p["Flags"]
    if not flags & 1 or flags & 2 or p["NextCommand"] != 0:
        raise ValueError("Tek SYNC yanıtı gerekli")
    if p["Command"] != 13 or p["MessageID"] != beklenen_id:
        raise ValueError("Beklenen ECHO yanıtı değil")
    return p["Status"], p["SessionID"], bool(flags & 8)
```
```hint
Bit bayraklarında eşitlik yerine & kullan. 64 baytlık bir nesnenin ayrıştırılabilmesi, beklediğin istekle eşleştiği anlamına gelmez.
```
:::

::: anlat Betik okuma köprüsünü kullan
Hazır betikte seçeneklerin hangi nesne alanına gittiğini izle: hedef adı, kimlik bilgisi ve bağlantı seçeneği ile burada gördüğün MessageID/SessionID alanları aynı şey değildir. Hata görünce önce import/sürüm hatasını, sonra yerel veri biçimi hatasını, en son gerçek sunucunun döndürdüğü durumu ayır.

Bu dersler SID ve SMB yapıları üzerinden **yerel parse/serialize** alt kümesini tamamlar. Gerçek LDAP/SMB/RPC bağlantısı, Kerberos/NTLM oturumu, sunucu izinleri ve imza doğrulaması için ayrı AD laboratuvarı gerekir; bu testlerin geçmesi o işlemlerin denendiği anlamına gelmez.
:::
