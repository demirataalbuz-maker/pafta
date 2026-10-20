---
id: sp13
title: Çok Değerli Alanlar
summary: Bir alanda birden çok değer; values ve list farkı, split ve makemv ile metinden çok değerli alan, mvcount, mvindex, mvjoin, mvdedup, mvexpand ile değerleri olaylara açmak ve aramada "herhangi bir değer eşleşirse" kuralı.
---

::: anlat Bir alan, birden çok değer
Splunk'ta bir alan aynı anda **birden çok değer** taşıyabilir. En sık üç yoldan doğar:

| Kaynak | Örnek |
|---|---|
| `stats values(x)` / `list(x)` | bir grubun bütün değerleri |
| `transaction` | işlemdeki olayların alanları (SP11) |
| `split()`, `makemv` | ayırıcıyla bölünmüş bir metin |

```spl
sourcetype=istekler kullanici=zeynep
| stats list(durum) as durumlar, values(durum) as farkli by kullanici
```

`list` değerleri olay sırasıyla ve tekrarlarıyla tutar; `values` tekrarsız ve **alfabetik** sıralıdır.

### Çok değerli alan fonksiyonları
| Fonksiyon | Döndürdüğü |
|---|---|
| `mvcount(x)` | değer sayısı |
| `mvindex(x, 0)`, `mvindex(x, -1)` | ilk, son değer |
| `mvjoin(x, ", ")` | değerleri tek metinde birleştirir |
| `mvdedup(x)`, `mvsort(x)` | tekrarsız, sıralı |
| `split(metin, ",")` | metni çok değerli alana böler |
| `mvappend(a, b)` | iki alanı birleştirir |

```spl
sourcetype=istekler
| stats values(kullanici) as kullanicilar by sunucu
| eval liste=mvjoin(kullanicilar, ", ")
| table sunucu liste
```

> [!TUZAK]
> Aramada (`search`) çok değerli bir alan için `alan=değer` **herhangi bir değer** eşleşirse doğrudur: `search mesaj="bitti"` mesajlarından biri `bitti` olan işlemi bulur. `NOT mesaj="bitti"` ise değerlerinden **hiçbiri** `bitti` olmayanları. `where` ve `eval` içindeki karşılaştırmalar ise çok değerli alanlarda beklenmedik davranabilir; önce `mvcount` ile değer sayısına bak ya da `mvexpand` ile tek değerli olaylara aç.
:::

::: anlat makemv ve mvexpand
Bir alan virgülle ayrılmış bir liste taşıyorsa (`"mobil,beta"`), `makemv` onu çok değerli bir alana çevirir. `mvexpand` ise her değeri **ayrı bir olaya** açar: KQL'deki `mv-expand`'in (KQ13) karşılığıdır. "Her etiket kaç istekte geçti?" sorusu için önce açmak gerekir:

```spl
sourcetype=istekler
| rex field=ayrinti "\"etiketler\":\[(?<etiketler>[^\]]*)\]"
| eval etiketler=replace(etiketler, "\"", "")
| makemv delim="," etiketler
| mvexpand etiketler
| stats count by etiketler
```

Bu arama `ayrinti` sütunundaki JSON'dan etiket listesini `rex` ile çeker, tırnakları siler, virgülden böler ve açar. Gerçek Splunk'ta JSON için hazır `spath` komutu vardır: `spath input=ayrinti path=etiketler{}`; bu tezgahta olmadığı için aynı işi açıkça yapıyoruz.
:::

::: tahmin
Tek satır yazar:

```spl
| makeresults
| eval etiket=split("web,prod,eu", ",")
| eval n=mvcount(etiket), ilk=mvindex(etiket, 0), son=mvindex(etiket, -1)
| table n ilk son
```

???

`3|web|eu`. `split` metni üç değerli bir alana böler. `mvindex` sıfırdan sayar; `-1` son değerdir.
:::

::: gorev Üçten çok yolu olanlar
Her kullanıcının istek attığı farklı yolları `yollar` (çok değerli) ve bunların sayısını `yol_sayisi` olarak getir; yalnızca **üç ve daha çok** farklı yola istek atmış kullanıcılar kalsın.

```starter
sourcetype=istekler
| stats count by kullanici yol
```

```test
eq(sutunlar, ["kullanici", "yollar", "yol_sayisi"], "sütunlar")
eq(sonuc, [("ayse", ["/api/bilet", "/api/bilet/17", "/api/rapor"], 3),
           ("can", ["/api/bilet", "/api/bilet/42", "/api/rapor"], 3)], "iki kullanıcı")
```

```solution
sourcetype=istekler
| stats values(yol) as yollar, dc(yol) as yol_sayisi by kullanici
| where yol_sayisi>=3
```

```hint
`stats values(yol) as yollar, dc(yol) as yol_sayisi by kullanici`; sonra `where yol_sayisi>=3`.
```
:::

::: gorev Sunucunun kullanıcıları
Her sunucuya istek atan farklı kullanıcıları alfabetik sırayla ve `", "` ile birleştirilmiş tek bir metin olarak `liste` alanında getir: `sunucu`, `liste`. Kullanıcısı olmayan isteklerin sunucusu da listede kalsın (listesi boş).

```starter
sourcetype=istekler
| stats values(kullanici) as kullanicilar by sunucu
```

```test
eq(sutunlar, ["sunucu", "liste"], "sütunlar")
eq(sonuc, [("web01", "ayse, mert, zeynep"), ("web02", "ayse, can, mert, selin"), ("web03", None)], "üç sunucu")
ok(kullanir("mvjoin"), "mvjoin kullan")
```

```solution
sourcetype=istekler
| stats values(kullanici) as kullanicilar by sunucu
| eval liste=mvjoin(kullanicilar, ", ")
| table sunucu liste
```

```hint
`values` zaten tekrarsız ve sıralıdır; `eval liste=mvjoin(kullanicilar, ", ")` ile birleştir.
```
:::

::: gorev Etiket sıklığı
`ayrinti` alanındaki etiket listesini çıkar, değerleri olaylara aç ve her etiketin kaç istekte geçtiğini getir: `etiketler`, `count`; çoktan aza, eşitlikte etikete göre.

```starter
sourcetype=istekler
| rex field=ayrinti "\"etiketler\":\[(?<etiketler>[^\]]*)\]"
| stats count by etiketler
```

```test
eq(sutunlar, ["etiketler", "count"], "sütunlar")
eq(sonuc, [("mobil", 7), ("otomatik", 4), ("yeniden-deneme", 3), ("ilk-ziyaret", 2), ("beta", 1)], "beş etiket")
ok(kullanir("mvexpand"), "değerleri mvexpand ile aç")
```

```solution
sourcetype=istekler
| rex field=ayrinti "\"etiketler\":\[(?<etiketler>[^\]]*)\]"
| eval etiketler=replace(etiketler, "\"", "")
| makemv delim="," etiketler
| mvexpand etiketler
| stats count by etiketler
| sort -count etiketler
```

```hint
Başlangıç kodu `"mobil","beta"` gibi listenin tamamını tek bir değer sayıyor. Tırnakları sil: `eval etiketler=replace(etiketler, "\"", "")`, sonra `makemv delim="," etiketler`.
```

```hint
`mvexpand etiketler` her etiketi ayrı bir olaya açar; ardından `stats count by etiketler` ve `sort -count etiketler`.
```
:::
