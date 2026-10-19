---
id: rx05
title: Gruplar ve Alternatif
summary: | ile seçenekler, ( ) ile gruplama ve yakalama, (?: ) ile yakalamayan grup, \1 ile değiştirme.
---

::: anlat Ya bu ya şu: |
Dikey çizgi `|` **alternatiftir**: "soldaki ya da sağdaki".

```regex
kedi|köpek
---
kedi, köpek ve kedicik
```

`|` regex'teki **en düşük öncelikli** işleçtir: bütün deseni ikiye böler. `^GET|POST$` "satır başındaki GET" **ya da** "satır sonundaki POST" demektir, "başta GET ya da POST" değil. Alternatifin kapsamını sınırlamak için parantez kullanırsın.

### Parantez: gruplama ve yakalama
`( )` iki iş yapar:

1. **Gruplar**: niceleyici ya da alternatif grubun tamamına uygulanır: `(ab)+`, `(GET|POST)`
2. **Yakalar**: eşleşen parça numaralı bir **grup** olarak saklanır (1, 2, 3... soldan açılan parantez sırasına göre)

```regex
(GET|POST|PUT|DELETE) (\S+)
---
GET /index.html HTTP/1.1
POST /api/giris HTTP/1.1
FETCH /yok HTTP/1.1
```

Tablodaki "gruplar" sütununa bak: 1. grup yöntem, 2. grup yol. Programlama dillerinde bu gruplar ayrı ayrı okunur; log ayrıştırmanın temeli budur.

### Yakalamayan grup: (?: )
Sadece gruplamak, yakalamamak istiyorsan `(?:...)` yaz. Daha hızlıdır ve grup numaralarını kaydırmaz:

```regex
(?:\d{1,3}\.){3}\d{1,3}
---
kaynak 10.0.0.5 hedef 192.168.1.10
```

> [!NOT]
> Değiştirme işlemlerinde yakalanan gruplara `\1`, `\2` ile (Python ve sed), bazı araçlarda `$1`, `$2` ile başvurulur. Tarihi `19.10.2026`'dan `2026-10-19`'a çevirmek tek bir değiştirmedir: desen `(\d{2})\.(\d{2})\.(\d{4})`, yerine `\3-\2-\1`.
:::

::: tahmin
Eşleşmeleri sırayla, ayrı satırlara yaz:

```regex
ab|cd
```

```stdin
abcd acbd cdab
```

???

`ab`, `cd`, `cd`, `ab`. Motor her konumda önce `ab`'yi, olmazsa `cd`'yi dener. `acbd` içinde ikisi de bitişik olarak geçmiyor.
:::

::: gorev HTTP isteği
Bir HTTP istek satırından yöntemi (sadece `GET`, `POST`, `PUT`, `DELETE`) **1. grupta** ve yolu (boşluğa kadar) **2. grupta** yakalayan bir desen yaz. Başka yöntemler eşleşmemeli.

```starter
(\w+) (\S+)
```

```test
eq(gruplar("GET /a HTTP/1.1"), ("GET", "/a"), "GET /a")
eq(gruplar("DELETE /kullanici/7 HTTP/1.1"), ("DELETE", "/kullanici/7"), "DELETE")
ok(not eslesir("FETCH /a HTTP/1.1"), "FETCH eşleşmemeli")
```

```solution
(GET|POST|PUT|DELETE) (\S+)
```

```hint
Alternatifleri grupla: `(GET|POST|PUT|DELETE)`.
```
:::

::: gorev Tarih biçimini çevir
Testler `degistir(metin, r"\3-\2-\1")` çağıracak. `GG.AA.YYYY` biçimindeki tarihleri `YYYY-AA-GG`'ye çevirecek şekilde **üç grupla** bir desen yaz.

```starter
\d{2}\.\d{2}\.\d{4}
```

```test
eq(degistir("19.10.2026", r"\3-\2-\1"), "2026-10-19", "tek tarih")
eq(degistir("Kayıtlar: 01.02.2025 ve 31.12.2024", r"\3-\2-\1"), "Kayıtlar: 2025-02-01 ve 2024-12-31", "metin içinde iki tarih")
```

```solution
(\d{2})\.(\d{2})\.(\d{4})
```

```hint
Gün, ay ve yılı ayrı ayrı parantez içine al.
```
:::

::: gorev Yakalamadan grupla
IPv4 biçimindeki adresleri bul; ama desen **hiç yakalayan grup içermesin** (tekrarlanan parçayı `(?:...)` ile grupla).

```starter
(\d{1,3}\.){3}\d{1,3}
```

```test
eq(bul("kaynak 10.0.0.5 hedef 192.168.1.10"), ["10.0.0.5", "192.168.1.10"], "iki adres")
eq(rx.groups, 0, "yakalayan grup sayısı 0 olmalı")
```

```solution
(?:\d{1,3}\.){3}\d{1,3}
```

```hint
`(` yerine `(?:` yaz.
```
:::
