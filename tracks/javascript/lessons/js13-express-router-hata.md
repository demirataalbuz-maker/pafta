---
id: js13
title: Express 5 · Router, Ara Katman Sırası ve Hata Akışı
summary: JS10'daki oyuncak zincirin gerçeği: sürümü kilitli Express 5.3.0 ile app.use ve Router, ara katmanların kayıt sırası, next(), next(err) ve next('route'), dört argümanlı hata işleyicisi, async işleyicide reddedilen Promise'in (Express 5) hata işleyicisine gitmesi, express.json'un 400/413 hataları, 404'ün aslında "hiçbir katman yanıt vermedi" olması ve yanıt gönderildikten sonraki hata. Gerçek yerel HTTP istekleriyle.
---

::: anlat Zincirin gerçeği
JS10'da ara katman zincirini kendin kurdun. Node'da web uygulamalarının çoğu bu fikrin olgun hâli olan **Express**'i kullanır. Bu derste projeye sabitlenmiş **Express 5.3.0** çalışır (`.deps\npm`); her örnek gerçek bir HTTP sunucusu açar (`127.0.0.1`, boş bir port), ona `fetch` ile istek gönderir ve kapanır.

```javascript
const express = require('express');
console.log(require('express/package.json').version);
```

Bir Express uygulaması, **kayıt sırasıyla** denenen katmanlar listesidir:

| Yazım | Ne kaydeder |
|---|---|
| `app.use(fn)` | her istekte çalışan ara katman |
| `app.use('/api', router)` | `/api` ile başlayan istekleri bir alt uygulamaya (Router) yollar |
| `router.get('/bilet/:id', fn)` | yöntemi ve yolu tutan işleyici; `req.params.id` |
| `app.use((err, req, res, next) => …)` | **dört** argümanlı: hata işleyicisi |

Her katman ya yanıtı bitirir (`res.send`, `res.json`, `res.status(…).end()`), ya `next()` ile sıradakine geçer, ya da `next(err)` ile **hata yoluna** sapar. Hata yolunda yalnız dört argümanlı katmanlar çalışır, normal katmanlar atlanır. Sıra her şeydir: bir ara katman, kendisinden **önce** kaydedilmiş bir işleyicinin isteklerini hiç görmez.

| Çağrı | Etkisi |
|---|---|
| `next()` | sıradaki uygun katman |
| `next(err)` | sıradaki **hata işleyicisi** |
| `next('route')` | aynı yolun sıradaki işleyicisi (bu işleyicinin kalanı atlanır) |
| `next('router')` | bu Router'dan çık, üst uygulamada devam et |

```javascript
const express = require('express');
const app = express();
app.use((req, res, next) => { console.log('1. kayıt', req.path); next(); });
app.get('/a', (req, res, next) => { console.log('2. işleyici'); next(); });
app.get('/a', (req, res) => { console.log('3. ikinci işleyici'); res.send('tamam'); });
app.use((req, res, next) => { console.log('hiç çalışmaz: /a yanıtlandı'); next(); });
const sunucu = app.listen(0, '127.0.0.1', async () => {
  const r = await fetch('http://127.0.0.1:' + sunucu.address().port + '/a');
  console.log(r.status, await r.text());
  sunucu.close();
});
```

Kaynak: [Express ara katmanları](https://expressjs.com/en/guide/using-middleware.html), [Router](https://expressjs.com/en/5x/api.html#router).
:::

::: anlat Hata akışı ve Express 5
Express 4'te async bir işleyicide fırlatılan hata (reddedilen Promise) hiçbir yere gitmez, istek yanıtsız asılı kalırdı; herkes `try/catch` ile `next(err)` yazardı. **Express 5**'te işleyicinin döndürdüğü Promise reddedilirse Express onu kendisi `next(err)`'e çevirir. Aşağıdaki tablonun her satırı gerçek isteklerle ölçülmüştür:

| İşleyicide | Hata işleyicisine gider mi |
|---|---|
| `throw new Error(…)` (eşzamanlı) | evet |
| `async` işleyicide `await` sonrası `throw` | **evet (Express 5)** |
| `next(new Error(…))` | evet |
| `setTimeout(() => { throw … })` | hayır: Promise zincirinin dışında; süreç çöker |

Hazır ara katmanlar da hata üretir. `express.json()` bozuk bir JSON gövdesinde `status: 400`, `type: 'entity.parse.failed'` taşıyan bir hatayla `next(err)` çağırır; 100 kB'yi aşan gövdede `413` ve `entity.too.large`. Bu hataların `expose: true` alanı, iletinin istemciye gösterilebileceğini söyler. Senin fırlattığın sıradan bir `Error`'ın iletisi ise ("veritabanı bağlantısı koptu") istemciye **gösterilmemelidir**.

**404 bir hata değildir:** hiçbir katman yanıt vermediğinde Express'in en sondaki kendi işleyicisi `404` ve bir HTML sayfası döndürür. JSON bir API istiyorsan bütün yolların **arkasına** kendi 404 katmanını, onun da arkasına hata işleyicini koyarsın.

Yanıt gönderildikten sonra `next(err)` çağrılırsa artık durum kodu değiştirilemez. Hata işleyicisi `res.headersSent` doğruysa işi Express'in varsayılan işleyicisine (`next(err)`) bırakmalıdır; o da bağlantıyı kapatır ve hatayı günlüğe yazar.

```javascript
const express = require('express');
const app = express();
app.use(express.json());
app.get('/esz', (req, res) => { throw new Error('eşzamanlı'); });
app.get('/async', async (req, res) => { await null; throw new Error('async'); });
app.post('/json', (req, res) => res.json({ aldim: req.body }));
app.use((err, req, res, next) => res.status(err.status || 500).json({ hata: err.type || err.message }));
const sunucu = app.listen(0, '127.0.0.1', async () => {
  const k = 'http://127.0.0.1:' + sunucu.address().port;
  for (const [y, opt] of [['/esz'], ['/async'], ['/yok'],
      ['/json', { method: 'POST', headers: { 'content-type': 'application/json' }, body: '{"a":' }]]) {
    const r = await fetch(k + y, opt);
    console.log(y, r.status, (await r.text()).slice(0, 40).replace(/\n/g, ' '));
  }
  sunucu.close();
});
```

> [!GÜVENLİK]
> Hata işleyicisi bir uygulamanın en çok bilgi sızdıran yeridir: yığın izi, SQL hatası, dosya yolu. Kural: istemciye yalnız `expose` edilebilir hataların iletisini ve genel bir "iç hata" ver; ayrıntıyı sunucu günlüğüne yaz. Kimlik doğrulama gibi bir ara katmanı da **korunacak yolların önüne** kaydet; arkasına kaydedilen bir denetim, önündeki yolları korumaz.
:::

::: tahmin Sıra ve atlanan işleyici
```javascript
const express = require('express');
const app = express();
const r = express.Router();
r.get('/:id', (req, res, next) => {
  if (req.params.id === 'atla') return next('route');
  res.send('ilk ' + req.params.id);
});
r.get('/:id', (req, res) => res.send('ikinci ' + req.params.id));
app.use('/b', r);
app.use((req, res) => res.status(404).send('yok'));
const sunucu = app.listen(0, '127.0.0.1', async () => {
  const k = 'http://127.0.0.1:' + sunucu.address().port;
  for (const y of ['/b/5', '/b/atla', '/c/5']) {
    const y2 = await fetch(k + y);
    console.log(y2.status, await y2.text());
  }
  sunucu.close();
});
```

???

```text
200 ilk 5
200 ikinci atla
404 yok
```

`/b/5` ilk işleyicide yanıtlanır. `/b/atla`'da `next('route')` bu işleyicinin kalanını atlar ve aynı yolun ikinci işleyicisine geçer. `/c/5` hiçbir yola uymaz; Router'a hiç girmez, sondaki katman `404 yok` döner.
:::

::: gorev JSON hata işleyicisi
Başlangıç kodundaki API'nin rotaları hazır; eksik olan hata akışı. Uygulamaya **yolların arkasına** iki katman ekle:

- Hiçbir yol eşleşmezse: `404` ve `{"hata":"bulunamadı"}`.
- Hata işleyicisi:
  - `express.json`'un bozuk JSON hatası (`type` `entity.parse.failed`): `400` ve `{"hata":"geçersiz JSON"}`;
  - istemciye gösterilebilir başka bir hata (`expose` doğru, `status` 400–499): o durum kodu ve `{"hata": <hatanın iletisi>}`;
  - geri kalan her hata: `500` ve `{"hata":"iç hata"}`. Hatanın kendi iletisi istemciye **gitmemeli**;
  - yanıt zaten gönderilmişse (`res.headersSent`), işi `next(err)` ile Express'e bırak.

En alttaki **DENEME** bölümünü değiştirme: girdinin her satırını bir isteğe çevirir (`YÖNTEM yol [başlık=değer ...] [| JSON gövde]`) ve `durum gövde` yazar.

```stdin
GET /api/saglik
GET /api/bilet/7
GET /api/bilet/0
GET /api/yok
```

```starter
const express = require('express');
const app = express();
app.use(express.json());

app.get('/api/saglik', (req, res) => res.json({ durum: 'iyi' }));
app.get('/api/bilet/:id', async (req, res) => {
  await null;
  if (req.params.id === '0') throw new Error('veritabanı bağlantısı koptu');
  res.json({ id: req.params.id });
});
app.post('/api/bilet', (req, res) => res.status(201).json({ alindi: req.body.baslik }));
app.get('/api/akis', (req, res, next) => { res.json({ akis: 'başladı' }); next(new Error('akış yarıda kesildi')); });

// --- hata katmanlarını buraya ekle ---

// --- DENEME: değiştirme ---
const satirlar = require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean);
const sunucu = app.listen(0, '127.0.0.1', async () => {
  const kok = 'http://127.0.0.1:' + sunucu.address().port;
  for (const s of satirlar) {
    const [bas, govde] = s.split(' | ');
    const [yontem, yol, ...basliklar] = bas.split(' ');
    const headers = Object.fromEntries(basliklar.map((b) => b.split('=')));
    if (govde !== undefined) headers['content-type'] = 'application/json';
    try {
      const r = await fetch(kok + yol, { method: yontem, headers, body: govde });
      console.log(r.status, await r.text());
    } catch (e) {
      console.log('bağlantı', e.cause ? e.cause.code : e.message);
    }
  }
  sunucu.close();
});
```

```test
eq(out, '200 {"durum":"iyi"}\n200 {"id":"7"}\n500 {"hata":"iç hata"}\n404 {"hata":"bulunamadı"}\n',
   "sağlık, bilet, async hata (ileti sızmaz) ve JSON 404")
eq(run(stdin='POST /api/bilet | {"baslik":"yazıcı"}\nPOST /api/bilet | {"baslik":\n'),
   '201 {"alindi":"yazıcı"}\n400 {"hata":"geçersiz JSON"}\n', "geçerli gövde ve bozuk JSON")
buyuk = '{"baslik":"' + "x" * 110000 + '"}'
eq(run(stdin="POST /api/bilet | " + buyuk + "\n"), '413 {"hata":"request entity too large"}\n',
   "gösterilebilir 4xx hata: kendi durum kodu ve iletisi")
eq(run(stdin="DELETE /api/saglik\nGET /\n"), '404 {"hata":"bulunamadı"}\n404 {"hata":"bulunamadı"}\n',
   "yanlış yöntem ve kök de JSON 404")
r = calis(stdin="GET /api/akis\nGET /api/saglik\n")
eq(r["cikti"], '200 {"akis":"başladı"}\n200 {"durum":"iyi"}\n', "yanıt gönderildikten sonraki hata durum kodunu bozmaz, sunucu çalışmaya devam eder")
ok("veritabanı bağlantısı koptu" not in out, "iç hatanın iletisi istemciye gitmez")

# Aynı hata işleyicisine gerçek Express route'undan kontrollü hata gönder.
probe="""app.get('/__audit/:status/:expose', (req,res,next) => {
  const err=new Error('gizli-ileti');
  err.status=Number(req.params.status);err.expose=req.params.expose==='true';
  next(err);
});
"""
code=src.replace('app.use(express.json());','app.use(express.json());\n'+probe,1)
requests=''.join('GET /__audit/%s/%s\n'%(status,expose) for status,expose in [(399,'true'),(400,'true'),(499,'true'),(500,'true'),(400,'false'),(499,'false'),(500,'false')])
eq(run_code(code,stdin=requests),'500 {"hata":"iç hata"}\n400 {"hata":"gizli-ileti"}\n499 {"hata":"gizli-ileti"}\n500 {"hata":"iç hata"}\n500 {"hata":"iç hata"}\n500 {"hata":"iç hata"}\n500 {"hata":"iç hata"}\n','expose ile kapalı 400/açık 500 sınırı birlikte; gizli ileti sızmaz')

```

```solution
const express = require('express');
const app = express();
app.use(express.json());

app.get('/api/saglik', (req, res) => res.json({ durum: 'iyi' }));
app.get('/api/bilet/:id', async (req, res) => {
  await null;
  if (req.params.id === '0') throw new Error('veritabanı bağlantısı koptu');
  res.json({ id: req.params.id });
});
app.post('/api/bilet', (req, res) => res.status(201).json({ alindi: req.body.baslik }));
app.get('/api/akis', (req, res, next) => { res.json({ akis: 'başladı' }); next(new Error('akış yarıda kesildi')); });

app.use((req, res) => res.status(404).json({ hata: 'bulunamadı' }));
app.use((err, req, res, next) => {
  if (res.headersSent) return next(err);
  if (err.type === 'entity.parse.failed') return res.status(400).json({ hata: 'geçersiz JSON' });
  if (err.expose && err.status >= 400 && err.status < 500) return res.status(err.status).json({ hata: err.message });
  res.status(500).json({ hata: 'iç hata' });
});

// --- DENEME: değiştirme ---
const satirlar = require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean);
const sunucu = app.listen(0, '127.0.0.1', async () => {
  const kok = 'http://127.0.0.1:' + sunucu.address().port;
  for (const s of satirlar) {
    const [bas, govde] = s.split(' | ');
    const [yontem, yol, ...basliklar] = bas.split(' ');
    const headers = Object.fromEntries(basliklar.map((b) => b.split('=')));
    if (govde !== undefined) headers['content-type'] = 'application/json';
    try {
      const r = await fetch(kok + yol, { method: yontem, headers, body: govde });
      console.log(r.status, await r.text());
    } catch (e) {
      console.log('bağlantı', e.cause ? e.cause.code : e.message);
    }
  }
  sunucu.close();
});
```

```hint
İki katman da bütün `app.get`/`app.post` kayıtlarının **arkasına**: önce iki argümanlı 404 katmanı, sonra dört argümanlı hata işleyicisi. Hata işleyicisinin imzası `(err, req, res, next)` olmalı; argüman sayısı eksikse Express onu hata işleyicisi saymaz.
```

```hint
Sıra: `res.headersSent` ise `next(err)`; `err.type === 'entity.parse.failed'` ise 400; `err.expose` ve 4xx ise `err.message`; değilse 500 ve genel ileti.
```
:::

::: gorev Korunan Router ve kayıt sırası
`/yonetim` altındaki her şey bir anahtar ister; `/saglik` herkese açıktır. Bir `Router` kur ve `/yonetim`'e bağla:

- Router'a giren **her** istek önce anahtarı denetlesin: `x-anahtar` başlığı yoksa `401` ve `{"hata":"anahtar gerekli"}`, varsa ama `gizli-42` değilse `403` ve `{"hata":"yetkisiz"}`.
- `GET /yonetim/rapor`: `{"rapor":"hazır"}`; sorgu dizgisinde `bozuk=1` varsa async işleyici bir hata fırlatır.
- `/yonetim` altında olmayan bir yol anahtarla bile `404` olur; ama anahtarsız gelen bir istek, yol var olsun olmasın, **önce** `401` almalı (yolun varlığı anahtarsız kişiye sızmamalı).
- `GET /saglik`: anahtarsız `{"durum":"iyi"}`.
- Hata işleyicisi: `500` ve `{"hata":"iç hata"}`. 404 katmanı: `{"hata":"bulunamadı"}`.

```stdin
GET /saglik
GET /yonetim/rapor
GET /yonetim/rapor x-anahtar=yanlis
GET /yonetim/rapor x-anahtar=gizli-42
```

```starter
const express = require('express');
const app = express();

app.get('/saglik', (req, res) => res.json({ durum: 'iyi' }));
app.get('/yonetim/rapor', async (req, res) => {
  await null;
  if (req.query.bozuk === '1') throw new Error('rapor üretilemedi');
  res.json({ rapor: 'hazır' });
});
app.use((req, res, next) => {
  if (req.path.startsWith('/yonetim') && req.get('x-anahtar') !== 'gizli-42') return res.status(401).json({ hata: 'anahtar gerekli' });
  next();
});
app.use((req, res) => res.status(404).json({ hata: 'bulunamadı' }));
app.use((err, req, res, next) => res.status(500).json({ hata: 'iç hata' }));

// --- DENEME: değiştirme ---
const satirlar = require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean);
const sunucu = app.listen(0, '127.0.0.1', async () => {
  const kok = 'http://127.0.0.1:' + sunucu.address().port;
  for (const s of satirlar) {
    const [bas, govde] = s.split(' | ');
    const [yontem, yol, ...basliklar] = bas.split(' ');
    const headers = Object.fromEntries(basliklar.map((b) => b.split('=')));
    if (govde !== undefined) headers['content-type'] = 'application/json';
    try {
      const r = await fetch(kok + yol, { method: yontem, headers, body: govde });
      console.log(r.status, await r.text());
    } catch (e) {
      console.log('bağlantı', e.cause ? e.cause.code : e.message);
    }
  }
  sunucu.close();
});
```

```test
eq(out, '200 {"durum":"iyi"}\n401 {"hata":"anahtar gerekli"}\n403 {"hata":"yetkisiz"}\n200 {"rapor":"hazır"}\n',
   "açık yol, anahtarsız, yanlış anahtar, doğru anahtar")
eq(run(stdin="GET /yonetim/yok\nGET /yonetim/yok x-anahtar=gizli-42\nGET /yonetim x-anahtar=yanlis\n"),
   '401 {"hata":"anahtar gerekli"}\n404 {"hata":"bulunamadı"}\n403 {"hata":"yetkisiz"}\n',
   "anahtarsız istek yolun varlığını öğrenemez; anahtarla olmayan yol 404")
eq(run(stdin="GET /yonetim/rapor?bozuk=1 x-anahtar=gizli-42\nGET /yonetim/rapor?bozuk=1\n"),
   '500 {"hata":"iç hata"}\n401 {"hata":"anahtar gerekli"}\n', "async hata 500; anahtarsız istek işleyiciye hiç ulaşmaz")
eq(run(stdin="GET /yonetimx/rapor\nGET /saglik x-anahtar=yanlis\n"), '404 {"hata":"bulunamadı"}\n200 {"durum":"iyi"}\n',
   "/yonetimx, /yonetim değildir; açık yol yanlış anahtardan etkilenmez")
eq(run(stdin="GET /yonetim/rapor x-anahtar=GIZLI-42\nPOST /yonetim/rapor x-anahtar=gizli-42\n"),
   '403 {"hata":"yetkisiz"}\n404 {"hata":"bulunamadı"}\n', "anahtar harfe duyarlı; yanlış yöntem anahtarla 404")
ok("Router" in src, "express.Router kullan")
```

```solution
const express = require('express');
const app = express();

app.get('/saglik', (req, res) => res.json({ durum: 'iyi' }));

const yonetim = express.Router();
yonetim.use((req, res, next) => {
  const anahtar = req.get('x-anahtar');
  if (anahtar === undefined) return res.status(401).json({ hata: 'anahtar gerekli' });
  if (anahtar !== 'gizli-42') return res.status(403).json({ hata: 'yetkisiz' });
  next();
});
yonetim.get('/rapor', async (req, res) => {
  await null;
  if (req.query.bozuk === '1') throw new Error('rapor üretilemedi');
  res.json({ rapor: 'hazır' });
});
app.use('/yonetim', yonetim);

app.use((req, res) => res.status(404).json({ hata: 'bulunamadı' }));
app.use((err, req, res, next) => res.status(500).json({ hata: 'iç hata' }));

// --- DENEME: değiştirme ---
const satirlar = require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean);
const sunucu = app.listen(0, '127.0.0.1', async () => {
  const kok = 'http://127.0.0.1:' + sunucu.address().port;
  for (const s of satirlar) {
    const [bas, govde] = s.split(' | ');
    const [yontem, yol, ...basliklar] = bas.split(' ');
    const headers = Object.fromEntries(basliklar.map((b) => b.split('=')));
    if (govde !== undefined) headers['content-type'] = 'application/json';
    try {
      const r = await fetch(kok + yol, { method: yontem, headers, body: govde });
      console.log(r.status, await r.text());
    } catch (e) {
      console.log('bağlantı', e.cause ? e.cause.code : e.message);
    }
  }
  sunucu.close();
});
```

```hint
Başlangıç kodunda denetim katmanı `/yonetim/rapor` işleyicisinin **arkasında**: o yolu hiç korumuyor. Denetimi bir Router'ın ilk katmanı yap ve rotaları o Router'a ekle: `yonetim.use(denetim)`, `yonetim.get('/rapor', …)`, `app.use('/yonetim', yonetim)`.
```

```hint
Router'a bağlanan her istek, yolu Router'da olsun olmasın, önce Router'ın ilk katmanından geçer; 404'e düşmeden önce 401/403 verilir. `app.use('/yonetim', …)` `/yonetimx`'i eşlemez.
```
:::
