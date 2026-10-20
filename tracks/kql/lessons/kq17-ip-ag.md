---
id: kq17
title: IP Adresleri ve Ağlar
summary: IPv4 adreslerini metin değil adres olarak ele almak; ipv4_is_private ile iç ve dış trafik, ipv4_is_in_range ile CIDR aralıkları, parse_ipv4 ile doğru sıralama, /24 alt ağlarına göre özet ve adlandırılmış ağ listesiyle aralık eşleştirme.
---

::: anlat Adres, metin değildir
Günlüklerde IP adresleri metin olarak durur ve metin gibi davranır. Bu da yanıltır:

```kql
datatable(ip:string)["10.0.0.9", "10.0.0.10", "10.0.0.100"]
| sort by ip asc
```

Metin sıralamasında `10.0.0.10`, `10.0.0.9`'dan önce gelir. Adresi bir sayıya çeviren `parse_ipv4` doğru sırayı verir:

```kql
datatable(ip:string)["10.0.0.9", "10.0.0.10", "10.0.0.100"]
| sort by parse_ipv4(ip) asc
```

| Fonksiyon | Döndürdüğü |
|---|---|
| `ipv4_is_private(ip)` | özel (RFC 1918) adres mi: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` |
| `ipv4_is_in_range(ip, "10.0.0.0/22")` | adres bu CIDR aralığında mı |
| `parse_ipv4(ip)` | adresin sayı karşılığı; sıralama ve karşılaştırma için |

### CIDR gösterimi
`10.0.0.0/22`'deki 22, adresin ilk 22 bitinin sabit olduğunu söyler. Geriye 10 bit, yani 1024 adres kalır: `10.0.0.0` ile `10.0.3.255` arası. Sık görülenler:

| Önek | Adres sayısı | Örnek aralık |
|---|---|---|
| `/32` | 1 | tek bir adres |
| `/24` | 256 | `10.0.1.0` – `10.0.1.255` |
| `/23` | 512 | `10.0.2.0` – `10.0.3.255` |
| `/16` | 65 536 | `192.168.0.0` – `192.168.255.255` |
| `/12` | ~1 milyon | `172.16.0.0` – `172.31.255.255` |

> [!NOT]
> Bu yolun verisindeki dış adresler (`203.0.113.x`, `198.51.100.x`) RFC 5737'nin **belgeleme** için ayırdığı aralıklardandır; gerçek internette hiçbir cihaza ait değildir. Örnek ve eğitim verisinde gerçek adres yerine bunları kullanmak iyi bir alışkanlıktır.
:::

::: anlat Ağlara göre özetlemek
**İç ve dış trafik**: istemciyi tek bir koşulla iki sınıfa ayır:

```kql
istekler
| extend ag = iff(ipv4_is_private(istemci), "iç", "dış")
| summarize istek = count(), istemci_sayisi = dcount(istemci) by ag
```

**Alt ağ özeti**: adresin ilk üç oktetini çıkarıp `/24` ağlarına göre grupla. Tek tek adreslere bakmak yerine "hangi ofis, hangi segment" sorusunu cevaplar.

**Adlandırılmış ağ listesi**: elinde `aralık → ad` diye bir envanter varsa, her adresi ait olduğu aralıkla eşleştirmek bir **aralık birleştirmesidir**. Eşitlik değil, "içinde mi" sorusudur; doğrudan `join ... on` ile yapılamaz. Küçük bir liste için yöntem: iki tarafa da sabit bir anahtar ekle, her adresi her aralıkla eşleştir, sonra `ipv4_is_in_range` ile süz:

```kql
let aglar = datatable(aralik:string, ag_adi:string)["10.0.1.0/24", "ofis-ist", "10.0.2.0/23", "ofis-izm"];
istekler
| extend k = 1
| join kind=inner (aglar | extend k = 1) on k
| where ipv4_is_in_range(istemci, aralik)
| project zaman, istemci, ag_adi
| take 5
```

> [!DERİN]
> Bu "sabit anahtarla çapraz birleştirme" satır sayısını çarpar: 1 milyon istek × 50 ağ, 50 milyon ara satır demektir. Büyük listelerde Kusto'nun buna özel `evaluate ipv4_lookup(...)` eklentisi aralıkları dizinleyerek aynı işi çok daha ucuza yapar. Pafta tezgahında eklenti yok; yöntemin mantığını görmek için çapraz birleştirme yeterli.
:::

::: tahmin
Tek satır, üç değer:

```kql
print a = ipv4_is_private("172.16.5.9"), b = ipv4_is_private("172.32.0.1"), c = ipv4_is_in_range("10.0.3.4", "10.0.0.0/22")
```

???

`true|false|true`. `172.16.0.0/12` aralığı `172.16.0.0` ile `172.31.255.255` arasıdır: `172.16.5.9` içinde, `172.32.0.1` dışında. `/22` aralığı 1024 adres kapsar: `10.0.0.0` ile `10.0.3.255` arası, yani `10.0.3.4` içinde.
:::

::: gorev İç ve dış trafik
İstekleri istemcinin adresine göre `"iç"` (özel adres) ve `"dış"` diye sınıflandır ve her sınıf için istek sayısını ve farklı istemci sayısını getir: `ag`, `istek`, `istemci_sayisi`; sınıfa göre artan.

```starter
istekler
| summarize istek = count() by istemci
```

```test
eq(sutunlar, ["ag", "istek", "istemci_sayisi"], "sütunlar")
eq(sonuc, [("dış", 6, 3), ("iç", 20, 6)], "iki sınıf")
ok(kullanir("ipv4_is_private"), "ipv4_is_private kullan")
```

```solution
istekler
| extend ag = iff(ipv4_is_private(istemci), "iç", "dış")
| summarize istek = count(), istemci_sayisi = dcount(istemci) by ag
| sort by ag asc
```

```hint
`iff(ipv4_is_private(istemci), "iç", "dış")` ile sınıfı bir sütuna koy, sonra `summarize ... by ag`.
```
:::

::: gorev /24 alt ağları
**Özel** adreslerden gelen istekleri `/24` alt ağlarına göre say. Alt ağ `10.0.1.0/24` biçiminde yazılsın: `alt_ag`, `istek`; çoktan aza, eşitlikte alt ağa göre artan.

```starter
istekler
| where ipv4_is_private(istemci)
| summarize istek = count() by istemci
```

```test
eq(sutunlar, ["alt_ag", "istek"], "sütunlar")
eq(sonuc, [("10.0.1.0/24", 10), ("10.0.2.0/24", 4), ("10.0.3.0/24", 4), ("172.16.5.0/24", 1), ("192.168.10.0/24", 1)], "beş alt ağ")
```

```solution
istekler
| where ipv4_is_private(istemci)
| extend alt_ag = strcat(extract(@"^(\d+\.\d+\.\d+)\.", 1, istemci), ".0/24")
| summarize istek = count() by alt_ag
| sort by istek desc, alt_ag asc
```

```hint
İlk üç okteti çıkar: `extract(@"^(\d+\.\d+\.\d+)\.", 1, istemci)`.
```

```hint
Sonuna `.0/24` ekle: `strcat(..., ".0/24")`.
```
:::

::: gorev Ağ envanteriyle eşleştir
Aşağıdaki ağ envanterini bir `datatable` olarak tanımla ve **özel** adreslerden gelen istekleri ait oldukları ağın adına göre say: `ag_adi`, `istek`; çoktan aza, eşitlikte ada göre.

| aralik | ag_adi |
|---|---|
| `10.0.1.0/24` | ofis-ist |
| `10.0.2.0/23` | ofis-izm |
| `172.16.0.0/12` | izleme |
| `192.168.0.0/16` | vpn |

```starter
istekler
| where ipv4_is_private(istemci)
| summarize istek = count() by istemci
```

```test
eq(sutunlar, ["ag_adi", "istek"], "sütunlar")
eq(sonuc, [("ofis-ist", 10), ("ofis-izm", 8), ("izleme", 1), ("vpn", 1)], "dört ağ; 10.0.3.4 de /23 içinde")
ok(kullanir("ipv4_is_in_range"), "aralığı ipv4_is_in_range ile denetle")
```

```solution
let aglar = datatable(aralik:string, ag_adi:string)[
    "10.0.1.0/24", "ofis-ist",
    "10.0.2.0/23", "ofis-izm",
    "172.16.0.0/12", "izleme",
    "192.168.0.0/16", "vpn"
];
istekler
| where ipv4_is_private(istemci)
| extend k = 1
| join kind=inner (aglar | extend k = 1) on k
| where ipv4_is_in_range(istemci, aralik)
| summarize istek = count() by ag_adi
| sort by istek desc, ag_adi asc
```

```hint
Aralık eşleştirmesi için iki tarafa da `extend k = 1` ekleyip `join kind=inner ... on k` ile çapraz birleştir.
```

```hint
Sonra `where ipv4_is_in_range(istemci, aralik)` ve `summarize istek = count() by ag_adi`. `10.0.2.0/23` aralığı `10.0.3.x`'i de kapsar.
```
:::
