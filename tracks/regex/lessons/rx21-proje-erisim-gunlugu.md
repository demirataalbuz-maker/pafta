---
id: rx21
title: Proje · Erişim Günlüğü Ayrıştırıcı
summary: Combined biçimindeki web sunucusu günlüğü için tek, sağlam bir desen; on bir alan, IPv6 istemci, boyutsuz yanıt, bozuk ya da boş istek satırı için ham metin yedeği, kaçışlı tırnaklı tarayıcı alanı ve zaman damgasının parçaları.
---

::: anlat Proje: her satırı ayrıştıran tek desen
RX18'de erişim günlüğünün ilk alanlarını okudun. Bu projede **bütün satırı**, sahada karşılaşacağın kenar durumlarıyla birlikte ayrıştıran bir desen kuracaksın. Hedef biçim:

```text
istemci kimlik kullanici [zaman] "istek" durum boyut "yonlendiren" "tarayici"
```

### Kenar durumları listesi
Desen yazmadan önce, standardın ve sunucuların gerçekte ürettiği satırların listesi:

| Durum | Örnek | Desene etkisi |
|---|---|---|
| IPv6 istemci | `2001:db8::7` | istemci `\S+` olmalı, IPv4 deseni değil |
| anonim kullanıcı | `-` | kullanıcı `\S+` |
| boyutsuz yanıt | `304 -` | boyut `\d+\|-` |
| boş istek | `"-"` | istek satırı yöntem/yol/protokol diye bölünemez |
| bozuk istek | `"BOZUK ISTEK"` | aynı şekilde; ham metin saklanmalı |
| tarayıcı alanında tırnak | `"izleyici/1.2 (\"dahili\")"` | tırnaklı alanlar RX15'teki gibi açılmış kalıpla |
| tarayıcı alanında köşeli parantez | `"Mozilla/5.0 [tr]"` | zaman alanı `[^\]]+` ile okunmalı, `.*` ile değil |

### Ham metin yedeği
Bozuk bir satırı **düşürmek** en kötü sonuçtur. Görmediğin satır, raporunda da yoktur. Sağlam ayrıştırıcılar istek satırını önce bütün olarak bir gruba alır, içini ise yalnızca düzgünse böler:

```text
"(?P<istek>(?P<yontem>[A-Z]+) (?P<yol>\S+) (?P<protokol>HTTP/...)|<tırnaklı metin>)"
```

`istek` her zaman doludur. Satır düzgünse `yontem`, `yol` ve `protokol` da doludur; değilse onlar `None` kalır ve satır yine de ayrıştırılmış olur.

> [!TUZAK]
> Uzun deseni `(?x)` ile yazacaksan satır sonunda boşluğu `\ ` diye kaçırma: pek çok düzenleyici satır sonundaki boşlukları siler, geriye kalan `\` ise satır sonu karakterini kaçırır ve desen gizlice bir satır sonu bekler. Bu projenin sınamaları sırasında tam olarak bu oldu. `(?x)` kipinde boşluğu her zaman `[ ]` diye yaz.

> [!İPUCU]
> Projede her görevin başlangıç kodu bir önceki adıma yakındır. Sırayla ilerle ve her adımdan sonra önceki görevlerin satırlarını da aklında tut: yeni bir kenar durumunu çözerken eskisini bozmamak, bu işin yarısıdır.
:::

::: tahmin
Bu desen tek başına bir erişim günlüğü satırında neleri yakalar?

```regex
\[[^\]]+\]
```

```stdin
192.168.1.20 - - [19/Oct/2026:08:20:11 +0300] "GET /static/app.js HTTP/1.1" 304 - "-" "Mozilla/5.0 [tr]"
```

???

İki parça: `[19/Oct/2026:08:20:11 +0300]` ve `[tr]`. Köşeli parantez tarayıcı alanında da geçebilir. Tek başına bir alan deseni yanlış parçayı da bulur. Bütün satırı soldan sağa, alan alan ve çapalı (`^...$`) yazdığında her parça kendi konumunda eşleşir ve `[tr]` tarayıcı alanının içinde kalır.
:::

::: gorev Düzgün satırlar
Düzgün satırları on bir adlı grupla ayrıştır: `istemci`, `kimlik`, `kullanici`, `zaman`, `yontem`, `yol`, `protokol`, `durum`, `boyut`, `yonlendiren`, `tarayici`. Başlangıç kodu yalnızca ilk örnek satıra göre yazılmış; anonim kullanıcıyı, boyutsuz yanıtı ve HTTP/2.0'ı da kabul edecek şekilde genelle.

```starter
^(?P<istemci>[\d.]+) - (?P<kullanici>\w+) \[(?P<zaman>[^\]]+)\] "(?P<yontem>[A-Z]+) (?P<yol>\S+) (?P<protokol>HTTP/1\.1)" (?P<durum>\d{3}) (?P<boyut>\d+) "(?P<yonlendiren>[^"]*)" "(?P<tarayici>[^"]*)"$
```

```test
L1 = '10.0.0.7 - ayse [19/Oct/2026:08:15:02 +0300] "GET /rapor?ay=10 HTTP/1.1" 200 5123 "https://pafta.local/" "Mozilla/5.0 (Windows NT 10.0)"'
L4 = '192.168.1.20 - - [19/Oct/2026:08:20:11 +0300] "GET /static/app.js HTTP/1.1" 304 - "https://pafta.local/rapor" "Mozilla/5.0 [tr]"'
L5 = '10.0.0.9 - - [19/Oct/2026:08:21:30 +0300] "PUT /api/bilet/42 HTTP/2.0" 204 0 "-" "izleyici/1.2"'
eq(adli(L1), {"istemci": "10.0.0.7", "kimlik": "-", "kullanici": "ayse", "zaman": "19/Oct/2026:08:15:02 +0300",
              "yontem": "GET", "yol": "/rapor?ay=10", "protokol": "HTTP/1.1", "durum": "200", "boyut": "5123",
              "yonlendiren": "https://pafta.local/", "tarayici": "Mozilla/5.0 (Windows NT 10.0)"}, "on bir alan")
a = adli(L4)
eq((a["kullanici"], a["boyut"], a["tarayici"]) if a else None, ("-", "-", "Mozilla/5.0 [tr]"), "anonim kullanıcı, boyutsuz yanıt")
a = adli(L5)
eq((a["yontem"], a["yol"], a["protokol"], a["durum"]) if a else None, ("PUT", "/api/bilet/42", "HTTP/2.0", "204"), "HTTP/2.0")
```

```solution
^(?P<istemci>\S+) (?P<kimlik>\S+) (?P<kullanici>\S+) \[(?P<zaman>[^\]]+)\] "(?P<yontem>[A-Z]+) (?P<yol>\S+) (?P<protokol>HTTP/\d(?:\.\d)?)" (?P<durum>\d{3}) (?P<boyut>\d+|-) "(?P<yonlendiren>[^"]*)" "(?P<tarayici>[^"]*)"$
```

```hint
Kimlik alanı için de bir grup gerekiyor: `(?P<kimlik>\S+)`. Kullanıcı `-` olabilir, `\w+` yetmez.
```

```hint
Protokol: `HTTP/\d(?:\.\d)?`. Boyut: `\d+|-`.
```
:::

::: gorev Kenar durumları
Deseni şu durumları da ayrıştıracak şekilde genişlet:

- IPv6 istemci adresi
- Boş (`"-"`) ya da bozuk istek satırı: **`istek`** adlı yeni grup istek satırının tamamını her zaman tutsun; `yontem`, `yol`, `protokol` yalnızca istek düzgünse dolsun
- Yönlendiren ve tarayıcı alanlarında kaçışlı tırnak (`\"`)

```starter
^(?P<istemci>\S+) (?P<kimlik>\S+) (?P<kullanici>\S+) \[(?P<zaman>[^\]]+)\] "(?P<yontem>[A-Z]+) (?P<yol>\S+) (?P<protokol>HTTP/\d(?:\.\d)?)" (?P<durum>\d{3}) (?P<boyut>\d+|-) "(?P<yonlendiren>[^"]*)" "(?P<tarayici>[^"]*)"$
```

```test
L1 = '10.0.0.7 - ayse [19/Oct/2026:08:15:02 +0300] "GET /rapor?ay=10 HTTP/1.1" 200 5123 "https://pafta.local/" "Mozilla/5.0 (Windows NT 10.0)"'
L2 = '2001:db8::7 - - [19/Oct/2026:08:15:09 +0300] "-" 400 - "-" "-"'
L3 = r'10.0.0.9 - - [19/Oct/2026:08:16:44 +0300] "POST /api/bilet HTTP/2.0" 201 87 "-" "izleyici/1.2 (\"dahili\")"'
B = '10.0.0.5 - - [19/Oct/2026:08:17:00 +0300] "BOZUK ISTEK" 400 0 "-" "-"'
grup_var = "istek" in rx.groupindex
ok(grup_var, "istek adlı grup olmalı")
if not grup_var:
    stop()
alanlar = ("istemci", "istek", "yontem", "yol", "protokol", "durum", "tarayici")
def ozet(satir):
    a = adli(satir)
    return tuple(a[k] for k in alanlar) if a else None
eq(ozet(L1), ("10.0.0.7", "GET /rapor?ay=10 HTTP/1.1", "GET", "/rapor?ay=10", "HTTP/1.1", "200", "Mozilla/5.0 (Windows NT 10.0)"), "düzgün satır bozulmadı")
eq(ozet(L2), ("2001:db8::7", "-", None, None, None, "400", "-"), "IPv6 ve boş istek")
eq(ozet(L3), ("10.0.0.9", "POST /api/bilet HTTP/2.0", "POST", "/api/bilet", "HTTP/2.0", "201", r'izleyici/1.2 (\"dahili\")'), "kaçışlı tırnaklı tarayıcı")
eq(ozet(B), ("10.0.0.5", "BOZUK ISTEK", None, None, None, "400", "-"), "bozuk istek ham metin olarak")
```

```solution
^(?P<istemci>\S+) (?P<kimlik>\S+) (?P<kullanici>\S+) \[(?P<zaman>[^\]]+)\] "(?P<istek>(?P<yontem>[A-Z]+) (?P<yol>\S+) (?P<protokol>HTTP/\d(?:\.\d)?)|[^"\\]*(?:\\.[^"\\]*)*)" (?P<durum>\d{3}) (?P<boyut>\d+|-) "(?P<yonlendiren>[^"\\]*(?:\\.[^"\\]*)*)" "(?P<tarayici>[^"\\]*(?:\\.[^"\\]*)*)"$
```

```hint
İstek satırını bir dış gruba al ve içine iki kol koy: önce düzgün biçim (yöntem, yol, protokol), olmazsa herhangi bir tırnaklı metin. Kollar bu sırayla denenir.
```

```hint
Tırnaklı metnin içi için RX15'in açılmış kalıbı: `[^"\\]*(?:\\.[^"\\]*)*`. Aynısını yönlendiren ve tarayıcı alanlarında da kullan.
```
:::

::: gorev Zaman damgasının parçaları
Son adım: `zaman` grubunun yerine zaman damgasını parçalarına ayır: `gun`, `ay`, `yil`, `saat` (`SS:DD:ss`), `dilim` (`+0300` gibi). Önceki görevdeki bütün satırlar yine eksiksiz ayrıştırılmalı.

```starter
^(?P<istemci>\S+) (?P<kimlik>\S+) (?P<kullanici>\S+) \[(?P<zaman>[^\]]+)\] "(?P<istek>(?P<yontem>[A-Z]+) (?P<yol>\S+) (?P<protokol>HTTP/\d(?:\.\d)?)|[^"\\]*(?:\\.[^"\\]*)*)" (?P<durum>\d{3}) (?P<boyut>\d+|-) "(?P<yonlendiren>[^"\\]*(?:\\.[^"\\]*)*)" "(?P<tarayici>[^"\\]*(?:\\.[^"\\]*)*)"$
```

```test
L1 = '10.0.0.7 - ayse [19/Oct/2026:08:15:02 +0300] "GET /rapor?ay=10 HTTP/1.1" 200 5123 "https://pafta.local/" "Mozilla/5.0 (Windows NT 10.0)"'
L2 = '2001:db8::7 - - [19/Oct/2026:08:15:09 +0300] "-" 400 - "-" "-"'
L3 = r'10.0.0.9 - - [19/Oct/2026:08:16:44 +0300] "POST /api/bilet HTTP/2.0" 201 87 "-" "izleyici/1.2 (\"dahili\")"'
L6 = '10.0.0.3 - - [01/Jan/2027:00:00:05 -0500] "GET / HTTP/1.1" 200 12 "-" "Mozilla/5.0 [tr]"'
B = '10.0.0.5 - - [19/Oct/2026:08:17:00 +0300] "BOZUK ISTEK" 400 0 "-" "-"'
gruplar_var = {"gun", "ay", "yil", "saat", "dilim"} <= set(rx.groupindex)
ok(gruplar_var, "gun, ay, yil, saat, dilim adlı grupları olmalı")
if not gruplar_var:
    stop()
def zaman(satir):
    a = adli(satir)
    return tuple(a[k] for k in ("gun", "ay", "yil", "saat", "dilim")) if a else None
eq(zaman(L1), ("19", "Oct", "2026", "08:15:02", "+0300"), "ilk satır")
eq(zaman(L6), ("01", "Jan", "2027", "00:00:05", "-0500"), "eksi saat dilimi")
ok(all(tam(s) for s in (L1, L2, L3, L6, B)), "bütün satırlar hâlâ ayrıştırılıyor")
```

```solution
^(?P<istemci>\S+) (?P<kimlik>\S+) (?P<kullanici>\S+) \[(?P<gun>\d{2})/(?P<ay>[A-Z][a-z]{2})/(?P<yil>\d{4}):(?P<saat>\d{2}:\d{2}:\d{2}) (?P<dilim>[+-]\d{4})\] "(?P<istek>(?P<yontem>[A-Z]+) (?P<yol>\S+) (?P<protokol>HTTP/\d(?:\.\d)?)|[^"\\]*(?:\\.[^"\\]*)*)" (?P<durum>\d{3}) (?P<boyut>\d+|-) "(?P<yonlendiren>[^"\\]*(?:\\.[^"\\]*)*)" "(?P<tarayici>[^"\\]*(?:\\.[^"\\]*)*)"$
```

```hint
Zaman damgası biçimi: `19/Oct/2026:08:15:02 +0300`. Ayırıcılar `/`, `:` ve boşluk.
```

```hint
`\[(?P<gun>\d{2})/(?P<ay>[A-Z][a-z]{2})/(?P<yil>\d{4}):(?P<saat>\d{2}:\d{2}:\d{2}) (?P<dilim>[+-]\d{4})\]`
```
:::
