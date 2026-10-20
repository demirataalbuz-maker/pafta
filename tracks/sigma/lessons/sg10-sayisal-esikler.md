---
id: sg10
title: Sayısal Eşikler ve Sınır Değerleri
summary: gt, gte, lt, lte; kapalı ve açık aralıkları kurmak, eşik altı/eşik/eşik üstü regresyonları.
---

::: anlat Büyük ile büyük-eşit aynı değildir
`BytesSent|gt: 1000`, 1000'i içermez. `gte` içerir; `lt` küçüktür, `lte` küçük veya eşittir. Bir ürünün sayısal alanı gerçekten sayı mı, yoksa `'1000'` gibi metin mi? Kaynak şemasını doğrulamadan eşiği çalışıyor sayma. Bu dersin JSON örneklerinde miktarlar sayıdır.

Bir değerin alt ve üst sınırı aynı anda isteniyorsa iki ayrı seçim kurup AND ile birleştirebilirsin. Aynı `BytesSent` anahtarını YAML'da tekrar yazmak yerine `selection_lower` ve `selection_upper` gibi adlar kullan. Böylece hangi sınırın dahil olduğu görünür kalır.

Eşik sihirli bir sayı değildir; birim ve gözlem penceresiyle anlam kazanır. `BytesSent` tek olayda gönderilen bayt mı, bir dakikalık toplam mı? Burada yalnız tek olay alanını karşılaştırıyoruz. Belirli bir süredeki toplamı kural motorunun bu olay bazındaki katmanına hayal ederek eklemiyoruz.

```sigma
title: Pafta sg10 Ornek
id: fe184062-aefc-4318-a8f5-62c48c94b727
status: experimental
logsource:
    category: application
detection:
    selection:
        BytesSent|gte: 1000
    condition: selection
level: medium
```
:::

::: anlat Üç nokta testi
Bir eşik için üç komşu değer dene: hemen altı, kendisi ve hemen üstü. `>= 1000` şartını yalnız 5000 ile sınamak `> 1000` yazma hatasını yakalayamaz. Aralık kuralında iki sınırın da çevresini dene.

Olay türünü de koşula ekle. Farklı olay ailelerindeki aynı adlı sayı aynı anlama gelmeyebilir. `Action: download` ile boyut eşiğini birleştirmek, ölçüm ve bağlamı birlikte anlatır. Eksik alanı sıfır saymak yerine verinin yokluğunu ayrıca ele al.

> [!NOT]
> Bu görevlerin eşikleri yalnız sınır mantığını öğrenmek için seçildi. Gerçek ortamda alarm eşiği, normal trafik dağılımı ve operasyon gereksinimleriyle değerlendirilir.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/modifiers.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg10 Ornek
id: fe184062-aefc-4318-a8f5-62c48c94b727
status: experimental
logsource:
    category: application
detection:
    selection:
        BytesSent|gte: 1000
    condition: selection
level: medium
```

```stdin
[
  {
    "BytesSent": 1000,
    "id": "e1"
  },
  {
    "BytesSent": 1001,
    "id": "e2"
  },
  {
    "BytesSent": 999,
    "id": "e3"
  }
]
```

???

`e1`, `e2` eşleşir. gte, 1000 sınırını dahil eder: ilk iki miktar 1000 ve 1001. Son miktar 999 olduğu için koşul yanlıştır.
:::

::: gorev Dahil olan alt eşik
`Action: download` ve `BytesSent >= 1048576` birlikte olsun. 1048576 dahil; bir bayt eksiği ve upload dışarıda kalsın.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg10 Dahil olan alt eşik
id: b08129c5-db9c-46fb-ba36-374c8e2007e5
status: experimental
logsource:
    category: webserver
detection:
    selection:
        # TODO: gorevdeki davranis kosullarini buraya yaz
        Action: 'TODO'
    condition: selection
level: medium
```

```stdin
[
  {
    "Action": "download",
    "BytesSent": 1048576,
    "id": "g1-1"
  },
  {
    "Action": "download",
    "BytesSent": 1048577,
    "id": "g1-2"
  },
  {
    "Action": "download",
    "BytesSent": 1048575,
    "id": "g1-3"
  },
  {
    "Action": "upload",
    "BytesSent": 2097152,
    "id": "g1-4"
  },
  {
    "Action": "download",
    "id": "g1-5"
  }
]
```

```test
ok(eslesir({'Action': 'download', 'BytesSent': 1048576}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Action': 'download', 'BytesSent': 1048577}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Action': 'download', 'BytesSent': 1048575}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Action': 'upload', 'BytesSent': 2097152}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Action': 'download'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg10 Dahil olan alt eşik
id: be58f623-ec0b-4a85-bd50-c564c1ad8346
status: experimental
logsource:
    category: webserver
detection:
    selection:
        Action: 'download'
        BytesSent|gte: 1048576
    condition: selection
level: medium
```

```hint
gte sınır değerini içerir; gt içermez.
```
:::

::: gorev Yarım açık aralık
`DurationMs` en az 200 ve 500’den küçük olsun: **200 <= DurationMs < 500**. İki ayrı seçimle iki sınırı birleştir.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg10 Yarım açık aralık
id: 4f271e74-da90-4c8a-9cf8-7b900187551c
status: experimental
logsource:
    category: application
detection:
    selection:
        # TODO: gorevdeki davranis kosullarini buraya yaz
        Action: 'TODO'
    condition: selection
level: medium
```

```stdin
[
  {
    "DurationMs": 200,
    "id": "g2-1"
  },
  {
    "DurationMs": 499,
    "id": "g2-2"
  },
  {
    "DurationMs": 350,
    "id": "g2-3"
  },
  {
    "DurationMs": 199,
    "id": "g2-4"
  },
  {
    "DurationMs": 500,
    "id": "g2-5"
  },
  {
    "DurationMs": 501,
    "id": "g2-6"
  },
  {
    "id": "g2-7"
  }
]
```

```test
ok(eslesir({'DurationMs': 200}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'DurationMs': 499}), 'Olumlu ornek 2 eslesmeli')
ok(eslesir({'DurationMs': 350}), 'Olumlu ornek 3 eslesmeli')
ok(not eslesir({'DurationMs': 199}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'DurationMs': 500}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'DurationMs': 501}), 'Olumsuz ornek 3 disarida kalmali')
ok(not eslesir({}), 'Olumsuz ornek 4 disarida kalmali')
```

```solution
title: Pafta sg10 Yarım açık aralık
id: 20393470-9a29-4db8-8dea-0df5d393d5eb
status: experimental
logsource:
    category: application
detection:
    selection_lower:
        DurationMs|gte: 200
    selection_upper:
        DurationMs|lt: 500
    condition: selection_lower and selection_upper
level: medium
```

```hint
Alt sınır gte, üst sınır lt; iki seçim arasında and.
```
:::
