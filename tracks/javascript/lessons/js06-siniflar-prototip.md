---
id: js06
title: Sınıflar ve Prototipler
summary: class, constructor, metot ve get; extends ve super; sınıfların altındaki prototip zinciri, instanceof, kendi özellikleri ile kalıtılanlar (Object.keys, for...in, Object.hasOwn) ve sözlük olarak Object.create(null) ya da Map.
---

::: anlat Sınıflar
`class` sözdizimi, Python sınıflarına çok benzer:

```javascript
class Sunucu {
  constructor(ad, cpu) {
    this.ad = ad;
    this.cpu = cpu;
  }
  get durum() { return this.cpu > 80 ? "yüksek" : "normal"; }   // alan gibi okunur: s.durum
  toString() { return `${this.ad}(${this.cpu})`; }
  static karsilastir(a, b) { return b.cpu - a.cpu; }          // sınıfın kendisinde: Sunucu.karsilastir
}

class Veritabani extends Sunucu {
  constructor(ad, cpu, motor) {
    super(ad, cpu);              // üst sınıfın constructor'ı: this'ten önce çağrılmalı
    this.motor = motor;
  }
  toString() { return super.toString() + "/" + this.motor; }
}

const d = new Veritabani("db01", 91, "pg");
console.log(String(d), d.durum, d instanceof Sunucu);
```

| Yazım | Anlamı |
|---|---|
| `constructor(...)` | `new` ile çağrılır; Python'daki `__init__` |
| `get ad()` | özellik gibi okunan metot |
| `static f()` | örneğe değil sınıfa ait |
| `extends`, `super` | kalıtım ve üst sınıfa erişim |
| `#gizli` | özel alan: sınıf dışından erişilemez |
:::

::: anlat Altında: prototip zinciri
`class` yeni bir mekanizma değildir; JavaScript'in **prototip** sisteminin daha okunaklı bir yazımıdır. Her nesnenin bir **prototipi** vardır; bir özellik nesnede bulunamazsa prototipte, orada da yoksa onun prototipinde aranır:

```text
d  →  Veritabani.prototype  →  Sunucu.prototype  →  Object.prototype  →  null
(ad, cpu, motor)  (toString)      (durum, toString)   (hasOwnProperty, ...)
```

Eski kodda aynı yapıyı `class` olmadan görürsün:

```javascript
function Eski(ad) { this.ad = ad; }
Eski.prototype.selam = function () { return "merhaba " + this.ad; };
console.log(new Eski("ayse").selam());
```

### Kendi özellikleri ve kalıtılanlar
| Yöntem | Neyi verir |
|---|---|
| `Object.keys(o)` | yalnızca **kendi**, sayılabilir özellikler |
| `for (const k in o)` | kendi **ve kalıtılan** sayılabilir özellikler |
| `Object.hasOwn(o, k)` | `k` nesnenin kendisinde mi? |
| `k in o` | kendisinde ya da prototip zincirinde mi? |

```javascript
const varsayilan = { tema: "koyu", dil: "tr" };
const ayar = Object.create(varsayilan);   // prototipi 'varsayilan' olan boş nesne
ayar.dil = "en";
console.log(Object.keys(ayar).join(","), ayar.tema, Object.hasOwn(ayar, "tema"));
```

> [!GÜVENLİK]
> Düz bir nesneyi kullanıcıdan gelen anahtarlarla doldurulan bir **sözlük** gibi kullanmak risklidir: `__proto__`, `constructor` gibi anahtarlar prototip zincirine dokunabilir. Bu yüzden özenli kod anahtarları dışarıdan gelen sözlükler için `Map` ya da prototipsiz `Object.create(null)` kullanır ve `obj[k]` yerine `Object.hasOwn` ile denetler.
:::

::: tahmin
Üç satır yazar:

```javascript
class Sunucu {
  constructor(ad, cpu) { this.ad = ad; this.cpu = cpu; }
  get durum() { return this.cpu > 80 ? "yüksek" : "normal"; }
  toString() { return `${this.ad}(${this.cpu})`; }
}
class Veritabani extends Sunucu {
  constructor(ad, cpu, motor) { super(ad, cpu); this.motor = motor; }
  toString() { return super.toString() + "/" + this.motor; }
}
const d = new Veritabani("db01", 91, "pg");
console.log(String(d), d.durum, d instanceof Sunucu);
console.log(Object.keys(d).join(","));
console.log(Object.getPrototypeOf(Object.getPrototypeOf(d)) === Sunucu.prototype);
```

???

`db01(91)/pg yüksek true`, `ad,cpu,motor`, `true`. `toString` alt sınıfta yeniden yazılmış ve `super.toString()` ile üst sınıfınkini kullanıyor. `durum` bir `get`; 91 > 80. `Object.keys` yalnızca nesnenin kendi alanlarını verir; metotlar prototiptedir. `d`'nin prototipi `Veritabani.prototype`, onunki `Sunucu.prototype`'tır.
:::

::: gorev Bilet ve acil bilet
`Bilet` sınıfını yaz: `constructor(id, oncelik)`, ve `#id [oncelik]` biçiminde metin döndüren `etiket()` metodu. Ondan türeyen `AcilBilet` sınıfını yaz: `etiket()`'in başına `ACİL ` eklesin (üst sınıfın metodunu `super` ile kullanarak). Alttaki satırlar olduğu gibi kalsın.

```starter
class Bilet {}
class AcilBilet {}

console.log(new Bilet(12, "orta").etiket());
console.log(new AcilBilet(7, "kritik").etiket());
console.log(new AcilBilet(7, "kritik") instanceof Bilet);
```

```test
eq(out, "#12 [orta]\nACİL #7 [kritik]\ntrue\n", "üç satır")
ok("super" in src, "üst sınıfın etiketini super ile kullan")
```

```solution
class Bilet {
  constructor(id, oncelik) { this.id = id; this.oncelik = oncelik; }
  etiket() { return `#${this.id} [${this.oncelik}]`; }
}
class AcilBilet extends Bilet {
  etiket() { return "ACİL " + super.etiket(); }
}

console.log(new Bilet(12, "orta").etiket());
console.log(new AcilBilet(7, "kritik").etiket());
console.log(new AcilBilet(7, "kritik") instanceof Bilet);
```

```hint
`class AcilBilet extends Bilet` yeterli; constructor yazmazsan üst sınıfınki kullanılır.
```

```hint
`etiket() { return "ACİL " + super.etiket(); }`
```
:::

::: gorev Yalnızca kendi ayarları
`ayar` nesnesinin prototipi `varsayilan`'dır. Kullanıcının **kendi değiştirdiği** ayarları `anahtar=değer` biçiminde, her biri ayrı satırda yazdır. Başlangıç kodu kalıtılan varsayılanları da yazıyor.

```starter
const varsayilan = { tema: "koyu", dil: "tr", boyut: 14 };
const ayar = Object.create(varsayilan);
ayar.dil = "en";
ayar.boyut = 16;
for (const k in ayar) {
  console.log(`${k}=${ayar[k]}`);
}
```

```test
eq(out, "dil=en\nboyut=16\n", "yalnızca kendi özellikleri")
```

```solution
const varsayilan = { tema: "koyu", dil: "tr", boyut: 14 };
const ayar = Object.create(varsayilan);
ayar.dil = "en";
ayar.boyut = 16;
for (const k of Object.keys(ayar)) {
  console.log(`${k}=${ayar[k]}`);
}
```

```hint
`for...in` prototip zincirindeki sayılabilir özellikleri de gezer. `Object.keys(ayar)` yalnızca kendi özelliklerini verir; ya da döngüde `Object.hasOwn(ayar, k)` ile süz.
```
:::
