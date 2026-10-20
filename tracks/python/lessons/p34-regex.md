---
id: p34
title: re · Desenle Metin Avı
summary: Düzenli ifadeler; search, findall, sub, gruplar, adlı gruplar, açgözlülük ve ReDoS.
---

::: anlat Metinde desen aramak
`split` ve `in` sabit metinler için iyidir. Peki "bir IP adresi", "bir e-posta" ya da "`for` kelimesinden sonra gelen kullanıcı adı" gibi **desenleri** nasıl ararsın? Cevap **düzenli ifadeler** (regular expressions, regex): metin için küçük bir desen dili.

```python
import re

satir = "Oct 19 08:02:10 sshd[812]: Failed password for root from 203.0.113.9 port 40022"
m = re.search(r"from (\d+\.\d+\.\d+\.\d+)", satir)   #! r"..." ham metin, şart
if m:                                                 #! eşleşme yoksa None döner
    print(m.group(0))       #! eşleşen tüm metin
    print(m.group(1))       #! 1. parantez grubu
print(re.findall(r"\d+", satir))                      #! tüm eşleşmeler, liste
```

### Desen alfabesi
| Desen | Anlamı |
|---|---|
| `.` | satır sonu hariç herhangi bir karakter |
| `\d` / `\D` | rakam / rakam olmayan |
| `\w` / `\W` | harf, rakam, `_` / olmayan |
| `\s` / `\S` | boşluk karakteri / olmayan |
| `[abc]` / `[^abc]` / `[a-z]` | küme / küme dışı / aralık |
| `*` `+` `?` | 0+, 1+, 0 ya da 1 tekrar |
| `{3}` / `{1,3}` | tam 3 / 1 ile 3 arası tekrar |
| `^` / `$` | satır başı / sonu |
| `\b` | kelime sınırı |
| `(...)` / `(?:...)` | yakalayan grup / yakalamayan grup |
| `a\|b` | a ya da b |
| `\.` | gerçek nokta (kaçış) |

### Temel fonksiyonlar
```python
import re

print(re.match(r"\d+", "443/tcp"))           #! sadece BAŞTAN eşleşir
print(re.search(r"tcp", "443/tcp"))          #! herhangi bir yerde
print(re.fullmatch(r"\d{1,5}", "443"))       #! TÜM metin desene uymalı (doğrulama için)
print(re.sub(r"\d", "#", "pin: 1234"))       #! değiştir
print(re.split(r"[;,\s]+", "a, b;c  d"))     #! desenle böl
for m in re.finditer(r"(\w+)=(\w+)", "a=1 b=2"):
    print(m.group(1), m.group(2), m.span())  #! konum bilgisiyle tek tek
```

> [!TUZAK]
> Doğrulama için `match` ya da `search` değil **`fullmatch`** (ya da `^...$`) kullan. `re.match(r"\d+", "443; rm -rf /")` eşleşir, çünkü baştaki 443 desene uyar ve geri kalanına hiç bakılmaz!
:::

::: tahmin
İki satır:

```python
import re
s = "Failed password for root from 203.0.113.9 port 40022"
m = re.search(r"for (\w+) from ([\d.]+)", s)
print(m.group(1), m.group(2))
print(re.findall(r"\d+", "a1b22c333"))
```

???

`root 203.0.113.9`, sonra `['1', '22', '333']`. `[\d.]+` "rakam ya da nokta, bir veya daha fazla" demektir. `\d+` açgözlüdür: ardışık bütün rakamları tek eşleşmede alır.
:::

::: anlat Adlı gruplar, açgözlülük, derleme
**Adlı gruplar** `(?P<ad>...)` desenini kendini belgeleyen hale getirir:

```python
import re

DESEN = re.compile(r"""
    Failed\ password\ for\ (?:invalid\ user\ )?   # isteğe bağlı 'invalid user'
    (?P<kullanici>\S+)\ from\ (?P<ip>[\d.]+)\ port\ (?P<port>\d+)
""", re.VERBOSE)                                   #! VERBOSE: boşluk ve yorum serbest

for satir in ["Failed password for root from 203.0.113.9 port 40022",
              "Failed password for invalid user admin from 198.51.100.4 port 51000"]:
    m = DESEN.search(satir)
    print(m.groupdict())
```

`re.compile` deseni bir kez derler ve tekrar tekrar kullanırsın. Milyonlarca log satırında fark yaratır. Diğer bayraklar: `re.IGNORECASE`, `re.MULTILINE` (`^`/`$` her satırda), `re.DOTALL` (`.` satır sonunu da kapsar).

### Açgözlü ve tembel
`*` ve `+` **açgözlüdür** (greedy): olabildiğince **çok** karakter yutar. Sonlarına `?` eklersen **tembel** (lazy) olurlar ve olabildiğince **az** yutarlar:

```python
import re
html = '<a href="x">bir</a><a href="y">iki</a>'
print(re.findall(r'href="(.*)"', html))     #! açgözlü: ilk " ile SON " arası
print(re.findall(r'href="(.*?)"', html))    #! tembel: her seferinde en yakın "
print(re.findall(r'href="([^"]*)"', html))  #! en iyisi: "tırnak olmayan" kümesi
```

`re.sub`'a metin yerine **fonksiyon** da verebilirsin; her eşleşme için çağrılır:

```python
import re
print(re.sub(r"\d+", lambda m: str(int(m.group()) * 2), "3 elma 10 armut"))
```

> [!GÜVENLİK]
> **ReDoS** (Regular expression Denial of Service): `(a+)+$` gibi iç içe tekrarlı desenler, eşleşmeyen bir girdide üstel sayıda geri izleme (backtracking) yapar. 30 karakterlik bir girdi bile sunucuyu dakikalarca kilitleyebilir. 2019'da Cloudflare'in tüm ağını 27 dakika düşüren olay bir WAF kuralındaki böyle bir desendi. Kural: iç içe niceleyicilerden (`(x+)+`, `(x*)*`, `(a|a)*`) kaçın, girdi uzunluğunu sınırla, mümkünse `[^"]*` gibi kesin kümeler kullan.

> [!NOT]
> Regex güçlüdür ama her şeyin cevabı değildir. HTML/XML ayrıştırmak için gerçek ayrıştırıcılar, IP doğrulamak için `ipaddress` modülü, tarih için `datetime.strptime` kullanılır. Yol haritasındaki **Regex** yolu SIEM kurallarına yönelik regex'i ayrıca derinlemesine işleyecek.
:::

::: tahmin
İki satır:

```python
import re
html = "<b>kalın</b> ve <i>eğik</i>"
print(re.findall(r"<.+>", html))
print(re.findall(r"<.+?>", html))
```

???

İlk satır `['<b>kalın</b> ve <i>eğik</i>']`: açgözlü `.+` ilk `<`'den **son** `>`'ye kadar her şeyi yutar. İkinci satır `['<b>', '</b>', '<i>', '</i>']`: tembel `.+?` her seferinde en yakın `>`'de durur.
:::

::: gorev IP avcısı
`ip_bul(metin)` fonksiyonu metindeki IPv4 biçimindeki adresleri (4 grup, 1–3 rakam, noktalarla) **ilk görülme sırasıyla ve tekrarsız** liste olarak döndürsün. Daha uzun bir sayı dizisinin parçası olanları alma (kelime sınırı kullan).

```starter
import re

def ip_bul(metin):
    pass
```

```test
need("ip_bul")
m = "giriş 10.0.0.7'den, sonra 203.0.113.9 ve yine 10.0.0.7; sürüm 1.2.3 ve 12345.1.1.1.9 değil"
eq(ip_bul(m), ["10.0.0.7", "203.0.113.9"], "tekrarsız, sıralı; 1.2.3 ve uzun dizi alınmaz")
eq(ip_bul("hiç ip yok"), [], "yoksa []")
eq(ip_bul("a=192.168.1.1,b=192.168.1.2"), ["192.168.1.1", "192.168.1.2"], "virgülle bitişik")
ok(calls("findall") or calls("finditer"), "re.findall ya da finditer kullan")
```

```solution
import re

def ip_bul(metin):
    bulunan = re.findall(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.]*\d)", metin)
    return list(dict.fromkeys(bulunan))
```

```hint
Temel desen: `(?:\d{1,3}\.){3}\d{1,3}`. Yakalamayan grup `(?:...)` şart, yoksa findall sadece grubu döndürür.
```

```hint
"12345.1.1.1.9" içinden "45.1.1.1" çıkmasın diye iki uca bakış ekle: `(?<![\d.])` (öncesinde rakam/nokta yok) ve `(?![\d.]*\d)` (sonrasında devam eden sayı yok). Tekrarsız + sıralı için `dict.fromkeys`.
```
:::

::: gorev sshd satırı ayrıştırıcı
`ayristir(satir)` fonksiyonu başarısız SSH giriş satırından `{"kullanici": ..., "ip": ..., "port": int}` sözlüğünü döndürsün. "invalid user" içeren biçimi de desteklesin. Eşleşmezse `None` döndürsün. **Adlı gruplar** kullan.

```starter
import re

def ayristir(satir):
    pass
```

```test
need("ayristir")
eq(ayristir("Oct 19 08:02:10 web01 sshd[812]: Failed password for root from 203.0.113.9 port 40022 ssh2"),
   {"kullanici": "root", "ip": "203.0.113.9", "port": 40022}, "normal biçim")
eq(ayristir("sshd[813]: Failed password for invalid user admin from 198.51.100.4 port 51000 ssh2"),
   {"kullanici": "admin", "ip": "198.51.100.4", "port": 51000}, "invalid user biçimi")
eq(ayristir("sshd[811]: Accepted publickey for ali from 10.0.0.5 port 50122"), None, "başarılı giriş → None")
ok("?P<" in src, "adlı gruplar (?P<ad>...) kullan")
```

```solution
import re

DESEN = re.compile(
    r"Failed password for (?:invalid user )?(?P<kullanici>\S+) from (?P<ip>[\d.]+) port (?P<port>\d+)"
)

def ayristir(satir):
    m = DESEN.search(satir)
    if not m:
        return None
    d = m.groupdict()
    d["port"] = int(d["port"])
    return d
```

```hint
`(?:invalid user )?` isteğe bağlı, yakalamayan bir grup. `m.groupdict()` adlı grupları sözlük olarak verir.
```
:::

::: gorev E-posta maskele
`maskele(metin)` metindeki her e-posta adresinin kullanıcı kısmını ilk harfi kalacak şekilde maskelesin: `ali.veli@ornek.com` → `a***@ornek.com`. `re.sub`'a fonksiyon ver.

```starter
import re

def maskele(metin):
    pass
```

```test
need("maskele")
eq(maskele("iletişim: ali.veli@ornek.com"), "iletişim: a***@ornek.com", "tek adres")
eq(maskele("x@a.io ve root.admin@sirket.com.tr"), "x***@a.io ve r***@sirket.com.tr", "iki adres")
eq(maskele("adres yok"), "adres yok", "değişiklik yok")
ok(calls("sub"), "re.sub kullan")
```

```solution
import re

def maskele(metin):
    return re.sub(r"([\w.+-])[\w.+-]*@([\w-]+(?:\.[\w-]+)+)", lambda m: f"{m.group(1)}***@{m.group(2)}", metin)
```

```hint
Desen: ilk karakteri yakala `([\w.+-])`, geri kalanını geç `[\w.+-]*`, sonra `@` ve alan adını yakala.
```
:::
