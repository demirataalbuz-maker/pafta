---
id: js09
title: Node.js Sunucu Kodunu Okumak
summary: require ve import, process.env ve process.argv, path ile dosya yolları, URL ve URLSearchParams, bir HTTP isteğinin yol haritası (yönlendirme, req.params, req.query, req.body) ve Express tarzı ara katman zinciri; kök dizinin dışına çıkan yolları reddetmek.
---

::: anlat Bir Node uygulamasının iskeleti
Web uygulamalarının sunucu tarafı büyük oranda Node.js ile yazılır. Bir dosyayı açtığında ilk satırlar neye bağlı olduğunu söyler:

```javascript
const path = require("path");               // CommonJS: Node'un geleneksel modül sistemi
// import path from "node:path";             // ES modülü: yeni kodlarda
// module.exports = { f };  /  export function f() {}   → dışarıya açılanlar

const port = process.env.PORT || 3000;     // ortam değişkeni; yoksa varsayılan
console.log(typeof port, process.argv.length >= 2);
```

| Yapı | Anlamı |
|---|---|
| `process.env.X` | ortam değişkeni (yapılandırma, gizli anahtarlar burada durur) |
| `process.argv` | komut satırı argümanları (`[node, betik, ...]`) |
| `__dirname` | betiğin bulunduğu klasör |
| `fs.readFileSync` / `fs.promises.readFile` | dosya okuma (eşzamanlı / Promise) |

### Yollar ve adresler
Dosya yollarını elle birleştirmek yerine `path`, adresleri ayrıştırmak için `URL` kullanılır:

```javascript
const path = require("path");
console.log(path.posix.join("/srv/site", "img", "../css/a.css"));     // .. çözülür
const u = new URL("https://pafta.local:8443/ara?q=regex&sayfa=2");
console.log(u.pathname, u.searchParams.get("q"), u.searchParams.get("yok"));
```

`path.join` platformun ayırıcısını kullanır (Windows'ta `\`); burada sonuç her yerde aynı olsun diye `path.posix` kullanıyoruz.
:::

::: anlat Bir isteğin yolculuğu
Express gibi çatılarda bir HTTP isteği sırayla **ara katmanlardan** (middleware) geçer. Her biri isteği inceler, değiştirir ve ya bir yanıt gönderip zinciri bitirir ya da `next()` ile sıradakine verir:

```javascript norun
app.use(gunlukle);                      // 1: her istek
app.use(express.json());                // 2: gövdeyi JSON olarak ayrıştır → req.body
app.use("/api", oturumDenetle);         // 3: yalnızca /api altı
app.get("/api/bilet/:id", (req, res) => {        // 4: yol eşleşirse
  res.json({ id: req.params.id, sekme: req.query.sekme });
});
```

| İstekteki | Nereden gelir | Örnek: `GET /api/bilet/42?sekme=gecmis` |
|---|---|---|
| `req.params` | yoldaki `:ad` parçaları | `{ id: "42" }` |
| `req.query` | `?` sonrası | `{ sekme: "gecmis" }` |
| `req.body` | istek gövdesi (POST, PUT) | JSON ayrıştırıcıdan |
| `req.headers` | başlıklar | `user-agent`, `authorization` |

Ara katmanların **sırası** davranışı belirler: oturum denetimi yönlendiriciden sonra eklenirse hiç çalışmaz. Kod okurken ilk iş, `app.use` satırlarını yukarıdan aşağı okuyup bir isteğin hangi denetimlerden geçtiğini çıkarmaktır.

> [!GÜVENLİK]
> `req.params`, `req.query`, `req.body` ve başlıklardaki her şey **istemciden** gelir; değerler her zaman metindir ve her şey olabilir. Bir dosya yolu bu değerlerden kuruluyorsa sonucun izin verilen kök klasörün içinde kaldığı mutlaka denetlenir: `path.resolve(kok, istenen)` ile mutlak yolu bul, `kok + "/"` ile başladığını doğrula. Veritabanı sorgularında parametreli sorgular, HTML çıktısında kaçırma (JS05) aynı ilkenin uygulamalarıdır.
:::

::: tahmin
Üç satır yazar:

```javascript
const path = require("path");
console.log(path.posix.join("/srv/site", "img", "../css/a.css"));
console.log(path.posix.basename("/srv/site/rapor.pdf"), path.posix.extname("arsiv.tar.gz"));
const u = new URL("https://pafta.local:8443/ara?q=regex&sayfa=2");
console.log(u.hostname, u.port, u.searchParams.get("q"), u.searchParams.get("yok"));
```

???

`/srv/site/css/a.css`, `rapor.pdf .gz`, `pafta.local 8443 regex null`. `join` parçaları birleştirip `..`'yu çözer: `img/..` birbirini götürür. `extname` yalnızca **son** uzantıyı verir. Olmayan bir sorgu parametresi `null` döner.
:::

::: gorev Ara katman zinciri
`calistir(katmanlar, istek)` fonksiyonunu yaz: katmanları sırayla çalıştırsın. Her katman `(istek, yanit, next)` alır; `next()` çağırırsa sıradaki katmana geçilir, çağırmazsa zincir orada biter. Başlangıç kodu bütün katmanları koşulsuz çalıştırıyor.

```starter
function calistir(katmanlar, istek) {
  const yanit = { durum: 200 };
  for (const k of katmanlar) k(istek, yanit, () => {});
  return yanit;
}

const gunlukle = (req, res, next) => { console.log("gunluk " + req.yol); next(); };
const oturum = (req, res, next) => {
  if (!req.kullanici) { res.durum = 401; console.log("reddedildi"); return; }
  next();
};
const islem = (req, res, next) => { console.log("işlendi " + req.kullanici); };

console.log(calistir([gunlukle, oturum, islem], { yol: "/api/bilet", kullanici: "ayse" }).durum);
console.log(calistir([gunlukle, oturum, islem], { yol: "/api/rapor" }).durum);
```

```test
eq(out, "gunluk /api/bilet\nişlendi ayse\n200\ngunluk /api/rapor\nreddedildi\n401\n", "ikinci istek oturum katmanında durur")
```

```solution
function calistir(katmanlar, istek) {
  const yanit = { durum: 200 };
  let sira = 0;
  const next = () => {
    const k = katmanlar[sira++];
    if (k) k(istek, yanit, next);
  };
  next();
  return yanit;
}

const gunlukle = (req, res, next) => { console.log("gunluk " + req.yol); next(); };
const oturum = (req, res, next) => {
  if (!req.kullanici) { res.durum = 401; console.log("reddedildi"); return; }
  next();
};
const islem = (req, res, next) => { console.log("işlendi " + req.kullanici); };

console.log(calistir([gunlukle, oturum, islem], { yol: "/api/bilet", kullanici: "ayse" }).durum);
console.log(calistir([gunlukle, oturum, islem], { yol: "/api/rapor" }).durum);
```

```hint
Döngü yerine bir `next` fonksiyonu kur: sıradaki katmanı alıp ona kendisini (`next`'i) versin. Katman `next()`'i çağırmazsa zincir kendiliğinden durur.
```
:::

::: gorev Kökün dışına çıkma
`guvenliYol(kok, istenen)` fonksiyonunu yaz: `istenen` (istemciden gelen göreli yol) `kok` klasörüne göre çözüldüğünde kökün **içinde** kalıyorsa mutlak yolu, kalmıyorsa `null` döndürsün. `path.posix` kullan. Bir metnin bir önekle başlayıp başlamadığını `metin.startsWith(onek)` söyler (`true` ya da `false`).

```starter
const path = require("path");

function guvenliYol(kok, istenen) {
  return path.posix.join(kok, istenen);
}

for (const y of ["css/a.css", "img/../rapor.pdf", "../etc/hosts", "a/../../gizli", "/etc/hosts", ""]) {
  console.log(JSON.stringify(guvenliYol("/srv/site", y)));
}
```

```test
eq(out, '"/srv/site/css/a.css"\n"/srv/site/rapor.pdf"\nnull\nnull\nnull\nnull\n', "yalnızca kökün içi")
```

```solution
const path = require("path");

function guvenliYol(kok, istenen) {
  const tam = path.posix.resolve(kok, istenen);
  return tam.startsWith(kok + "/") ? tam : null;
}

for (const y of ["css/a.css", "img/../rapor.pdf", "../etc/hosts", "a/../../gizli", "/etc/hosts", ""]) {
  console.log(JSON.stringify(guvenliYol("/srv/site", y)));
}
```

```hint
`path.posix.resolve(kok, istenen)` mutlak yolu verir; `istenen` `/` ile başlıyorsa kökü tamamen yok sayar, `..` parçalarını da çözer.
```

```hint
Sonucun `kok + "/"` ile başladığını denetle. Yalnızca `kok` ile başlamasına bakmak `/srv/site-yedek` gibi komşu klasörleri de kabul ederdi; boş yol ise kökün kendisini verir, bir dosya değildir.
```
:::
