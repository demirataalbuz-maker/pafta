---
id: js04
title: Asenkron Kod ve Olay Döngüsü
summary: setTimeout, Promise, async ve await; olay döngüsünün çalışma sırası ve sıralı ya da paralel beklemek.
---

::: anlat Kod yazıldığı sırada çalışmaz
JavaScript tek iş parçacığında çalışır ama beklemeyi engellemez: zamanlayıcılar, ağ istekleri ve dosya işlemleri **sonra** çalışacak işleri sıraya koyar. Asenkron kodu okumanın anahtarı bu sıradır:

1. Önce senkron kodun **tamamı** çalışır.
2. Sonra Promise'lerin `then` işleri (mikro görevler) çalışır.
3. Sonra `setTimeout` gibi zamanlayıcı işleri çalışır; 0 ms beklemesi olanlar bile.

```javascript
console.log("başla");
setTimeout(() => console.log("zamanlayıcı"), 0);
Promise.resolve().then(() => console.log("promise"));
console.log("bitir");
```

### Promise ve async/await
Promise, ileride gelecek bir değerdir. `async` fonksiyonun içinde `await`, Promise sonuçlanana kadar **o fonksiyonu** bekletir; programın geri kalanı çalışmaya devam eder:

```javascript
const bekle = (ms, deger) => new Promise(coz => setTimeout(() => coz(deger), ms));

async function ana() {
  const a = await bekle(20, "ilk");
  const b = await bekle(10, "ikinci");
  console.log(a, b);
  return "bitti";
}
ana().then(sonuc => console.log(sonuc));
console.log("ana() çağrıldı ama henüz bitmedi");
```

Birbirinden bağımsız işleri sırayla beklemek yerine **aynı anda** başlatıp hepsini birlikte beklemek için `Promise.all`:

```javascript
const bekle = (ms, deger) => new Promise(coz => setTimeout(() => coz(deger), ms));
Promise.all([bekle(30, 1), bekle(10, 2), bekle(20, 3)]).then(d => console.log(d));
```

`Promise.all` sonuçları işlerin bitiş sırasıyla değil, **verildikleri sırayla** döndürür.

> [!TUZAK]
> `await` yalnızca `async` fonksiyonun içinde çalışır ve yalnızca o fonksiyonu bekletir. `dizi.forEach(async x => await ...)` döngüyü beklemez: forEach bütün işleri başlatır ve hemen döner. Sıralı beklemek için `for (const x of dizi) { await ... }` kullanılır.
:::

::: tahmin
Dört satırı hangi sırayla yazar?

```javascript
console.log("1");
setTimeout(() => console.log("2"), 0);
Promise.resolve().then(() => console.log("3"));
console.log("4");
```

???

`1`, `4`, `3`, `2`. Önce senkron satırlar (1 ve 4) çalışır. Ardından Promise işi (3), en son zamanlayıcı (2) gelir: 0 ms beklemeli zamanlayıcı bile mikro görevlerden sonra sıraya girer.
:::

::: gorev Sırayla bekle
Başlangıç kodu `a`, `b`, `c` değerlerini farklı sürelerde hazırlıyor ve sonuçları bitiş sırasıyla, ters yazdırıyor. `async`/`await` kullanarak üçünü **a, b, c** sırasıyla yazdır.

```starter
const bekle = (ms, deger) => new Promise(coz => setTimeout(() => coz(deger), ms));
bekle(30, "a").then(console.log);
bekle(20, "b").then(console.log);
bekle(10, "c").then(console.log);
```

```test
eq(out, "a\nb\nc\n", "a, b, c sırasıyla")
ok("await" in src, "await kullan")
```

```solution
const bekle = (ms, deger) => new Promise(coz => setTimeout(() => coz(deger), ms));

async function ana() {
  console.log(await bekle(30, "a"));
  console.log(await bekle(20, "b"));
  console.log(await bekle(10, "c"));
}
ana();
```

```hint
Bir `async function ana()` yaz; içinde her `bekle(...)`'yi `await` ile sırayla bekle, sonra `ana()`'yı çağır.
```
:::

::: gorev Hepsini birlikte bekle
Üç değer aynı anda hazırlanıyor. `Promise.all` ile hepsini bekle ve **toplamlarını** tek satırda yazdır.

```starter
const bekle = (ms, deger) => new Promise(coz => setTimeout(() => coz(deger), ms));
const isler = [bekle(30, 5), bekle(10, 7), bekle(20, 9)];
console.log(isler.length);
```

```test
eq(out, "21\n", "5 + 7 + 9 = 21")
ok("Promise.all" in src, "Promise.all kullan")
```

```solution
const bekle = (ms, deger) => new Promise(coz => setTimeout(() => coz(deger), ms));
const isler = [bekle(30, 5), bekle(10, 7), bekle(20, 9)];
Promise.all(isler).then(degerler => {
  console.log(degerler.reduce((t, x) => t + x, 0));
});
```

```hint
`Promise.all(isler).then(degerler => ...)`: `degerler` bir dizi; `reduce` ile topla.
```
:::
