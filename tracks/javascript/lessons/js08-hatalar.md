---
id: js08
title: Hatalar ve Hata Yönetimi
summary: throw, try/catch/finally, Error türleri ve kendi hata sınıfları, asenkron kodda hatalar (await ile try/catch, .catch), işlenmeyen reddedilmeler, Promise.allSettled ve hata yutan kodu okumak.
kazanim: JSA 3.12.1, JSA 4.8.1, JSA 4.9.1
---

::: anlat throw, try, catch, finally
Bir hata `throw` ile fırlatılır ve çağrı yığınında yukarı doğru, onu yakalayan ilk `try/catch`'e kadar ilerler:

```javascript
function bol(a, b) {
  if (b === 0) throw new RangeError("sıfıra bölme");
  return a / b;
}
try {
  console.log(bol(6, 3));
  console.log(bol(1, 0));
  console.log("buraya gelinmez");
} catch (e) {
  console.log(`${e.name}: ${e.message}`);
} finally {
  console.log("finally her durumda çalışır");
}
```

| Hata türü | Ne zaman |
|---|---|
| `TypeError` | yanlış türde değer: `undefined`'ın özelliğini okumak, fonksiyon olmayanı çağırmak |
| `ReferenceError` | tanımsız değişken |
| `RangeError` | aralık dışı değer |
| `SyntaxError` | `JSON.parse("{bozuk")` gibi ayrıştırma hataları |

Kendi hata türlerini `Error`'dan türeterek tanımlarsın; `instanceof` ile yalnızca beklediğin hatayı yakalayıp gerisini yukarı geçirebilirsin:

```javascript
class DogrulamaHatasi extends Error {
  constructor(mesaj) { super(mesaj); this.name = "DogrulamaHatasi"; }
}
try {
  throw new DogrulamaHatasi("port 0-65535 arasında olmalı");
} catch (e) {
  if (!(e instanceof DogrulamaHatasi)) throw e;   // beklemediğin hatayı yutma, yukarı geçir
  console.log(e.name, "-", e.message);
}
```

> [!TUZAK]
> `catch (e) {}` boş bırakılmış bir yakalama bloğu, kod okurken aranacak ilk kırmızı bayraklardan biridir: hata sessizce kaybolur, program yanlış veriyle devam eder ve sorunun izi kalmaz. En azından günlüğe yaz; yapacak bir şeyin yoksa hiç yakalama.
:::

::: anlat Asenkron hatalar
Promise içinde fırlatılan hata Promise'i **reddeder** (rejected). İki yakalama biçimi vardır:

```javascript
const getir = (ok) => new Promise((coz, reddet) =>
  setTimeout(() => (ok ? coz("veri") : reddet(new Error("zaman aşımı"))), 5));

getir(false).catch(e => console.log("catch:", e.message));      // .then/.catch zinciri

async function ana() {
  try {
    await getir(false);                                         // await reddedilmeyi fırlatır
  } catch (e) {
    console.log("try:", e.message);
  }
}
ana();
```

Hiçbir yerde yakalanmayan bir reddedilme Node.js'te programı **sonlandırır** (`UnhandledPromiseRejection`). Birkaç işten bazılarının başarısız olabileceğini kabul ediyorsan `Promise.all` yerine `Promise.allSettled` kullan: biri reddedilse bile hepsinin sonucunu verir:

```javascript
Promise.allSettled([Promise.resolve(1), Promise.reject(new Error("x")), Promise.resolve(3)])
  .then(s => console.log(s.map(x => x.status).join(",")));      // fulfilled,rejected,fulfilled
```

| İşlev | Biri reddedilirse |
|---|---|
| `Promise.all` | hemen reddedilir; öteki sonuçlar kaybolur |
| `Promise.allSettled` | hepsini bekler; her biri `{status, value}` ya da `{status, reason}` |
| `Promise.any` | ilk **başarılı** olanla çözülür |
| `Promise.race` | ilk biten (başarılı ya da değil) kazanır |
:::

::: tahmin
Üç satır yazar:

```javascript
function bol(a, b) {
  if (b === 0) throw new RangeError("sıfıra bölme");
  return a / b;
}
try {
  console.log(bol(6, 3));
  console.log(bol(1, 0));
  console.log("buraya gelmez");
} catch (e) {
  console.log(e.name + ": " + e.message);
} finally {
  console.log("finally");
}
```

???

`2`, `RangeError: sıfıra bölme`, `finally`. İlk bölme 2 yazar. İkincisi hata fırlatır; `try` bloğunun geri kalanı atlanır ve `catch` çalışır. `finally` her durumda en sonda çalışır.
:::

::: gorev Güvenli JSON
`guvenliParse(metin, varsayilan)` fonksiyonunu yaz: metin geçerli JSON'sa ayrıştırılmış değeri, değilse `varsayilan`'ı döndürsün. Alttaki üç satır olduğu gibi kalsın.

```starter
function guvenliParse(metin, varsayilan) {
  return JSON.parse(metin);
}

console.log(JSON.stringify(guvenliParse('{"port": 8443}', {})));
console.log(JSON.stringify(guvenliParse("{bozuk", { port: 80 })));
console.log(JSON.stringify(guvenliParse("", null)));
```

```test
eq(out, '{"port":8443}\n{"port":80}\nnull\n', "geçerli, bozuk ve boş metin")
```

```solution
function guvenliParse(metin, varsayilan) {
  try {
    return JSON.parse(metin);
  } catch (e) {
    return varsayilan;
  }
}

console.log(JSON.stringify(guvenliParse('{"port": 8443}', {})));
console.log(JSON.stringify(guvenliParse("{bozuk", { port: 80 })));
console.log(JSON.stringify(guvenliParse("", null)));
```

```hint
`JSON.parse` bozuk metinde `SyntaxError` fırlatır; `try/catch` ile yakala ve varsayılanı döndür.
```
:::

::: gorev Bazıları başarısız olabilir
Üç sunucuya "durum sorgusu" atılıyor; biri başarısız oluyor. `Promise.allSettled` kullanarak önce başarılı sorgu sayısını, sonra her başarısız sorgunun hata mesajını ayrı satırda yazdır.

```starter
const sorgu = (ad, ok, ms) => new Promise((coz, reddet) =>
  setTimeout(() => (ok ? coz(ad + " tamam") : reddet(new Error(ad + " yanıt vermedi"))), ms));

Promise.all([sorgu("web01", true, 20), sorgu("web02", false, 10), sorgu("web03", true, 5)])
  .then(sonuclar => console.log(sonuclar.length))
  .catch(e => console.log("hepsi kayboldu"));
```

```test
eq(out, "2\nweb02 yanıt vermedi\n", "başarılı sayısı ve hata mesajı")
ok("allSettled" in src, "Promise.allSettled kullan")
```

```solution
const sorgu = (ad, ok, ms) => new Promise((coz, reddet) =>
  setTimeout(() => (ok ? coz(ad + " tamam") : reddet(new Error(ad + " yanıt vermedi"))), ms));

Promise.allSettled([sorgu("web01", true, 20), sorgu("web02", false, 10), sorgu("web03", true, 5)])
  .then(sonuclar => {
    console.log(sonuclar.filter(s => s.status === "fulfilled").length);
    for (const s of sonuclar) {
      if (s.status === "rejected") console.log(s.reason.message);
    }
  });
```

```hint
`Promise.allSettled` her işin sonucunu `{status: "fulfilled", value}` ya da `{status: "rejected", reason}` olarak verir.
```
:::

::: gorev Yalnızca beklenen hatayı yakala
`portDogrula(p)` fonksiyonunu yaz: `p` 0 ile 65535 arasında bir tam sayı değilse `DogrulamaHatasi` fırlatsın (mesaj: `geçersiz port: <p>`), geçerliyse `p`'yi döndürsün. Alttaki döngü her girdi için ya portu ya da `hata: <mesaj>` yazmalı.

```starter
class DogrulamaHatasi extends Error {}

function portDogrula(p) {
  return p;
}

for (const p of [443, 70000, -1, 8080.5, 22]) {
  try {
    console.log(portDogrula(p));
  } catch (e) {
    if (!(e instanceof DogrulamaHatasi)) throw e;
    console.log("hata: " + e.message);
  }
}
```

```test
eq(out, "443\nhata: geçersiz port: 70000\nhata: geçersiz port: -1\nhata: geçersiz port: 8080.5\n22\n", "beş girdi")
```

```solution
class DogrulamaHatasi extends Error {}

function portDogrula(p) {
  if (!Number.isInteger(p) || p < 0 || p > 65535) {
    throw new DogrulamaHatasi("geçersiz port: " + p);
  }
  return p;
}

for (const p of [443, 70000, -1, 8080.5, 22]) {
  try {
    console.log(portDogrula(p));
  } catch (e) {
    if (!(e instanceof DogrulamaHatasi)) throw e;
    console.log("hata: " + e.message);
  }
}
```

```hint
Tam sayı denetimi: `Number.isInteger(p)`. Aralık dışındaysa `throw new DogrulamaHatasi("geçersiz port: " + p)`.
```
:::
