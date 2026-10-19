---
id: rx13
title: Unicode ve Türkçe Metin
summary: \w ve \d'nin Unicode anlamı, [a-z]'nin Türkçe harfleri kaçırması, (?a) ASCII kipi, (?i)'nin i/ı/İ/I'yi eşitlemesi, ayrışık (NFD) harfler ve görünmez boşluklar; [^\S ...] sınıf farkı hilesi.
---

::: anlat Harf dediğin nedir?
Python 3'te desenler varsayılan olarak **Unicode** kurallarıyla çalışır:

| Öğe | Unicode kipinde | `(?a)` ASCII kipinde |
|---|---|---|
| `\w` | her dilin harfleri, rakamları ve `_`: `ç ğ ı İ ö ş ü` dahil | yalnızca `[A-Za-z0-9_]` |
| `\d` | her yazı sisteminin **ondalık rakamları**: `٣` (Arapça), `１` (tam genişlik) dahil | yalnızca `[0-9]` |
| `\s` | bütün boşluk karakterleri: bölünmez boşluk (U+00A0), ince boşluk (U+2009) dahil | yalnızca ASCII boşluklar |
| `\b` | `\w`'nin tanımına göre | ASCII `\w`'ye göre |

```regex
\w+
---
çağrı İzmir ŞEHİR öğün
```

Buna karşılık `[a-z]` yalnızca İngiliz alfabesidir; `ç ğ ı ö ş ü` ona dahil değildir:

```regex
[a-z]+
---
çağrı
```

> [!TUZAK]
> `\d` doğrulamada sinsi bir açık bırakır: `\d+` Arapça ya da tam genişlikli rakamları da kabul eder ve Python'un `int()` fonksiyonu da onları sessizce sayıya çevirir (`int("٣٤")` sonucu 34). Girdi doğrularken `[0-9]` ya da `(?a)\d` yaz.

### (?i) ve Türkçe harfler
Python'da `(?i)` bayrağı `i`, `ı`, `I` ve `İ`'yi **birbirine eşit** sayar. Bu, "büyük harfle yazılmış Türkçeyi de bul" işinde rahatlıktır ama bir bedeli vardır: `(?i)sınır` deseni `sinir` kelimesini de bulur.

```regex
(?i)sınır
---
sınır SINIR sinir Sinir
```

Bu yüzden Türkçe metinde kesinlik gerekiyorsa büyük-küçük harf farkını bayrağa bırakma; sınıfla açıkça yaz: `[Ss][ıI]n[ıI]r`.

### Aynı görünen, farklı yazılan harfler
Unicode'da `ş` iki biçimde saklanabilir: tek karakter (U+015F, birleşik biçim, **NFC**) ya da `s` + birleştirici çengel işareti (U+0327, ayrışık biçim, **NFD**). Ekranda aynı görünürler ama regex için farklıdırlar: birleştirici işaret `\w` sayılmaz, ayrışık `şeker` kelimesi `s` ve `eker` diye bölünür. macOS'tan gelen dosya adları ve bazı kopyala-yapıştır metinler ayrışık olabilir. Çözüm regex'te değil, önce metni normalleştirmektir:

```python
import unicodedata
metin = unicodedata.normalize("NFC", metin)
```

> [!NOT]
> PCRE, .NET, Java ve JavaScript (`u` bayrağıyla) Unicode özellik sınıflarını destekler: `\p{L}` (her harf), `\p{Lu}` (büyük harf), `\p{Nd}` (ondalık rakam). Python'un yerleşik `re` modülünde bunlar yoktur; harici `regex` paketinde vardır. Splunk desenlerinde `\p{L}` kullanabilirsin.
:::

::: anlat Sınıf farkı: [^\S ...]
Çift olumsuzlama ilk bakışta tuhaf görünür ama güçlü bir hiledir. `\S` "boşluk olmayan" demektir; `[^\S]` ise "boşluk olmayan **olmayan**", yani `\s`. İçine başka karakterler eklediğinde onları da dışarıda bırakırsın:

| Sınıf | Anlamı |
|---|---|
| `[^\S\n]` | satır sonu **dışındaki** boşluklar (satırı aşmadan boşluk atlamak için) |
| `[^\S \t\r\n]` | sıradan boşluk, sekme ve satır sonu dışındaki **görünmez** boşluklar |
| `[^\W\d_]` | rakam ve alt çizgi **olmayan** kelime karakterleri: yani her dilde **harf** |

```regex
[^\W\d_]+
---
sunucu_01 çağrı42 İzmir
```

`[^\W\d_]` Python'da `\p{L}`'nin yerini tutan pratik bir harf sınıfıdır.
:::

::: tahmin
Hangi parçalar yakalanır? Ayrı satırlara yaz.

```regex
(?a)\b\w+\b
```

```stdin
eski şehir web01
```

???

`eski`, `ehir`, `web01`. ASCII kipinde `ş` kelime karakteri sayılmaz. Bu yüzden `ş` ile `e` arasında bir kelime sınırı oluşur ve ikinci eşleşme `şehir` değil `ehir` olur. Unicode kipinde (bayraksız) aynı desen `şehir`'i bütün olarak bulurdu.
:::

::: gorev Türkçe özel adlar
Büyük harfle başlayıp küçük harflerle devam eden kelimeleri bul. Türkçe büyük harfler (`Ç Ğ İ Ö Ş Ü`) ve küçük harfler (`ç ğ ı ö ş ü`) de sayılsın. Kesme işaretinden sonraki ek (`'den`) kelimeye dahil olmasın.

```starter
\b[A-Z][a-z]+\b
```

```test
eq(bul("Çağrı İzmir'den Ömer ile Ankara'ya gitti; şehir Üsküdar değil."), ["Çağrı", "İzmir", "Ömer", "Ankara", "Üsküdar"], "beş özel ad")
eq(bul("ŞEHİR Şehir şehir"), ["Şehir"], "tamamı büyük ya da tamamı küçük olan alınmaz")
```

```solution
\b[A-ZÇĞİÖŞÜ][a-zçğıöşü]+\b
```

```hint
`[A-Z]` Türkçe büyük harfleri kapsamaz; sınıfa `ÇĞİÖŞÜ` ekle. Küçük harf sınıfına da `çğıöşü` gerekir.
```
:::

::: gorev Yalnızca ASCII rakamlar
Bir form alanından gelen metindeki sayıları bul; **yalnızca** `0-9` rakamlarından oluşanlar kabul edilsin. Arapça (`٣٤`) ya da tam genişlikli (`１２`) rakamlar sayı sayılmasın.

```starter
\d+
```

```test
eq(bul("kod 42, ٣٤ ve １２ değil, 7 tamam"), ["42", "7"], "yalnızca 42 ve 7")
eq(bul("port 8080"), ["8080"], "sıradan sayı")
```

```solution
[0-9]+
```

```hint
Unicode kipinde `\d` her yazı sisteminin rakamını kabul eder. Ya açık aralık `[0-9]` yaz ya da ASCII kipini aç: `(?a)\d+`.
```
:::

::: gorev Görünmez boşlukları bul
Bir yapılandırma dosyası, kopyala-yapıştırla gelen **görünmez** boşluklar yüzünden hatalı okunuyor. Sıradan boşluk, sekme ve satır sonları **dışındaki** bütün boşluk karakterlerini bul (bölünmez boşluk U+00A0, ince boşluk U+2009 gibi).

```starter
\s
```

```test
eq(bul("port\u00a0=\u20098080\tadres = yerel\n"), ["\u00a0", "\u2009"], "iki görünmez boşluk")
eq(bul("temiz satır\tsekme\n"), [], "temiz satırda bulgu yok")
```

```solution
[^\S \t\r\n]
```

```hint
`\s` hepsini bulur. Ondan bazılarını çıkarmak için sınıf farkı hilesi: `[^\S...]`, "boşluk olmayan ve ... olmayan dışındaki her şey".
```

```hint
`[^\S \t\r\n]`: boşluk olup sıradan boşluk, sekme, satır başı ve satır sonu olmayanlar.
```
:::
