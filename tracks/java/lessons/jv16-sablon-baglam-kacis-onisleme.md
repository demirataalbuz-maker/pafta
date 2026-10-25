---
id: jv16
title: Şablon Motorları · Bağlam, Otomatik Kaçış ve Ön İşleme
summary: Thymeleaf HTML kipinde th:text ve [[${...}]] değeri kaçırır, th:utext ve [(${...})] ham basar; th:href önce URL kodlaması sonra HTML kaçışı uygular, JAVASCRIPT kipi ise JS dizgisi üretip kapanış etiketini bozacak slash işaretini kaçırır. FreeMarker varsayılanı terstir: ${x} hiç kaçırmaz; kaçış ya output_format HTML ile ya ?html ile gelir ve bu ikisi birbirini dışlar. __${...}__ ön işlemesi veriyi ifadeye çevirir: ${alan} değeri metin olarak basarken __${alan}__ onu değerlendirip sonucunu basar.
---

::: anlat Aynı değer, dört farklı bağlam
Şablon motoru bir değeri sayfaya yazarken onu **bulunduğu yere göre** dönüştürür. Aynı değişken, metin gövdesinde, bir URL parametresinde ve bir `<script>` içinde üç ayrı biçimde çıkar. Kaçış bir anahtar değil, **bağlamın bir fonksiyonudur**.

Bu dersin ölçümü gerçek `thymeleaf 3.1.3.RELEASE` ve `freemarker 2.3.34` üzerinde, JDK 21 ile alındı. Taşınan değer her yerde aynı:

```
<b>ad</b> & "x" 'y'
```

Thymeleaf HTML kipinde dört yazım var ve ikisi kaçırır, ikisi kaçırmaz:

| Yazım | Davranış |
|---|---|
| `th:text="${ad}"` | HTML kaçışı uygular |
| `th:utext="${ad}"` | **ham** basar (`u` = unescaped) |
| `[[${ad}]]` | satır içi çıktı, `th:text` gibi kaçırır |
| `[(${ad})]` | satır içi **ham** çıktı, `th:utext` gibi |

`u` harfi ve parantez biçimi arasındaki fark tek karakterdir; bir şablonu okurken aradığın şey budur.

`th:href` ile bir URL parametresi yazıldığında **iki katman** üst üste gelir: değer önce URL kodlamasından geçer (`<` → `%3C`, boşluk → `%20`), sonra bütün öznitelik değeri HTML olarak kaçırılır. Bu yüzden çıktıda hem `%3C` hem `&#39;` görürsün — biri URL katmanından, öteki HTML katmanından. `/` karakteri URL'de zararsız olduğu için kodlanmadan kalır: URL kodlayıcı her şeyi değil, **o bağlamda tehlikeli olanı** kodlar.

`JAVASCRIPT` kipinde ise çıktı HTML değil bir **JS dizgisidir**: değer çift tırnak içine alınır, içindeki `"` kaçırılır, `&` `&` olur ve `</` ikilisi `<\/` yazılır. Son ayrıntı güvenliğin kendisidir: HTML ayrıştırıcısı `<script>` bloğunu ilk `</script>` dizisinde kapatır, JS dizgisinin içinde olup olmadığına bakmaz. Slash işaretini kaçırmak o diziyi oluşmaz hâle getirir.
:::

::: anlat İki motor, ters varsayılan
Thymeleaf'te kaçış **varsayılandır**; kaçmamak için `utext` yazman gerekir. FreeMarker'da durum tersidir: `${x}` hiçbir şey kaçırmaz. Kaçış iki yoldan gelir:

- Şablonun **çıktı biçimi** HTML ise (`output_format`): her `${x}` otomatik kaçar.
- Ya da tek tek istenir: `${x?html}`.

Ölçümün söylediği üçüncü şey ise bu ikisinin **birbirini dışladığıdır**: çıktı biçimi HTML iken `?html` yazmak ayrıştırma hatası verir (kaçış zaten var, ikinci kez istenemez), çıktı biçimi yokken `?no_esc` yazmak da ayrıştırma hatası verir (kapatılacak otomatik kaçış yok). `?no_esc` yalnız otomatik kaçışın açık olduğu yerde anlamlıdır ve orada onu kapatır.

Aynı iki satır, iki motorda zıt sonuç verir:

```html
<!-- Thymeleaf: kaçar -->      <p th:text="${ad}"></p>
<!-- FreeMarker: ham basar --> <p>${ad}</p>
```

Bir şablonu okurken "burada `${}` var, demek ki kaçıyor" diyemezsin; önce **hangi motor** ve **hangi çıktı biçimi** sorusunu yanıtlaman gerekir.
:::

::: anlat İfade mi, veri mi?
Son incelik şablon dilinin kendisiyle ilgili. Thymeleaf bir özniteliği değerlendirmeden önce **ön işleme** adımı uygular: metinde `__${...}__` kalıbı varsa, önce o kalıbın yerine değişkenin **değeri** yazılır, **sonra** ortaya çıkan metin ifade olarak değerlendirilir.

Fark iki satırda görünür. `alan` değişkeninin değeri `${2*21}` metni olsun:

```html
<p th:text="${alan}"></p>        <!-- değer metin olarak basılır -->
<p th:text="__${alan}__"></p>    <!-- değer ifade olarak değerlendirilir -->
```

> [!TUZAK] Ön işleme veriyi koda çevirir
> `${alan}` yazdığında değer veridir: içinde ne olursa olsun olduğu gibi basılır. `__${alan}__` yazdığında ise değer **ifadenin kendisi** olur; şablonun ne hesaplayacağına artık veri karar verir. Bu, kaçışla kapatılabilecek bir şey değildir — kaçış çıktıyı korur, ön işleme ise çıktıdan önceki adımda çalışır. Bir şablonda `__${` dizisi gördüğünde sorulacak soru "bu kaçıyor mu" değil, "bu değeri kim üretiyor"dur.
:::

::: tahmin Hangi bağlam neyi kaçırır?
Taşınan değer `<b>ad</b> & "x" 'y'`. Ön işleme bölümünde `alan` değişkeninin değeri `${2*21}` metni, `duz` değişkeninin değeri `ayse`; `yok` diye bir değişken tanımlı değil.

FreeMarker satırlarında `+ output HTML`, şablonun çıktı biçiminin HTML olduğu anlamına gelir; `duz` ise çıktı biçimi verilmediği durumdur.

```gercek
yuk                 : <b>ad</b> & "x" 'y'
--- Thymeleaf 3.1.3 / HTML kipi ---
th:text="${ad}"      : <p>&lt;b&gt;ad&lt;/b&gt; &amp; &quot;x&quot; &#39;y&#39;</p>
th:utext="${ad}"     : <p><b>ad</b> & "x" 'y'</p>
[[${ad}]]           : <p>&lt;b&gt;ad&lt;/b&gt; &amp; &quot;x&quot; &#39;y&#39;</p>
[(${ad})]           : <p><b>ad</b> & "x" 'y'</p>
th:href="@{a(q=..)}" : <a href="a?q=%3Cb%3Ead%3C/b%3E%20%26%20%22x%22%20&#39;y&#39;">l</a>
JAVASCRIPT kipi     : var s = "<b>ad<\/b> & \"x\" 'y'";
--- on isleme (alan = ${2*21}, duz = ayse) ---
th:text="${alan}"    : <p>${2*21}</p>
th:text="__${alan}__": <p>42</p>
th:text="__${duz}__" : <p>ayse</p>
th:text="'x' + __${duz}__": <p>xayse</p>
th:text="__${yok}__" : <p></p>
--- FreeMarker 2.3.34 ---
${ad}               : <p><b>ad</b> & "x" 'y'</p>
${ad} + output HTML : <p>&lt;b&gt;ad&lt;/b&gt; &amp; &quot;x&quot; &#39;y&#39;</p>
${ad?html}          : <p>&lt;b&gt;ad&lt;/b&gt; &amp; &quot;x&quot; &#39;y&#39;</p>
${ad?html} + HTML   : HATA ParseException
${ad?no_esc} + HTML : <p><b>ad</b> & "x" 'y'</p>
${ad?no_esc} duz    : HATA ParseException
```

???

**Thymeleaf dörtlüsü** tabloyu doğruluyor: `th:text` ve `[[${ad}]]` beş karakteri de kaçırıyor (`&amp; &lt; &gt; &quot; &#39;`), `th:utext` ve `[(${ad})]` değeri olduğu gibi basıyor. Dikkat: tek tırnak `&#39;` oluyor — kaçırılan küme yalnız `<` ve `>` değil.

**`th:href`** satırı iki katmanı birlikte gösteriyor. `<` `%3C` olmuş (URL katmanı), ama tek tırnak `&#39;` olmuş (HTML katmanı): URL kodlayıcı tek tırnağı tehlikeli saymadı, sonra öznitelik yazıcısı onu kaçırdı. `/` ise ikisinden de geçmeden kaldı. Yani "kaçırıldı mı" sorusu tek bir yanıt istemiyor; her katman kendi tehlikeli kümesine bakıyor.

**JAVASCRIPT kipi** HTML kaçışı *yapmıyor* — `<b>` olduğu gibi duruyor. Yaptığı şey bir JS dizgisi üretmek: `"` kaçırılmış, `&` `&` olmuş, `</b>` ise `<\/b>` yazılmış. Tek tırnak kaçırılmamış, çünkü dizgi çift tırnakla kapatılıyor ve orada zararsız. Bağlam değişince tehlikeli karakter kümesi de değişiyor.

**Ön işleme.** `${alan}` değeri metin olarak basıyor: çıktı `${2*21}`. `__${alan}__` ise `42` basıyor — aynı veri, bu kez ifade olarak çalıştırıldı. `__${duz}__` `ayse` basıyor; ön işlemeden sonra kalan `ayse` metni Thymeleaf'in değişmez simge (literal token) kuralıyla okunuyor. `'x' + __${duz}__` bunu doğruluyor: ön işleme `'x' + ayse` üretiyor, değerlendirme `xayse` veriyor. Tanımsız `yok` ise boş dizgiye dönüşüyor ve geriye boş bir ifade kalıyor.

**FreeMarker** Thymeleaf'in tersi: çıplak `${ad}` hiçbir şey kaçırmıyor. Kaçış `output_format` HTML ile ya da `?html` ile geliyor. İki `HATA ParseException` satırı ise ikisinin birlikte kullanılamadığını gösteriyor: oto-kaçış açıkken `?html` fazladır, kapalıyken `?no_esc` boşunadır. `?no_esc` yalnız oto-kaçış açıkken anlam taşır ve orada onu kapatır — dolayısıyla bir FreeMarker şablonunda `?no_esc` görmek, o şablonun çıktı biçiminin ayarlı olduğunu da söyler.
:::

::: gorev HTML kaçışını modelle
`kacir(deger, kip)` yaz: ölçülen HTML kaçışını uygula.

- `kip` `"kacir"` ise beş karakteri dönüştür: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`, `'` → `&#39;`.
- `kip` `"ham"` ise değeri olduğu gibi döndür.
- Başka her `kip` için `None`.

```starter
def kacir(deger, kip):
    if kip == "ham":
        return deger
    for eski, yeni in (("<", "&lt;"), (">", "&gt;"), ("&", "&amp;")):
        deger = deger.replace(eski, yeni)
    return deger
```

```test
need("kacir")
YUK = "<b>ad</b> & \"x\" 'y'"
BEK = "&lt;b&gt;ad&lt;/b&gt; &amp; &quot;x&quot; &#39;y&#39;"
eq(kacir(YUK, "kacir"), BEK, "ölçülen: th:text çıktısı")
eq(kacir(YUK, "ham"), YUK, "ölçülen: th:utext çıktısı")
eq(kacir("&", "kacir"), "&amp;", "tek başına ve işareti")
eq(kacir("<", "kacir"), "&lt;", "ve işaretini sonra çevirirsen bu &amp;lt; olur")
eq(kacir(">", "kacir"), "&gt;", "kapanış köşeli")
eq(kacir("\"", "kacir"), "&quot;", "çift tırnak da kaçar")
eq(kacir("'", "kacir"), "&#39;", "ölçülen: tek tırnak &#39; olur, &apos; değil")
eq(kacir("&lt;", "kacir"), "&amp;lt;", "zaten kaçmış metin ikinci kez kaçar")
eq(kacir("", "kacir"), "", "boş değer")
eq(kacir("ayse", "kacir"), "ayse", "özel karakter yok")
eq(kacir("a&b<c", "ham"), "a&b<c", "ham kip hiç dokunmaz")
eq(kacir(YUK, "bilinmeyen"), None, "tanınmayan kip")
eq(kacir("", "ham"), "", "boş değer, ham kip")
```

```solution
def kacir(deger, kip):
    if kip == "ham":
        return deger
    if kip != "kacir":
        return None
    for eski, yeni in (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"),
                       ("\"", "&quot;"), ("'", "&#39;")):
        deger = deger.replace(eski, yeni)
    return deger
```

```hint
Başlangıç kodu iki şeyi atlıyor: tırnak karakterleri ve **sıra**. `&` ilk sırada dönüştürülmelidir; `<` önce dönüşürse ürettiği `&lt;` metninin `&` işareti de sonradan kaçar ve `&amp;lt;` çıkar.
```

```hint
Tek tırnak için ölçülen karşılık `&#39;` — Thymeleaf `&apos;` yazmıyor. Tanınmayan kip için `None` döndürmeyi de unutma; sessizce kaçırmak en kötü seçenektir.
```
:::

::: gorev Motor varsayılanlarını modelle
`sablonKarari(motor, ifade, ciktiBicimi)` yaz: bir yazımın değeri kaçırıp kaçırmadığını söyle.

- `ciktiBicimi` `"HTML"` ya da `None` (çıktı biçimi verilmemiş) olur.
- `motor` `"thymeleaf"` ise: `"th:text"` ve `"[[..]]"` → `"kacar"`; `"th:utext"` ve `"[(..)]"` → `"ham"`. Çıktı biçimi kararı etkilemez.
- `motor` `"freemarker"` ise:
  - `"${x}"` → çıktı biçimi `"HTML"` ise `"kacar"`, değilse `"ham"`.
  - `"${x?html}"` → çıktı biçimi `"HTML"` **değilse** `"kacar"`; HTML ise geçersiz.
  - `"${x?no_esc}"` → çıktı biçimi `"HTML"` **ise** `"ham"`; değilse geçersiz.
- Tanınmayan motor, tanınmayan ifade ve geçersiz birleşimler için `None`.

```starter
def sablonKarari(motor, ifade, ciktiBicimi):
    if ifade in ("th:utext", "[(..)]", "${x?no_esc}"):
        return "ham"
    return "kacar"
```

```test
need("sablonKarari")
eq(sablonKarari("thymeleaf", "th:text", None), "kacar", "ölçülen: th:text kaçırır")
eq(sablonKarari("thymeleaf", "th:utext", None), "ham", "ölçülen: th:utext ham basar")
eq(sablonKarari("thymeleaf", "[[..]]", None), "kacar", "ölçülen: satır içi çıktı th:text gibi")
eq(sablonKarari("thymeleaf", "[(..)]", None), "ham", "ölçülen: satır içi ham çıktı")
eq(sablonKarari("thymeleaf", "th:text", "HTML"), "kacar", "Thymeleaf kararı çıktı biçimine bakmaz")
eq(sablonKarari("thymeleaf", "th:utext", "HTML"), "ham", "ham olan ham kalır")
eq(sablonKarari("freemarker", "${x}", None), "ham", "ölçülen: FreeMarker varsayılanı kaçırmaz")
eq(sablonKarari("freemarker", "${x}", "HTML"), "kacar", "ölçülen: output_format HTML kaçırır")
eq(sablonKarari("freemarker", "${x?html}", None), "kacar", "ölçülen: açıkça istenen kaçış")
eq(sablonKarari("freemarker", "${x?html}", "HTML"), None,
   "ölçülen: oto-kaçış açıkken ?html ayrıştırma hatası")
eq(sablonKarari("freemarker", "${x?no_esc}", "HTML"), "ham", "ölçülen: no_esc oto-kaçışı kapatır")
eq(sablonKarari("freemarker", "${x?no_esc}", None), None,
   "ölçülen: kapatacak oto-kaçış yok, ayrıştırma hatası")
eq(sablonKarari("jinja", "{{x}}", None), None, "tanınmayan motor")
eq(sablonKarari("thymeleaf", "th:value", None), None, "tanınmayan Thymeleaf yazımı")
eq(sablonKarari("freemarker", "${x?upper_case}", None), None, "tanınmayan FreeMarker yazımı")
eq(sablonKarari("thymeleaf", "${x}", None), None, "FreeMarker yazımı Thymeleaf motorunda geçersiz")
```

```solution
def sablonKarari(motor, ifade, ciktiBicimi):
    if motor == "thymeleaf":
        if ifade in ("th:text", "[[..]]"):
            return "kacar"
        if ifade in ("th:utext", "[(..)]"):
            return "ham"
        return None
    if motor == "freemarker":
        html = ciktiBicimi == "HTML"
        if ifade == "${x}":
            return "kacar" if html else "ham"
        if ifade == "${x?html}":
            return None if html else "kacar"
        if ifade == "${x?no_esc}":
            return "ham" if html else None
        return None
    return None
```

```hint
Başlangıç kodu her iki motorun kaçırdığını varsayıyor; ölçüm bunun tersini gösterdi. Önce motora göre ayrıl: Thymeleaf kararı yazımdan okunur, FreeMarker kararı yazım **ve** çıktı biçiminden.
```

```hint
`?html` ile `?no_esc` birbirinin aynası: biri oto-kaçış **kapalıyken**, öteki **açıkken** geçerlidir. Yanlış tarafta ikisi de `None` döndürmeli — ölçümde ayrıştırma hatası veriyorlar.
```
:::

::: gorev Ön işlemeyi modelle
`onIsleme(ifade, veri)` yaz: Thymeleaf ön işlemesini uygula ve değerin hangi rolde kullanıldığını söyle.

- Metindeki her `__${ad}__` parçası, `veri[ad]` değerinin metin hâliyle değiştirilir. `ad` sözlükte yoksa yerine boş dizgi yazılır.
- Dönüş `(calisacakIfade, rol)` ikilisi. `rol`, en az bir `__${...}__` parçası bulunduysa `"kod"`, hiç bulunmadıysa `"veri"`.
- Kapanışı olmayan `__${` dizisi ön işleme sayılmaz, metin olduğu gibi kalır.

```starter
def onIsleme(ifade, veri):
    for ad, deger in veri.items():
        ifade = ifade.replace("__${" + ad + "}__", str(deger))
    return (ifade, "veri")
```

```test
need("onIsleme")
V = {"alan": "${2*21}", "duz": "ayse"}
eq(onIsleme("${alan}", V), ("${alan}", "veri"), "ölçülen: değer metin olarak basılır")
eq(onIsleme("__${alan}__", V), ("${2*21}", "kod"), "ölçülen: değer ifadeye dönüşür, 42 basılır")
eq(onIsleme("__${duz}__", V), ("ayse", "kod"), "ölçülen: ayse basılır")
eq(onIsleme("'x' + __${duz}__", V), ("'x' + ayse", "kod"), "ölçülen: xayse basılır")
eq(onIsleme("__${yok}__", V), ("", "kod"), "ölçülen: tanımsız değişken boş dizgiye dönüşür")
eq(onIsleme("${duz}", V), ("${duz}", "veri"), "sıradan ifade dokunulmaz")
eq(onIsleme("__${duz}__ __${alan}__", V), ("ayse ${2*21}", "kod"), "iki parça birden")
eq(onIsleme("__${duz}", V), ("__${duz}", "veri"), "kapanış yok: ön işleme değil")
eq(onIsleme("${__duz__}", V), ("${__duz__}", "veri"), "alt çizgiler içte: desen tutmaz")
eq(onIsleme("", V), ("", "veri"), "boş ifade")
eq(onIsleme("__${alan}__", {}), ("", "kod"), "sözlük boş: parça bulundu, değer yok")
eq(onIsleme("sabit metin", V), ("sabit metin", "veri"), "hiç ifade yok")
```

```solution
def onIsleme(ifade, veri):
    sonuc = ""
    kalan = ifade
    bulundu = False
    while True:
        bas = kalan.find("__${")
        if bas < 0:
            break
        son = kalan.find("}__", bas)
        if son < 0:
            break
        ad = kalan[bas + 4:son]
        bulundu = True
        sonuc += kalan[:bas] + str(veri.get(ad, ""))
        kalan = kalan[son + 3:]
    return (sonuc + kalan, "kod" if bulundu else "veri")
```

```hint
Başlangıç kodu sözlükteki adları tek tek arıyor; bu yüzden sözlükte **olmayan** bir adı hiç görmez ve `__${yok}__` metni çıktıda kalır. Metni soldan tara: `__${` ile başlayan, `}__` ile kapanan parçaları bul, aradaki adı sözlükte ara.
```

```hint
`rol` değeri parçanın **bulunmasına** bağlıdır, değerin var olmasına değil: `__${yok}__` de ön işlemeden geçmiş sayılır. Kapanışı olmayan `__${` dizisinde ise hiç değişiklik yapılmaz ve rol `"veri"` kalır.
```
:::
