---
id: rx15
title: Döngüyü Açmak
summary: Kaçış karakterli metinler için normal*(özel normal*)* kalıbı; tırnak içinde \" ve \\, tembel noktanın ve "kaçışlı tırnak" alternatifinin neden yanıldığı, blok yorumlar ve JSON değerleri.
---

::: anlat Kaçış karakteri olan metinler
Tırnak içindeki bir metni bulmak RX07'de kolaydı: `"[^"]*"`. Ama gerçek dünyada tırnağın içinde **kaçışlı tırnak** olabilir: `"o \"merhaba\" dedi"`. Üç yaygın deneme ve sonuçları:

| Desen | Sorun |
|---|---|
| `"[^"]*"` | ilk `\"`'de durur |
| `".*?"` | o da ilk `\"`'de durur; tembellik kaçışı bilmez |
| `"(?:\\"\|[^"])*"` | `\"`'yi tanır ama `"C:\\"` gibi **kaçışlı ters eğik çizgiyle** biten metinde kapanış tırnağını kaçış sanıp taşar |

Doğru düşünce şudur: tırnağın içinde iki tür parça vardır. **Sıradan** karakterler (tırnak ve ters eğik çizgi dışındaki her şey) ve **kaçış dizileri** (ters eğik çizgi ve ardından **herhangi** bir karakter). Ters eğik çizgi her zaman kendisinden sonraki karakterle birlikte tüketilir; böylece `\\` bir çift olarak gider ve ardından gelen `"` gerçekten kapanış olur.

### Kalıp: normal* (özel normal*)*
Jeffrey Friedl'ın "döngüyü açmak" (unrolling the loop) adını verdiği kalıp:

```regex
"[^"\\]*(?:\\.[^"\\]*)*"
---
mesaj="a \"b\" c" yol="C:\\" bos=""
```

| Parça | Görevi |
|---|---|
| `[^"\\]*` | **normal**: sıradan karakterler, olabildiğince çok |
| `\\.` | **özel**: bir kaçış dizisi (iki karakter birden) |
| `[^"\\]*` | ardından yine sıradan karakterler |
| `(?: ... )*` | özel + normal çiftleri tekrar |

`"(?:[^"\\]|\\.)*"` de doğru sonuç verir; ama her karakterde bir alternatif seçimi yapar. Açılmış biçim sıradan karakterleri tek bir sınıfla, toplu halde tüketir. Bu makinede 10 000 karakterlik bir metinde yaklaşık iki kat hızlı çalıştı. Daha önemlisi, `normal` ve `özel` parçalar **aynı karakterle başlayamadığı** için motorun geri izleyerek deneyebileceği yanlış yol yoktur. Bu, RX11'deki felaket geri izlemeye karşı da bir güvencedir.

> [!İPUCU]
> Kalıbı genelle: "özel" kısım her zaman normal kısmın dışladığı bir karakterle başlamalı. Ayraç tek tırnaksa `'[^'\\]*(?:\\.[^'\\]*)*'`, SQL'deki gibi kaçış çift tırnakla yapılıyorsa (`''`) `'[^']*(?:''[^']*)*'`.
:::

::: anlat Aynı kalıp, başka kılıklar
**Blok yorumları** `/* ... */` aynı fikirle çözülür: normal = yıldız olmayan karakterler, özel = yıldızlar ve ardından `/` olmayan bir karakter:

```regex
/\*[^*]*\*+(?:[^/*][^*]*\*+)*/
---
a /* bir */ b /** iki * yıldız **/ c
```

| Parça | Görevi |
|---|---|
| `/\*` | açılış |
| `[^*]*\*+` | yıldız olmayanlar, sonra bir ya da daha çok yıldız |
| `(?:[^/*][^*]*\*+)*` | yıldızlardan sonra `/` gelmediyse devam: yeni normal + yıldızlar |
| `/` | yıldızlardan hemen sonra gelen `/` kapanıştır |

Desen satır sonunu da doğal olarak geçer, çünkü `[^*]` satır sonunu kapsar; `(?s)` bayrağına gerek yoktur. C, JavaScript, CSS ve SQL kaynaklarındaki blok yorumlar böyle bulunur.

> [!NOT]
> Bu teknik kodu **okumak** için iyidir: yorumları ayıklamak, sabit metinleri listelemek. Ama bir dilin tamamını regex'le ayrıştırmaya kalkma. Yorumun içinde tırnak, tırnağın içinde yorum işareti gibi durumlar artınca o dilin gerçek ayrıştırıcısını kullan.
:::

::: tahmin
Hangi parçalar yakalanır? Ayrı satırlara yaz.

```regex
"[^"\\]*(?:\\.[^"\\]*)*"
```

```stdin
"a\"b" "c\\" "d"
```

???

`"a\"b"`, `"c\\"`, `"d"`. İlkinde `\"` bir kaçış dizisi olarak tüketilir ve metin sondaki tırnakta kapanır. İkincisinde `\\` bir çift olarak gider; ardından gelen tırnak kaçışlı değildir, metni kapatır. `(?:\\"|[^"])*` gibi bir desen burada `\` karakterini sıradan sayıp `\"`'yi kaçış sanabilir ve taşabilirdi.
:::

::: gorev Kaçışlı tırnak
Çift tırnak içindeki metinleri tırnaklarıyla birlikte bul. Metinde `\"` (kaçışlı tırnak) ve `\\` (kaçışlı ters eğik çizgi) geçebilir.

```starter
"[^"]*"
```

```test
eq(bul(r'mesaj="a \"b\" c" kod="x" bos=""'), [r'"a \"b\" c"', '"x"', '""'], "kaçışlı tırnak metnin içinde kalır")
eq(bul(r'yol="C:\\" sonra="y"'), [r'"C:\\"', '"y"'], "kaçışlı ters eğik çizgiyle biten metin")
```

```solution
"[^"\\]*(?:\\.[^"\\]*)*"
```

```hint
Tırnağın içinde iki tür parça var: tırnak ve ters eğik çizgi dışındaki karakterler `[^"\\]`, ve bir ters eğik çizgiyle ardından gelen herhangi bir karakter `\\.`.
```

```hint
Açılmış biçim: `"[^"\\]*(?:\\.[^"\\]*)*"`.
```
:::

::: gorev Blok yorumlar
Kaynak koddaki `/* ... */` blok yorumlarını bul. Yorumun içinde tek yıldızlar ve satır sonları olabilir, yorum birden çok yıldızla da bitebilir (`**/`). Tembel nokta (`.*?`) **kullanmadan**, döngüyü açarak yaz.

```starter
/\*.*\*/
```

```test
import re
kod = "a /* bir */ b /** iki * yıldız **/ c /* üç\nsatır */ d"
eq(bul(kod), ["/* bir */", "/** iki * yıldız **/", "/* üç\nsatır */"], "üç yorum")
eq(bul("x = 2 * 3; /**/ y"), ["/**/"], "boş yorum, çarpma işareti yorum değil")
ok(not re.search(r"\.[*+]\?", src), "tembel nokta yerine döngüyü açarak yaz")
```

```solution
/\*[^*]*\*+(?:[^/*][^*]*\*+)*/
```

```hint
Açılıştan sonra: yıldız olmayanlar `[^*]*`, sonra bir ya da daha çok yıldız `\*+`. Yıldızlardan sonra `/` gelirse yorum biter.
```

```hint
Gelmezse devam: `(?:[^/*][^*]*\*+)*`. Tamamı: `/\*[^*]*\*+(?:[^/*][^*]*\*+)*/`.
```
:::

::: gorev JSON metin değerleri
Tek satırlık bir JSON nesnesinden `"anahtar": "değer"` biçimindeki **metin** çiftlerini bul. Anahtar `anahtar`, değer `deger` adlı gruba girsin (tırnaklar hariç, kaçış dizileri olduğu gibi). Değerlerde `\"` ve `\\` geçebilir; sayı değerleri alınmasın.

```starter
"(?P<anahtar>[^"]*)"\s*:\s*"(?P<deger>[^"]*)"
```

```test
nesne = r'{"ad": "Ali \"Usta\"", "yol": "C:\\Temp\\", "n": 5}'
eq(hepsi(nesne), [{"anahtar": "ad", "deger": r'Ali \"Usta\"'},
                  {"anahtar": "yol", "deger": r"C:\\Temp\\"}], "iki metin çifti, sayı hariç")
```

```solution
"(?P<anahtar>[^"\\]*(?:\\.[^"\\]*)*)"\s*:\s*"(?P<deger>[^"\\]*(?:\\.[^"\\]*)*)"
```

```hint
Hem anahtarın hem değerin içi için açılmış kalıbı kullan: `[^"\\]*(?:\\.[^"\\]*)*`.
```
:::
