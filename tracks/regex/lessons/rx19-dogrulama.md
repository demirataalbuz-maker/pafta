---
id: rx19
title: Doğrulama Desenleri ve Sınırları
summary: Sayı aralıklarını rakam rakam kurmak (ay, gün, saat), tutarlı ayırıcı için geri başvuru (MAC), uzunluk sınırı için ileriye bakınma (ana makine adı), UUID ve sürüm; regex'in biçimi doğrulayıp anlamı doğrulayamadığı yerler.
---

::: anlat Biçim doğrulamak
Doğrulama deseni bir metnin **tamamını** denetler: Python'da `fullmatch`, başka yerlerde `^...$` (ya da `\A...\z`). Doğrulamanın üç temel tekniği vardır.

### 1. Sayı aralığını rakam rakam kurmak
Regex sayı bilmez, **karakter** bilir. "01 ile 12 arası" demek için aralığı ilk rakama göre parçalara bölersin:

| Aralık | Desen | Mantık |
|---|---|---|
| ay 01–12 | `0[1-9]\|1[0-2]` | 0 ile başlıyorsa 1–9, 1 ile başlıyorsa 0–2 |
| gün 01–31 | `0[1-9]\|[12]\d\|3[01]` | 0x, 1x–2x, 3 ile başlıyorsa 0–1 |
| saat 00–23 | `[01]\d\|2[0-3]` | 0x–1x, 2 ile başlıyorsa 0–3 |
| dakika 00–59 | `[0-5]\d` | |
| oktet 0–255 | `25[0-5]\|2[0-4]\d\|1\d\d\|[1-9]?\d` | RX10'daki gibi |

### 2. Tutarlılık için geri başvuru
MAC adresi `00:1A:2B:3C:4D:5E` ya da `00-1A-2B-3C-4D-5E` yazılabilir, ama ikisi **karışık** yazılamaz. İlk ayırıcıyı yakala, sonrakilerde `\1` ile aynısını iste:

```regex
[0-9A-Fa-f]{2}([:-])(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}
---
00:1A:2b:3C:4d:5E 00-1A-2B-3C-4D-5E 00:1A-2B:3C:4D:5E
```

### 3. Genel kural için ileriye bakınma
Bir ana makine adının **toplam uzunluğu** en fazla 253 karakterdir. Bu kural parçaların kurallarından bağımsızdır. Çapalı bir ileriye bakınma, deseni değiştirmeden başına bir koşul ekler:

```text
(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}
└────┬─────┘    └──────────────────┬───────────────────┘   └───┬───┘
toplam uzunluk  etiket: 1–63 karakter, tireyle başlamaz/bitmez    üst alan
```

### Hazır kalıplar
| Ne | Desen | Not |
|---|---|---|
| UUID | `[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}` | 3. grubun ilk hanesi sürüm, 4. grubunki varyant |
| sürüm (SemVer çekirdeği) | `(0\|[1-9]\d*)\.(0\|[1-9]\d*)\.(0\|[1-9]\d*)` | baştaki sıfıra izin vermez: `01.2.3` geçersiz |
| e-posta (pratik) | `[^@\s]+@[^@\s]+\.[^@\s]+` | gerçek doğrulama: adrese onay iletisi göndermek |
:::

::: anlat Regex'in sınırı: biçim evet, anlam hayır
Yukarıdaki tarih deseni `2026-02-31`'i kabul eder: her parça kendi aralığında ama böyle bir gün yoktur. Bunu regex'le çözmeye çalışmak (ay ay gün sayısı, artık yıllar) okunamaz bir canavar üretir. Doğru yol iki aşamalıdır:

1. **Regex** biçimi denetler ve parçaları yakalar.
2. **Kod** anlamı denetler: `datetime.strptime`, `ipaddress.ip_address`, `uuid.UUID`, `[datetime]::ParseExact`.

| İş | Regex'e bırakma, şunu kullan |
|---|---|
| tarihin gerçekten var olması | tarih kütüphanesi |
| IP'nin bir ağa (CIDR) dahil olması | `ipaddress.ip_network(...)` ile karşılaştırma |
| büyük sayı aralıkları (1–65535 port) | sayıya çevir, karşılaştır |
| iç içe yapılar (HTML, JSON) | ayrıştırıcı |
| e-postanın gerçekten var olması | onay iletisi |

> [!İPUCU]
> Port gibi aralıkları regex'le yazmak mümkündür (`6553[0-5]|655[0-2]\d|...`) ama SIEM sorgusunda bile genellikle daha iyi bir yol vardır: alanı regex'le çıkar, sonra sayıya çevirip karşılaştır (`toint()` KQL'de, `tonumber()` Splunk'ta).
:::

::: tahmin
Bu desen `GG.AA.YYYY` biçimindeki tarihleri doğruluyor. Neleri yakalar?

```regex
(?:0[1-9]|[12]\d|3[01])\.(?:0[1-9]|1[0-2])\.\d{4}
```

```stdin
31.02.2026 15.13.2026 01.12.2026
```

???

`31.02.2026` ve `01.12.2026`. `15.13.2026`'da ay 13 olduğu için `0[1-9]|1[0-2]` tutmaz. Ama `31.02.2026` geçer: gün de ay da kendi aralığındadır. Şubatın 31'i olmadığını regex bilemez; bunu bir tarih kütüphanesi denetler.
:::

::: gorev Tarih ve saat aralıkları
`YYYY-AA-GG SS:DD` biçimindeki bir metnin tamamını doğrula: yıl 1900–2099, ay 01–12, gün 01–31, saat 00–23, dakika 00–59.

```starter
\d{4}-\d{2}-\d{2} \d{2}:\d{2}
```

```test
ok(tam("2026-10-19 23:59") and tam("2000-01-01 00:00") and tam("1999-12-31 12:30"), "geçerli zamanlar")
ok(not tam("2026-13-01 10:00") and not tam("2026-00-10 10:00"), "geçersiz ay")
ok(not tam("2026-10-32 10:00") and not tam("2026-10-00 10:00"), "geçersiz gün")
ok(not tam("2026-10-19 24:00") and not tam("2026-10-19 12:60"), "geçersiz saat ve dakika")
ok(not tam("2126-10-19 10:00"), "yıl aralık dışında")
```

```solution
(?:19|20)\d\d-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]) (?:[01]\d|2[0-3]):[0-5]\d
```

```hint
Her alanı ilk rakamına göre parçala: ay `0[1-9]|1[0-2]`, gün `0[1-9]|[12]\d|3[01]`, saat `[01]\d|2[0-3]`. Alternatifleri `(?:...)` içine almayı unutma.
```
:::

::: gorev MAC adresi
Bir metnin tamamının MAC adresi olup olmadığını denetle: altı çift onaltılık rakam (büyük ya da küçük harf), ayırıcı `:` ya da `-`, ama **hep aynı** ayırıcı.

```starter
(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}
```

```test
ok(tam("00:1A:2b:3C:4d:5E") and tam("00-1A-2B-3C-4D-5E"), "iki geçerli biçim")
ok(not tam("00:1A-2B:3C:4D:5E"), "karışık ayırıcı geçersiz")
ok(not tam("001A2B3C4D5E"), "ayırıcısız biçim kabul edilmiyor")
ok(not tam("00:1A:2B:3C:4D"), "beş çift eksik")
ok(not tam("00:1A:2B:3C:4D:5G"), "G onaltılık değil")
```

```solution
[0-9A-Fa-f]{2}([:-])(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}
```

```hint
İlk ayırıcıyı bir gruba al: `[0-9A-Fa-f]{2}([:-])`. Sonraki dört çiftin her birinden sonra `\1` iste.
```
:::

::: gorev Ana makine adı
Bir metnin tamamının geçerli bir tam ana makine adı (FQDN) olup olmadığını denetle. Büyük-küçük harf fark etmez.

- En az iki etiket, noktayla ayrılmış (`ornek` tek başına geçmez)
- Her etiket 1–63 karakter: harf, rakam ve tire; tireyle başlamaz ve bitmez
- Son etiket (üst alan) yalnızca harflerden oluşur, 2–63 karakter

```starter
[\w.-]+\.[a-z]+
```

```test
ok(tam("web01.pafta.local") and tam("a.io") and tam("db-01.ornek.com.tr") and tam("xn--5ca.com"), "geçerli adlar")
ok(tam("WEB01.Pafta.Local"), "büyük harf")
ok(not tam("-web.ornek.com") and not tam("web-.ornek.com"), "tireyle başlayan ya da biten etiket")
ok(not tam("web..ornek.com") and not tam("web_01.ornek.com"), "boş etiket ya da alt çizgi")
ok(tam("a" * 63 + ".com") and not tam("a" * 64 + ".com"), "etiket en fazla 63 karakter")
ok(not tam("ornek") and not tam("ornek.c0m"), "tek etiket ya da rakamlı üst alan")
```

```solution
(?i)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}
```

```hint
Bir etiket: bir harf ya da rakam, ardından isteğe bağlı olarak en fazla 61 karakterlik orta kısım ve yine bir harf ya da rakam: `[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?`.
```

```hint
Etiket ve noktası bir veya daha çok kez, sonra üst alan: `(?:etiket\.)+[a-z]{2,63}`. Başa `(?i)` koy.
```
:::
