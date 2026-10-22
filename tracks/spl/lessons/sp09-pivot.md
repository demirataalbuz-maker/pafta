---
id: sp09
title: Pivot Tablolar
summary: chart ile iki boyutlu özet (over ... by ...), boş hücreler ve fillnull, limit ve useother ile OTHER sütunu, stats sonucunu genişleten xyseries ve geniş tabloyu uzun biçime çeviren untable.
kazanim: PU 1.1, PU 2.3, APU 12.2, APU 12.3
---

::: anlat chart: satırlar ve sütunlar
`stats count by sunucu yontem` her (sunucu, yöntem) çifti için bir satır verir: **uzun** bir tablo. İnsan gözü ise çoğu zaman **geniş** bir tablo ister: satırlarda sunucular, sütunlarda yöntemler. `chart` tam bunu yapar:

```spl
sourcetype=istekler
| chart count over sunucu by yontem
```

| Yazım | Anlamı |
|---|---|
| `chart count over A by B` | satırlar A'nın değerleri, sütunlar B'nin değerleri |
| `chart count by A B` | aynısı, kısa yazım |
| `chart avg(sure_ms) over sunucu by yol` | hücrelerde başka bir toplama |
| `chart count by A` | tek boyut: `stats count by A` ile aynı |

Hiç olayı olmayan birleşimin hücresi **boş** kalır; 0 değil. Raporda sıfır görmek istiyorsan arkasına `fillnull value=0` ekle:

```spl
sourcetype=istekler
| chart count over sunucu by yontem
| fillnull value=0
```

### Çok sütunlu bölmeler
Sütun alanının çok farklı değeri varsa tablo okunmaz hale gelir. `limit=N` en büyük N seriyi tutar; `useother=t` geri kalanları `OTHER` adlı tek bir sütunda toplar:

```spl
sourcetype=istekler
| chart count over yol by sunucu limit=2 useother=t
```

> [!NOT]
> Gerçek Splunk'ta `chart` ve `timechart`'ın varsayılan `limit` değeri 10'dur ve `useother` varsayılan olarak açıktır: on birinci seriden itibaren her şey sessizce `OTHER`'a düşer. Bir panoda beklediğin sunucuyu göremiyorsan önce buna bak.
:::

::: anlat xyseries ve untable
`chart` hem toplar hem genişletir. Elinde zaten toplanmış bir sonuç varsa (ör. birkaç `eval` ve `stats` sonrası), onu yalnızca **genişletmek** için `xyseries` kullanılır:

```spl
sourcetype=istekler kullanici=*
| stats count by kullanici sunucu
| xyseries kullanici sunucu count
```

`xyseries satır_alanı sütun_alanı değer_alanı`: üç alan alır. Tersi `untable`'dır: geniş tabloyu yeniden **uzun** biçime çevirir. Geniş tablo üzerinde sıralama ve süzme yapmak zordur; uzun biçimde ise her hücre bir satır olduğu için `sort` ve `where` doğrudan çalışır:

```spl
sourcetype=istekler
| chart count over sunucu by yol
| untable sunucu yol adet
| sort -adet
| head 3
```

| Komut | Dönüşüm |
|---|---|
| `chart` | olaylar → geniş tablo |
| `xyseries` | uzun (toplanmış) tablo → geniş tablo |
| `untable` | geniş tablo → uzun tablo |
:::

::: tahmin
Üç satır yazar:

```spl
sourcetype=istekler
| chart count over sunucu by yontem
| fillnull value=0
```

???

`web01|0|11|0|0`, `web02|1|5|2|1`, `web03|0|6|0|0`. Sütunlar alfabetik sıradadır: `DELETE`, `GET`, `POST`, `PUT`. web01 ve web03 yalnızca GET isteği almış; öteki hücreleri boştu, `fillnull` onları 0 yaptı.
:::

::: gorev Durum sınıfı pivotu
İstekleri durum koduna göre sınıflandır: 500 ve üstü `5xx`, 400 ve üstü `4xx`, geri kalanı `2xx`. Satırlarda sunucular, sütunlarda sınıflar olan bir tablo kur; boş hücreler 0 olsun.

```starter
sourcetype=istekler
| stats count by sunucu durum
```

```test
eq(sutunlar, ["sunucu", "2xx", "4xx", "5xx"], "sütunlar")
eq(sonuc, [("web01", 8, 0, 3), ("web02", 7, 1, 1), ("web03", 6, 0, 0)], "üç sunucu")
ok(kullanir("chart"), "chart kullan")
```

```solution
sourcetype=istekler
| eval sinif=case(durum>=500, "5xx", durum>=400, "4xx", true(), "2xx")
| chart count over sunucu by sinif
| fillnull value=0
```

```hint
Sınıfı `eval sinif=case(durum>=500, "5xx", durum>=400, "4xx", true(), "2xx")` ile kur.
```

```hint
`chart count over sunucu by sinif`, ardından `fillnull value=0`.
```
:::

::: gorev Kullanıcı ve sunucu tablosu
Kullanıcısı olan istekleri `stats` ile kullanıcı ve sunucuya göre say, sonra sonucu `xyseries` ile satırlarda kullanıcılar, sütunlarda sunucular olacak şekilde genişlet; boş hücreler 0 olsun.

```starter
sourcetype=istekler kullanici=*
| stats count by kullanici sunucu
```

```test
eq(sutunlar, ["kullanici", "web01", "web02"], "sütunlar")
eq(sonuc, [("ayse", 3, 2), ("can", 0, 5), ("mert", 3, 1), ("selin", 0, 1), ("zeynep", 4, 0)], "beş kullanıcı")
ok(kullanir("xyseries"), "xyseries kullan")
```

```solution
sourcetype=istekler kullanici=*
| stats count by kullanici sunucu
| xyseries kullanici sunucu count
| fillnull value=0
```

```hint
`xyseries kullanici sunucu count`: satır alanı, sütun alanı, değer alanı.
```
:::

::: gorev En yoğun üç sunucu ve yol çifti
Satırlarda sunucular, sütunlarda yollar olan istek sayısı tablosunu kur; sonra `untable` ile uzun biçime çevirip en çok isteği olan üç (sunucu, yol) çiftini getir: `sunucu`, `yol`, `adet`; adede göre azalan.

```starter
sourcetype=istekler
| chart count over sunucu by yol
```

```test
eq(sutunlar, ["sunucu", "yol", "adet"], "sütunlar")
eq(sonuc, [("web01", "/api/rapor", 6), ("web01", "/api/bilet", 4), ("web02", "/api/bilet", 4)], "ilk üç çift")
ok(kullanir("untable"), "untable kullan")
```

```solution
sourcetype=istekler
| chart count over sunucu by yol
| untable sunucu yol adet
| sort -adet
| head 3
```

```hint
`untable sunucu yol adet` her hücreyi bir satıra çevirir. Sonra `sort -adet` ve `head 3`.
```
:::
