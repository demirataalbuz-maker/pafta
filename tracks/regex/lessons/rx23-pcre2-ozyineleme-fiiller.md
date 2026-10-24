---
id: rx23
title: PCRE2: Özyineleme, Alt Yordamlar ve Kontrol Fiilleri
summary: Hazır PCRE2 desenlerini okumak: (?R) ve (?1) ile özyineleme, (?&ad) alt yordamları ve (?(DEFINE)...) dilbilgisi blokları, (?|...) branch reset, (*SKIP)(*FAIL) ile "bunun dışında" eşleşme ve (*COMMIT). Bu derste desenler Python re'de değil, gerçek PCRE2'de çalışır.
---

::: anlat Bu derste motor değişiyor
Şimdiye kadar her desen Python'un `re` modülünde çalıştı. Sahada okuyacağın desenlerin çoğu ise **PCRE2** içindir: PHP'nin `preg_*` fonksiyonları, ModSecurity/OWASP CRS kuralları, Suricata ve Snort'un `pcre` seçeneği, `grep -P`, Nginx ve HAProxy. PCRE2'de Python `re`'nin hiç tanımadığı yapılar vardır ve `re` onları görünce derleme hatası verir:

```regex
\((?:[^()]++|(?R))*\)
---
çağrı f(a, g(b, h(c))) ve (eksik ve ()
```

Bu derste **bütün desenler gerçek PCRE2 kitaplığında** (10.47, UTF ve UCP kipinde) çalışır: `\w`, `\d` ve `\b` Python'daki gibi Unicode'a göre davranır. Aynı deseni öteki derslerin tezgahına yapıştırırsan `re` reddeder; bu bir hata değil, lehçe farkıdır (RX16).

> [!NOT]
> Bu yapıları Python'a "çevirmeye" çalışma. `re`'de özyineleme yoktur; iç içe yapıyı derinlik sınırı koyup elle açmak (`\((?:[^()]|\((?:[^()]|\([^()]*\))*\))*\)`) hem okunmaz hem de bir seviye fazlasında sessizce yanılır. Python'da gerçekten gerekiyorsa üçüncü taraf `regex` modülü bu yapıların çoğunu destekler; ama çoğu zaman doğru araç bir ayrıştırıcıdır.

Bir PCRE2 desenini okurken iki şeyi unutma: `++`, `*+`, `?+` **iyelikçi** niceleyicilerdir (RX12'deki atomik grubun kısa yazımı: geri verilmez) ve `(*...)` ile başlayan her şey bir **fiil** ya da seçenektir, bir grup değildir.

```meta
motor: pcre2
```
:::

::: anlat Özyineleme ve alt yordamlar
Yukarıdaki desen bir **özyinelemedir**: `(?R)` "bütün deseni burada yeniden uygula" demektir. Parçalara ayıralım:

| Parça | Anlamı |
|---|---|
| `\(` | bir açılış parantezi |
| `(?:[^()]++\|(?R))*` | parantez olmayan karakterler **ya da** başka bir tam parantezli yapı, sıfır ya da daha çok kez |
| `\)` | onun kapanışı |

Böylece `f(a, g(b, h(c)))` içindeki dış parantezden başlayan tek bir eşleşme çıkar; kapanmayan `(eksik` ise hiç eşleşmez ve motor içindeki `()`'yu ayrıca bulur.

Bütün desen yerine **tek bir grubu** çağırmak da mümkündür. Buna **alt yordam çağrısı** denir:

| Yazım | Neyi çağırır |
|---|---|
| `(?R)` ya da `(?0)` | bütün deseni |
| `(?1)`, `(?2)` | o numaralı grubun **desenini** |
| `(?-1)`, `(?+1)` | göreli: bir önceki / bir sonraki grup |
| `(?&ad)` | `(?<ad>...)` grubunun desenini |
| `(?P>ad)` | aynısı, Python benzeri yazım |

Alt yordam çağrısı ile geri başvuru farklı şeylerdir: `(\w)-\1` "aynı **metni** tekrar et" der (`a-a`), `(\w)-(?1)` "aynı **deseni** tekrar uygula" der (`a-b` de uyar). Çağrının içinde yakalanan değerler çağrı bitince geri alınır: `a-b` eşleşmesinde 1. grup yine `a`'dır.

```regex
(\w)-(?1)
---
a-a ve a-b ve -c
```

Uzun desenler parçalarını bir **dilbilgisi** gibi en başta tanımlar. `(?(DEFINE)...)` bloğu içindeki gruplar kendi başına hiçbir şey eşlemez; yalnızca adlarıyla çağrılmak için oradadır:

```regex
(?(DEFINE)(?<oktet>25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))\b(?&oktet)(?:\.(?&oktet)){3}\b
---
10.0.0.255 ve 10.0.0.256 ve 1.2.3.4
```

`oktet` bir kez yazılır, dört kez çağrılır. `10.0.0.256` geçmez, çünkü 256 hiçbir oktet dalına uymaz ve `\b` son oktetin yarıda kesilmesine izin vermez. `oktet` grubu DEFINE içinde tanımlandığı için eşleşmede hiçbir değer taşımaz (`None`).

```meta
motor: pcre2
```
:::

::: anlat Branch reset ve kontrol fiilleri
Aynı bilgiyi farklı biçimlerde arayan bir alternatifte her dalın grubu **ayrı numara** alır; okuyan kod hangi grubun dolu olduğunu aramak zorunda kalır. `(?|...)` **branch reset** grubunda her dal numaralandırmaya baştan başlar:

| Desen | `2026-10` | `10/2026` |
|---|---|---|
| `(\d{4})-(\d{2})\|(\d{2})/(\d{4})` | `('2026', '10', None, None)` | `(None, None, '10', '2026')` |
| `(?\|(\d{4})-(\d{2})\|(\d{2})/(\d{4}))` | `('2026', '10')` | `('10', '2026')` |

Dikkat: branch reset **numaraları** birleştirir, anlamı değil. İkinci dalda 1. grup ay, 2. grup yıldır. Dallar aynı sırada aynı şeyi yakalamıyorsa sonuç yanıltır.

**Geri izleme kontrol fiilleri** motorun deneme sırasına doğrudan karışır. Hazır desenlerde en sık göreceğin kalıp **"şunu atla, geri kalanında ara"**dır:

```regex
"[^"]*"(*SKIP)(*FAIL)|\bsifre\b
---
sifre "sifre burada geçmez" ve sifre
```

Sol dal tırnaklı bir metni eşler, sonra `(*FAIL)` (kısaca `(*F)`) eşleşmeyi bilerek düşürür. `(*SKIP)` motora "geri izlersen, bir sonraki denemeye **buradan**, yani tırnağın sonundan başla" der. Sonuç: tırnak içindeki bölge bütünüyle atlanır, sağ dal yalnızca dışarıdaki `sifre`'leri bulur. `(*SKIP)` olmadan `(*FAIL)` yalnızca o konumdaki denemeyi düşürür; motor bir sonraki karakterden yeniden başlar ve tırnağın içindeki `sifre`'yi yine bulur.

| Fiil | Ne yapar |
|---|---|
| `(*FAIL)`, `(*F)` | burada başarısız ol (geri izlemeye zorla) |
| `(*SKIP)` | geri izleme buraya dönerse, sonraki denemeyi bu konumdan başlat |
| `(*COMMIT)` | geri izleme buraya dönerse bütün eşleşme biter; **başka konumdan da denenmez** |
| `(*PRUNE)` | geri izleme buraya dönerse bu başlangıç konumundaki deneme biter |
| `(*ACCEPT)` | eşleşmeyi hemen başarıyla bitir |

`(*COMMIT)`'in etkisi şaşırtıcıdır: `a+(*COMMIT)b` deseni `aaac aab` metninde **hiçbir şey** bulmaz. İlk denemede `aaa`'dan sonra `b` gelmez, geri izleme `(*COMMIT)`'e çarpar ve motor bütün aramayı bırakır; sonraki `aab`'ye hiç bakılmaz. Kurallarda bu fiil "buraya geldiysen başka yerde arama" diye hız için kullanılır.

> [!GÜVENLİK]
> WAF ve IDS kurallarında `(*SKIP)(*F)` "yorumu ya da tırnak içini sayma" diye kullanılır. Saldırgan açısından da aynı bilgi önemlidir: atlanan bölge (örneğin tırnağın içi) kuralın **kör noktasıdır**. Bir kuralı denetlerken her atlanan dalın neyi görünmez yaptığını sor; kaçışlı tırnak (`\"`) ya da kapanmayan tırnak bu kör noktayı genişletebilir.

```meta
motor: pcre2
```
:::

::: tahmin
Hangi parçalar yakalanır? Ayrı satırlara yaz.

```regex
#.*(*SKIP)(*F)|\b\d+\b
```

```stdin
port=80 # eski 8080
yedek=443
```

```meta
motor: pcre2
```

???

`80` ve `443`. Sol dal `#` ile başlayan yorumu satır sonuna kadar eşler (`.` satır sonunu geçmez), `(*F)` onu düşürür ve `(*SKIP)` aramayı yorumun sonuna atlatır: yorumdaki `8080` hiç denenmez. İkinci satırda yorum yoktur; `443` sağ dalla eşleşir.
:::

::: gorev İç içe süslü parantez blokları
Bir yapılandırma metninde **dengeli** süslü parantez bloklarını bul: `{` ile başlayıp ona karşılık gelen `}` ile biten en dış bloklar. Bloklar istediği kadar iç içe olabilir; içleri boş da olabilir. Kapanmayan bir blok eşleşmemeli (ama içindeki dengeli bloklar ayrıca bulunabilir).

```meta
motor: pcre2
```

```starter
\{[^{}]*\}
```

```test
eq(bul("a {x} b"), ["{x}"], "tek düz blok")
eq(bul("a {b {c {d}} e} f"), ["{b {c {d}} e}"], "üç seviye iç içe: yalnız en dış blok")
eq(bul("{} {{}}"), ["{}", "{{}}"], "boş bloklar")
eq(bul("{açık {kapalı}"), ["{kapalı}"], "kapanmayan dış blok eşleşmez, içindeki dengeli blok bulunur")
eq(bul("}{ ters"), [], "ters sıra blok değildir")
eq(bul("{a}{b}"), ["{a}", "{b}"], "yan yana iki blok")
eq(bul(""), [], "boş metin")
ok(tam("{" * 30 + "}" * 30), "otuz seviye derinlik")
ok(not tam("{" * 30 + "}" * 29), "bir kapanış eksik")
```

```solution
\{(?:[^{}]++|(?R))*\}
```

```hint
Parantez örneğinin aynısı: açılış, sonra "parantez olmayan karakterler ya da bütün desen yeniden", sonra kapanış. `(?R)` bütün deseni çağırır.
```

```hint
`[^{}]++` iyelikçi tekrardır: aynı karakterleri iki ayrı yoldan denemeyi önler. `\{(?:[^{}]++|(?R))*\}`.
```
:::

::: gorev Üç biçimde tek grup
Üç farklı sistemin günlükleri kullanıcı adını üç biçimde yazıyor: `user=ali`, `kullanici: "ayşe"` ve e-posta başlığı gibi `<can@`. Üçünü de bulan bir desen yaz; kullanıcı adı her biçimde **1. grupta** olsun ve desende **tek bir** yakalayan grup numarası bulunsun. Kullanıcı adı harf, rakam ve alt çizgiden oluşur, en az bir karakterdir; `kullanici` biçiminde tırnaklar zorunludur.

```meta
motor: pcre2
```

```starter
user=(\w+)|kullanici: "(\w+)"|<(\w+)@
```

```test
eq(grup("x user=ali y"), "ali", "user= biçimi")
eq(grup('kullanici: "ayşe" giriş'), "ayşe", "tırnaklı biçim, Türkçe harf")
eq(grup("From: <can_2@ornek>"), "can_2", "e-posta biçimi")
eq(len(gruplar("user=ali")), 1, "desende tek grup numarası")
eq([g[0] for g in hepsi('user=a kullanici: "b" <c@x> user=d')], ["a", "b", "c", "d"], "dört eşleşmenin hepsinde 1. grup")
ok(not eslesir("user= boş"), "boş kullanıcı adı eşleşmez")
ok(not eslesir("kullanici: veli"), "tırnaksız kullanici biçimi eşleşmez")
ok(not eslesir('kullanici: ""'), "boş tırnak eşleşmez")
ok(not eslesir(""), "boş metin")
```

```solution
(?|user=(\w+)|kullanici: "(\w+)"|<(\w+)@)
```

```hint
Üç dal aynı kalır; onları `(?|` ... `)` içine al. Her dal numaralandırmaya 1'den başlar.
```
:::

::: gorev Tırnak dışındaki eval çağrıları
Bir betik satırındaki `eval(` çağrılarını bul, ama çift tırnaklı metinlerin **içindekileri sayma**. Tırnaklı metnin içinde ters bölüyle kaçırılmış tırnak (`\"`) metni bitirmez. Kapanmayan bir tırnak metin sayılmaz: ondan sonraki `eval(` bulunur. Eşleşme yalnızca `eval(` olsun; `myeval(` gibi başka bir adın parçası sayılmaz.

```meta
motor: pcre2
```

```starter
\beval\(
```

```test
eq(bul('eval(a)'), ["eval("], "düz çağrı")
eq(bul('x = "eval(" + eval(y)'), ["eval("], "tırnak içindeki sayılmaz, dışındaki sayılır")
eq(len(bul(r'"a \" eval(b" eval(c)')), 1, "kaçışlı tırnak metni bitirmez")
eq(len(bul('"" eval(c) ""')), 1, "boş tırnaklar")
eq(len(bul('"açık eval(d)')), 1, "kapanmayan tırnaktan sonraki çağrı bulunur")
eq(bul('myeval(1) evaluate(2)'), [], "başka adın parçası değil")
eq(bul(r'"\\" eval(e)'), ["eval("], "kaçışlı ters bölüden sonra tırnak metni bitirir")
eq(bul(''), [], "boş satır")
ok(all(m == "eval(" for m in bul('eval( "q" eval(')), "eşleşme yalnızca eval(")
```

```solution
"(?:[^"\\]|\\.)*"(*SKIP)(*F)|\beval\(
```

```hint
Kalıp: `atlanacak(*SKIP)(*F)|aranan`. Atlanacak bölge çift tırnaklı metindir.
```

```hint
Kaçışlı tırnağı da kapsayan tırnaklı metin: `"(?:[^"\\]|\\.)*"`. Tırnak ve ters bölü dışındaki her karakter ya da ters bölüyle başlayan iki karakterlik bir kaçış.
```
:::

::: gorev DEFINE ile IPv4
Metnin **tamamı** bir IPv4 adresi mi? Dört oktet, noktayla ayrılır; her oktet 0 ile 255 arasıdır ve başında gereksiz sıfır yoktur (`0` olur, `01` olmaz). Oktet desenini `(?(DEFINE)(?<oktet>...))` bloğunda bir kez tanımla ve `(?&oktet)` ile çağır.

```meta
motor: pcre2
```

```starter
\d{1,3}(?:\.\d{1,3}){3}
```

```test
ok(tam("192.168.1.10") and tam("8.8.8.8"), "sıradan adresler")
ok(tam("255.255.255.255"), "sınırın kendisi: 255")
ok(not tam("256.1.1.1") and not tam("1.1.1.256"), "sınırın bir üstü: 256, baştaki ve sondaki oktette")
ok(tam("254.249.250.199"), "her basamak dalının sınırları: 254, 249, 250, 199")
ok(not tam("260.1.1.1") and not tam("300.1.1.1"), "üç basamaklı ama aralık dışı")
ok(tam("0.0.0.0"), "sıfırlar")
ok(not tam("01.1.1.1") and not tam("1.1.1.00"), "baştaki gereksiz sıfır")
ok(not tam("1.2.3") and not tam("1.2.3.4.5"), "eksik ya da fazla oktet")
ok(not tam("") and not tam("1..2.3"), "boş metin ve boş oktet")
ok("(?(DEFINE)" in desen and "(?&oktet)" in desen, "oktet DEFINE içinde tanımlanıp adıyla çağrılmalı")
```

```solution
(?(DEFINE)(?<oktet>25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(?&oktet)(?:\.(?&oktet)){3}
```

```hint
Oktetin dalları büyükten küçüğe: `25[0-5]`, `2[0-4]\d`, `1\d\d`, `[1-9]?\d`. Son dal 0–99'u baştaki sıfır olmadan verir.
```

```hint
`(?(DEFINE)(?<oktet>...))` bloğundan sonra `(?&oktet)(?:\.(?&oktet)){3}`. Tamlığı test `tam()` ile denetler; çapa gerekmez.
```
:::
