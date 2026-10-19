---
id: rx10
title: Log Atölyesi
summary: Gerçek log alanları için desenler; ISO zaman damgası, katı IPv4, anahtar=değer çiftleri.
---

::: anlat Logdan alan çıkarmak
Log analizinin günlük işi, yapılandırılmamış satırlardan **alan** çıkarmaktır. SIEM'lerde buna "ayrıştırma" ya da "alan çıkarma" denir: Splunk'ta `rex`, Sentinel'de `extract()` / `parse`, Logstash'te `grok`. Hepsinin altında aynı regex'ler vardır.

Bir web uygulamasının log satırına bakalım:

```regex
(?P<zaman>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\s+(?P<seviye>[A-Z]+)\s+(?P<mesaj>.*)
---
2026-10-19T08:15:02 INFO istek tamam
2026-10-19 08:15:09 ERROR veritabanı zaman aşımı
```

Adlı gruplarla her satır bir kayda dönüştü: `zaman`, `seviye`, `mesaj`.

### Gevşek ve katı desenler
`\d{1,3}(\.\d{1,3}){3}` IP adresi **biçimindeki** her şeyi bulur, `999.999.999.999` dahil. Hızlı bir tarama için yeterlidir. Doğrulama gerekiyorsa her okteti 0–255 ile sınırlayan katı bir desen yazılır:

```regex
\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b
---
10.0.0.1 192.168.1.255 256.1.1.1 999.1.1.1
```

Oktet alternatifi büyükten küçüğe sıralanmıştır: 250–255, 200–249, 100–199, 0–99. Alternatiflerin sırası önemlidir; nedenini P11'de gördün.

> [!NOT]
> Her zaman katı desen en iyisi değildir. Bir analiz sorgusunda biraz geniş bir desenle hızlıca tarayıp sonucu ikinci bir adımda süzmek, dev bir "her şeyi bilen" desenden genellikle daha okunaklı ve daha hızlıdır.
:::

::: tahmin
Bu katı desen hangi parçaları yakalar? Ayrı satırlara yaz.

```regex
\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b
```

```stdin
10.0.0.1 192.168.1.255 256.1.1.1
```

???

`10.0.0.1` ve `192.168.1.255`. `256` hiçbir oktet alternatifine uymaz: `25[0-5]` en fazla 255'e izin verir. `56.1.1.1` parçası da yakalanmaz, çünkü önünde `2` olduğu için orada bir kelime sınırı yok.
:::

::: gorev Zaman damgası
`YYYY-AA-GG SS:DD:ss` biçimindeki zaman damgalarını bul. Tarih ile saat arasında boşluk ya da `T` olabilir; isteğe bağlı olarak sonda nokta ve saniye kesri (`.123`) bulunabilir.

```starter
\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}
```

```test
metin = "a 2026-10-19 08:15:02 b 2026-10-19T08:15:09.123 c 19.10.2026 08:00:00"
eq(bul(metin), ["2026-10-19 08:15:02", "2026-10-19T08:15:09.123"], "iki ISO zaman damgası")
```

```solution
\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?
```

```hint
Ayırıcı için sınıf: `[T ]`. Kesir isteğe bağlı bir grup: `(?:\.\d+)?`.
```
:::

::: gorev Katı IPv4 doğrulama
Bir metnin **tamamının** geçerli bir IPv4 adresi olup olmadığını denetleyen desen yaz: dört oktet, her biri 0–255, başında gereksiz sıfır yok (`01` geçersiz).

```starter
\d{1,3}(\.\d{1,3}){3}
```

```test
ok(tam("192.168.1.10"), "192.168.1.10 geçerli")
ok(tam("0.0.0.0") and tam("255.255.255.255"), "sınır değerler geçerli")
ok(not tam("256.1.1.1"), "256 geçersiz")
ok(not tam("01.2.3.4"), "baştaki sıfır geçersiz")
ok(not tam("1.2.3"), "üç oktet geçersiz")
ok(not tam("999.999.999.999"), "999 geçersiz")
```

```solution
(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)
```

```hint
Bir oktet: `(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)`. Üç kez noktayla, bir kez noktasız.
```

```hint
Testler `tam()` kullanıyor, yani desenin metnin tamamına uyması gerekiyor; çapa yazmana gerek yok.
```
:::

::: gorev Anahtar=değer çiftleri
`anahtar=değer` çiftlerini bul: anahtar `anahtar` adlı gruba, değer `deger` adlı gruba girsin. Değer ya çift tırnak içinde (boşluk içerebilir, tırnaklar dahil) ya da boşluğa kadar olan bir dizidir.

```starter
(?P<anahtar>\w+)=(?P<deger>\S+)
```

```test
satir = 'kullanici=ali mesaj="giriş başarılı" ip=10.0.0.5 bos=""'
eq(hepsi(satir), [{"anahtar": "kullanici", "deger": "ali"},
                  {"anahtar": "mesaj", "deger": '"giriş başarılı"'},
                  {"anahtar": "ip", "deger": "10.0.0.5"},
                  {"anahtar": "bos", "deger": '""'}], "dört çift")
```

```solution
(?P<anahtar>\w+)=(?P<deger>"[^"]*"|\S+)
```

```hint
Değer için alternatif: önce tırnaklı biçim `"[^"]*"`, olmazsa `\S+`. Sıra önemli: tırnaklı biçim önce denenmeli.
```
:::
