---
id: js15
title: postMessage ve Ham HTML Güven Sınırı
summary: Pencereler arası mesajlaşmada event.origin gönderenin kökenidir ve dinleyici denetlemezse her kökenden mesaj kabul edilir; targetOrigin uyuşmazsa mesaj sessizce teslim edilmez; veri yapılandırılmış kopyayla taşınır; event.source gönderen pencereyi tanır. Ham HTML tarafında innerHTML'in hangi yapıyı çalıştırdığı basit bir kurala uymaz: gerçek tarayıcıda ölçüldü — script etiketi DOM'a girer ama çalışmaz, img onerror ve iframe srcdoc çalışır, svg onload çalışmaz.
kazanim: JSA 4.6.1, JSA 1.4.1
---

::: anlat Mesaj geldi: kimden?
`JS09`'da DOM'u gördün. Bir sayfa başka bir pencereyle (iframe, açılan sekme, gömülü widget) konuşmak istediğinde `postMessage` kullanır. Bu, **güven sınırını geçen** bir kanaldır: iki taraf farklı kökenlerde olabilir ve birbirlerinin DOM'una erişemezler, yalnız mesaj yollayabilirler.

```javascript norun
hedefPencere.postMessage(veri, hedefOrigin);     // gönderen
addEventListener('message', (e) => { ... });      // alan
```

Alıcıdaki olayın üç alanı önemlidir:

| Alan | Ne söyler |
|---|---|
| `e.origin` | mesajı **gönderenin** kökeni; alıcının kendi kökeni değil |
| `e.source` | gönderen pencere nesnesi; `iframe.contentWindow` ile karşılaştırılabilir |
| `e.data` | veri; **yapılandırılmış kopya** (structured clone) ile taşınır, metne çevrilmez |

Bu dersin ölçümleri gerçek bir tarayıcıda yapıldı (Node bu davranışı gösteremez). Düzenek: ana sayfa `http://127.0.0.1:8731`, içindeki çerçeve `http://localhost:8731`. Dikkat: **aynı sunucu, aynı port, ama farklı köken** — `127.0.0.1` ile `localhost` köken karşılaştırmasında eşit sayılmaz.

Gönderirken verdiğin `hedefOrigin` bir **teslim koşuludur**: alıcı pencerenin kökeni ona uymazsa mesaj teslim edilmez ve sana hiçbir hata dönmez. `'*'` yazarsan koşul yok demektir, mesaj kimin eline geçerse geçsin gider.

> [!TUZAK] Dinleyici kökeni denetlemezse herkes konuşabilir
> `addEventListener('message', ...)` sayfadaki **bütün** mesajları alır: başka bir iframe'den, sayfayı açan pencereden ya da sayfanın gömüldüğü üst çerçeveden gelenleri de. Gönderen tarafta `hedefOrigin` vermek yalnız **senin gönderdiğin** mesajı korur; sana gelenleri korumaz. Alırken her zaman `e.origin`'i beklediğin kökenler listesiyle karşılaştır, gerekiyorsa `e.source`'u da tanıdığın pencereyle doğrula.
:::

::: anlat innerHTML neyi çalıştırır?
İkinci güven sınırı, gelen veriyi DOM'a **ham HTML** olarak yazmaktır: `element.innerHTML = veri` ya da React'te `dangerouslySetInnerHTML`. Yaygın bilgi şudur: "innerHTML script çalıştırmaz". Doğrudur ama eksiktir ve yanlış bir güven duygusu verir.

Aynı tarayıcıda, aynı düzenekte ölçüldü — her yapı `innerHTML` ile yazıldı ve çalışıp çalışmadığına bakıldı:

| Yazılan | DOM'a girdi mi | Çalıştı mı |
|---|---|---|
| `<script>...</script>` | evet | **hayır** |
| `<img src=yok.png onerror=...>` | evet | **evet** |
| `<iframe srcdoc="&lt;script&gt;...">` | evet | **evet** |
| `<svg onload=...>` | evet | hayır |
| `<a href="javascript:...">` | evet | hayır (tıklanana kadar) |
| `<b>kalın</b>` | evet | hayır |

Listeye bakınca basit bir kural çıkarmak isteyebilirsin — "olay işleyicileri çalışır" gibi. Ama `svg onload` bir olay işleyicisidir ve çalışmadı; `iframe srcdoc`'un içindeki script ise `<script>` etiketidir ve çalıştı. Hangi yapının ne zaman çalıştığı tarayıcıya, etiketin türüne ve olayın doğal olarak tetiklenip tetiklenmediğine bağlıdır.

> [!TUZAK] Bu tablo bir izin listesi değildir
> Buradan "`svg onload` güvenli" sonucunu çıkarma; ölçüm bu tarayıcının bu sürümündeki davranıştır ve kodu okurken hangi yapıların **çalışabildiğini** göstermek içindir. Doğru savunma, listeyi ezberlemek ya da kendi süzgecini yazmak değildir: güvenilmeyen metni ham HTML olarak hiç yazma. Metin göstereceksen `textContent` kullan — orada hiçbir şey ayrıştırılmaz. HTML göstermek zorundaysan bakımlı bir temizleyici kütüphanesi kullan ve kararı ona bırak.
:::

::: tahmin Üç mesaj, kaç teslim?
Ana sayfa `http://127.0.0.1:8731`, çerçeve `http://localhost:8731`. Çerçeve aldığı her mesajı, gördüğü `origin` ve veri türüyle birlikte geri bildiriyor. Ne yazar?

```javascript
const f = document.getElementById('c').contentWindow;
f.postMessage({ tur: 'nesne', sayi: 42 }, '*');
f.postMessage('duz-metin', 'http://127.0.0.1:9999');
f.postMessage({ tur: 'dogru-hedef' }, 'http://localhost:8731');
// 700 ms sonra gelen yanıtlar yazdırılır
```

```gercek
gelen yanit sayisi: 2
1 cerceve gordu: origin=http://127.0.0.1:8731 tip=object veri={"tur":"nesne","sayi":42}
2 cerceve gordu: origin=http://127.0.0.1:8731 tip=object veri={"tur":"dogru-hedef"}
yanit origin=http://localhost:8731 kaynak===cerceve: true
```

???

Üç mesaj gönderildi, **iki** tanesi teslim edildi.

Teslim edilmeyen ikincidir: `hedefOrigin` olarak `http://127.0.0.1:9999` verildi, çerçevenin kökeni ise `http://localhost:8731`. Koşul tutmadığı için tarayıcı mesajı sessizce düşürdü — ne bir istisna ne bir uyarı var. Bir mesajın "gitmemesi" çoğu hata ayıklama oturumunun burada tıkandığı yerdir.

Birinci (`'*'`) ve üçüncü (doğru köken) teslim edildi. Çerçevenin gördüğü `origin` ikisinde de **`http://127.0.0.1:8731`** — yani **gönderenin** kökeni. Veri `tip=object` olarak geldi: yapılandırılmış kopya nesneyi nesne olarak taşır, JSON metnine çevirmez.

Son satır ters yöndür: ana sayfanın aldığı yanıtta `origin` artık `http://localhost:8731`'dir (şimdi gönderen çerçevedir) ve `e.source` tam olarak o iframe'in `contentWindow`'una eşittir. Aynı sunucunun aynı portu olmasına rağmen iki köken farklıdır.
:::

::: gorev Mesajı kabul etmeli miyim?
`mesajKabul(olay, izinliKokenler, beklenenKaynak)` yaz: bir `message` olayını kabul edip etmeyeceğine karar ver. Kabul koşulları:

- `olay.origin` `izinliKokenler` listesinde **tam olarak** bulunmalı (parça eşleşmesi değil).
- `beklenenKaynak` `null` değilse `olay.source` ona **aynı nesne** olmalı.
- `olay.data` bir nesne olmalı (dizi ve `null` olmaz) ve içinde metin türünde bir `tur` alanı bulunmalı.

Hepsi sağlanıyorsa `true`, değilse `false` döndür.

En alttaki **DENEME** bölümünü değiştirme.

```stdin
http://a.test|{"tur":"merhaba"}|dogru
http://kotu.test|{"tur":"merhaba"}|dogru
http://a.test|{"tur":"merhaba"}|yanlis
http://a.test|"duz metin"|dogru
http://a.test|{"sayi":1}|dogru
http://a.test|[1,2]|dogru
```

```starter
function mesajKabul(olay, izinliKokenler, beklenenKaynak) {
  return izinliKokenler.some((k) => olay.origin.includes(k));
}

// --- DENEME: değiştirme ---
const pencere = { ad: 'cerceve' }, baskaPencere = { ad: 'baska' };
for (const satir of require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean)) {
  const [origin, veriJson, kaynakAdi] = satir.split('|');
  const veri = veriJson === 'DIZI-TUR' ? Object.assign([1, 2], { tur: 'x' }) : JSON.parse(veriJson);
  const olay = { origin, data: veri, source: kaynakAdi === 'dogru' ? pencere : baskaPencere };
  console.log(mesajKabul(olay, ['http://a.test', 'http://b.test'], pencere));
}
```

```test
eq(out, 'true\nfalse\nfalse\nfalse\nfalse\nfalse\n',
   "yalnız izinli köken + doğru kaynak + tur alanı olan nesne kabul edilir")
eq(run(stdin='http://b.test|{"tur":"x"}|dogru\n'), 'true\n', "listenin ikinci kökeni")
eq(run(stdin='http://a.test.kotu.test|{"tur":"x"}|dogru\n'), 'false\n',
   "köken parça olarak geçiyor diye kabul edilmemeli")
eq(run(stdin='http://a.tes|{"tur":"x"}|dogru\n'), 'false\n', "eksik harfli köken")
eq(run(stdin='http://a.test|{"tur":5}|dogru\n'), 'false\n', "tur alanı metin olmalı")
eq(run(stdin='http://a.test|null|dogru\n'), 'false\n', "null nesne sayılmaz")
eq(run(stdin='http://a.test|{"tur":"x","ek":1}|dogru\n'), 'true\n', "fazladan alan sorun değil")
eq(run(stdin='http://a.test|DIZI-TUR|dogru\n'), 'false\n',
   "tur alanı taşıyan bir dizi de reddedilmeli: yapılandırılmış kopya diziye özellik iliştirebilir")
```

```solution
function mesajKabul(olay, izinliKokenler, beklenenKaynak) {
  if (!izinliKokenler.includes(olay.origin)) return false;
  if (beklenenKaynak !== null && olay.source !== beklenenKaynak) return false;
  const v = olay.data;
  if (v === null || typeof v !== 'object' || Array.isArray(v)) return false;
  return typeof v.tur === 'string';
}

// --- DENEME: değiştirme ---
const pencere = { ad: 'cerceve' }, baskaPencere = { ad: 'baska' };
for (const satir of require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean)) {
  const [origin, veriJson, kaynakAdi] = satir.split('|');
  const veri = veriJson === 'DIZI-TUR' ? Object.assign([1, 2], { tur: 'x' }) : JSON.parse(veriJson);
  const olay = { origin, data: veri, source: kaynakAdi === 'dogru' ? pencere : baskaPencere };
  console.log(mesajKabul(olay, ['http://a.test', 'http://b.test'], pencere));
}
```

```hint
Başlangıç kodu `includes` ile **parça** arıyor; `http://a.test.kotu.test` içinde `http://a.test` geçtiği için onu da kabul eder. Dizinin `includes`'u ile metnin `includes`'unu karıştırma: `izinliKokenler.includes(olay.origin)` tam eşleşmedir.
```

```hint
`typeof null === 'object'` ve `typeof [] === 'object'`'tir; ikisini de ayrıca ele. Kaynak karşılaştırması `===` ile nesne kimliğine bakar, adına değil.
```
:::

::: gorev Gelen mesajları işle
`isle(olaylar, izinliKokenler, beklenenKaynak)` yaz: bir olay listesini sırayla değerlendirip `{ kabul, ret }` döndür.

- `kabul`: kabul edilen olayların `data.tur` değerleri, geldikleri sırayla.
- `ret`: reddedilenler için `"<origin>:<neden>"` dizgileri. `neden` ilk başarısız olan denetimdir ve şu sırayla bakılır: `"koken"`, `"kaynak"`, `"bicim"`.

Kurallar bir önceki görevdekiyle aynı.

```stdin
http://a.test|{"tur":"merhaba"}|dogru
http://kotu.test|{"tur":"x"}|dogru
http://a.test|{"tur":"x"}|yanlis
http://a.test|{"sayi":1}|dogru
http://b.test|{"tur":"son"}|dogru
```

```starter
function isle(olaylar, izinliKokenler, beklenenKaynak) {
  const kabul = [], ret = [];
  for (const o of olaylar) kabul.push(o.data.tur);
  return { kabul, ret };
}

// --- DENEME: değiştirme ---
const pencere = { ad: 'cerceve' }, baskaPencere = { ad: 'baska' };
const olaylar = require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean).map((s) => {
  const [origin, veriJson, kaynakAdi] = s.split('|');
  const veri = veriJson === 'DIZI-TUR' ? Object.assign([1, 2], { tur: 'x' }) : JSON.parse(veriJson);
  return { origin, data: veri, source: kaynakAdi === 'dogru' ? pencere : baskaPencere };
});
const s = isle(olaylar, ['http://a.test', 'http://b.test'], pencere);
console.log(JSON.stringify(s.kabul));
console.log(JSON.stringify(s.ret));
```

```test
eq(out, '["merhaba","son"]\n["http://kotu.test:koken","http://a.test:kaynak","http://a.test:bicim"]\n',
   "iki kabul; üç ret, her biri ilk başarısız denetimin adıyla")
eq(run(stdin='http://kotu.test|"x"|yanlis\n'), '[]\n["http://kotu.test:koken"]\n',
   "birden çok denetim başarısızsa ilki bildirilir: köken")
eq(run(stdin='http://a.test|"x"|yanlis\n'), '[]\n["http://a.test:kaynak"]\n',
   "köken geçerse sıradaki denetim kaynaktır")
eq(run(stdin='http://a.test|[1]|dogru\n'), '[]\n["http://a.test:bicim"]\n', "dizi biçim hatasıdır")
eq(run(stdin='http://a.test|DIZI-TUR|dogru\n'), '[]\n["http://a.test:bicim"]\n',
   "tur alanı olsa bile dizi biçim hatasıdır")
eq(run(stdin=''), '[]\n[]\n', "boş liste")
```

```solution
function isle(olaylar, izinliKokenler, beklenenKaynak) {
  const kabul = [], ret = [];
  for (const o of olaylar) {
    let neden = null;
    const v = o.data;
    if (!izinliKokenler.includes(o.origin)) neden = 'koken';
    else if (beklenenKaynak !== null && o.source !== beklenenKaynak) neden = 'kaynak';
    else if (v === null || typeof v !== 'object' || Array.isArray(v) || typeof v.tur !== 'string') neden = 'bicim';
    if (neden) ret.push(o.origin + ':' + neden);
    else kabul.push(v.tur);
  }
  return { kabul, ret };
}

// --- DENEME: değiştirme ---
const pencere = { ad: 'cerceve' }, baskaPencere = { ad: 'baska' };
const olaylar = require('fs').readFileSync(0, 'utf8').split('\n').filter(Boolean).map((s) => {
  const [origin, veriJson, kaynakAdi] = s.split('|');
  const veri = veriJson === 'DIZI-TUR' ? Object.assign([1, 2], { tur: 'x' }) : JSON.parse(veriJson);
  return { origin, data: veri, source: kaynakAdi === 'dogru' ? pencere : baskaPencere };
});
const s = isle(olaylar, ['http://a.test', 'http://b.test'], pencere);
console.log(JSON.stringify(s.kabul));
console.log(JSON.stringify(s.ret));
```

```hint
Denetimleri `else if` zinciriyle sırala; böylece ilk başarısız olan nedeni verir. Hepsini ayrı `if`'lerle yazarsan son başarısız denetim kazanır ve `"koken"` yerine `"bicim"` raporlarsın.
```
:::
