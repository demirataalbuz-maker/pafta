---
id: js14
title: Prototype Pollution · Kaynaktan Kalıtılan Özelliğe, Oradan Karara
summary: JSON.parse'ın "__proto__" anahtarını kendi özelliği olarak üretmesi ve naif bir derin birleştirmenin bunu Object.prototype'a taşıması; kirlenmiş özelliğin her nesnede görünmesi ama Object.keys ve JSON.stringify çıktısında hiç yer almaması; kararın own yerine kalıtılan değeri okuması; savunmalar: tehlikeli anahtarları atlamak, null prototipli hedef, Object.freeze(Object.prototype) ve kararı Object.hasOwn ile vermek.
kazanim: JSA 1.11.1, JSA 1.4.1
---

::: anlat Kaynak: dışarıdan gelen bir anahtar
`JS06`'da prototip zincirini gördün: bir nesnede bulunmayan özellik `Object.prototype`'a kadar aranır. Bu zincirin yazılabilir olması, dışarıdan gelen veriyle buluşunca bir güvenlik sorununa dönüşür.

İlk tuğla, çoğu kişinin beklemediği bir ayrıntıdır: **`JSON.parse` `"__proto__"` anahtarını sıradan, kendine ait bir özellik olarak üretir.**

```javascript norun
const nesne = { __proto__: { a: 1 } };              // literal: prototipi DEĞİŞTİRİR
const cozulen = JSON.parse('{"__proto__":{"a":1}}'); // parse: KENDİ özelliği olur
Object.hasOwn(cozulen, '__proto__');                 // true
```

Tek başına zararsızdır: `cozulen`'in prototipi değişmemiştir, yalnız tuhaf adlı bir alanı vardır. Zarar, bu nesneyi **anahtar adlarını gezerek kopyalayan** bir kod işlediğinde doğar:

```javascript norun
function birlestir(hedef, kaynak) {
  for (const k of Object.keys(kaynak)) {
    if (kaynak[k] && typeof kaynak[k] === 'object') {
      if (!hedef[k]) hedef[k] = {};
      birlestir(hedef[k], kaynak[k]);     // k === '__proto__' olduğunda...
    } else hedef[k] = kaynak[k];          // ...burada Object.prototype'a yazılır
  }
  return hedef;
}
```

`hedef['__proto__']` okunduğunda `Object.prototype` gelir; özyineleme bir sonraki turda oraya yazar. Böylece dışarıdan gelen bir JSON gövdesi, uygulamadaki **bütün** sıradan nesnelerin gördüğü bir değer bırakır. Bu derste ölçüldü (Node v24.20.0): naif birleştirmeden sonra yepyeni bir `{}` nesnesinde `yonetici` `true` görünür.
:::

::: anlat Karar ve görünmezlik
Kirlilik tehlikelidir çünkü **karar veren kod** çoğu zaman "own mu, kalıtılan mı" diye sormaz:

```javascript norun
if (istek.yonetici) { /* yönetici işlemi */ }     // kalıtılan değeri de okur
if (ayarlar.hataAyikla) { /* ayrıntılı hata */ }
```

İsteğin içinde böyle bir alan hiç olmasa bile koşul geçer. Ölçülen tanıklar:

| Soru | Yanıt |
|---|---|
| `istek.yonetici` | `true` |
| `Object.hasOwn(istek, 'yonetici')` | `false` |
| `'yonetici' in istek` | `true` |
| `Object.keys(istek)` | `[ 'kullanici' ]` |
| `JSON.stringify(istek)` | `{"kullanici":"ayse"}` |

Son iki satır bu konunun en can sıkıcı yanıdır: kirlenmiş özellik **sayılabilir anahtarlar arasında görünmez**. İsteği günlüğe yazdığında, hata ayıklarken ekrana bastığında ya da olduğu gibi serileştirdiğinde ortada hiçbir anormallik yoktur — ama `if` başka karar verir.

Savunmalar (hepsi ölçüldü):

| Önlem | Etkisi |
|---|---|
| Birleştirmede `__proto__`, `constructor`, `prototype` anahtarlarını atlamak | kirlilik oluşmaz |
| Hedefi `Object.create(null)` yapmak | `__proto__` **kendi** özelliği olur, prototipe yazılmaz |
| `Object.freeze(Object.prototype)` | yazma sessizce başarısız olur (katı kipte hata verir) |
| Kararı `Object.hasOwn(nesne, alan)` ile vermek | kalıtılan değer karara giremez |

> [!TUZAK] Kirlilik sürece aittir, isteğe değil
> Bir istek `Object.prototype`'ı kirlettiğinde etki o isteğin yanıtıyla bitmez: aynı Node sürecindeki **sonraki bütün istekler** kirli değeri görür. Ölçüldü: aynı kodu yeni bir süreçte çalıştırınca `({}).yonetici` yine `undefined`'dır — yani sorunu yeniden üretmeye çalışırken süreç yeniden başlatıldıysa iz kaybolur. Hata ayıklarken "bende olmuyor" demeden önce aynı süreçte mi çalıştığını kontrol et.
:::

::: tahmin Görünmeyen alan
```javascript
function birlestir(hedef, kaynak) {
  for (const k of Object.keys(kaynak)) {
    if (kaynak[k] && typeof kaynak[k] === 'object') {
      if (!hedef[k]) hedef[k] = {};
      birlestir(hedef[k], kaynak[k]);
    } else hedef[k] = kaynak[k];
  }
  return hedef;
}
const disaridan = JSON.parse('{"__proto__":{"yonetici":true}}');
console.log(Object.hasOwn(disaridan, '__proto__'));
birlestir({}, disaridan);
const istek = { kullanici: 'ayse' };
console.log(istek.yonetici, Object.hasOwn(istek, 'yonetici'));
console.log(Object.keys(istek), JSON.stringify(istek));
```

???

```text
true
true false
[ 'kullanici' ] {"kullanici":"ayse"}
```

Birinci satır kaynağı gösterir: `JSON.parse` `"__proto__"`'yu **kendi** özelliği yaptı (`true`), prototipi henüz değiştirmedi.

İkinci satır birleştirmenin sonucudur. `istek` nesnesi `birlestir` çağrısına hiç karışmadı, içinde yalnız `kullanici` var — ama `istek.yonetici` `true`. Değer `Object.prototype`'tan geliyor, bu yüzden `Object.hasOwn` `false` diyor. Bir `if (istek.yonetici)` koşulu burada geçerdi.

Üçüncü satır görünmezliği kanıtlar: `Object.keys` yalnız `kullanici`'yı sayar ve `JSON.stringify` yalnız onu yazar. Nesneyi günlüğe bassan kirliliği göremezsin.
:::

::: gorev Kirletmeyen birleştirme
`guvenliBirlestir(hedef, kaynak)` yaz: `kaynak`'ı `hedef`'e derinlemesine kopyalasın ama `Object.prototype`'ı **hiçbir girdide** kirletmesin. Tehlikeli anahtarlar (`__proto__`, `constructor`, `prototype`) atlanır; kalan alanlar, iç içe nesneler dahil, kopyalanır. `hedef`'i döndür.

En alttaki **DENEME** bölümünü değiştirme: girdinin her satırını JSON olarak çözer, taze bir hedefe birleştirir ve `<birleşmiş JSON> <temiz|kirli>` yazar.

```stdin
{"ad":"web01","ayar":{"port":8080}}
{"__proto__":{"yonetici":true}}
{"ad":"web02"}
```

```starter
function guvenliBirlestir(hedef, kaynak) {
  for (const k of Object.keys(kaynak)) {
    if (kaynak[k] && typeof kaynak[k] === 'object') {
      if (!hedef[k]) hedef[k] = {};
      guvenliBirlestir(hedef[k], kaynak[k]);
    } else hedef[k] = kaynak[k];
  }
  return hedef;
}

// --- DENEME: değiştirme ---
for (const satir of require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean)) {
  const hedef = guvenliBirlestir({}, JSON.parse(satir));
  console.log(JSON.stringify(hedef), ({}).yonetici === undefined ? 'temiz' : 'kirli');
}
```

```test
eq(out, '{"ad":"web01","ayar":{"port":8080}} temiz\n{} temiz\n{"ad":"web02"} temiz\n',
   "iç içe alanlar kopyalanır, __proto__ atlanır, prototip kirlenmez")
eq(run(stdin='{"a":{"b":{"c":1}}}\n'), '{"a":{"b":{"c":1}}} temiz\n', "üç kat derinlik")
eq(run(stdin='{"__proto__":{"x":1}}\n{"constructor":{"y":2}}\n{"prototype":{"z":3}}\n'),
   '{} temiz\n{} temiz\n{} temiz\n', "üç tehlikeli anahtar da atlanır")
eq(run(stdin='{"ayar":{"__proto__":{"derin":true}}}\n'), '{"ayar":{}} temiz\n',
   "iç içe gelen __proto__ da atlanır")
eq(run(stdin='{"sayi":0,"metin":"","yok":null,"dogru":false}\n'),
   '{"sayi":0,"metin":"","yok":null,"dogru":false} temiz\n', "yanlış-değerli alanlar kopyalanır")
eq(run(stdin='{}\n'), '{} temiz\n', "boş nesne")
```

```solution
function guvenliBirlestir(hedef, kaynak) {
  for (const k of Object.keys(kaynak)) {
    if (k === '__proto__' || k === 'constructor' || k === 'prototype') continue;
    if (kaynak[k] && typeof kaynak[k] === 'object') {
      if (!hedef[k]) hedef[k] = {};
      guvenliBirlestir(hedef[k], kaynak[k]);
    } else hedef[k] = kaynak[k];
  }
  return hedef;
}

// --- DENEME: değiştirme ---
for (const satir of require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean)) {
  const hedef = guvenliBirlestir({}, JSON.parse(satir));
  console.log(JSON.stringify(hedef), ({}).yonetici === undefined ? 'temiz' : 'kirli');
}
```

```hint
Döngünün en başına bir süzgeç koy: anahtar üç tehlikeli addan biriyse `continue`. Süzgeci özyinelemeli çağrının **içinde de** çalıştığından emin ol — iç içe bir nesnede gelen `__proto__` da atlanmalı.
```

```hint
`null` bir nesne gibi görünür (`typeof null === 'object'`), bu yüzden `kaynak[k] &&` denetimi gerekir; yoksa `null` değerli alan için boş nesne üretirsin. Başlangıç kodu bunu zaten doğru yapıyor, eksik olan yalnız anahtar süzgeci.
```
:::

::: gorev Kararı own özellikten ver
`yetkiVar(istek, alan)` yaz: `istek` nesnesinde `alan` adlı özellik **kendine ait** ve değeri doğru sayılan bir şeyse `true`, değilse `false` döndür. Prototipten gelen bir değer kararı değiştirmemeli.

En alttaki **DENEME** bölümünü değiştirme: `Object.prototype`'ı bilerek kirletir, sonra her girdi satırını `alan|JSON` diye okuyup kararı yazar.

```stdin
yonetici|{"kullanici":"ayse"}
yonetici|{"kullanici":"ayse","yonetici":true}
yonetici|{"kullanici":"ayse","yonetici":false}
rol|{"rol":"editor"}
```

```starter
function yetkiVar(istek, alan) {
  return Boolean(istek[alan]);
}

// --- DENEME: değiştirme ---
Object.prototype.yonetici = true;
for (const satir of require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean)) {
  const [alan, govde] = satir.split('|');
  console.log(alan, yetkiVar(JSON.parse(govde), alan));
}
```

```test
eq(out, 'yonetici false\nyonetici true\nyonetici false\nrol true\n',
   "kirlenmiş prototipten gelen true karara girmez; kendi alanı olan true girer")
eq(run(stdin='yok|{"a":1}\n'), 'yok false\n', "hiç bulunmayan alan")
eq(run(stdin='a|{"a":0}\na|{"a":""}\na|{"a":null}\n'), 'a false\na false\na false\n',
   "kendi alanı var ama değeri yanlış sayılıyor")
eq(run(stdin='a|{"a":"evet"}\na|{"a":1}\n'), 'a true\na true\n', "doğru sayılan değerler")
eq(run(stdin='toString|{"x":1}\n'), 'toString false\n',
   "prototipten gelen hazır metotlar da karara girmemeli")
eq(run(stdin='yonetici|{"yonetici":"hayir"}\n'), 'yonetici true\n',
   "boş olmayan metin doğru sayılır: karar değere değil, önce sahipliğe bakar")
```

```solution
function yetkiVar(istek, alan) {
  return Object.hasOwn(istek, alan) && Boolean(istek[alan]);
}

// --- DENEME: değiştirme ---
Object.prototype.yonetici = true;
for (const satir of require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean)) {
  const [alan, govde] = satir.split('|');
  console.log(alan, yetkiVar(JSON.parse(govde), alan));
}
```

```hint
İki koşul gerekir ve sırası önemlidir: önce özellik **kendine ait mi** (`Object.hasOwn`), sonra değeri doğru sayılıyor mu. `'alan' in istek` yazarsan prototipten geleni de kabul edersin.
```
:::
