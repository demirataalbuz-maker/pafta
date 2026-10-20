---
id: sg09
title: Eksik Alan, Boş Değer ve Harf Duyarlılığı
summary: exists ile telemetri eksikliği, boş metnin farkı ve cased ile bilinçli harf duyarlı eşleşme.
---

::: anlat Eksik bilgi, normal bilgi değildir
Bir JSON olayında alan hiç olmayabilir, alanın değeri `null` olabilir veya alan boş metin taşıyabilir. Bu üç durum veri hattında farklı sebeplerden doğabilir. Kuralı yazarken hangisini aradığını açıkça belirt; her boşluk bir gizleme girişimi değildir, her eksiklik de masum sayılamaz.

`Field|exists: true` alan varlığına ilişkin koşulu, `Field|exists: false` yokluk koşulunu ifade eder. Boş metin aramak ise `Field: ''` biçimindedir. Gerçek backendlerde boş/null davranışı farklılaşabilir; ürün testine bu örnekleri de ekle. Pafta görevlerinde tartışmasız durumları, açıkça var olan veya hiç bulunmayan alanları kullanıyoruz.

`not selection` kullanırken seçim alanının kayıtta olmaması sonucun tersini çevirebilir. Bu yüzden önce ilgilendiğin olay türünü seç, sonra o olayın zorunlu alanındaki eksikliği denetle. Bütün kayıt evreninde eksik CommandLine aramak anlamsız derecede geniştir.

```sigma
title: Pafta sg09 Ornek
id: ce1ec816-d208-448c-b0cf-34d1d5d46834
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection_type:
        EventType: 'process_creation'
    selection_missing:
        CommandLine|exists: false
    condition: selection_type and selection_missing
level: medium
```
:::

::: anlat Harf duyarlılığı bir veri kararıdır
Sigma'nın normal metin değerleri varsayılan olarak harf duyarsız karşılaştırılır. `|cased` belirli bir değerde harf farkını anlamlı hale getirir. Kullanıcı adları, tokenlar, Linux yolları ve uygulama alanları için doğru seçim veri kaynağının anlamına bağlıdır; her alana körce uygulanmaz.

Dosya sistemi hassasiyeti ile olay metni karşılaştırması aynı katman değildir. Bu tezgah bir dosyayı açmadığı için `cased` yalnız kaydın metnini kıyaslar. Bir Linux hedef yolunu harf duyarlı seçmek istediğinde bu gereksinimi kuralda ayrıca belirtmelisin.

> [!TUZAK]
> `exists` değerini `'false'` diye tırnaklama. Bu bir Boolean anahtarıdır; yanlış tür bir sözdizimi ya da semantik hataya dönüşebilir.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/modifiers.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg09 Ornek
id: ce1ec816-d208-448c-b0cf-34d1d5d46834
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection_type:
        EventType: 'process_creation'
    selection_missing:
        CommandLine|exists: false
    condition: selection_type and selection_missing
level: medium
```

```stdin
[
  {
    "EventType": "process_creation",
    "Image": "tool",
    "id": "e1"
  },
  {
    "EventType": "process_creation",
    "CommandLine": "tool --help",
    "id": "e2"
  },
  {
    "EventType": "network_connection",
    "id": "e3"
  }
]
```

???

`e1` eşleşir. `e1` bir süreç olayıdır ve CommandLine anahtarı yoktur. `e2`de anahtar var; `e3` ise zaten başka olay türüdür. Boşluk aramadan önce olay türünü daraltmak önemlidir.
:::

::: gorev Komut satırı eksik süreç kaydı
`EventType: process_creation` olan kayıtlardan CommandLine alanı hiç bulunmayanları seç. CommandLine mevcutsa veya olay başka türdeyse eşleşmesin.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg09 Komut satırı eksik süreç kaydı
id: 1d7e42fc-c817-4ff9-ab8c-4418ddf4654d
status: experimental
logsource:
    category: process_creation
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
    "EventType": "process_creation",
    "Image": "tool.exe",
    "id": "g1-1"
  },
  {
    "EventType": "process_creation",
    "CommandLine": "tool.exe --help",
    "id": "g1-2"
  },
  {
    "EventType": "process_creation",
    "CommandLine": "",
    "id": "g1-3"
  },
  {
    "EventType": "network_connection",
    "id": "g1-4"
  }
]
```

```test
ok(eslesir({'EventType': 'process_creation', 'Image': 'tool.exe'}), 'Olumlu ornek 1 eslesmeli')
ok(not eslesir({'EventType': 'process_creation', 'CommandLine': 'tool.exe --help'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'EventType': 'process_creation', 'CommandLine': ''}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'EventType': 'network_connection'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg09 Komut satırı eksik süreç kaydı
id: f5aa06fb-ff44-4466-a954-e2f2b1b8de51
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        EventType: 'process_creation'
        CommandLine|exists: false
    condition: selection
level: medium
```

```hint
Olay türünü ve CommandLine|exists: false koşulunu aynı seçimde tut.
```
:::

::: gorev Linux yolunda büyük harf farkı
`TargetPath` yalnız tam `/opt/Pafta/Config` değeriyse eşleşsin. `/opt/pafta/config` ve `/opt/Pafta/Config.bak` eşleşmesin; `cased` kullan.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg09 Linux yolunda büyük harf farkı
id: aec2de7c-ed5e-4a86-9198-c246b6bf2a66
status: experimental
logsource:
    category: file_event
    product: linux
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
    "TargetPath": "/opt/Pafta/Config",
    "id": "g2-1"
  },
  {
    "TargetPath": "/opt/pafta/config",
    "id": "g2-2"
  },
  {
    "TargetPath": "/opt/Pafta/Config.bak",
    "id": "g2-3"
  },
  {
    "id": "g2-4"
  }
]
```

```test
ok(eslesir({'TargetPath': '/opt/Pafta/Config'}), 'Olumlu ornek 1 eslesmeli')
ok(not eslesir({'TargetPath': '/opt/pafta/config'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'TargetPath': '/opt/Pafta/Config.bak'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({}), 'Olumsuz ornek 3 disarida kalmali')
ok('|cased' in src, 'Harf duyarlılığını açık belirt')
```

```solution
title: Pafta sg09 Linux yolunda büyük harf farkı
id: 3c569ad8-c4c2-456c-9b3f-76242a55ab33
status: experimental
logsource:
    category: file_event
    product: linux
detection:
    selection:
        TargetPath|cased: '/opt/Pafta/Config'
    condition: selection
level: medium
```

```hint
Alan adına |cased ekle; modifier olmadan normal karşılaştırma harf duyarsızdır.
```
:::
