---
id: rx17
title: Yapılandırılmış Metni Ayrıştırmak
summary: URL'yi şema, ana makine, port, yol, sorgu ve parça olarak bölmek (RFC 3986'nın kendi deseni), sorgu dizesi parametreleri, tırnaklı ve çift tırnak kaçışlı CSV alanları; isteğe bağlı parçaları doğru sırayla isteğe bağlı yapmak.
---

::: anlat URL'nin anatomisi
Günlüklerde, proxy kayıtlarında ve yapılandırma dosyalarında en sık ayrıştırılan yapılardan biri URL'dir:

```text
https://pafta.local:8443/ders/rx17?sekme=gorev#ipucu
└─┬─┘   └────┬────┘ └┬─┘└───┬────┘ └────┬────┘ └─┬─┘
 şema   ana makine  port   yol        sorgu    parça
```

URL standardı (RFC 3986) kendi ekinde bir regex verir. Her parçayı, kendisinden sonra gelen parçanın **başlangıç karakterini dışlayan** bir sınıfla tüketir:

```regex
^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?
---
https://pafta.local:8443/ders/rx17?sekme=gorev#ipucu
```

| Grup | Desen | Tükettiği |
|---|---|---|
| 2 | `[^:/?#]+` | şema: `:` gelene kadar |
| 4 | `[^/?#]*` | yetki alanı: `/`, `?` ya da `#` gelene kadar |
| 5 | `[^?#]*` | yol: `?` ya da `#` gelene kadar |
| 7 | `[^#]*` | sorgu: `#` gelene kadar |
| 9 | `.*` | parça: geri kalan her şey |

Kalıbın dersi şudur: **sonraki parçanın işaretini dışlayan sınıf** kullan. Böylece hiçbir parça komşusunun alanına taşmaz ve geri izlemeye gerek kalmaz.

### İsteğe bağlı parçalar
Port, yol, sorgu ve parça her URL'de olmayabilir. Her birini **ayıracıyla birlikte** isteğe bağlı bir gruba al: `(?::(?P<port>\d+))?`. İki nokta portun parçası değildir ama port yoksa iki nokta da yoktur. Grup eşleşmediğinde `adli()` sonucunda değeri `None` olur.

> [!NOT]
> Gerçek bir programda URL'yi regex'le değil standart kütüphaneyle ayrıştır: Python'da `urllib.parse.urlsplit`, PowerShell'de `[uri]`. Regex, bunların olmadığı yerde, yani SIEM sorgularında ve komut satırı araçlarında işe yarar. KQL'de ise hazır `parse_url()` fonksiyonu vardır.
:::

::: anlat Sorgu dizesi ve CSV
**Sorgu parametreleri** `?` ya da `&` ile başlar, `=` ile ayrılır ve `&` ya da `#` ile biter. Değer boş olabilir:

```regex
[?&](?P<ad>[^=&#]+)=(?P<deger>[^&#]*)
---
/ara?q=regex&sayfa=2&bos=#sonuc
```

**CSV** göründüğünden zordur: virgül içeren bir alan çift tırnak içine alınır ve alanın içindeki çift tırnak **ikilenerek** (`""`) yazılır. `[^,]+` bu yüzden yanılır:

```regex
(?:^|,)(?P<alan>"(?:[^"]|"")*"|[^,]*)
---
ali,"Yılmaz, Ayşe","dedi ki ""merhaba""",42,
```

| Parça | Görevi |
|---|---|
| `(?:^\|,)` | alan ya satır başında ya da bir virgülden sonra başlar |
| `"(?:[^"]\|"")*"` | tırnaklı alan: tırnak dışı karakterler ya da ikilenmiş tırnaklar |
| `[^,]*` | tırnaksız alan; boş da olabilir (`,,` ya da sondaki virgül) |

Tırnaklı alanı RX14'teki gibi açarak da yazabilirsin: `"[^"]*(?:""[^"]*)*"`. Burada "özel" kısım bir kaçış dizisi değil, ikilenmiş tırnaktır.

> [!TUZAK]
> Tırnaklı alanın içinde satır sonu da olabilir; satır satır okuyan hiçbir desen bunu doğru işleyemez. Gerçek CSV için Python'da `csv`, PowerShell'de `Import-Csv` kullan. Regex hızlı bir göz atmak ve bozuk satırları bulmak içindir.
:::

::: tahmin
Hangi parçalar yakalanır? Ayrı satırlara yaz.

```regex
[?&][^=&#]+=
```

```stdin
/a?x=1&y=&z#k=2
```

???

`?x=` ve `&y=`. `&z`'den sonra `=` yerine `#` gelir ve sınıf `#`'yi dışladığı için eşleşme orada kırılır. `#`'den sonraki `k=` parça (fragment) kısmındadır ve önünde `?` ya da `&` olmadığı için alınmaz.
:::

::: gorev URL parçaları
Bir URL'nin tamamını `sema`, `ana`, `port`, `yol`, `sorgu` adlı gruplarla ayrıştır. Port, yol ve sorgu isteğe bağlıdır; yoksa grupları eşleşmesin (`None`). Ana makine adında port bulunmasın.

```starter
(?P<sema>\w+)://(?P<ana>[^/]+)(?P<yol>/.*)?
```

```test
gruplar_var = {"sema", "ana", "port", "yol", "sorgu"} <= set(rx.groupindex)
ok(gruplar_var, "sema, ana, port, yol, sorgu adlı grupları olmalı")
if not gruplar_var:
    stop()
a = adli("https://pafta.local:8443/ders/rx17?sekme=gorev#ipucu")
eq((a["sema"], a["ana"], a["port"], a["yol"], a["sorgu"]), ("https", "pafta.local", "8443", "/ders/rx17", "sekme=gorev"), "bütün parçalar")
a = adli("http://ornek.com")
eq((a["sema"], a["ana"], a["port"], a["sorgu"]), ("http", "ornek.com", None, None), "yalnızca şema ve ana makine")
ok(a["yol"] in (None, ""), "yol yok")
a = adli("ftp://10.0.0.5:21/yedek/")
eq((a["ana"], a["port"], a["yol"]), ("10.0.0.5", "21", "/yedek/"), "IP adresli ana makine")
a = adli("https://ornek.com?q=1")
eq((a["ana"], a["sorgu"]), ("ornek.com", "q=1"), "yolsuz sorgu")
```

```solution
^(?P<sema>[a-z][a-z0-9+.-]*)://(?P<ana>[^:/?#]+)(?::(?P<port>\d+))?(?P<yol>/[^?#]*)?(?:\?(?P<sorgu>[^#]*))?(?:#.*)?$
```

```hint
Her parçayı, ardından gelen parçanın işaretini dışlayan bir sınıfla tüket: ana makine `[^:/?#]+`, yol `/[^?#]*`, sorgu `[^#]*`.
```

```hint
İsteğe bağlı parçaları ayıracıyla birlikte grupla: `(?::(?P<port>\d+))?`, `(?:\?(?P<sorgu>[^#]*))?`.
```
:::

::: gorev Sorgu parametreleri
Bir istek yolundaki sorgu parametrelerini `ad` ve `deger` adlı gruplarla bul. Değer boş olabilir; `#`'den sonraki kısım parametre değildir.

```starter
(?P<ad>\w+)=(?P<deger>\w+)
```

```test
eq(hepsi("/ara?q=regex&sayfa=2&bos=#sonuc"), [{"ad": "q", "deger": "regex"}, {"ad": "sayfa", "deger": "2"}, {"ad": "bos", "deger": ""}], "üç parametre, biri boş")
eq(hepsi("/rapor?ay=10&tur=aylik-ozet#k=v"), [{"ad": "ay", "deger": "10"}, {"ad": "tur", "deger": "aylik-ozet"}], "tireli değer, parçadaki k=v hariç")
```

```solution
[?&](?P<ad>[^=&#]+)=(?P<deger>[^&#]*)
```

```hint
Parametre `?` ya da `&` ile başlar. Değer `&` ya da `#` gelene kadar sürer ve boş olabilir: `[^&#]*`.
```
:::

::: gorev CSV alanları
Bir CSV satırının alanlarını `alan` adlı grupla bul. Tırnaklı alanlar virgül ve ikilenmiş tırnak (`""`) içerebilir; tırnaklar alanın parçası olarak kalsın. Boş alanlar da (sondaki virgülden sonraki dahil) boş metin olarak gelsin.

```starter
(?P<alan>[^,]+)
```

```test
satir = 'ali,"Yılmaz, Ayşe","dedi ki ""merhaba""",42,'
eq([d["alan"] for d in hepsi(satir)], ["ali", '"Yılmaz, Ayşe"', '"dedi ki ""merhaba"""', "42", ""], "beş alan")
eq([d["alan"] for d in hepsi(",,x")], ["", "", "x"], "boş alanlar")
```

```solution
(?:^|,)(?P<alan>"(?:[^"]|"")*"|[^,]*)
```

```hint
Her alan ya satır başında ya da bir virgülden sonra başlar: `(?:^|,)`. Sonra iki seçenek: tırnaklı alan ya da virgüle kadar olan (boş olabilen) alan.
```

```hint
Tırnaklı alan: `"(?:[^"]|"")*"`. Önce tırnaklı kol denenmeli.
```
:::
