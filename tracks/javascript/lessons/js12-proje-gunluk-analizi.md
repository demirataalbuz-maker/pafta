---
id: js12
title: Proje · Günlük Analizi Betiği
summary: Bir web uygulamasının istek günlüğünü okuyan küçük bir Node.js aracı; satırları regex ile ayrıştırıp bozukları saymak, durum sınıfları ve uç nokta kalıplarına göre özet, ve hata oranı, en yavaş istek ve istemci listesini içeren bir JSON raporu.
---

::: anlat Proje tanımı
Ekip, bir sunucunun istek günlüğünden hızlıca rapor çıkaran küçük bir Node.js aracı istiyor. Günlüğün her satırı şu biçimde:

```text
2026-10-19T09:01:12Z 10.0.3.4 GET /api/rapor 500 2300
zaman                istemci  yöntem yol     durum süre(ms)
```

Arada sunucunun yeniden başlatıldığını gösteren bozuk satırlar da var. Araç üç adımda kurulacak; her adım bir öncekinin üzerine çıkar:

| Adım | Ne yapar | Araçlar |
|---|---|---|
| 1 | satırları nesnelere çevirir, bozukları sayar | `split`, regex, `Number` |
| 2 | durum sınıflarına ve uç nokta kalıplarına göre sayar | nesne sayaçları, `replace`, `sort` |
| 3 | tek satırlık bir JSON raporu üretir | `filter`, `reduce`, `Set`, `toFixed` |

Bu projede JS dersleri boyunca okuduğun her şeyi **yazarak** kullanacaksın. Gerçek bir araç bu kodu bir dosyadan (`fs.readFileSync(process.argv[2], "utf8")`) okurdu; tezgahta aynı metni bir sabitte tutuyoruz.

> [!İPUCU]
> Sayaç nesnesinin deyimi: `sayac[anahtar] = (sayac[anahtar] || 0) + 1`. Anahtar sırası ekleme sırasıdır; çıktının her çalıştırmada aynı olması için yazdırmadan önce anahtarları sırala (`Object.keys(s).sort()`).
:::

::: tahmin
Tek satır yazar:

```javascript
const satir = "2026-10-19T09:01:12Z 10.0.3.4 GET /api/rapor 500 2300";
const [zaman, ip, yontem, yol, durum, sure] = satir.split(" ");
console.log(yol, Number(durum) >= 500, Number(sure) / 1000);
```

???

`/api/rapor true 2.3`. `split(" ")` altı parçayı verir ve ayrıştırma (destructuring) onları sırayla adlara bağlar. Durum 500 olduğu için koşul doğrudur; 2300 ms 2,3 saniyedir.
:::

::: gorev 1 · Ayrıştır
`ayristir(metin)` fonksiyonunu yaz: `{kayitlar, bozuk}` döndürsün. Her geçerli satır `{zaman, ip, yontem, yol, durum, sure}` nesnesi olsun (`durum` ve `sure` **sayı**); kalıba uymayan satırlar `bozuk` sayacını artırsın. Alttaki iki satır olduğu gibi kalsın.

`satir.match(/desen/)` eşleşme yoksa `null`, varsa bir dizi döndürür: `m[0]` eşleşen bütün metin, `m[1]`, `m[2]`... parantezli grupların yakaladıkları (Python'daki `re.match(...).group(n)` gibi).

```starter
const GUNLUK = `2026-10-19T09:01:12Z 10.0.3.4 GET /api/rapor 500 2300
2026-10-19T09:02:40Z 10.0.3.4 GET /api/rapor 500 2410
2026-10-19T09:04:05Z 10.0.1.15 GET /api/bilet 200 140
2026-10-19T09:10:33Z 203.0.113.7 GET /giris 200 60
-- yeniden başlatma --
2026-10-19T09:12:01Z 10.0.2.8 GET /api/rapor 503 30
2026-10-19T09:15:20Z 10.0.1.22 GET /api/bilet/42 200 110
2026-10-19T10:03:10Z 10.0.1.15 DELETE /api/bilet/17 404 25`;

function ayristir(metin) {
  const kayitlar = metin.split("\n").map(s => s.split(" "));
  return { kayitlar, bozuk: 0 };
}

const { kayitlar, bozuk } = ayristir(GUNLUK);
console.log(`ayrıştırılan=${kayitlar.length} bozuk=${bozuk}`);
console.log(JSON.stringify(kayitlar[0]));
```

```test
eq(out, 'ayrıştırılan=7 bozuk=1\n{"zaman":"2026-10-19T09:01:12Z","ip":"10.0.3.4","yontem":"GET","yol":"/api/rapor","durum":500,"sure":2300}\n', "yedi kayıt, bir bozuk satır")
```

```solution
const GUNLUK = `2026-10-19T09:01:12Z 10.0.3.4 GET /api/rapor 500 2300
2026-10-19T09:02:40Z 10.0.3.4 GET /api/rapor 500 2410
2026-10-19T09:04:05Z 10.0.1.15 GET /api/bilet 200 140
2026-10-19T09:10:33Z 203.0.113.7 GET /giris 200 60
-- yeniden başlatma --
2026-10-19T09:12:01Z 10.0.2.8 GET /api/rapor 503 30
2026-10-19T09:15:20Z 10.0.1.22 GET /api/bilet/42 200 110
2026-10-19T10:03:10Z 10.0.1.15 DELETE /api/bilet/17 404 25`;

const DESEN = /^(\S+) (\S+) ([A-Z]+) (\S+) (\d{3}) (\d+)$/;

function ayristir(metin) {
  const kayitlar = [];
  let bozuk = 0;
  for (const satir of metin.split("\n")) {
    const m = satir.match(DESEN);
    if (!m) { bozuk++; continue; }
    kayitlar.push({ zaman: m[1], ip: m[2], yontem: m[3], yol: m[4], durum: Number(m[5]), sure: Number(m[6]) });
  }
  return { kayitlar, bozuk };
}

const { kayitlar, bozuk } = ayristir(GUNLUK);
console.log(`ayrıştırılan=${kayitlar.length} bozuk=${bozuk}`);
console.log(JSON.stringify(kayitlar[0]));
```

```hint
Her satırı bir regex'le dene: `/^(\S+) (\S+) ([A-Z]+) (\S+) (\d{3}) (\d+)$/`. Eşleşmezse `bozuk++`.
```

```hint
Nesnede alan sırası JSON çıktısındaki sıradır: `zaman, ip, yontem, yol, durum, sure`; sayılar için `Number(...)`.
```
:::

::: gorev 2 · Özetle
Ayrıştırılan kayıtlardan iki özet çıkar ve yazdır:

1. Durum sınıflarına (`2xx`, `4xx`, `5xx`) göre sayım: anahtarları **sıralı** bir nesne olarak `JSON.stringify` ile.
2. Sondaki sayısal kimliği `{id}` ile değiştirilmiş yol kalıplarından en çok istek alanı ve sayısı (`/api/rapor 3`); eşitlikte alfabetik olarak önce gelen.

```starter
const GUNLUK = `2026-10-19T09:01:12Z 10.0.3.4 GET /api/rapor 500 2300
2026-10-19T09:02:40Z 10.0.3.4 GET /api/rapor 500 2410
2026-10-19T09:04:05Z 10.0.1.15 GET /api/bilet 200 140
2026-10-19T09:10:33Z 203.0.113.7 GET /giris 200 60
-- yeniden başlatma --
2026-10-19T09:12:01Z 10.0.2.8 GET /api/rapor 503 30
2026-10-19T09:15:20Z 10.0.1.22 GET /api/bilet/42 200 110
2026-10-19T10:03:10Z 10.0.1.15 DELETE /api/bilet/17 404 25`;

const DESEN = /^(\S+) (\S+) ([A-Z]+) (\S+) (\d{3}) (\d+)$/;
const kayitlar = GUNLUK.split("\n").map(s => s.match(DESEN)).filter(Boolean)
  .map(m => ({ zaman: m[1], ip: m[2], yontem: m[3], yol: m[4], durum: Number(m[5]), sure: Number(m[6]) }));

console.log(kayitlar.length);
```

```test
eq(out, '{"2xx":3,"4xx":1,"5xx":3}\n/api/rapor 3\n', "sınıflar ve en yoğun kalıp")
```

```solution
const GUNLUK = `2026-10-19T09:01:12Z 10.0.3.4 GET /api/rapor 500 2300
2026-10-19T09:02:40Z 10.0.3.4 GET /api/rapor 500 2410
2026-10-19T09:04:05Z 10.0.1.15 GET /api/bilet 200 140
2026-10-19T09:10:33Z 203.0.113.7 GET /giris 200 60
-- yeniden başlatma --
2026-10-19T09:12:01Z 10.0.2.8 GET /api/rapor 503 30
2026-10-19T09:15:20Z 10.0.1.22 GET /api/bilet/42 200 110
2026-10-19T10:03:10Z 10.0.1.15 DELETE /api/bilet/17 404 25`;

const DESEN = /^(\S+) (\S+) ([A-Z]+) (\S+) (\d{3}) (\d+)$/;
const kayitlar = GUNLUK.split("\n").map(s => s.match(DESEN)).filter(Boolean)
  .map(m => ({ zaman: m[1], ip: m[2], yontem: m[3], yol: m[4], durum: Number(m[5]), sure: Number(m[6]) }));

const siniflar = {};
for (const k of kayitlar) {
  const s = Math.floor(k.durum / 100) + "xx";
  siniflar[s] = (siniflar[s] || 0) + 1;
}
const sirali = {};
for (const s of Object.keys(siniflar).sort()) sirali[s] = siniflar[s];
console.log(JSON.stringify(sirali));

const yollar = {};
for (const k of kayitlar) {
  const y = k.yol.replace(/\/\d+$/, "/{id}");
  yollar[y] = (yollar[y] || 0) + 1;
}
const [enYol, enSayi] = Object.entries(yollar).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0];
console.log(enYol, enSayi);
```

```hint
Sınıf: `Math.floor(k.durum / 100) + "xx"`. Sıralı nesne için anahtarları `Object.keys(s).sort()` ile gezip yeni bir nesneye koy.
```

```hint
Kalıp: `k.yol.replace(/\/\d+$/, "/{id}")`. En yoğun: `Object.entries(yollar).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0]`.
```
:::

::: gorev 3 · JSON raporu
Aşağıdaki alanları içeren raporu tek satırlık JSON olarak yazdır:

- `toplam`: geçerli kayıt sayısı
- `hataOrani`: 500 ve üstü durumların yüzdesi, bir ondalık (sayı)
- `enYavas`: en uzun süren isteğin `{yol, sure}`'si
- `istemciler`: farklı istemci adresleri, sıralı

```starter
const GUNLUK = `2026-10-19T09:01:12Z 10.0.3.4 GET /api/rapor 500 2300
2026-10-19T09:02:40Z 10.0.3.4 GET /api/rapor 500 2410
2026-10-19T09:04:05Z 10.0.1.15 GET /api/bilet 200 140
2026-10-19T09:10:33Z 203.0.113.7 GET /giris 200 60
-- yeniden başlatma --
2026-10-19T09:12:01Z 10.0.2.8 GET /api/rapor 503 30
2026-10-19T09:15:20Z 10.0.1.22 GET /api/bilet/42 200 110
2026-10-19T10:03:10Z 10.0.1.15 DELETE /api/bilet/17 404 25`;

const DESEN = /^(\S+) (\S+) ([A-Z]+) (\S+) (\d{3}) (\d+)$/;
const kayitlar = GUNLUK.split("\n").map(s => s.match(DESEN)).filter(Boolean)
  .map(m => ({ zaman: m[1], ip: m[2], yontem: m[3], yol: m[4], durum: Number(m[5]), sure: Number(m[6]) }));

const rapor = { toplam: kayitlar.length };
console.log(JSON.stringify(rapor));
```

```test
eq(out, '{"toplam":7,"hataOrani":42.9,"enYavas":{"yol":"/api/rapor","sure":2410},"istemciler":["10.0.1.15","10.0.1.22","10.0.2.8","10.0.3.4","203.0.113.7"]}\n', "rapor")
```

```solution
const GUNLUK = `2026-10-19T09:01:12Z 10.0.3.4 GET /api/rapor 500 2300
2026-10-19T09:02:40Z 10.0.3.4 GET /api/rapor 500 2410
2026-10-19T09:04:05Z 10.0.1.15 GET /api/bilet 200 140
2026-10-19T09:10:33Z 203.0.113.7 GET /giris 200 60
-- yeniden başlatma --
2026-10-19T09:12:01Z 10.0.2.8 GET /api/rapor 503 30
2026-10-19T09:15:20Z 10.0.1.22 GET /api/bilet/42 200 110
2026-10-19T10:03:10Z 10.0.1.15 DELETE /api/bilet/17 404 25`;

const DESEN = /^(\S+) (\S+) ([A-Z]+) (\S+) (\d{3}) (\d+)$/;
const kayitlar = GUNLUK.split("\n").map(s => s.match(DESEN)).filter(Boolean)
  .map(m => ({ zaman: m[1], ip: m[2], yontem: m[3], yol: m[4], durum: Number(m[5]), sure: Number(m[6]) }));

const hatali = kayitlar.filter(k => k.durum >= 500).length;
const enYavas = kayitlar.reduce((en, k) => (k.sure > en.sure ? k : en));
const rapor = {
  toplam: kayitlar.length,
  hataOrani: Number((100 * hatali / kayitlar.length).toFixed(1)),
  enYavas: { yol: enYavas.yol, sure: enYavas.sure },
  istemciler: [...new Set(kayitlar.map(k => k.ip))].sort(),
};
console.log(JSON.stringify(rapor));
```

```hint
Hata oranı: `Number((100 * hatali / toplam).toFixed(1))`. `toFixed` metin döndürür; JSON'da sayı olması için `Number(...)`.
```

```hint
En yavaş: `reduce((en, k) => (k.sure > en.sure ? k : en))`. Farklı istemciler: `[...new Set(kayitlar.map(k => k.ip))].sort()`.
```
:::
