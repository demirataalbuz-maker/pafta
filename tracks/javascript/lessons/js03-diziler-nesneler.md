---
id: js03
title: Diziler, Nesneler ve JSON
summary: map, filter, reduce, find; nesneler, ayrıştırma (destructuring) ve yayma (spread); JSON.parse ve JSON.stringify; ?. ve ?? işleçleri; Map ve Set.
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

::: anlat Map ve Set
Düz nesneler (`{}`) sözlük gibi kullanılabilir ama iki sınırları vardır: anahtarlar her zaman **metne** çevrilir ve nesnenin kendi özellikleriyle karışabilir. ES2015'ten beri bunun için iki ayrı yapı var.

**`Set`** tekrarsız bir değer topluluğudur:

```javascript
const roller = new Set(["web", "db", "web", "cache"]);
console.log(roller.size, roller.has("db"));     // 3 true
roller.add("db");                                // zaten var: değişmez
roller.delete("cache");
console.log([...roller]);                        // eklenme sırasıyla
console.log([...new Set([3, 1, 3, 2, 1])]);      // tekrarları atmanın kısa yolu
```

**`Map`** anahtarı **her türden** olabilen bir sözlüktür ve eklenme sırasını korur:

```javascript
const sayac = new Map();
for (const yol of ["/api/bilet", "/api/rapor", "/api/bilet"]) {
  sayac.set(yol, (sayac.get(yol) ?? 0) + 1);
}
for (const [yol, adet] of sayac) console.log(yol, adet);
console.log(sayac.size, sayac.has("/api/rapor"), sayac.get("/yok"));
console.log(Object.fromEntries(sayac));          // düz nesneye çevirmek
```

| | Düz nesne `{}` | `Map` |
|---|---|---|
| anahtar türü | metin (ve Symbol); `1` ile `"1"` aynı anahtardır | her tür; `1` ile `"1"` ayrı anahtarlardır |
| eleman sayısı | `Object.keys(o).length` | `m.size` |
| sıra | çoğunlukla eklenme sırası, ama tam sayı gibi görünen anahtarlar öne ve sıralı geçer | her zaman eklenme sırası |
| JSON | `JSON.stringify` doğrudan yazar | `JSON.stringify(m)` **`{}`** verir: önce `Object.fromEntries(m)` |

`Set` ve `Map` değerleri **SameValueZero** kuralıyla karşılaştırır: `NaN` kendine eşit sayılır; nesneler ise içerikleriyle değil **kimlikleriyle** karşılaştırılır. `new Set([{a: 1}, {a: 1}])`'in iki elemanı vardır. `WeakMap` ve `WeakSet` yalnızca nesne anahtar alır ve o nesne başka yerde kullanılmayınca kendiliğinden silinir; bir nesneye geçici veri iliştirmek için kullanılır.

> [!TUZAK]
> `JSON.stringify(new Map(...))` ve `JSON.stringify(new Set(...))` hata vermez, sessizce `{}` yazar. Bir API yanıtına `Map` koyan kod boş bir nesne gönderir. Göndermeden önce `Object.fromEntries(map)` ve `[...set]` ile çevir.
:::

::: tahmin
Dört satır yazar:

```javascript
const s = new Set([3, 1, 3, "3", NaN, NaN]);
console.log(s.size, [...s].join(","));
const m = new Map([[1, "sayı"], ["1", "metin"]]);
console.log(m.size, m.get(1), m.get("1"));
const o = { 1: "sayı", "1": "metin" };
console.log(Object.keys(o).length, o[1]);
console.log(JSON.stringify(m), JSON.stringify(Object.fromEntries(m)));
```

???

`4 3,1,3,NaN`, `2 sayı metin`, `1 metin` ve `{} {"1":"metin"}`. `Set` sayı olan 3'ü ve metin olan `"3"`'ü ayrı tutar, iki `NaN`'ı tek sayar: 3, 1, `"3"`, `NaN`. `Map`'te `1` ile `"1"` iki ayrı anahtardır. Düz nesnede ikisi de `"1"` anahtarına dönüşür; sonraki değer öncekinin üstüne yazar. `JSON.stringify` bir `Map`'i `{}` yazar; `Object.fromEntries` ise anahtarları metne çevirdiği için yine tek bir `"1"` kalır.
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

::: gorev Yol başına tekil istemci
Girdi, isteklerin bir JSON dizisidir (`ip`, `yol`). Her yol için kaç **farklı** istemcinin (`ip`) istek gönderdiğini, yolların girdide **ilk göründüğü sırayla** `yol: sayı` biçiminde yazdır. En sonda bütün yollarda kaç farklı istemci olduğunu `tekil: sayı` diye yazdır. Bir `Map` (yol → `Set`) kullan.

```starter
const istekler = JSON.parse(require("fs").readFileSync(0, "utf8"));
console.log(`tekil: ${istekler.length}`);
```

```stdin
[{"ip":"10.0.0.5","yol":"/api/bilet"},{"ip":"10.0.0.9","yol":"/api/rapor"},{"ip":"10.0.0.5","yol":"/api/bilet"},{"ip":"10.0.0.50","yol":"/api/bilet"}]
```

```test
eq(run('[{"ip":"10.0.0.5","yol":"/api/bilet"},{"ip":"10.0.0.9","yol":"/api/rapor"},{"ip":"10.0.0.5","yol":"/api/bilet"},{"ip":"10.0.0.50","yol":"/api/bilet"}]'),
   "/api/bilet: 2\n/api/rapor: 1\ntekil: 3\n", "aynı istemci bir kez sayılır; 10.0.0.5 ile 10.0.0.50 ayrı")
eq(run('[{"ip":"1.1.1.1","yol":"/z"},{"ip":"1.1.1.1","yol":"/a"},{"ip":"2.2.2.2","yol":"/z"}]'),
   "/z: 2\n/a: 1\ntekil: 2\n", "ilk görünme sırası (alfabetik değil); aynı ip iki yolda tek istemci")
eq(run("[]"), "tekil: 0\n", "boş girdi")
ok("new Map" in src and "new Set" in src, "Map ve Set kullan")
```

```solution
const istekler = JSON.parse(require("fs").readFileSync(0, "utf8"));
const yollar = new Map();
const hepsi = new Set();
for (const { ip, yol } of istekler) {
  if (!yollar.has(yol)) yollar.set(yol, new Set());
  yollar.get(yol).add(ip);
  hepsi.add(ip);
}
for (const [yol, ipler] of yollar) {
  console.log(`${yol}: ${ipler.size}`);
}
console.log(`tekil: ${hepsi.size}`);
```

```hint
Her yol için bir `Set` tut: `if (!yollar.has(yol)) yollar.set(yol, new Set());` sonra `yollar.get(yol).add(ip)`. `Map` eklenme sırasını korur.
```

```hint
Bütün istemciler için ayrı bir `Set` yeter; sayısı `.size`'dır.
```
:::

::: gorev İki listenin farkı
Girdi, iki dizi taşıyan bir JSON nesnesidir: `{"dun": [...], "bugun": [...]}` (sunucu adları). Üç satır yazdır, her birinde adlar **virgülle** ve **ilk göründükleri sırayla**, tekrarsız:

- `yeni:` bugün olup dün olmayanlar
- `giden:` dün olup bugün olmayanlar
- `ortak:` ikisinde de olanlar (dünkü sırayla)

Liste boşsa satır `yeni: ` gibi iki noktadan sonra bir boşlukla biter.

```starter
const { dun, bugun } = JSON.parse(require("fs").readFileSync(0, "utf8"));
console.log(`yeni: ${bugun.join(",")}`);
```

```stdin
{"dun":["web01","db01","web02"],"bugun":["web01","cache01","web02","cache01"]}
```

```test
eq(run('{"dun":["web01","db01","web02"],"bugun":["web01","cache01","web02","cache01"]}'),
   "yeni: cache01\ngiden: db01\nortak: web01,web02\n", "tekrarlanan yeni sunucu bir kez")
eq(run('{"dun":["a","b","a"],"bugun":[]}'), "yeni: \ngiden: a,b\nortak: \n", "bugün boş; dünkü tekrar bir kez")
eq(run('{"dun":["x"],"bugun":["x","x"]}'), "yeni: \ngiden: \nortak: x\n", "aynı küme")
eq(run('{"dun":["web1"],"bugun":["web10","web1"]}'), "yeni: web10\ngiden: \nortak: web1\n", "web1 ile web10 ayrı adlar")
eq(run('{"dun":["db01","web01"],"bugun":["web01","db01"]}'), "yeni: \ngiden: \nortak: db01,web01\n", "ortaklar dünkü sırayla")
```

```solution
const { dun, bugun } = JSON.parse(require("fs").readFileSync(0, "utf8"));
const d = new Set(dun);
const b = new Set(bugun);
const yeni = [...b].filter((x) => !d.has(x));
const giden = [...d].filter((x) => !b.has(x));
const ortak = [...d].filter((x) => b.has(x));
console.log(`yeni: ${yeni.join(",")}`);
console.log(`giden: ${giden.join(",")}`);
console.log(`ortak: ${ortak.join(",")}`);
```

```hint
Önce her diziyi bir `Set`'e çevir: tekrarlar gider, sıra korunur. Sonra `[...b].filter((x) => !d.has(x))` gibi süz.
```
:::
