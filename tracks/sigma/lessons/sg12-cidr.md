---
id: sg12
title: IP Ağları ve CIDR Koşulları
summary: Adres öneki yerine ağ üyeliği; cidr listeleri, IPv4/IPv6 ve eksik veri karşısında dış ağ tanımı.
---

::: anlat Bir IP adresi metin öneki değildir
`DestinationIp|startswith: '10.'` yalnız metne bakar. `|cidr: '10.0.0.0/8'` bir IP adresinin belirtilen ağda olup olmadığını sorar. CIDR, ağın sabit bit sayısını taşır: `/24` IPv4'te 256 adreslik bir aralıktır. `10.0.2.0/23` hem 10.0.2.x hem 10.0.3.x adreslerini içerir.

CIDR altında liste kullandığında ağlardan herhangi birine üyelik yeterlidir. Özel adres aralıklarını topluca yazmak, bir sürü metin öneki ve istisna kurmaktan daha açık olur. IPv6 için de bir IPv6 CIDR değeri kullanılabilir; aynı alanda sürüm farklarını test etmek gerekir.

Bu yolun dış adres örnekleri belgeleme için ayrılmış sentetik aralıklardandır. Gerçek bir sunucuya bağlantı kurulmaz. Kural yalnız olay içindeki DestinationIp değerini değerlendirir.

```sigma
title: Pafta sg12 Ornek
id: 20908556-cca8-4bba-9189-37ca687a410d
status: experimental
logsource:
    category: network_connection
    product: windows
detection:
    selection:
        DestinationIp|cidr: '10.0.2.0/23'
    condition: selection
level: medium
```
:::

::: anlat İç ağ değil demek için adres de gerekli
`not filter_internal` yazmak, DestinationIp hiç bulunmadığında da doğru olabilir. Ağ bağlantısı olaylarında dış adres arıyorsan önce gerekli alanın varlığını ve olay türünü iste; kurumunun normalleştirme hattında adreslerin geçerli IP olduğu önkoşulunu da doğrula.

Burada “dış” yalnız yazdığımız özel ağ listelerinin dışında demektir. Bu, “internette yönlendirilebilir ve saldırgan” anlamına gelmez: loopback, link-local ve başka özel amaçlı aralıklar ayrıca ele alınabilir. İş ihtiyacının neyi dışarıda bırakacağını tarif et.

Kuralı ağın ilk adresi, son adresi ve hemen dışındaki adresle sınamak sınır hatalarını yakalar. /23'ü /24 sanmak gibi bir hata, yalnız ağın ilk yarısından örnek verirsen görünmez.

Kaynak: [Sigma resmi belgesi](https://sigmahq.io/docs/basics/modifiers.html).
:::

::: tahmin
Girdi kutusundaki sentetik olaylardan hangilerinin `id` değerleri eşleşir? Kuralı ve olayları birlikte oku. Çıktıda eşleşen kimlikler sırayla gösterilir.

```sigma
title: Pafta sg12 Ornek
id: 20908556-cca8-4bba-9189-37ca687a410d
status: experimental
logsource:
    category: network_connection
    product: windows
detection:
    selection:
        DestinationIp|cidr: '10.0.2.0/23'
    condition: selection
level: medium
```

```stdin
[
  {
    "DestinationIp": "10.0.2.1",
    "id": "e1"
  },
  {
    "DestinationIp": "10.0.3.255",
    "id": "e2"
  },
  {
    "DestinationIp": "10.0.4.0",
    "id": "e3"
  },
  {
    "DestinationIp": "10.0.1.255",
    "id": "e4"
  }
]
```

???

`e1`, `e2` eşleşir. /23 ağı 10.0.2.0 ile 10.0.3.255 arasını içerir. İlk iki adres içeride; 10.0.4.0 ve 10.0.1.255 ağın hemen dışında.
:::

::: gorev İki alt ağı kapsayan aralık
DestinationIp alanı `10.0.2.0/23` içinde olsun. İlk ve son adres dahil; 10.0.1.255 ve 10.0.4.0 dışarıda kalmalı.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg12 İki alt ağı kapsayan aralık
id: 0a61ecca-346b-4c81-a6d1-b70a5270371f
status: experimental
logsource:
    category: network_connection
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
    "DestinationIp": "10.0.2.0",
    "id": "g1-1"
  },
  {
    "DestinationIp": "10.0.2.99",
    "id": "g1-2"
  },
  {
    "DestinationIp": "10.0.3.255",
    "id": "g1-3"
  },
  {
    "DestinationIp": "10.0.1.255",
    "id": "g1-4"
  },
  {
    "DestinationIp": "10.0.4.0",
    "id": "g1-5"
  },
  {
    "id": "g1-6"
  }
]
```

```test
ok(eslesir({'DestinationIp': '10.0.2.0'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'DestinationIp': '10.0.2.99'}), 'Olumlu ornek 2 eslesmeli')
ok(eslesir({'DestinationIp': '10.0.3.255'}), 'Olumlu ornek 3 eslesmeli')
ok(not eslesir({'DestinationIp': '10.0.1.255'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'DestinationIp': '10.0.4.0'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({}), 'Olumsuz ornek 3 disarida kalmali')
```

```solution
title: Pafta sg12 İki alt ağı kapsayan aralık
id: 6cdc564f-ed28-4c07-94d7-9bf2bf1ce3a7
status: experimental
logsource:
    category: network_connection
    product: windows
detection:
    selection:
        DestinationIp|cidr: '10.0.2.0/23'
    condition: selection
level: medium
```

```hint
Metin öneki değil cidr modifierı kullan.
```
:::

::: gorev Adresli, özel ağ dışı TCP
EventType network_connection ve Protocol tcp olsun; DestinationIp alanı bulunsun. 10.0.0.0/8, 172.16.0.0/12 ve 192.168.0.0/16 aralıklarını dışla. Bu görevde giriş adresleri geçerli IPv4 kabul edilir.

Girdi kutusundaki olayları Çalıştır ile deneyebilir, Kontrol et ile olumlu ve olumsuz örneklerin tümünü sınayabilirsin.

```starter
title: Pafta sg12 Adresli, özel ağ dışı TCP
id: 06a8bec0-9291-4184-ad7e-6e8b0b21c615
status: experimental
logsource:
    category: network_connection
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
    "EventType": "network_connection",
    "Protocol": "tcp",
    "DestinationIp": "203.0.113.42",
    "id": "g2-1"
  },
  {
    "EventType": "network_connection",
    "Protocol": "tcp",
    "DestinationIp": "172.32.0.1",
    "id": "g2-2"
  },
  {
    "EventType": "network_connection",
    "Protocol": "tcp",
    "DestinationIp": "10.0.1.4",
    "id": "g2-3"
  },
  {
    "EventType": "network_connection",
    "Protocol": "tcp",
    "DestinationIp": "172.31.255.255",
    "id": "g2-4"
  },
  {
    "EventType": "network_connection",
    "Protocol": "tcp",
    "DestinationIp": "192.168.2.8",
    "id": "g2-5"
  },
  {
    "EventType": "network_connection",
    "Protocol": "udp",
    "DestinationIp": "203.0.113.42",
    "id": "g2-6"
  },
  {
    "EventType": "network_connection",
    "Protocol": "tcp",
    "id": "g2-7"
  }
]
```

```test
ok(eslesir({'EventType': 'network_connection', 'Protocol': 'tcp', 'DestinationIp': '203.0.113.42'}), 'Olumlu ornek 1 eslesmeli')
ok(eslesir({'EventType': 'network_connection', 'Protocol': 'tcp', 'DestinationIp': '172.32.0.1'}), 'Olumlu ornek 2 eslesmeli')
ok(not eslesir({'EventType': 'network_connection', 'Protocol': 'tcp', 'DestinationIp': '10.0.1.4'}), 'Olumsuz ornek 1 disarida kalmali')
ok(not eslesir({'EventType': 'network_connection', 'Protocol': 'tcp', 'DestinationIp': '172.31.255.255'}), 'Olumsuz ornek 2 disarida kalmali')
ok(not eslesir({'EventType': 'network_connection', 'Protocol': 'tcp', 'DestinationIp': '192.168.2.8'}), 'Olumsuz ornek 3 disarida kalmali')
ok(not eslesir({'EventType': 'network_connection', 'Protocol': 'udp', 'DestinationIp': '203.0.113.42'}), 'Olumsuz ornek 4 disarida kalmali')
ok(not eslesir({'EventType': 'network_connection', 'Protocol': 'tcp'}), 'Olumsuz ornek 5 disarida kalmali')
```

```solution
title: Pafta sg12 Adresli, özel ağ dışı TCP
id: 478912b2-fb08-4c4a-b628-d19cde29d1ac
status: experimental
logsource:
    category: network_connection
    product: windows
detection:
    selection:
        EventType: 'network_connection'
        Protocol: 'tcp'
        DestinationIp|exists: true
    filter_internal:
        DestinationIp|cidr:
            - '10.0.0.0/8'
            - '172.16.0.0/12'
            - '192.168.0.0/16'
    condition: selection and not filter_internal
level: medium
```

```hint
Pozitif seçim tür, protokol ve alan varlığı; özel aralıklar ayrı filtre.
```
:::
