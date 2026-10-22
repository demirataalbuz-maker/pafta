---
id: js11
title: Küçültülmüş Kodu Okumak
summary: Üretimdeki JavaScript'in küçültülmüş (minified) hâli; !0 ve void 0, virgül işleci, && ve || ile koşul yazımı, iç içe üçlü işleç, hemen çağrılan fonksiyonlar (IIFE), paketleyici sarmalayıcıları ve kodu açıp yeniden adlandırma yöntemi.
kazanim: JSA 4.2.1
---

::: anlat Neden böyle görünüyor?
Tarayıcıya giden JavaScript, boyutu küçülsün diye **küçültülür**: boşluklar silinir, değişken adları tek harfe iner, ifadeler en kısa eşdeğerlerine çevrilir. Sonuç aynı işi yapar ama okunması zordur. Bir sayfanın gerçekte ne yaptığını anlamak (hangi adrese istek attığı, hangi veriyi okuduğu) çoğu zaman bu kodu okumayı gerektirir.

| Küçültülmüş | Anlamı |
|---|---|
| `!0` / `!1` | `true` / `false` |
| `void 0` | `undefined` |
| `a&&b()` | `if (a) b();` |
| `a\|\|(a=5)` | `if (!a) a = 5;` |
| `x=(f(),g(),y)` | virgül işleci: `f()` ve `g()` çalışır, sonuç `y` |
| `a?b?c:d:e` | `a ? (b ? c : d) : e` |
| `!function(){...}()` | hemen çağrılan fonksiyon (IIFE); `!` yalnızca sözdizimi içindir |
| `""+x`, `+x`, `!!x` | metne, sayıya, bool'a çevirme |

```javascript
console.log(!0, !1, void 0, (1, 2, 3));
var a = 0;
a || (a = 5);
console.log(a);
!function () { var gizli = "iife içinde"; console.log(gizli); }();
```

### Paketleyici sarmalayıcıları
webpack, Rollup, esbuild gibi paketleyiciler onlarca dosyayı tek dosyada birleştirir. Çıktıda modüller bir nesnenin ya da dizinin içinde fonksiyon olarak durur ve kendi küçük `require` fonksiyonlarıyla birbirini çağırır:

```javascript
(function (moduller) {
  var onbellek = {};
  function iste(id) {
    if (onbellek[id]) return onbellek[id].exports;
    var m = (onbellek[id] = { exports: {} });
    moduller[id](m, m.exports, iste);
    return m.exports;
  }
  iste(0);                                          // giriş modülü
})([
  function (m, e, iste) { var y = iste(1); console.log(y.selam("dünya")); },
  function (m, e) { e.selam = function (a) { return "merhaba " + a; }; },
]);
```
:::

::: anlat Açma yöntemi
Küçültülmüş bir fonksiyonu okurken sırayla:

1. **Biçimlendir.** Tarayıcı geliştirici araçlarında `{ }` (pretty print) düğmesi ya da bir biçimlendirici satırları ayırır.
2. **Kısa yazımları aç.** Yukarıdaki tabloyla `&&`, `||`, virgül ve üçlü işleçleri `if` cümlelerine çevir.
3. **Adlandır.** Bir değişkenin ne işe yaradığını anladığın anda ona anlamlı bir ad ver (`e` → `dizi`, `n` → `toplam`).
4. **Sınama girdileriyle doğrula.** Açtığın sürümü birkaç girdide eskisiyle karşılaştır; aynı sonucu vermiyorsa bir yeri yanlış açmışsındır.

```javascript
var t=function(e){for(var n=0,r=0;r<e.length;r++)e[r]%2||(n+=e[r]);return n};
// açılmış hâli:
function ciftlerinToplami(dizi) {
  let toplam = 0;
  for (let i = 0; i < dizi.length; i++) {
    if (dizi[i] % 2 === 0) toplam += dizi[i];
  }
  return toplam;
}
console.log(t([1, 2, 3, 4, 10]), ciftlerinToplami([1, 2, 3, 4, 10]));
```

> [!İPUCU]
> Bazı kodlar yalnızca küçültülmüş değil, okunmasın diye kasıtlı olarak **karartılmıştır** (obfuscation): metinler bir dizide saklanır, adlar anlamsızlaştırılır, akış dolambaçlı hâle getirilir. Yöntem aynıdır, yalnızca daha sabır ister: önce metin dizisini çöz, sonra adlandırarak ilerle. Tanımadığın bir betiği hiçbir zaman "ne yapıyor görmek için" kendi tarayıcında çalıştırma; önce oku.
:::

::: tahmin
Üç satır yazar:

```javascript
console.log(!0, !1, void 0, (1, 2, 3));
var a = 0, b = "x";
a || (a = 5);
b && console.log("b dolu");
console.log(a, typeof function () {}, ![] + "", +"");
```

???

`true false undefined 3`, `b dolu`, `5 function false 0`. `!0` doğru, `!1` yanlış; `void 0` her zaman `undefined`; virgül işleci son değeri verir. `a` 0 olduğu için `||`'nin sağı çalışır ve `a` 5 olur. `b` dolu olduğu için `&&`'nin sağı çalışır. `[]` doğrumsudur, `![]` yanlıştır ve metne çevrilince `"false"` olur; `+""` 0'dır.
:::

::: gorev Açılmış yaz: topla
Aşağıdaki küçültülmüş fonksiyonla **aynı sonuçları** veren, okunur bir `topla(a, b)` yaz: iç içe üçlü işleç ve `||` kullanmadan, `if` cümleleriyle. Alttaki satır olduğu gibi kalsın.

```javascript
var f=function(a,b){return a?b?a+b:a:b||0};
```

```starter
function topla(a, b) {
  return a + b;
}

console.log([topla(2, 3), topla(2, 0), topla(0, 5), topla(0, 0), topla(null, undefined)].join(","));
```

```test
eq(out, "5,2,5,0,0\n", "küçültülmüş sürümle aynı sonuçlar")
ok("?" not in src.split("console.log")[0] and "||" not in src, "üçlü işleç ve || olmadan")
```

```solution
function topla(a, b) {
  if (a) {
    if (b) return a + b;
    return a;
  }
  if (b) return b;
  return 0;
}

console.log([topla(2, 3), topla(2, 0), topla(0, 5), topla(0, 0), topla(null, undefined)].join(","));
```

```hint
`a ? (b ? a + b : a) : (b || 0)`: önce parantezleri koy, sonra her `?`'yi bir `if`'e çevir.
```

```hint
`b || 0`: `b` doğrumsuysa `b`, değilse 0.
```
:::

::: gorev Paketten bir modül
Aşağıdaki paket iki modül içeriyor. Giriş modülünü (0) değiştirerek, 1 numaralı modülün `rapor` fonksiyonunu `[3, 4]` ile çağır ve sonucunu yazdır. Diğer satırlara dokunma.

```starter
(function (moduller) {
  var onbellek = {};
  function iste(id) {
    if (onbellek[id]) return onbellek[id].exports;
    var m = (onbellek[id] = { exports: {} });
    moduller[id](m, m.exports, iste);
    return m.exports;
  }
  iste(0);
})([
  function (m, e, iste) { console.log("giriş"); },
  function (m, e) { e.rapor = function (d) { return "toplam=" + d.reduce(function (t, x) { return t + x; }, 0); }; },
]);
```

```test
eq(out, "toplam=7\n", "modül 1'in rapor fonksiyonu")
ok("iste(1)" in src, "modülü iste(1) ile al")
```

```solution
(function (moduller) {
  var onbellek = {};
  function iste(id) {
    if (onbellek[id]) return onbellek[id].exports;
    var m = (onbellek[id] = { exports: {} });
    moduller[id](m, m.exports, iste);
    return m.exports;
  }
  iste(0);
})([
  function (m, e, iste) { console.log(iste(1).rapor([3, 4])); },
  function (m, e) { e.rapor = function (d) { return "toplam=" + d.reduce(function (t, x) { return t + x; }, 0); }; },
]);
```

```hint
Giriş modülü üçüncü argüman olarak `iste` fonksiyonunu alıyor. `iste(1)` modül 1'in `exports` nesnesini döndürür.
```
:::
