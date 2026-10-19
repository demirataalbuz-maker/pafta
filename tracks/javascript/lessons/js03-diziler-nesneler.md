---
id: js03
title: Diziler, Nesneler ve JSON
summary: map, filter, reduce, find; nesneler, ayrıştırma (destructuring) ve yayma (spread); JSON.parse ve JSON.stringify; ?. ve ?? işleçleri.
---

::: anlat Dizi metotları
Modern JavaScript kodunda döngülerin çoğu dizi metotlarıyla yazılır:

```javascript
const sunucular = [
  { ad: "web01", rol: "web", cpu: 72 },
  { ad: "db01", rol: "veritabanı", cpu: 91 },
  { ad: "web03", rol: "web", cpu: 18 },
];
console.log(sunucular.filter(s => s.cpu > 50).map(s => s.ad));      #! süz, dönüştür
console.log(sunucular.reduce((toplam, s) => toplam + s.cpu, 0));    #! tek değere indir
console.log(sunucular.find(s => s.rol === "veritabanı").ad);         #! ilk eşleşen
console.log(sunucular.some(s => s.cpu > 90), sunucular.every(s => s.cpu > 10));
```

| Metot | Döndürdüğü |
|---|---|
| `map(fn)` | her elemanın dönüştürülmüş hali (yeni dizi) |
| `filter(fn)` | koşulu sağlayanlar (yeni dizi) |
| `reduce(fn, başlangıç)` | tek bir değer |
| `find(fn)` | ilk eşleşen eleman ya da `undefined` |
| `some(fn)`, `every(fn)` | en az biri / hepsi |

### Ayrıştırma ve yayma
```javascript
const { ad, cpu, ...geri } = { ad: "db01", cpu: 91, rol: "veritabanı", sehir: "İstanbul" };
console.log(ad, cpu, geri);
const [ilk, ikinci] = ["a", "b", "c"];
console.log(ilk, ikinci);
const ayar = { port: 443, tls: true };
console.log({ ...ayar, port: 8443 });       #! kopyala ve bir alanı değiştir
```

### JSON
Web uygulamaları veriyi JSON olarak taşır: `JSON.parse` metni nesneye, `JSON.stringify` nesneyi metne çevirir:

```javascript
const yanit = '{"sunucu":"web01","olcumler":[40,58,72]}';
const veri = JSON.parse(yanit);
console.log(veri.olcumler.length, Math.max(...veri.olcumler));
console.log(JSON.stringify({ ad: "web01", aktif: true }));
```

### ?. ve ??
`a?.b`, `a` `null` ya da `undefined` ise hata vermek yerine `undefined` döner. `x ?? y`, `x` `null`/`undefined` ise `y`'yi verir (`||`'dan farkı: `0` ve `""` korunur):

```javascript
const k = { profil: null, deneme: 0 };
console.log(k.profil?.ad, k.deneme ?? 5, k.deneme || 5);
```
:::

::: tahmin
Dört satır yazar:

```javascript
const s = [{ ad: "web01", cpu: 72 }, { ad: "db01", cpu: 91 }, { ad: "web03", cpu: 18 }];
console.log(s.filter(x => x.cpu > 50).map(x => x.ad).join(","));
console.log(s.reduce((t, x) => t + x.cpu, 0));
const { ad, ...geri } = s[1];
console.log(ad, JSON.stringify(geri));
console.log(s[5]?.ad ?? "yok");
```

???

`web01,db01`, `181`, `db01 {"cpu":91}`, `yok`. CPU'su 50'yi aşan iki sunucunun adları birleştirilir; `reduce` CPU'ları toplar (72 + 91 + 18). Ayrıştırma `ad`'ı alır, kalanı `geri`'ye koyar. `s[5]` yok: `?.` hata vermeden `undefined` döner, `??` yerine "yok" koyar.
:::

::: gorev Rollere göre say
Girdi, sunucuların bir JSON dizisidir (`ad`, `rol`, `cpu`). Her rolün kaç sunucusu olduğunu `rol: sayı` biçiminde, role göre **alfabetik** sırayla yazdır.

```starter
const sunucular = JSON.parse(require("fs").readFileSync(0, "utf8"));
console.log(sunucular.length);
```

```stdin
[{"ad":"web01","rol":"web","cpu":72},{"ad":"db01","rol":"db","cpu":91},{"ad":"web03","rol":"web","cpu":18}]
```

```test
eq(run('[{"ad":"web01","rol":"web","cpu":72},{"ad":"db01","rol":"db","cpu":91},{"ad":"web03","rol":"web","cpu":18}]'), "db: 1\nweb: 2\n", "db 1, web 2")
eq(run('[{"ad":"a","rol":"x","cpu":1}]'), "x: 1\n", "tek sunucu")
eq(run("[]"), "", "boş dizi → çıktı yok")
```

```solution
const sunucular = JSON.parse(require("fs").readFileSync(0, "utf8"));
const sayim = sunucular.reduce((s, x) => {
  s[x.rol] = (s[x.rol] ?? 0) + 1;
  return s;
}, {});
for (const rol of Object.keys(sayim).sort()) {
  console.log(`${rol}: ${sayim[rol]}`);
}
```

```hint
`reduce` ile bir nesne biriktir: `s[x.rol] = (s[x.rol] ?? 0) + 1`.
```

```hint
Anahtarları sırala: `Object.keys(sayim).sort()`.
```
:::

::: gorev En yoğun sunucu
Aynı JSON girdisinden CPU'su **en yüksek** sunucunun adını yazdır; dizi boşsa `yok` yazdır.

```starter
const sunucular = JSON.parse(require("fs").readFileSync(0, "utf8"));
console.log(sunucular[0].ad);
```

```stdin
[{"ad":"web01","rol":"web","cpu":72},{"ad":"db01","rol":"db","cpu":91},{"ad":"web03","rol":"web","cpu":18}]
```

```test
eq(run('[{"ad":"web01","rol":"web","cpu":72},{"ad":"db01","rol":"db","cpu":91},{"ad":"web03","rol":"web","cpu":18}]'), "db01\n", "db01")
eq(run('[{"ad":"x","rol":"r","cpu":5},{"ad":"y","rol":"r","cpu":50}]'), "y\n", "sonda olan en yüksek")
eq(run("[]"), "yok\n", "boş dizi → yok")
```

```solution
const sunucular = JSON.parse(require("fs").readFileSync(0, "utf8"));
const enYogun = sunucular.reduce((en, s) => (en === null || s.cpu > en.cpu ? s : en), null);
console.log(enYogun?.ad ?? "yok");
```

```hint
`reduce` ile şimdiye kadarki en yüksek elemanı taşı; başlangıç değeri `null` olsun.
```

```hint
Boş dizide sonuç `null` kalır: `enYogun?.ad ?? "yok"`.
```
:::
