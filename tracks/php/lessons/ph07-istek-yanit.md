---
id: ph07
title: İstek, Yanıt ve Güvenli Çıktı
summary: $_GET ve $_POST, ?? ile varsayılan, htmlspecialchars ile çıktıyı kaçırmak, json_encode'un varsayılanları, hazırlanmış sorgular ve küçük bir uç noktayı okumak.
kazanim: ZCPE 3.2, ZCPE 4.1, ZCPE 4.3, ZCPE 6.1, ZCPE 6.2
---

::: anlat İstekten yanıta
Bir PHP betiği her HTTP isteğinde baştan çalışır. İstek verisi hazır dizilerde gelir:

| Dizi | İçeriği |
|---|---|
| `$_GET` | adresteki parametreler: `durum.php?sunucu=web01` → `$_GET["sunucu"]` |
| `$_POST` | form gövdesi |
| `$_SERVER` | istek bilgileri: `$_SERVER["REQUEST_METHOD"]`, `$_SERVER["REMOTE_ADDR"]` |

Olmayan bir anahtarı okumak uyarı üretir; `??` işleci "yoksa şunu kullan" der: `$sayfa = $_GET["sayfa"] ?? 1;`.

```php
<?php
header("Content-Type: application/json; charset=utf-8");
$ad = $_GET["sunucu"] ?? "";
if ($ad === "") {
    http_response_code(400);
    echo json_encode(["hata" => "sunucu parametresi gerekli"]);
    exit;
}
```

### Çıktıyı kaçırmak
> [!GÜVENLİK]
> İstekten gelen bir değeri HTML'e olduğu gibi yazmak, o değerin sayfada kod olarak yorumlanmasına izin vermektir. PHP'de HTML'e yazılan her dış değer `htmlspecialchars()`'tan geçirilir. Veritabanı sorgularında değerler sorgu metnine birleştirilmez; **hazırlanmış sorgularla** parametre olarak verilir:
>
> ```php
> $st = $pdo->prepare("SELECT cpu FROM sunucular WHERE ad = ?");
> $st->execute([$ad]);
> ```
>
> Kod okurken `echo $_GET[...]` ya da `"... WHERE ad = '$ad'"` gibi doğrudan birleştirmeler, düzeltilmesi gereken yerlerdir.

`htmlspecialchars` PHP 8.1'den beri varsayılan olarak beş karakteri çevirir: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`, `'` → `&#039;`.

### json_encode'un varsayılanları
- Boşluksuz yazar: `{"a":1,"b":true}`
- ASCII dışındaki karakterleri `\u` kaçışıyla yazar: `"yoğun"` → `"yoğun"` (`JSON_UNESCAPED_UNICODE` bayrağı bunu kapatır)
- `/` karakterini `\/` olarak yazar (`JSON_UNESCAPED_SLASHES` kapatır)
:::

::: tahmin
İstek parametresi olmadan, PHP 8.1+ ile çıktı:

```php
<?php
$q = "<b>web01</b> & \"db\"";
echo htmlspecialchars($q), "\n";
echo json_encode(["ad" => "web01", "cpu" => 72, "aktif" => true]), "\n";
echo $_GET["sayfa"] ?? 1, "\n";
```

```gercek
&lt;b&gt;web01&lt;/b&gt; &amp; &quot;db&quot;
{"ad":"web01","cpu":72,"aktif":true}
1
```

???

`&lt;b&gt;web01&lt;/b&gt; &amp; &quot;db&quot;`, `{"ad":"web01","cpu":72,"aktif":true}` ve `1`. İlk satırda açılı parantezler, `&` ve çift tırnaklar HTML karşılıklarına çevrilir; tarayıcı bunu kalın yazı değil düz metin olarak gösterir. `json_encode` diziyi boşluksuz bir JSON nesnesine çevirir; `true` JSON'da da `true`'dur. İstekte `sayfa` parametresi olmadığı için `??` varsayılan değer olan 1'i verir.
:::

::: gorev htmlspecialchars
PHP 8.1+'daki `htmlspecialchars($s)` varsayılan davranışını Python'da `html_kacir(s)` olarak yaz.

```starter
def html_kacir(s):
    return s.replace("<", "&lt;").replace(">", "&gt;")
```

```test
need("html_kacir")
eq(html_kacir('<a href="x">'), "&lt;a href=&quot;x&quot;&gt;", "etiket ve çift tırnak")
eq(html_kacir("Ece'nin & Can'ın"), "Ece&#039;nin &amp; Can&#039;ın", "tek tırnak &#039; olur")
eq(html_kacir("&amp;"), "&amp;amp;", "& her zaman çevrilir")
eq(html_kacir("düz metin"), "düz metin", "değişmeyen metin")
```

```solution
def html_kacir(s):
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#039;"))
```

```hint
`&` ilk çevrilmeli. Tek tırnak PHP'de `&#039;` olur (sıfırlı).
```
:::

::: gorev Durum uç noktası
Aşağıdaki PHP fonksiyonu bir uç noktanın yanıtını hesaplıyor. Python'a `durum_yaniti(get, sunucular)` olarak çevir: `(durum_kodu, govde)` çiftini döndürsün; gövde, PHP'nin `json_encode` varsayılanlarıyla **birebir** aynı metin olsun.

```php
function durum_yaniti(array $get, array $sunucular): array {
    $ad = $get["sunucu"] ?? "";
    if ($ad === "") {
        return [400, json_encode(["hata" => "sunucu parametresi gerekli"])];
    }
    if (!array_key_exists($ad, $sunucular)) {
        return [404, json_encode(["hata" => "sunucu bulunamadı"])];
    }
    $cpu = $sunucular[$ad];
    $durum = $cpu >= 80 ? "yoğun" : "normal";
    return [200, json_encode(["sunucu" => $ad, "cpu" => $cpu, "durum" => $durum])];
}
```

```starter
import json

def durum_yaniti(get, sunucular):
    ad = get["sunucu"]
    cpu = sunucular[ad]
    return 200, json.dumps({"sunucu": ad, "cpu": cpu, "durum": "normal"})
```

```test
need("durum_yaniti")
S = {"web01": 72, "db01": 91}
eq(durum_yaniti({"sunucu": "web01"}, S), (200, '{"sunucu":"web01","cpu":72,"durum":"normal"}'), "web01 normal")
eq(durum_yaniti({"sunucu": "db01"}, S), (200, '{"sunucu":"db01","cpu":91,"durum":"yo\\u011fun"}'), "db01 yoğun (\\u kaçışıyla)")
eq(durum_yaniti({}, S), (400, '{"hata":"sunucu parametresi gerekli"}'), "parametre yok → 400")
eq(durum_yaniti({"sunucu": ""}, S), (400, '{"hata":"sunucu parametresi gerekli"}'), "boş parametre → 400")
eq(durum_yaniti({"sunucu": "x"}, S), (404, '{"hata":"sunucu bulunamad\\u0131"}'), "bilinmeyen sunucu → 404")
eq(durum_yaniti({"sunucu": "app01"}, {"app01": 80}), (200, '{"sunucu":"app01","cpu":80,"durum":"yo\\u011fun"}'), "tam 80 → yoğun")
```

```solution
import json

def _json(veri):
    return json.dumps(veri, separators=(",", ":"))       # PHP gibi boşluksuz; ensure_ascii varsayılan: \u kaçışı

def durum_yaniti(get, sunucular):
    ad = get.get("sunucu", "")
    if ad == "":
        return 400, _json({"hata": "sunucu parametresi gerekli"})
    if ad not in sunucular:
        return 404, _json({"hata": "sunucu bulunamadı"})
    cpu = sunucular[ad]
    durum = "yoğun" if cpu >= 80 else "normal"
    return 200, _json({"sunucu": ad, "cpu": cpu, "durum": durum})
```

```hint
`$get["sunucu"] ?? ""` Python'da `get.get("sunucu", "")`.
```

```hint
Python'un `json.dumps`'ı varsayılan olarak `", "` ve `": "` ile boşluk koyar; PHP koymaz: `separators=(",", ":")`. ASCII dışı karakterleri iki dil de varsayılan olarak `\u` ile kaçırır.
```
:::
