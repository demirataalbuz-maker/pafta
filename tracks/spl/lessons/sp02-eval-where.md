---
id: sp02
title: Alanlar, eval ve where
summary: table, fields, rename; eval ile hesaplanan alanlar, metin birleştirme ve if/case; where ile ifadeyle süzmek ve search'ten farkı.
---

::: anlat Alanlarla çalışmak
| Komut | Ne yapar |
|---|---|
| `table a b c` | yalnızca bu alanlar, bu sırayla |
| `fields a b` / `fields - a b` | alanları tut / at |
| `rename a AS b, c AS "Yeni Ad"` | yeniden adlandır |
| `eval x = ifade` | yeni alan hesapla (varsa üzerine yazar) |
| `where ifade` | ifadesi doğru olanları bırak |

```spl
sourcetype=sunucular
| eval bos = 100 - cpu, etiket = ad . " (" . rol . ")"
| table etiket cpu bos
| rename etiket AS Sunucu, bos AS "Boş %"
```

`eval`'de metinler `.` ile birleştirilir. Koşullu değer için `if(koşul, doğruysa, yanlışsa)` ya da `case(koşul1, değer1, koşul2, değer2, ...)`; `case`'te varsayılan için son koşul olarak `true()` yazılır:

```spl
sourcetype=sunucular
| eval yuk = case(cpu >= 80, "yüksek", cpu >= 50, "orta", true(), "düşük")
| table ad cpu yuk
```

Bir alanın boş olup olmadığını `isnull(alan)` ve `isnotnull(alan)` söyler. Boş alan `alan=""` ile değil, bu iki fonksiyonla yakalanır:

```spl
sourcetype=biletler
| where isnull(kapanis)
| eval atandi = if(isnotnull(atanan_id), "evet", "hayır")
| table id baslik atandi
```

### search mi where mi?
| | `search` (aramanın kendisi) | `where` |
|---|---|---|
| Karşılaştırma | büyük-küçük harfe **duyarsız** | **duyarlı** |
| Joker | `ad=web*` | `like(ad, "web%")` |
| Sağ taraf | sabit değer | ifade: `cpu > ram_gb * 2`, fonksiyonlar |

```spl
sourcetype=sunucular
| where cpu > 50 AND like(ad, "web%")
| table ad cpu
```

> [!TUZAK]
> `eval` ve `where` içinde **çift tırnak metin**, **tek tırnak alan adı** demektir. `where rol='web'` yazarsan `web` adlı bir alanı ararsın; doğrusu `where rol="web"`. Tek tırnak, `'avg(cpu)'` gibi tuhaf adlı alanlar içindir.
:::

::: tahmin
İki arama, iki sayı:

```spl
sourcetype=sunucular rol=WEB
| stats count

sourcetype=sunucular
| where rol="WEB"
| stats count
```

???

`3`, sonra `0`. Aramadaki `rol=WEB` büyük-küçük harfe duyarsızdır, üç web sunucusunu bulur. `where` içindeki karşılaştırma ise harfi harfine yapılır: verideki değer `web`, `WEB` değil.
:::

::: gorev Boş kapasite
Her sunucunun adını ve CPU'da kalan boş yüzdeyi `bos` adıyla getir.

```starter
sourcetype=sunucular
| table ad cpu
```

```test
eq(sutunlar, ["ad", "bos"], "alanlar: ad, bos")
eq(sorted(sonuc), sorted(sorgu("SELECT ad, 100 - cpu FROM sunucular")), "bos = 100 - cpu")
```

```solution
sourcetype=sunucular
| eval bos = 100 - cpu
| table ad bos
```

```hint
`eval bos = 100 - cpu`, sonra `table ad bos`.
```
:::

::: gorev Yük sınıfı
Her sunucu için `ad` ve `yuk` alanlarını getir: CPU 80 ve üstüyse `yüksek`, 50 ve üstüyse `orta`, değilse `düşük`.

```starter
sourcetype=sunucular
| eval yuk = "düşük"
| table ad yuk
```

```test
eq(sutunlar, ["ad", "yuk"], "alanlar: ad, yuk")
beklenen = sorgu("SELECT ad, CASE WHEN cpu >= 80 THEN 'yüksek' WHEN cpu >= 50 THEN 'orta' ELSE 'düşük' END FROM sunucular")
eq(sorted(sonuc), sorted(beklenen), "sınıflar doğru")
```

```solution
sourcetype=sunucular
| eval yuk = case(cpu >= 80, "yüksek", cpu >= 50, "orta", true(), "düşük")
| table ad yuk
```

```hint
`case(cpu >= 80, "yüksek", cpu >= 50, "orta", true(), "düşük")`: varsayılan için son koşul `true()`.
```
:::

::: gorev Rapor sütunları
Bütün sunucuların `ad` ve `cpu` alanlarını, rapor için `Sunucu` ve `CPU %` adlarıyla getir.

```starter
sourcetype=sunucular
| table ad cpu
```

```test
eq(sutunlar, ["Sunucu", "CPU %"], "alan adları: Sunucu, CPU %")
eq(len(sonuc), 12, "12 sunucu")
```

```solution
sourcetype=sunucular
| table ad cpu
| rename ad AS Sunucu, cpu AS "CPU %"
```

```hint
Boşluk ya da işaret içeren adları tırnakla yaz: `rename cpu AS "CPU %"`.
```
:::
