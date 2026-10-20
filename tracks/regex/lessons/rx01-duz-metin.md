---
id: rx01
title: Düz Metin ve Özel Karakterler
summary: Desen bir arama tarifidir; düz karakterler kendini eşler, on dört karakter özeldir.
---

::: anlat Desen bir arama tarifidir
**Düzenli ifade** (regular expression, kısaca regex), metin içinde arama yapmak için küçük bir dildir. Bir **desen** yazarsın, motor metni soldan sağa tarar ve desene uyan her parçayı **eşleşme** olarak verir.

En basit desen düz metindir: harfler ve rakamlar **kendilerini** eşler.

```regex
hata
---
hata: disk dolu
Hata: ağ yok
uyarı: hata sayısı 3
```

Bu bloğu **⇢ Tezgaha al** ile sağa al ve **▶ Çalıştır**'a bas. Desen editörde, metin alttaki **Metin** kutusunda durur. Eşleşmeler metnin üzerinde işaretlenir ve altta bir tabloda listelenir.

İki şeye dikkat et:

- `Hata` eşleşmedi: regex varsayılan olarak **büyük-küçük harfe duyarlıdır**
- `hata sayısı` içindeki `hata` eşleşti: desen kelime değil **karakter dizisi** arar

> [!NOT]
> Bu yolda desenler Python'un `re` motorunda çalışır. Temel sözdizimi grep, SIEM araçları (Splunk, Sentinel), JavaScript, Sigma ve YARA'daki regex'le büyük ölçüde aynıdır; motorlar arası farkları yeri geldikçe belirteceğim.
:::

::: anlat On dört özel karakter
Şu karakterler düz metin değil, **komuttur** (metakarakter):

```text
.  ^  $  *  +  ?  {  }  [  ]  \  |  (  )
```

En sık karşılaşacağın ilki **nokta**: `.` "satır sonu dışında **herhangi bir** karakter" demektir. Bu yüzden şu desen umduğundan fazlasını yakalar:

```regex
10.0.0.1
---
10.0.0.1 ve 10a0b0c1
```

Gerçek bir nokta aramak için onu ters eğik çizgiyle **kaçışla**: `\.`

```regex
10\.0\.0\.1
---
10.0.0.1 ve 10a0b0c1 ve 10.0.0.15
```

Artık `10a0b0c1` eşleşmiyor. Ama `10.0.0.15`'in içindeki `10.0.0.1` hâlâ eşleşiyor: desen "bu dizi burada **bitmeli**" demiyor. Bunu RX04'te (sınırlar) çözeceğiz.

Her metakarakter `\` ile düz karaktere döner: `\?`, `\(`, `\$`, `\\` (gerçek ters eğik çizgi).

> [!TUZAK]
> Kaçışı unutmak en yaygın regex hatasıdır ve **sessizdir**: desen yine çalışır, sadece fazlasını yakalar. Bir alan adı kuralında `ornek.com` yazarsan `ornekXcom` da eşleşir. Güvenlik kurallarında bu, bir izin listesinin sanıldığından geniş olması demektir.

> [!İPUCU]
> Tezgahtaki **Ağaç** düğmesi desenin motor tarafından nasıl okunduğunu gösterir: `LITERAL 104` ("h" harfinin kodu), `ANY` (nokta) gibi. Bir desenin neden beklediğin gibi çalışmadığını anlamanın en hızlı yolu budur.
:::

::: tahmin
Bu desen metinde hangi parçaları yakalar? Her eşleşmeyi ayrı satıra yaz.

```regex
c.t
```

```stdin
cat cut c.t ct coat
```

???

`cat`, `cut` ve `c.t`. Nokta herhangi bir **tek** karakterdir: `a`, `u` ve `.` olabilir. `ct`'de arada karakter yok, `coat`'ta ise `c`'den sonra iki karakter var.
:::

::: gorev Sürüm numarası
`v2.1` metnini **tam olarak** arayan bir desen yaz. Nokta gerçek nokta olmalı; `v2x1` eşleşmemeli.

```starter
v2.1
```

```test
ok(eslesir("sürüm v2.1 yayında"), "'sürüm v2.1 yayında' içinde bulunmalı")
ok(not eslesir("v2x1"), "'v2x1' eşleşmemeli (nokta kaçışlanmalı)")
eq(bul("v2.1 v2-1 v2.1"), ["v2.1", "v2.1"], "iki gerçek eşleşme")
```

```solution
v2\.1
```

```hint
Nokta "herhangi bir karakter" demektir. Gerçek nokta için `\.` yaz.
```
:::

::: gorev Log dosyası uzantısı
Metindeki `.log` uzantılarını (nokta dahil) bul. `alog` gibi noktasız diziler eşleşmemeli.

```starter
.log
```

```test
eq(bul("a.log b.txt c.log alog"), [".log", ".log"], "sadece gerçek .log uzantıları")
ok(not eslesir("katalog"), "'katalog' eşleşmemeli")
```

```solution
\.log
```

```hint
Desenin başındaki nokta şu an "herhangi bir karakter" anlamında. Onu kaçışla.
```
:::

::: gorev Soru işareti
`ne?` dizisini (soru işareti dahil) bul. Soru işareti de bir metakarakterdir.

```starter
ne?
```

```test
eq(bul("ne? nee ne"), ["ne?"], "sadece 'ne?' eşleşmeli")
```

```solution
ne\?
```

```hint
`?` "önceki karakter isteğe bağlı" demektir (RX03'te göreceksin). Gerçek soru işareti için `\?`.
```
:::
