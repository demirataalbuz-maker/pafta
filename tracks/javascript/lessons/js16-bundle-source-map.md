---
id: js16
title: Bundle ve Source Map · Çalışan Kodu Kaynağa Eşlemek
summary: Paketlenmiş tek satırlık üretim kodunda yığın izindeki konumun işe yaramaması; sourceMappingURL yorumu ve .map dosyasının yapısı (sources, sourcesContent, mappings); base64 VLQ parçalarının [üretilen sütun, kaynak, özgün satır, özgün sütun] farklarını taşıması; Node'un --enable-source-maps bayrağıyla yığın izinin özgün dosyaya dönmesi ama fonksiyon adının küçültülmüş hâlde kalması; bir üretilen sütunun hangi parçaya düştüğünün "son küçük eşit" kuralıyla bulunması.
kazanim: JSA 4.2.1, JSA 3.9.1
---

::: anlat Üretimdeki kod ile yazdığın kod
`JS11`'de küçültülmüş kodu elle okudun. Gerçekte üretime giden dosya genellikle hem **küçültülmüş** hem **paketlenmiştir**: birçok kaynak dosya tek bir çıktıda birleşir, adlar kısalır, satır sonları silinir.

Böyle bir dosyada bir hata oluştuğunda yığın izi şuna benzer:

```text
Error: sifira bolme
    at a (bundle.js:1:32)
```

`1:32` doğrudur ama işe yaramaz: dosyanın tamamı tek satırdır. Hangi kaynak dosyanın kaçıncı satırını yazdığını bilmiyorsun.

Köprüyü **source map** kurar. Paketleyici çıktının sonuna bir yorum bırakır:

```javascript norun
//# sourceMappingURL=bundle.js.map
```

`.map` dosyası bir JSON'dur:

| Alan | İçerik |
|---|---|
| `version` | biçim sürümü (3) |
| `sources` | özgün dosya yolları |
| `sourcesContent` | özgün dosyaların **içeriği** (isteğe bağlı ama yaygın) |
| `names` | özgün tanıtıcı adları |
| `mappings` | konum eşlemesi, base64 VLQ ile kodlanmış |

`mappings` virgülle ayrılmış **parçalardan** oluşur; her parça 4 (ya da 5) sayı taşır ve bu sayılar **bir öncekine göre fark** olarak yazılır:

```text
[üretilen sütun, kaynak dizini, özgün satır, özgün sütun]
```

Satırlar ve sütunlar 0 tabanlıdır. Noktalı virgül üretilen dosyada yeni satıra geçildiğini gösterir; tek satırlık bir pakette hiç noktalı virgül olmaz.
:::

::: anlat Eşlemeyi çalıştırmak
Node bir bayrakla haritayı kendisi uygular. Bu derste ölçüldü (Node v24.20.0) — aynı paket, iki çalıştırma:

```text
$ node bundle.js
Error: sifira bolme
    at a (bundle.js:1:32)

$ node --enable-source-maps bundle.js
  if (b === 0) throw new Error('sifira bolme');
Error: sifira bolme
    at a (src/hesap.js:2:16)
```

İkinci çalıştırmada üç şey değişti: dosya adı özgün dosya oldu, satır/sütun özgün konuma döndü ve Node o satırın **metnini** bastı — metni `sourcesContent`'ten okudu, diskteki dosyaya bakmadı.

> [!TUZAK] Harita konumu çevirir, adı değil
> İkinci izde fonksiyon hâlâ **`a`** görünüyor; özgün adı `bol`du. Eşleme konum tabanlıdır; adların geri gelmesi için haritada `names` dizisinin ve parçaların beşinci alanının bulunması gerekir, paketleyici bunu her zaman üretmez. Bir yığın izinde "dosya ve satır tanıdık ama fonksiyon adı saçma" görüyorsan harita çalışıyor, yalnız ad bilgisi yok demektir.

Tarayıcıda aynı işi DevTools yapar: `.map` dosyasını indirip Sources panelinde özgün dosyaları gösterir, kesme noktalarını özgün satırlara koyarsın. İki ortamda da harita **ayrı bir dosyadır** ve çalışması için erişilebilir olması gerekir.

> [!DERİN] Haritayı yayına koymak kaynağı yayına koymaktır
> `sourcesContent` özgün dosyaların tamamını içerir. `.map` dosyasını herkese açık sunucuya koyarsan, küçültülmüş kodun arkasındaki okunabilir kaynağı da yayınlamış olursun — yorumlar ve geliştirme sırasında bırakılmış notlar dahil. Bu bir açık değil, bir karardır: ya haritayı yalnız hata izleme servisine yükle, ya da yayınladığını bilerek yayınla.
:::

::: tahmin Aynı hata, iki iz
`bundle.js` tek satırlık paket; yanında `bundle.js.map` var ve `src/hesap.js`'in 2. satırı `  if (b === 0) throw new Error('sifira bolme');`. Ne yazar?

```javascript
// $ node bundle.js
// $ node --enable-source-maps bundle.js
```

```gercek
$ node bundle.js
once: 5
Error: sifira bolme
    at a (bundle.js:1:32)

$ node --enable-source-maps bundle.js
once: 5
  if (b === 0) throw new Error('sifira bolme');
Error: sifira bolme
    at a (src/hesap.js:2:16)
```

???

Haritasız çalıştırmada konum `bundle.js:1:32`'dir: paket tek satır olduğu için satır numarası hep `1`, tek bilgi 32. sütundur. Hangi kaynak dosyanın neresi olduğunu söylemez.

Bayrakla çalıştırıldığında aynı hata `src/hesap.js:2:16` olur — özgün dosya, özgün satır ve sütun. Node ayrıca o satırın metnini yazar; bunu diskten değil haritanın `sourcesContent` alanından alır, yani kaynak dosyalar yanında olmasa da satır görünür.

Değişmeyen şey fonksiyon adıdır: iki izde de **`a`**. Özgün ad `bol`du ama harita yalnız konumları çeviriyor.
:::

::: gorev VLQ parçalarını çöz
`cozParcalar(mappings)` yaz: tek satırlık bir `mappings` dizgisini çözüp her parça için **mutlak** `[üretilenSutun, kaynakIndex, ozgunSatir, ozgunSutun]` dizilerinden oluşan bir liste döndür.

- Parçalar virgülle ayrılır; her parça base64 VLQ ile kodlanmış 4 sayı taşır.
- Sayılar bir öncekine göre **fark**tır; ilk parça 0'lardan başlar.
- Base64 alfabesi: `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/`.
- Bir VLQ sayısı 5 bitlik gruplardan oluşur; her grubun 6. biti (değer 32) "devam ediyor" demektir. En düşük bit **işarettir**: 1 ise sayı negatiftir.
- Boş dizgi boş liste verir.

```starter
const B = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';

function cozParcalar(mappings) {
  return mappings.split(',').map((p) => [B.indexOf(p[0]), 0, 0, 0]);
}

// --- DENEME: değiştirme ---
for (const satir of require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean)) {
  console.log(JSON.stringify(cozParcalar(satir === '-' ? '' : satir)));
}
```

```stdin
AAAA,gBACE,SAAa,gCACb,cCDF,6BACA
AAAA
-
```

```test
eq(out,
   '[[0,0,0,0],[16,0,1,2],[25,0,1,15],[57,0,2,2],[71,1,1,0],[100,1,2,0]]\n[[0,0,0,0]]\n[]\n',
   "gerçek bundle.js.map'in mappings dizgisi: altı parça, iki kaynak dosya")
eq(run(stdin='AAAA,CAAC\n'), '[[0,0,0,0],[1,0,0,1]]\n', "iki parça, birer birim ileri")
eq(run(stdin='AAAA,DAAD\n'), '[[0,0,0,0],[-1,0,0,-1]]\n', "negatif fark: en düşük bit işaret")
eq(run(stdin='gBAAA\n'), '[[16,0,0,0]]\n', "iki karakterlik VLQ: devam biti")
eq(run(stdin='-\n'), '[]\n', "boş mappings")
```

```solution
const B = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';

function cozParcalar(mappings) {
  if (!mappings) return [];
  const sonuc = [];
  const bugun = [0, 0, 0, 0];
  for (const parca of mappings.split(',')) {
    let i = 0;
    for (let alan = 0; alan < 4; alan++) {
      let deger = 0, kaydir = 0, sayi;
      do {
        sayi = B.indexOf(parca[i++]);
        deger += (sayi & 31) << kaydir;
        kaydir += 5;
      } while (sayi & 32);
      bugun[alan] += (deger & 1) ? -(deger >> 1) : (deger >> 1);
    }
    sonuc.push(bugun.slice());
  }
  return sonuc;
}

// --- DENEME: değiştirme ---
for (const satir of require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean)) {
  console.log(JSON.stringify(cozParcalar(satir === '-' ? '' : satir)));
}
```

```hint
İki döngü gerekir: dış döngü parçaları, iç döngü bir parçanın dört alanını okur. Her alan için 5 bitlik grupları `deger += (sayi & 31) << kaydir` ile biriktir, `sayi & 32` sıfır olana kadar sür.
```

```hint
İşaret en sonda çözülür: biriken `deger`'in en düşük biti 1 ise sonuç `-(deger >> 1)`, değilse `deger >> 1`. Farkları bir birikmiş diziye ekle ve her parçada o dizinin **kopyasını** (`slice()`) listeye koy; aynı diziyi koyarsan hepsi son değeri gösterir.
```
:::

::: gorev Üretilen konumdan kaynağa
`kaynagaEsle(parcalar, sutun)` yaz: `cozParcalar`'ın verdiği mutlak parça listesinde, üretilen dosyanın `sutun` sütununa karşılık gelen özgün konumu bul.

- Kural: üretilen sütunu `sutun`'dan **küçük ya da eşit** olan parçalardan **sonuncusu** geçerlidir.
- Dönüş `[kaynakIndex, ozgunSatir, ozgunSutun]`; hiçbir parça uymuyorsa (`sutun` ilk parçadan önce) `null`.

```starter
const PARCALAR = [[0,0,0,0],[16,0,1,2],[25,0,1,15],[57,0,2,2],[71,1,1,0],[100,1,2,0]];

function kaynagaEsle(parcalar, sutun) {
  const p = parcalar.find((x) => x[0] === sutun);
  return p ? [p[1], p[2], p[3]] : null;
}

// --- DENEME: değiştirme ---
for (const satir of require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean)) {
  console.log(JSON.stringify(kaynagaEsle(PARCALAR, Number(satir))));
}
```

```stdin
32
0
25
70
71
120
```

```test
eq(out, '[0,1,15]\n[0,0,0]\n[0,1,15]\n[0,2,2]\n[1,1,0]\n[1,2,0]\n',
   "kendi parçası olmayan sütun bir öncekine bağlanır: 32 -> throw satırı (gerçek yığın izindeki sütun), 70 -> return satırı")
eq(run(stdin='15\n16\n'), '[0,0,0]\n[0,1,2]\n', "sınır: 16 kendi parçasına, 15 bir öncekine")
eq(run(stdin='9999\n'), '[1,2,0]\n', "son parçadan sonrası son parçaya bağlanır")
```

```solution
const PARCALAR = [[0,0,0,0],[16,0,1,2],[25,0,1,15],[57,0,2,2],[71,1,1,0],[100,1,2,0]];

function kaynagaEsle(parcalar, sutun) {
  let bulunan = null;
  for (const p of parcalar) {
    if (p[0] <= sutun) bulunan = p;
    else break;
  }
  return bulunan ? [bulunan[1], bulunan[2], bulunan[3]] : null;
}

// --- DENEME: değiştirme ---
for (const satir of require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean)) {
  console.log(JSON.stringify(kaynagaEsle(PARCALAR, Number(satir))));
}
```

```hint
Başlangıç kodu **tam** eşleşme arıyor; oysa paketteki çoğu sütunun kendi parçası yoktur. Listeyi gez, üretilen sütunu `sutun`'u geçmeyen son parçayı tut.
```

```hint
Parçalar üretilen sütuna göre artan sıradadır, bu yüzden ilk büyük parçayı görünce durabilirsin. Dönüşte parçanın ilk alanını (üretilen sütun) **atla**; yalnız son üçünü döndür.
```
:::
