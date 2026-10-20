---
id: sg15
title: Alan Eşleme, Backend ve Dağıtım
summary: Sigma kuralı ile SIEM sorgusu; pipeline alan eşlemesi, indeks/kaynak seçimi ve yerel tezgahın sınırı.
---

::: anlat Taşınabilir fikir, eşleme olmadan çalışmaz
Bir Sigma kuralı, doğrudan her SIEM'de aynı dosyayla çalışacak sihirli bir sorgu değildir. Backend hedef sorgu dilini üretir; processing pipeline alan adlarını, kaynak seçimini ve ortama ait dönüşümleri uygular. Örneğin Sigma'daki `Image`, kurumunda `process.executable` olarak tutuluyor olabilir.

Burada iki ayrı doğrulama vardır: davranış mantığı doğru mu; üretilen sorgu gerçek indekste doğru alan ve veri türünü mü okuyor? Pafta ilk kısmı sentetik olaylarda çalıştırır. Bu dersin görevleri alan adını açıkça değiştirerek eşlemenin etkisini gözle görünür yapar; otomatik backend dönüşümü yaptığını iddia etmez.

Bir field-name mapping, `Image` koşulunu `process.executable` koşuluna taşıyabilir. Kaynak seçimi ise örneğin doğru indeks, sourcetype veya tabloyu belirler. Birini yapmak diğerini yapmış sayılmaz.

```sigma
title: Pafta sg15 Ornek
id: f5aa475e-c524-402d-9427-b7781a8d5681
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        process.executable|endswith: '\audit.exe'
    condition: selection
level: medium
```
:::

::: anlat Dağıtım incelemesinin somut çıktısı
Bir kuralı devretmeden önce gereken telemetri, ham örnek kayıt, kullanılan alan eşlemesi, üretilen sorgu ve olumlu/olumsuz sonuçlar birlikte incelenmelidir. Aynı arama ifadesinin hatasız derlenmesi, verinin gerçekten o tabloya aktığını göstermez.

Yeni alan adına geçince eski alanı taşıyan sentetik kayıt artık eşleşmemelidir; aksi halde görev eşlemeyi gerçekten uygulamamıştır. Görevlerde noktalı alan adları, JSON'da **düz anahtar** olarak yazılır: `{"process.executable": "..."}`. İç içe nesne biçimi bu tezgahın farklı bir şemasıdır; kendiliğinden düzleştirilmez.

> [!NOT]
> Bu yoldaki `logsource` metadata olarak incelenir. Pafta gerçek SIEM bağlantısı kurmaz, sorgu dağıtmaz ve zamanlanmış alarm oluşturmaz. Pipeline ve korelasyon dosyalarını görmekle çalıştırmak arasındaki farkı koru.

### Pipeline dosyasını okumak

Aşağıdaki dosya bir **okuma örneğidir**; Pafta bu pipeline'ı uygulamaz. `field_name_mapping`, Image alanını kurumun düz `process.executable` alan adına taşır. Gerçek dönüşümde ayrıca uygun backend ve veri kaynağı/indeks seçimi gerekir.

```yaml
name: Pafta Field Mapping Example
priority: 100
transformations:
    - id: map_process_path
      type: field_name_mapping
      mapping:
          Image: process.executable
```

`base64`, `base64offset`, `utf16le`, `utf16be`, `wide`, `windash`, `expand` ve `fieldref` gibi modifierlar da Sigma ekosisteminde bulunur. Bunların tamamı Pafta'nın yerel olay değerlendiricisinde desteklenmez; burada desteklenmeyen bir işlemin sessizce atlanması yerine hata bekle. Böyle bir kuralı gerçek backendde denemeden eşdeğer çalıştığını varsayma. Bu yolun çalıştırılabilir kapsamı, görevlerde kullandığımız alan ve koşul modifierlarıdır.


Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/digging-deeper/pipelines.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg15 Ornek
id: f5aa475e-c524-402d-9427-b7781a8d5681
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        process.executable|endswith: '\audit.exe'
    condition: selection
level: medium
```

```stdin
[
  {
    "process.executable": "C:\\Tools\\audit.exe",
    "id": "e1"
  },
  {
    "Image": "C:\\Tools\\audit.exe",
    "id": "e2"
  },
  {
    "process.executable": "C:\\Tools\\other.exe",
    "id": "e3"
  }
]
```

???

`e1` eşleşir. İlk kayıt kuralın aradığı yeni alan adını taşıyor. İkinci kayıt yalnız eski Image alanına sahip; üçüncüde doğru alan olsa da başka program yazıyor.
:::

::: gorev Image alanını açıkça eşle
Yeni şemada Image yerine düz anahtar `process.executable` var. Bu alan `\inventory.exe` ile bitsin. Eski Image alanı tek başına eşleşmesin; başka süreçler de dışarıda kalsın.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg15 Image alanını açıkça eşle
id: a2f7bd0e-e51f-4861-937c-e7b78c639001
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
    "process.executable": "C:\\Tools\\inventory.exe",
    "id": "g1-1"
  },
  {
    "process.executable": "D:\\Ops\\INVENTORY.EXE",
    "id": "g1-2"
  },
  {
    "Image": "C:\\Tools\\inventory.exe",
    "id": "g1-3"
  },
  {
    "process.executable": "C:\\Tools\\other.exe",
    "id": "g1-4"
  },
  {
    "id": "g1-5"
  }
]
```

```test
ok(eslesir({'process.executable': 'C:\\Tools\\inventory.exe'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'process.executable': 'D:\\Ops\\INVENTORY.EXE'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'Image': 'C:\\Tools\\inventory.exe'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'process.executable': 'C:\\Tools\\other.exe'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg15 Image alanını açıkça eşle
id: e15fba28-7edf-4cc7-b0f1-02cd8dc95818
status: experimental
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        process.executable|endswith: '\inventory.exe'
    condition: selection
level: medium
```

```hint
Noktalı adı JSON’daki düz anahtarla aynı yaz; burada iç içe nesne gezilmiyor.
```
:::

::: gorev Olay kodu eşlemesi
Security veri kümesinin yeni şemasında Channel yerine `winlog.channel`, EventID yerine `event.code` kullanılıyor. winlog.channel Security ve event.code **metin** `4625` olsun. Eski alanlar veya başarılı 4624 eşleşmesin.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg15 Olay kodu eşlemesi
id: a2636bae-7e29-47d4-a3a7-06760713f6da
status: experimental
logsource:
    product: windows
    service: security
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
    "winlog.channel": "Security",
    "event.code": "4625",
    "user.name": "demo",
    "id": "g2-1"
  },
  {
    "Channel": "Security",
    "EventID": 4625,
    "id": "g2-2"
  },
  {
    "winlog.channel": "Security",
    "event.code": "4624",
    "id": "g2-3"
  },
  {
    "winlog.channel": "Application",
    "event.code": "4625",
    "id": "g2-4"
  }
]
```

```test
ok(eslesir({'winlog.channel': 'Security', 'event.code': '4625', 'user.name': 'demo'}), 'Olumlu ornek 1 eslesmeli')
ok(not eslesir({'Channel': 'Security', 'EventID': 4625}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'winlog.channel': 'Security', 'event.code': '4624'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'winlog.channel': 'Application', 'event.code': '4625'}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg15 Olay kodu eşlemesi
id: 2cde0d57-599d-4321-9cbd-ccc371dc80d3
status: experimental
logsource:
    product: windows
    service: security
detection:
    selection:
        winlog.channel: 'Security'
        event.code: '4625'
    condition: selection
level: medium
```

```hint
Eşleme yalnız alan adını değil veri şemasının tür beklentisini de ilgilendirir.
```
:::
