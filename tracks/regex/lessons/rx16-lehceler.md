---
id: rx16
title: Regex Lehçeleri
summary: Python, PCRE (grep -P, Splunk), .NET (PowerShell), JavaScript, RE2 (KQL) ve POSIX (grep -E, sed, awk) arasındaki farklar; kaçış katmanları, bakınmasız ve geri başvurusuz yazmak, taşınabilir desen.
---

::: anlat Tek dil, birçok lehçe
Regex'in çekirdeği (`.`, `[...]`, `*`, `+`, `?`, `{n,m}`, `|`, `( )`, `^`, `$`) her yerde aynıdır. Ama analist olarak gün içinde Python, `grep`, `sed`, PowerShell, Splunk ve KQL arasında gidip gelirsin ve her birinin motoru farklıdır:

| Araç | Motor |
|---|---|
| Python `re` | Python'un kendi geri izlemeli motoru |
| `grep -P`, Splunk (`rex`, `regex`), PHP `preg_*` | PCRE |
| PowerShell (`-match`, `-replace`, `Select-String`) | .NET |
| JavaScript, Node | ECMAScript |
| KQL (Sentinel, Defender, Data Explorer), Go | **RE2**: doğrusal zamanlı, geri izlemesiz |
| `grep`, `grep -E`, `sed`, `sed -E`, `awk` | POSIX BRE / ERE |

### Özellik tablosu
| Özellik | Python | PCRE | .NET | JS | RE2 | POSIX ERE |
|---|---|---|---|---|---|---|
| `\d \w \s` | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ (`[0-9]`, `[[:digit:]]`) |
| tembel `*?` | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| bakınma `(?=` `(?<=` | ✓ | ✓ | ✓ | ✓ | **✗** | ✗ |
| geri başvuru `\1` | ✓ | ✓ | ✓ | ✓ | **✗** | GNU uzantısı |
| adlı grup | `(?P<ad>)` | `(?<ad>)` | `(?<ad>)` | `(?<ad>)` | `(?P<ad>)` | ✗ |
| atomik `(?>` | 3.11+ | ✓ | ✓ | ✗ | ✗ | ✗ |
| koşullu `(?(1)` | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| `\p{L}` | ✗ | ✓ | ✓ | `u` ile | ✓ | ✗ |
| satır içi `(?i)` | ✓ | ✓ | ✓ | `/.../i` | ✓ | araç seçeneği (`grep -i`) |

RE2'nin eksikleri bir tasarım tercihidir: bakınma ve geri başvuru olmadan her desen, metnin uzunluğuyla **doğrusal** sürede çalışır ve felaket geri izleme (RX11) imkânsızdır. Binlerce kullanıcının sorgu yazdığı bir platform için bu, özelliklerden daha değerlidir.

> [!TUZAK]
> POSIX araçlarında `\d` yoktur ve hata da vermeyebilir. Bu makinedeki GNU grep 3.0'da `echo "disk 42" | grep -oE '\d+'` komutu `42` değil `d` yazar: `\d` sessizce `d` harfine dönüşür. Yeni grep sürümleri en azından uyarı verir. `grep`, `sed` ve `awk`'ta rakam için `[0-9]` yaz.

### Aynı iş, beş yazım
| Araç | Kullanıcı adını çıkarmak |
|---|---|
| Python | `re.search(r"kullanici=(?P<ad>\w+)", satir)["ad"]` |
| PowerShell | `if ($satir -match 'kullanici=(?<ad>\w+)') { $Matches.ad }` |
| Splunk | `... \| rex field=_raw "kullanici=(?<kullanici>\w+)"` |
| KQL | `... \| extend Kullanici = extract(@"kullanici=(\w+)", 1, Mesaj)` |
| grep | `grep -oE 'kullanici=[A-Za-z0-9_]+'` (ardından `cut -d= -f2`) |

### Kaçış katmanları
Desen motora ulaşmadan önce **barındıran dilin** metin kurallarından geçer. Ters eğik çizgiler o katmanda kaybolabilir:

| Dil | Deseni nasıl yazarsın |
|---|---|
| Python | ham metin: `r"\d+\.\d+"` |
| KQL | düz metin: `@"\d+\.\d+"`; normal tırnakta ters eğik çizgiyi ikile: `"\\d+"` |
| PowerShell | tek tırnak: `'\d+\.\d+'` (çift tırnakta `$` değişken sanılır) |
| bash | tek tırnak: `grep -E '[0-9]+\.[0-9]+'` |
| Splunk | çift tırnak içinde; desendeki çift tırnağı `\"` yaz |

> [!NOT]
> PowerShell'in `-match` ve `-replace` işleçleri varsayılan olarak **büyük-küçük harfe duyarsızdır**: `'ABC' -match 'abc'` doğru döner. Duyarlı karşılaştırma için `-cmatch` ve `-creplace` kullan. Python, PCRE, JavaScript ve RE2'de varsayılan tersidir: duyarlıdır.
:::

::: tahmin
Bu desen yalnızca POSIX ERE öğeleri kullanıyor; `grep -E`'de de aynı sonucu verir. Neleri yakalar?

```regex
[A-Z][a-z]+ [0-9]{1,2}
```

```stdin
Oct 19 Eki 5 nov 3
```

???

`Oct 19` ve `Eki 5`. `nov` küçük harfle başladığı için `[A-Z]`'ye uymaz. Desende `\d`, `(?:`, tembel niceleyici ya da bakınma olmadığı için Python, grep, sed, awk, PCRE ve RE2'de aynı davranır.
:::

::: gorev RE2 uyumlu çıkarım
KQL'in `extract()` fonksiyonu RE2 kullanır ve **bakınma desteklemez**. `kullanici=` alanının değerini bakınma kullanmadan çıkar: değer 1. yakalayan gruba girsin (KQL'de `extract(desen, 1, Mesaj)` diye kullanılacak). Kullanıcı adlarında harf, rakam, nokta, alt çizgi ve tire olabilir.

```starter
(?<=kullanici=)[\w.-]+
```

```test
import re
ok(not re.search(r"\(\?<?[=!]", src), "bakınma kullanma: RE2'de yok")
ok(rx.groups == 1, "tek yakalayan grup olmalı")
eq(grup("zaman=09:12 kullanici=ayse.k sonuc=tamam"), "ayse.k", "nokta içeren ad")
eq(grup("kullanici=can_01 sonuc=red"), "can_01", "satır başında")
eq(grup("eski-kullanici=x yeni kullanici=mert-y"), "mert-y", "başka bir alanın sonu sayılmaz")
```

```solution
(?:^|\s)kullanici=([\w.-]+)
```

```hint
Geriye bakınma yerine önekin kendisini eşleşmeye kat ve değeri bir grupla yakala: `kullanici=([\w.-]+)`.
```

```hint
`eski-kullanici=` içindeki `kullanici=` da eşleşir. Önekin önünde satır başı ya da boşluk olmalı: `(?:^|\s)kullanici=([\w.-]+)`. `\b` burada yetmez: `-` kelime karakteri olmadığı için `eski-kullanici`'de `k`'nin önünde bir kelime sınırı vardır.
```
:::

::: gorev grep -E'ye taşınabilir desen
`SS:DD:ss` saatinden sonra bir boşluk ve `ERROR` ya da `WARN` gelen parçaları bul. Desen `grep -E`, `sed -E` ve `awk`'ta da çalışacak: `\d`, `\w`, `\s` gibi kısayollar, `(?:...)`, tembel niceleyiciler ve bakınma **kullanma**.

```starter
\d{2}:\d{2}:\d{2} (?:ERROR|WARN)
```

```test
import re
gunluk = "09:12:01 ERROR disk dolu\n09:12:05 INFO tamam\n09:13:40 WARN bellek %91\n9:14:00 ERROR kısa saat"
eq(bul(gunluk), ["09:12:01 ERROR", "09:13:40 WARN"], "iki satır")
ok(not re.search(r"\\[dwsDWSb]", src), "\\d \\w \\s \\b gibi kısayollar POSIX ERE'de yok")
ok("(?" not in src, "(?: ve bakınma POSIX ERE'de yok")
ok(not re.search(r"[*+?}]\?", src), "tembel niceleyici POSIX ERE'de yok")
```

```solution
[0-9]{2}:[0-9]{2}:[0-9]{2} (ERROR|WARN)
```

```hint
`\d` yerine `[0-9]`. POSIX ERE'de yalnızca düz parantez vardır: `(ERROR|WARN)`. `bul` eşleşmenin tamamını döndürdüğü için yakalayan grup sonucu değiştirmez.
```
:::

::: gorev Geri başvurusuz tırnaklar
Çift ya da tek tırnak içindeki metinleri bul; açılan tırnak **aynı** tırnakla kapanmalı. RE2 ve POSIX ERE'de geri başvuru (`\1`) olmadığı için onu kullanmadan yaz.

```starter
(["']).*?\1
```

```test
import re
eq(bul("""a="x" b='y' d='o "dedi"' e="it's" bos=''"""), ['"x"', "'y'", """'o "dedi"'""", '"it\'s"', "''"], "eşleşen tırnaklar")
ok(not re.search(r"\\[1-9]|\(\?P=", src), "geri başvuru kullanma")
```

```solution
"[^"]*"|'[^']*'
```

```hint
Geri başvurunun yaptığı işi alternatifle yap: her tırnak türü için ayrı bir kol.
```
:::
