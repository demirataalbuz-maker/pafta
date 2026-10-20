---
id: sp13
title: transaction
summary: Birbiriyle ilgili olayları tek bir işlemde toplamak; ortak alan, maxpause ve maxspan, startswith ve endswith, duration ve eventcount, yarım kalan işlemleri bulmak ve transaction yerine daha hızlı stats kalıbı.
---

::: anlat Olaylardan işlemlere
Bir gece yedeği tek bir olay değildir: "başladı", "ilerleme %50", "bitti" diye üç ayrı satır bırakır. `isler` kaynağına bak:

```spl
sourcetype=isler
| head 7
| table zaman sunucu is_adi calisma mesaj
```

"Yedek ne kadar sürdü?" sorusunu cevaplamak için bu satırları **tek bir işlemde** toplamak gerekir. `transaction` aynı alan değerine sahip olayları zaman sırasıyla birleştirir:

```spl
sourcetype=isler
| transaction calisma
| table _time calisma duration eventcount mesaj
```

Her işlem için Splunk iki alan üretir:

| Alan | Anlamı |
|---|---|
| `duration` | ilk ve son olay arasındaki süre (saniye) |
| `eventcount` | işlemdeki olay sayısı |

Öteki alanlar **çok değerli** olur: `mesaj` alanında işlemin bütün mesajları birlikte durur (SP12). Sonuçlar en yeni işlemden eskiye sıralanır.

### İşlemi ne başlatır, ne bitirir?
| Seçenek | Anlamı |
|---|---|
| `maxpause=10m` | iki olay arası 10 dakikayı aşarsa yeni işlem |
| `maxspan=1h` | işlem bir saatten uzun süremez |
| `startswith="başladı"` | işlem bu olayla başlar |
| `endswith="bitti"` | işlem bu olayla biter |

Ortak bir kimlik alanı yoksa, zaman yakınlığı işlemleri ayırır. Aynı sunucunun önbellek ısıtma işleri 06:00 ve 06:30'da başlamış:

```spl
sourcetype=isler is_adi=onbellek-isit
| transaction sunucu maxpause=10m
| table _time sunucu duration eventcount
```

> [!TUZAK]
> `startswith` ve `endswith` verildiğinde, başlangıcı ya da bitişi olmayan işlemler **sessizce atılır**: 19 Ekim'in hâlâ süren yedeği (Y19) sonuçta görünmez. "Biten işlerin süresi" için doğru davranış budur; "yarım kalan iş var mı?" sorusu için ise bu seçenekleri kullanmadan işlemleri kur ve bitişi olmayanları ara.
:::

::: anlat transaction yerine stats
`transaction` güçlüdür ama **pahalıdır**: bütün olayları belleğe alıp gruplamak zorundadır, büyük veride yavaşlar ve sınırlara takılır. Ortak bir kimlik alanı (burada `calisma`) varsa aynı sonucun büyük kısmı `stats` ile çok daha ucuza alınır:

```spl
sourcetype=isler
| stats min(_time) as bas, max(_time) as bit, count as olay, values(mesaj) as mesajlar by calisma is_adi
| eval dk=(bit-bas)/60
| table calisma is_adi dk olay mesajlar
```

| İhtiyaç | Seç |
|---|---|
| ortak kimlik var, süre ve sayım yeterli | `stats` |
| kimlik yok, işlemi zaman boşluğu ayırıyor (`maxpause`) | `transaction` |
| başlangıç ve bitiş olayına göre kesmek gerekiyor | `transaction startswith/endswith` |

> [!İPUCU]
> Splunk'ın kendi önerisi de budur: "Önce `stats` ile çözmeyi dene, olmuyorsa `transaction` kullan." Panolarda ve zamanlanmış aramalarda bu fark dakikalarla ölçülür.
:::

::: tahmin
Tek satır yazar:

```spl
sourcetype=isler is_adi=onbellek-isit
| transaction sunucu maxpause=1h
| table sunucu duration eventcount
```

???

`web01|1860|4`. Önbellek ısıtma olayları 06:00, 06:02, 06:30 ve 06:31'de. Aralarındaki en uzun boşluk 28 dakika, bir saatlik `maxpause`'u aşmıyor. Dördü tek işlemde birleşir: 06:00'dan 06:31'e 31 dakika, yani 1860 saniye. `maxpause=10m` ile iki ayrı işlem olurdu.
:::

::: gorev Biten işlerin süresi
Başlayıp biten her iş çalışmasını tek bir işlem olarak topla ve `calisma`, `is_adi`, `dk` (süre, dakika), `eventcount` alanlarını getir. Hâlâ süren çalışma listede olmasın.

```starter
sourcetype=isler
| transaction calisma
| table calisma is_adi duration eventcount
```

```test
eq(sutunlar, ["calisma", "is_adi", "dk", "eventcount"], "sütunlar")
eq(sonuc, [("B19", "bakim", 50, 3), ("W18B", "onbellek-isit", 1, 2), ("W18A", "onbellek-isit", 2, 2),
           ("Y18", "gece-yedek", 140, 3), ("L17", "log-dondur", 4, 2), ("B17", "bakim", 35, 2),
           ("Y17", "gece-yedek", 85, 3)], "yedi biten çalışma, en yeniden eskiye")
```

```solution
sourcetype=isler
| transaction calisma startswith="başladı" endswith="bitti"
| eval dk=duration/60
| table calisma is_adi dk eventcount
```

```hint
`startswith="başladı" endswith="bitti"` yalnızca başlayıp biten işlemleri bırakır.
```

```hint
`duration` saniyedir: `eval dk=duration/60`.
```
:::

::: gorev Yarım kalan iş
Bütün iş çalışmalarını işlemlere topla ve **bitişi olmayan** (mesajları arasında `bitti` geçmeyen) çalışmaları `calisma`, `is_adi`, `eventcount` alanlarıyla getir.

```starter
sourcetype=isler
| transaction calisma startswith="başladı" endswith="bitti"
| table calisma is_adi eventcount
```

```test
eq(sutunlar, ["calisma", "is_adi", "eventcount"], "sütunlar")
eq(sonuc, [("Y19", "gece-yedek", 2)], "yalnızca Y19")
```

```solution
sourcetype=isler
| transaction calisma
| search NOT mesaj="bitti"
| table calisma is_adi eventcount
```

```hint
`startswith/endswith` yarım kalanları atar; bu soruda onları istemiyorsun. Seçeneksiz `transaction calisma` kur.
```

```hint
`mesaj` çok değerlidir; `search NOT mesaj="bitti"` değerlerinden hiçbiri `bitti` olmayan işlemleri bırakır.
```
:::

::: gorev Aynı sonuç, stats ile
İş türü başına, **biten** çalışmaların ortalama süresini (dakika, bir ondalık) ve en uzun süresini (dakika) getir: `is_adi`, `ort_dk`, `en_uzun_dk`; iş adına göre. Bu kez `transaction` kullanma: çalışmaları `stats` ile özetle ve mesajlarında `bitti` olanları tut.

```starter
sourcetype=isler
| transaction calisma startswith="başladı" endswith="bitti"
| eval dk=duration/60
| stats avg(dk) as ort_dk, max(dk) as en_uzun_dk by is_adi
```

```test
eq(sutunlar, ["is_adi", "ort_dk", "en_uzun_dk"], "sütunlar")
eq(sonuc, [("bakim", 42.5, 50), ("gece-yedek", 112.5, 140), ("log-dondur", 4, 4), ("onbellek-isit", 1.5, 2)], "dört iş türü")
ok(not kullanir("transaction"), "transaction kullanma")
```

```solution
sourcetype=isler
| stats min(_time) as bas, max(_time) as bit, values(mesaj) as mesajlar by calisma is_adi
| search mesajlar="bitti"
| eval dk=(bit-bas)/60
| stats avg(dk) as ort_dk, max(dk) as en_uzun_dk by is_adi
| eval ort_dk=round(ort_dk, 1)
```

```hint
Çalışma başına: `stats min(_time) as bas, max(_time) as bit, values(mesaj) as mesajlar by calisma is_adi`.
```

```hint
Biten çalışmaları `search mesajlar="bitti"` ile tut; süreyi `(bit-bas)/60` ile hesapla ve iş türüne göre yeniden `stats`.
```
:::
