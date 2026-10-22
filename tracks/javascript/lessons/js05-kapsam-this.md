---
id: js05
title: Kapsam, Yukarı Taşıma ve this
summary: var ile let/const kapsam farkı, yukarı taşıma (hoisting) ve geçici ölü bölge, this'in çağrılış biçimine göre değişmesi, ok fonksiyonlarında this, bind/call/apply, katı kip ve döngülerdeki kapanış tuzağı.
kazanim: JSA 1.7.1, JSA 4.2.1, JSA 4.3.1
---

::: anlat Kapsam ve yukarı taşıma
JavaScript'te değişkenin **nerede görüneceğini** onu nasıl tanımladığın belirler:

| Tanım | Kapsam | Tanımdan önce kullanılırsa |
|---|---|---|
| `var x` | **fonksiyon** kapsamı (bloklara aldırmaz) | `undefined` (bildirim yukarı taşınır, değer taşınmaz) |
| `let x`, `const x` | **blok** kapsamı (`{ }`) | `ReferenceError` (geçici ölü bölge) |
| `function f() {}` | fonksiyon kapsamı | çağrılabilir: tamamı yukarı taşınır |

```javascript
console.log(typeof eski);        // "undefined": var yukarı taşındı ama değeri yok
var eski = 1;
try {
  console.log(yeni);
} catch (e) {
  console.log(e.name);           // ReferenceError: let'in geçici ölü bölgesi
}
let yeni = 2;
```

Eski kodda (ve küçültülmüş paketlerde) `var` hâlâ çok yaygındır. `var`'ın bloklara aldırmaması, onu okurken en sık şaşırtan şeydir:

```javascript
if (true) { var a = 1; let b = 2; }
console.log(typeof a, typeof b);  // "number undefined": a bloktan sızdı, b sızmadı
```
:::

::: anlat this: kim çağırdı?
`this`, fonksiyonun **nerede tanımlandığına** değil, **nasıl çağrıldığına** bağlıdır (ok fonksiyonları hariç):

| Çağrı | `this` |
|---|---|
| `nesne.metot()` | `nesne` |
| `metot()` (nesnesiz) | katı kipte `undefined`; katı olmayan kipte küresel nesne |
| `new Sinif()` | yeni oluşturulan nesne |
| `f.call(x, ...)`, `f.apply(x, [...])` | `x` |
| `f.bind(x)` | `x`'e kalıcı olarak bağlanmış yeni bir fonksiyon döner |
| ok fonksiyonu `() => ...` | kendi `this`'i yoktur; **tanımlandığı yerin** `this`'ini kullanır |

Klasik hata: bir metodu nesnesinden koparıp bir geri çağırmaya vermek. Sınıf gövdeleri ve ES modülleri her zaman **katı kipte** (`"use strict"`) çalışır; orada kopan `this` `undefined` olur ve program `TypeError` ile durur:

```javascript
"use strict";
class Sayac {
  constructor() { this.n = 0; }
  artir() { this.n++; return this.n; }
}
const s = new Sayac();
const kopuk = s.artir;
try { kopuk(); } catch (e) { console.log(e.name); }   // TypeError
const bagli = s.artir.bind(s);
console.log(bagli());                                  // 1
setTimeout(() => console.log(s.artir()), 0);           // ok fonksiyonu: this kaybolmaz → 2
```

### Döngüdeki kapanış
Bir kapanış değişkenin **değerini değil kendisini** hatırlar. `var` ile yazılmış bir döngüde bütün kapanışlar **aynı** değişkeni paylaşır ve döngü bittiğinde onun son değerini görür; `let` ise her tur için yeni bir değişken oluşturur:

```javascript
const a = [], b = [];
for (var i = 0; i < 3; i++) a.push(() => i);
for (let j = 0; j < 3; j++) b.push(() => j);
console.log(a.map(f => f()).join(","), b.map(f => f()).join(","));   // 3,3,3 0,1,2
```
:::

::: tahmin
Dört satır yazar:

```javascript
"use strict";
const sayac = { n: 0, artir() { this.n++; return this.n; } };
console.log(sayac.artir());
const f = sayac.artir;
try { f(); } catch (e) { console.log(e.name); }
const g = sayac.artir.bind(sayac);
console.log(g());
const isler = [];
for (var i = 0; i < 3; i++) isler.push(() => i);
console.log(isler.map(h => h()).join(","));
```

???

`1`, `TypeError`, `2`, `3,3,3`. `sayac.artir()` nesne üzerinden çağrılır, `this` sayaçtır. `f()` nesnesiz çağrılır; katı kipte `this` `undefined` olduğu için `this.n` hata verir. `bind` this'i sayaca bağlar: n 2 olur. `var i` bütün kapanışlarca paylaşılır; döngü bitince 3'tür.
:::

::: gorev Bağımsız sayaçlar
`sayacYap()` fonksiyonunu yaz: her çağrıda **kendi** sayısını tutan yeni bir sayaç döndürsün; sayacın `artir()` metodu sayıyı bir artırıp yeni değeri döndürsün. Başlangıç kodundaki sayaçlar aynı sayıyı paylaşıyor; aşağıdaki üç satır `1`, `2`, `1` yazmalı.

```starter
var sayi = 0;
function sayacYap() {
  return { artir() { sayi++; return sayi; } };
}

const a = sayacYap();
const b = sayacYap();
console.log(a.artir());
console.log(a.artir());
console.log(b.artir());
```

```test
eq(out, "1\n2\n1\n", "her sayaç kendi sayısını tutar")
```

```solution
function sayacYap() {
  let sayi = 0;
  return { artir() { sayi++; return sayi; } };
}

const a = sayacYap();
const b = sayacYap();
console.log(a.artir());
console.log(a.artir());
console.log(b.artir());
```

```hint
Sayıyı fonksiyonun **içinde** tanımla: her `sayacYap()` çağrısı yeni bir `sayi` değişkeni oluşturur ve döndürülen nesne onu kapanışla hatırlar.
```
:::

::: gorev Döngüde zamanlayıcı
Başlangıç kodu `3`, `3`, `3` yazıyor. Kodu, her zamanlayıcı kendi turunun sayısını yazacak şekilde (`0`, `1`, `2`) düzelt.

```starter
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}
```

```test
eq(out, "0\n1\n2\n", "her tur kendi değerini yazar")
```

```solution
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}
```

```hint
Zamanlayıcılar döngü bittikten sonra çalışır. `var` bütün turlar için tek bir değişkendir; `let` her tura yeni bir değişken verir.
```
:::

::: gorev Kopan this
`Gunluk` sınıfının `yaz` metodu bir dizi üzerinde `map`'e veriliyor ve `this` kopuyor. Kodu düzelt: çıktı `[web] başladı` ve `[web] durdu` olmalı. Sınıfı değiştirme; yalnızca son iki satırla oyna.

```starter
class Gunluk {
  constructor(etiket) { this.etiket = etiket; }
  yaz(mesaj) { return `[${this.etiket}] ${mesaj}`; }
}
const g = new Gunluk("web");
const satirlar = ["başladı", "durdu"].map(g.yaz);
satirlar.forEach(s => console.log(s));
```

```test
eq(out, "[web] başladı\n[web] durdu\n", "this korunmalı")
ok("class Gunluk" in src and "yaz(mesaj) { return `[${this.etiket}] ${mesaj}`; }" in src, "sınıf değişmemeli")
```

```solution
class Gunluk {
  constructor(etiket) { this.etiket = etiket; }
  yaz(mesaj) { return `[${this.etiket}] ${mesaj}`; }
}
const g = new Gunluk("web");
const satirlar = ["başladı", "durdu"].map(m => g.yaz(m));
satirlar.forEach(s => console.log(s));
```

```hint
`map(g.yaz)` metodu nesnesinden koparır. Ya bir ok fonksiyonuyla nesne üzerinden çağır (`m => g.yaz(m)`) ya da `g.yaz.bind(g)` ver.
```
:::
