---
id: js02
title: Fonksiyonlar ve Kapanışlar
summary: function bildirimi, ok fonksiyonları, varsayılan parametreler, fonksiyonu değer olarak geçirmek ve kapanışların değişkeni hatırlaması.
---

::: anlat Fonksiyonun üç yazımı
Aynı fonksiyonu kodlarda üç biçimde görürsün:

```javascript
function kare(x) { return x * x; }           #! bildirim
const kare2 = function (x) { return x * x; };  #! ifade
const kare3 = x => x * x;                    #! ok fonksiyonu: tek ifade, örtük return
console.log(kare(3), kare2(4), kare3(5));
```

Ok fonksiyonunda gövde süslü parantezle yazılırsa `return` gerekir: `x => { return x * x; }`. Tek bir nesne döndürürken parantez gerekir: `x => ({ deger: x })`.

### Varsayılan parametreler
Eksik verilen argüman `undefined` olur; varsayılan değer bunu karşılar:

```javascript
function baglan(host, port = 443) {
  return `${host}:${port}`;
}
console.log(baglan("web01"), baglan("db01", 5432));
```

### Fonksiyon bir değerdir
Fonksiyonlar başka fonksiyonlara verilebilir (geri çağırma, callback) ve fonksiyondan döndürülebilir:

```javascript
const uygula = (dizi, fn) => dizi.map(fn);
console.log(uygula([1, 2, 3], x => x * 10));
```

### Kapanış (closure)
İçeride tanımlanan bir fonksiyon, dışındaki değişkenleri **hatırlar**; dış fonksiyon bitse bile:

```javascript
function sayacUret() {
  let n = 0;
  return () => ++n;
}
const say = sayacUret();
say();
say();
console.log(say());
```

> [!NOT]
> Kapanışlar web kodunda her yerdedir: bir düğmeye bağlanan olay işleyicisi, tanımlandığı yerdeki değişkenleri tıklandığı an hâlâ görür. Kodu okurken "bu fonksiyon hangi değişkenleri yakalamış?" sorusu, davranışını anlamanın anahtarıdır.
:::

::: tahmin
Tek satır yazar:

```javascript
function sayacUret() {
  let n = 0;
  return () => ++n;
}
const a = sayacUret();
const b = sayacUret();
a();
a();
console.log(a(), b());
```

???

`3 1`. Her `sayacUret()` çağrısı kendi `n` değişkenini yaratır. `a` iki kez çağrıldıktan sonra üçüncüde 3 döner; `b`'nin sayacı ayrıdır ve ilk çağrısında 1 döner.
:::

::: gorev Varsayılan selam
`selamla` fonksiyonu ad verilmezse `misafir` kullansın. Betik `selamla()` ve `selamla("Ece")` sonuçlarını yazdırsın.

```starter
function selamla(ad) {
  return `Merhaba, ${ad}!`;
}
console.log(selamla());
console.log(selamla("Ece"));
```

```test
eq(out, "Merhaba, misafir!\nMerhaba, Ece!\n", "varsayılan ve verilen ad")
```

```solution
function selamla(ad = "misafir") {
  return `Merhaba, ${ad}!`;
}
console.log(selamla());
console.log(selamla("Ece"));
```

```hint
Parametreye varsayılan değer: `function selamla(ad = "misafir")`.
```
:::

::: gorev Çarpan üreteci
`carpanUret(k)` fonksiyonu, aldığı sayıyı `k` ile çarpan bir **fonksiyon** döndürsün. Girdinin her satırı `k x` biçiminde; her satır için `carpanUret(k)(x)` sonucunu yazdır.

```starter
function carpanUret(k) {
  return k;
}
const satirlar = require("fs").readFileSync(0, "utf8").trim().split("\n");
for (const s of satirlar) {
  const [k, x] = s.split(" ").map(Number);
  console.log(carpanUret(k)(x));
}
```

```stdin
3 5
10 7
```

```test
eq(run("3 5\n10 7\n"), "15\n70\n", "3·5 ve 10·7")
eq(run("0 99\n-2 4\n"), "0\n-8\n", "0 ve negatif çarpan")
```

```solution
function carpanUret(k) {
  return x => x * k;
}
const satirlar = require("fs").readFileSync(0, "utf8").trim().split("\n");
for (const s of satirlar) {
  const [k, x] = s.split(" ").map(Number);
  console.log(carpanUret(k)(x));
}
```

```hint
Bir fonksiyon döndür: `return x => x * k;`. İçteki fonksiyon `k`'yi kapanışla hatırlar.
```
:::
