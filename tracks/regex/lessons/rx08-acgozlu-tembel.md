---
id: rx08
title: Açgözlü ve Tembel
summary: Niceleyiciler olabildiğince çok alır; ? ile en aza iner; olumsuz sınıf çoğu zaman en iyi çözümdür.
---

::: anlat Açgözlülük ve geri izleme
Bütün niceleyiciler varsayılan olarak **açgözlüdür** (greedy): olabildiğince **çok** karakter alır, desenin geri kalanı tutmazsa birer birer **geri verir** (geri izleme, backtracking).

```regex
<.+>
---
<b>kalın</b> ve <i>eğik</i>
```

`.+` ilk `<`'den sonra satırın **sonuna kadar** her şeyi yuttu. Sonra `>` bulabilmek için geri geri gelip **son** `>`'de durdu. Tek bir dev eşleşme çıktı.

### Tembel niceleyici: ?
Niceleyicinin sonuna `?` eklersen **tembel** (lazy) olur: olabildiğince **az** alır ve desenin geri kalanı tutar tutmaz durur.

```regex
<.+?>
---
<b>kalın</b> ve <i>eğik</i>
```

| Açgözlü | Tembel |
|---|---|
| `*` | `*?` |
| `+` | `+?` |
| `?` | `??` |
| `{2,5}` | `{2,5}?` |

### Daha iyisi: olumsuz sınıf
"`>`'ye kadar her şey" demenin en kesin ve en hızlı yolu "`>` **olmayan** karakterler"dir:

```regex
<[^>]+>
---
<b>kalın</b> ve <i>eğik</i>
```

Olumsuz sınıf hiç geri izleme yapmaz: `>`'yi görür görmez durur. Tembel `.+?` ise her karakterde "şimdi durabilir miyim?" diye sorar. Ayrıca `.` satır sonunu geçmezken `[^>]` geçer; çok satırlı yapılarda bu fark önemlidir.

> [!TUZAK]
> HTML ya da JSON'u regex'le **ayrıştırmaya** çalışma. İç içe yapıları düzenli ifadeler doğru tanıyamaz: `<div><div></div></div>`'nin hangi kapanışının hangi açılışa ait olduğunu bilemez. Basit **ayıklamalar** (bir log satırından bir alanı çekmek) için regex harikadır; yapısal veri için gerçek bir ayrıştırıcı kullan.
:::

::: tahmin
Eşleşmeleri ayrı satırlara yaz:

```regex
\d+?
```

```stdin
123
```

???

`1`, `2`, `3`. Tembel `+?` en az bir rakamla yetinir ve desenin geri kalanı (burada hiçbir şey) hemen tuttuğu için her eşleşme tek rakamdır.
:::

::: gorev Tırnak içindeki değerler
`ad="ali" rol="admin"` gibi metinlerde çift tırnaklı değerleri (tırnaklar dahil) **ayrı ayrı** bul.

```starter
".*"
```

```test
eq(bul('ad="ali" rol="admin"'), ['"ali"', '"admin"'], "iki ayrı değer")
eq(bul('bos="" dolu="x"'), ['""', '"x"'], "boş değer de eşleşmeli")
```

```solution
"[^"]*"
```

```hint
Açgözlü `.*` son tırnağa kadar gider. Tembel `.*?` ya da daha iyisi olumsuz sınıf `[^"]*`.
```
:::

::: gorev Etiket adları
HTML açılış etiketlerinin **adlarını** 1. grupta yakala: `<b>` → `b`, `<a href="x">` → `a`. Kapanış etiketleri (`</b>`) eşleşmemeli. Testler her eşleşmenin gruplarını alacak.

```starter
<(.+)>
```

```test
eq(hepsi('<b>x</b><a href="y">z</a>'), [("b",), ("a",)], "iki açılış etiketi")
eq(hepsi("<br/>"), [("br",)], "kendinden kapanan etiket")
```

```solution
<(\w+)[^>]*>
```

```hint
Ad kelime karakterlerinden oluşur: `(\w+)`. Etiketin geri kalanı için `>` olmayan karakterler.
```
:::

::: gorev Köşeli parantez içleri
Köşeli parantez içindeki parçaları (parantezler dahil) ayrı ayrı bul; boş parantez de sayılır.

```starter
\[.*\]
```

```test
eq(bul("[a] metin [b c] [] son"), ["[a]", "[b c]", "[]"], "üç parça")
```

```solution
\[[^\]]*\]
```

```hint
Açılış `\[`, sonra `]` olmayan karakterler `[^\]]*`, sonra kapanış `\]`.
```
:::
