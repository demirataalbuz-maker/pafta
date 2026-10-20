---
id: sg02
title: YAML, Değer Türleri ve Alan Adları
summary: Metin, sayı, Boolean ve YAML girintisi; Windows yollarını güvenle yazmak ve alan adlarını doğrulamak.
---

::: anlat Görünen metnin arkasında bir tür var
YAML'daki `EventID: 4625` bir sayıdır; `EventID: '4625'` metindir. Olay kaynağın hangi türü üretiyor? Kuralı kaynağı görmeden yazarsan bu fark sessiz kaçırmalara dönüşebilir. Pafta'da örneklerin türlerini bilerek tutarlı kullanıyoruz; gerçek üründe alan şeması ve dönüştürme hattı da doğrulanmalıdır.

Bir Windows yolunu tek tırnakla yazmak çoğu zaman okunaklıdır: `'C:\Tools\audit.exe'`. Tek tırnak içinde ters eğik çizgi kaçış başlatmaz. Çift tırnaklı YAML metninde ters eğik çizgilerin ayrı kuralları vardır. JSON girdi kutusunda ise yolun ters eğik çizgilerini JSON kuralına göre çift yazarsın. Bunlar iki ayrı dosya biçimidir.

YAML anahtarları aynı düzeyde hizalanmalı. `condition`, `selection` ile aynı girintide; `Image` gibi alanlar seçimin altında olmalıdır. Bozuk girintiyi değer değiştirerek çözmeye çalışma; önce ağacın yapısını kontrol et.

```sigma
title: Pafta sg02 Ornek
id: 3e98b5b7-7afa-4e48-9bc0-eacfce19efb1
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'lock'
        Enabled: false
    condition: selection
level: medium
```
:::

::: anlat Şemayı önce küçük örnekle doğrula
Alan adının büyük-küçük harfi, değerin karşılaştırılmasından ayrı konudur. Sigma'nın normal metin eşleşmesi varsayılan olarak harf duyarsız olsa da `Image` adını `image` diye yazman başka bir alan aramaktır. Kaydın ham haline bak; kopyalanan ekran etiketini alan adı sanma.

Boolean değerleri `true` ve `false` olarak tırnaksız yaz. `false`, `0`, boş metin ve eksik alan aynı bilgi değildir. Bu ayrımlar sonradan `exists` ve eksik veri dersinde önem kazanacak. Öğrendiğin her alan için adını, türünü ve bir normal örneğini not etmek, yüz satırlık kurala rastgele yeni koşul eklemekten daha faydalıdır.

> [!TUZAK]
> YAML'da aynı eşleme anahtarını iki kez yazarak iki koşul tanımlama. Bazı okuyucular son değeri tutar. Aynı alanda iki ayrı gereksinim için ayrı seçimler veya uygun liste ve `all` düzenini kullanacağız.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/sigma-specification/specification/sigma-rules-specification.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg02 Ornek
id: 3e98b5b7-7afa-4e48-9bc0-eacfce19efb1
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'lock'
        Enabled: false
    condition: selection
level: medium
```

```stdin
[
  {
    "Action": "lock",
    "Enabled": false,
    "id": "e1"
  },
  {
    "Action": "lock",
    "Enabled": true,
    "id": "e2"
  }
]
```

???

`e1` eşleşir. İki olay da lock eylemi taşıyor. `e1`de Enabled false, `e2`de true olduğu için yalnız ilki iki alanı birlikte sağlar.
:::

::: gorev Yolu ve işlemi eşleştir
`Image` alanı tam `C:\Tools\audit.exe`, `Action` alanı `start` olan kayıtları yakala. Başka klasördeki aynı dosya adı yeterli değildir.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg02 Yolu ve işlemi eşleştir
id: 511607ce-136e-4f53-9e63-60cb6859e53a
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
    "Image": "C:\\Tools\\audit.exe",
    "Action": "start",
    "id": "g1-1"
  },
  {
    "Image": "c:\\tools\\AUDIT.EXE",
    "Action": "START",
    "id": "g1-2"
  },
  {
    "Image": "C:\\Temp\\audit.exe",
    "Action": "start",
    "id": "g1-3"
  },
  {
    "Image": "C:\\Tools\\audit.exe",
    "Action": "stop",
    "id": "g1-4"
  },
  {
    "image": "C:\\Tools\\audit.exe",
    "Action": "start",
    "id": "g1-5"
  }
]
```

```test
ok(eslesir({'Image': 'C:\\Tools\\audit.exe', 'Action': 'start'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Image': 'c:\\tools\\AUDIT.EXE', 'Action': 'START'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Image': 'C:\\Temp\\audit.exe', 'Action': 'start'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Image': 'C:\\Tools\\audit.exe', 'Action': 'stop'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'image': 'C:\\Tools\\audit.exe', 'Action': 'start'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg02 Yolu ve işlemi eşleştir
id: 40cb1871-1ada-4bcf-82e5-64677f4b26f7
status: experimental
logsource:
    category: application
detection:
    selection:
        Image: 'C:\Tools\audit.exe'
        Action: 'start'
    condition: selection
level: medium
```

```hint
Tek selection altındaki iki alan birlikte aranır; Windows yolunu tek tırnak içine al.
```
:::

::: gorev Boolean alanı
`Action: policy_changed` ve `Enabled: false` birlikte olsun. Etkinleştirme veya başka bir eylemi yakalama. `Enabled` alanı olmayan kayıt da yeterli değildir.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg02 Boolean alanı
id: bf97e625-d3ad-406b-9c15-2e1c723c366c
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
    "Action": "policy_changed",
    "Enabled": false,
    "id": "g2-1"
  },
  {
    "Action": "POLICY_CHANGED",
    "Enabled": false,
    "id": "g2-2"
  },
  {
    "Action": "policy_changed",
    "Enabled": true,
    "id": "g2-3"
  },
  {
    "Action": "policy_viewed",
    "Enabled": false,
    "id": "g2-4"
  },
  {
    "Action": "policy_changed",
    "id": "g2-5"
  }
]
```

```test
ok(eslesir({'Action': 'policy_changed', 'Enabled': False}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'Action': 'POLICY_CHANGED', 'Enabled': False}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Action': 'policy_changed', 'Enabled': True}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'Action': 'policy_viewed', 'Enabled': False}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'Action': 'policy_changed'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg02 Boolean alanı
id: d8f1521c-86c9-4163-852c-b91145626a4c
status: experimental
logsource:
    category: application
detection:
    selection:
        Action: 'policy_changed'
        Enabled: false
    condition: selection
level: medium
```

```hint
false değerini tırnaksız yaz; metin değil Boolean istiyoruz.
```
:::
