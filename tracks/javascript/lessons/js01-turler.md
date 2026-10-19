---
id: js01
title: Türler ve Karşılaştırma
summary: const ve let, typeof, şablon metinler, == ile === farkı, örtük tür dönüşümü, doğrumsu ve yanlışımsı değerler, null ve undefined.
---

::: anlat Değişkenler ve türler
JavaScript'i okumayı öğrenmenin büyük kısmı, dilin **örtük tür dönüşümlerini** tanımaktır. Önce temeller:

```javascript
const ad = "web01";          #! değiştirilemez bağ
let cpu = 72;                #! değiştirilebilir
cpu += 5;
console.log(`${ad}: %${cpu}`);    #! şablon metin: ters tırnak ve ${...}
console.log(typeof ad, typeof cpu, typeof true, typeof undefined, typeof {}, typeof []);
```

Eski kodlarda `var` görürsün; `let` gibidir ama blok değil fonksiyon kapsamlıdır. Yeni kodda `const` ve `let` kullanılır.

### == ve ===
`===` **katı** eşitliktir: tür de aynı olmalı. `==` ise karşılaştırmadan önce türleri dönüştürmeye çalışır ve şaşırtıcı sonuçlar verir:

```javascript
console.log(1 == "1", 1 === "1");
console.log(0 == "", 0 == "0", "" == "0");
console.log(null == undefined, null === undefined);
console.log("2" + 1, "2" - 1, "2" * "3");
```

`+` iki taraftan biri metinse **birleştirir**; `-`, `*`, `/` ise her şeyi sayıya çevirir.

### Doğrumsu ve yanlışımsı
`if` içinde şu değerler yanlış sayılır: `false`, `0`, `""` (boş metin), `null`, `undefined`, `NaN`. Geri kalan her şey doğrudur; `"0"`, `[]` ve `{}` dahil:

```javascript
for (const deger of [0, "0", "", [], null, "yok"]) {
  console.log(JSON.stringify(deger), deger ? "doğru" : "yanlış");
}
```

> [!TUZAK]
> `Number("")` sonucu `0`'dır, `NaN` değil. Bu yüzden boş bir form alanı "sayı mı?" denetiminden geçebilir. Sayı denetiminde boş metni ayrıca kontrol et.

> [!GÜVENLİK]
> Kod okurken `==` gördüğün her yer, özellikle kimlik, rol ya da durum denetiminde, durup bakmaya değer: örtük dönüşüm beklenmeyen değerleri eşit sayabilir. Güvenli kod `===` kullanır.
:::

::: tahmin
Dört satır yazar:

```javascript
console.log(1 + "2");
console.log("5" - 2);
console.log(0 == "", 0 === "");
console.log(typeof null);
```

???

`12`, `3`, `true false`, `object`. `+` metinle karşılaşınca birleştirir; `-` metni sayıya çevirir. `0 == ""` örtük dönüşümle doğru, `===` tür farkından yanlış. `typeof null` tarihî bir hata yüzünden `"object"` verir.
:::

::: gorev Dolu satırlar
Girdideki satırlardan, boşluklar atıldıktan sonra **boş olmayanların** sayısını yazdır.

```starter
const girdi = require("fs").readFileSync(0, "utf8");
console.log(girdi.split("\n").length);
```

```stdin
web01

  db01
   
```

```test
eq(run("a\n\nb\n"), "2\n", "a, boş, b → 2")
eq(run("web01\n\n  db01\n   \n"), "2\n", "yalnızca boşluk olan satır sayılmaz")
eq(run(""), "0\n", "boş girdi → 0")
```

```solution
const girdi = require("fs").readFileSync(0, "utf8");
const dolu = girdi.split("\n").filter(satir => satir.trim() !== "");
console.log(dolu.length);
```

```hint
`split("\n")` sondaki satır sonundan bir boş eleman daha üretir. `filter(satir => satir.trim() !== "")` ile boşları at.
```
:::

::: gorev Sayı mı, metin mi?
Girdinin her satırı için, satır (baştaki ve sondaki boşluklar atıldıktan sonra) geçerli bir sayıysa `sayı`, değilse `metin` yazdır. Boş satır **metin** sayılmalı.

```starter
const satirlar = require("fs").readFileSync(0, "utf8").split("\n");
satirlar.pop();
for (const s of satirlar) {
  console.log(isNaN(s) ? "metin" : "sayı");
}
```

```stdin
42
abc

3.5
```

```test
eq(run("42\nabc\n\n3.5\n"), "sayı\nmetin\nmetin\nsayı\n", "42, abc, boş, 3.5")
eq(run("  7 \n1e3\n12px\n"), "sayı\nsayı\nmetin\n", "boşluklu 7, 1e3, 12px")
eq(run("   \n"), "metin\n", "yalnızca boşluk → metin")
```

```solution
const satirlar = require("fs").readFileSync(0, "utf8").split("\n");
satirlar.pop();
for (const s of satirlar) {
  const t = s.trim();
  console.log(t !== "" && Number.isFinite(Number(t)) ? "sayı" : "metin");
}
```

```hint
`isNaN("")` yanlış döner çünkü `Number("")` 0'dır. Önce `trim()` et, boşsa doğrudan `metin` de.
```

```hint
`Number.isFinite(Number(t))`: metni sayıya çevir, sonuç sonlu bir sayı mı bak.
```
:::
