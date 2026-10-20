---
id: sg11
title: Regex ile Biçim Denetimi
summary: re modifierı, baş/son işaretleri, karakter sınıfları; normal jokerden farkı ve pahalı desenlerden kaçınmak.
---

::: anlat Literal parça değil biçim arıyorsan
`contains` bilinen metin parçası için iyidir. Ama `REQ-` ile başlayıp tam altı rakamla biten bir kimlik arıyorsan biçim bilgisine ihtiyaç vardır. `RequestId|re: '^REQ-[0-9]{6}$'` bunu ifade eder. Buradaki `^` ve `$`, değerin tamamını sınırlar; bunlar olmadan daha uzun bir metnin içindeki parça da eşleşebilir.

Sigma'nın normal jokerleri ile regex farklı dillerdir. Jokerde `*` tek başına çok karakter demektir; regex'te önceki parçayı tekrarlar. Her dosya adı sorusuna regex yazmak yerine önce düz eşleşme veya `startswith/endswith` yeterli mi diye düşün.

Regex eşleştirmesinde harf davranışını varsayma: standart `re` normal metin eşleştirmesinden farklı olarak varsayılan harf duyarlılığına sahiptir; destekleyen backendlerde `re|i` gibi alt modifierlarla davranış değişebilir. Pafta görevleri bu derste harf duyarlı ASCII desenler kullanır; böylece motor lehçesi farkını gizlemeyiz.

```sigma
title: Pafta sg11 Ornek
id: 49472221-2c1f-4129-bf01-e5a9f128d208
status: experimental
logsource:
    category: application
detection:
    selection:
        RequestId|re: '^REQ-[0-9]{6}$'
    condition: selection
level: medium
```
:::

::: anlat Deseni örnek sınırlarında kır
İyi negatif örnekler yalnız bambaşka metinler değildir: bir rakamı eksik/fazla kimlik, yanlış önek, başına ek metin, sonuna ek metin de gerekir. Bu örnekler desende sınır işaretlerinin unutulmasını yakalar.

Regex motorları aynı bütün özellikleri sunmaz. Bir backend Python re, diğeri farklı regex lehçesi kullanabilir. Özel lookbehind ve pahalı iç içe tekrarlar yerine mümkün olduğunda açık karakter sınıfları ve sınırlı uzunluklar kullan. Çok büyük log alanlarında desen maliyeti de tespit tasarımının parçasıdır.

> [!TUZAK]
> Regex uygun bir alanı sınar; kaydın ham JSON metnini baştan sona aramaz. RequestId koşulunu Message alanına yazmak, doğru desenle bile yanlış veriyi aramak demektir.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/modifiers.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg11 Ornek
id: 49472221-2c1f-4129-bf01-e5a9f128d208
status: experimental
logsource:
    category: application
detection:
    selection:
        RequestId|re: '^REQ-[0-9]{6}$'
    condition: selection
level: medium
```

```stdin
[
  {
    "RequestId": "REQ-123456",
    "id": "e1"
  },
  {
    "RequestId": "REQ-12345",
    "id": "e2"
  },
  {
    "RequestId": "xREQ-123456",
    "id": "e3"
  }
]
```

???

`e1` eşleşir. İlk kimlik REQ- önekinden sonra tam altı rakam taşır. İkincide bir rakam eksik; üçüncünün başındaki x, başlangıç işareti ^ nedeniyle kabul edilmez.
:::

::: gorev Etiket biçimi
`AssetTag` yalnız `SRV-` ve ardından tam dört rakam biçimindeyse eşleşsin. Başta veya sonda başka karakter kabul etme; büyük SRV gerekir.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg11 Etiket biçimi
id: 88a8c9d7-8b34-4398-be64-fa516dcd9e22
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
    "AssetTag": "SRV-0001",
    "id": "g1-1"
  },
  {
    "AssetTag": "SRV-9876",
    "id": "g1-2"
  },
  {
    "AssetTag": "SRV-001",
    "id": "g1-3"
  },
  {
    "AssetTag": "SRV-00001",
    "id": "g1-4"
  },
  {
    "AssetTag": "srv-0001",
    "id": "g1-5"
  },
  {
    "AssetTag": "xSRV-0001",
    "id": "g1-6"
  },
  {
    "AssetTag": "SRV-0001.bak",
    "id": "g1-7"
  }
]
```

```test
ok(eslesir({'AssetTag': 'SRV-0001'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'AssetTag': 'SRV-9876'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'AssetTag': 'SRV-001'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'AssetTag': 'SRV-00001'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'AssetTag': 'srv-0001'}), 'Olumsuz ornek 3 disarida kalmali')
ok(not eslesir({'AssetTag': 'xSRV-0001'}), 'Olumsuz ornek 4 disarida kalmali')
ok(not eslesir({'AssetTag': 'SRV-0001.bak'}), 'Olumsuz ornek 5 disarida kalmali')
```

```solution
title: Pafta sg11 Etiket biçimi
id: ee55273f-6180-4c29-a9c2-01f910941279
status: experimental
logsource:
    category: application
detection:
    selection:
        AssetTag|re: '^SRV-[0-9]{4}$'
    condition: selection
level: medium
```

```hint
Baş ve son işaretleriyle [0-9]{4} tekrarını birleştir.
```
:::

::: gorev Dosya adının yapısı
`TargetFilename` alanının tamamı `daily_YYYYMMDD.json` biçiminde olsun; YYYYMMDD tam sekiz rakamdır. Takvim geçerliliği istenmiyor, yalnız biçim. Noktayı gerçek nokta olarak eşleştir.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg11 Dosya adının yapısı
id: f501d1f3-d298-40d1-a5e5-1235b5e8bb4b
status: experimental
logsource:
    category: file_event
    product: windows
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
    "TargetFilename": "daily_20261020.json",
    "id": "g2-1"
  },
  {
    "TargetFilename": "daily_20000101.json",
    "id": "g2-2"
  },
  {
    "TargetFilename": "daily_2026102.json",
    "id": "g2-3"
  },
  {
    "TargetFilename": "daily_20261020Xjson",
    "id": "g2-4"
  },
  {
    "TargetFilename": "daily_20261020.json.bak",
    "id": "g2-5"
  },
  {
    "TargetFilename": "monthly_20261020.json",
    "id": "g2-6"
  }
]
```

```test
ok(eslesir({'TargetFilename': 'daily_20261020.json'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'TargetFilename': 'daily_20000101.json'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'TargetFilename': 'daily_2026102.json'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'TargetFilename': 'daily_20261020Xjson'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'TargetFilename': 'daily_20261020.json.bak'}), 'Olumsuz ornek 3 disarida kalmali')
ok(not eslesir({'TargetFilename': 'monthly_20261020.json'}), 'Olumsuz ornek 4 disarida kalmali')
```

```solution
title: Pafta sg11 Dosya adının yapısı
id: e6c6ad55-01e3-439d-a809-a1651464c1c0
status: experimental
logsource:
    category: file_event
    product: windows
detection:
    selection:
        TargetFilename|re: '^daily_[0-9]{8}\.json$'
    condition: selection
level: medium
```

```hint
Regex’te gerçek nokta \. olur; tek tırnaklı YAML bunu korur.
```
:::
