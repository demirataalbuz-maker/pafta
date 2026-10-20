---
id: ph11
title: Proje · Bir API Uç Noktasını Okumak
summary: Bilet oluşturan bir PHP uç noktasını satır satır okuyup aynı davranışı Python'da kurmak; ham gövdeyi JSON olarak ayrıştırmak, tür ve uzunluk doğrulaması, izin listesiyle sıkı karşılaştırma, parametreli INSERT ve durum koduyla JSON yanıt.
---

::: anlat Proje tanımı
Aşağıdaki PHP betiği, bir bilet sisteminin `POST /api/bilet` uç noktasıdır. Görevin onu **okumak** ve aynı davranışı Python'da adım adım kurmak. Gerçek bir kod incelemesinde de yaptığın şey budur: her satırın neyi kabul edip neyi reddettiğini çıkarmak.

```php
<?php
declare(strict_types=1);

function yanit(int $kod, array $govde): never {
    http_response_code($kod);
    header("Content-Type: application/json; charset=utf-8");
    echo json_encode($govde, JSON_UNESCAPED_UNICODE);
    exit;
}

$girdi = json_decode(file_get_contents("php://input"), true);      // ham istek gövdesi
if (!is_array($girdi)) {
    yanit(400, ["hata" => "geçersiz JSON"]);
}

$baslik = $girdi["baslik"] ?? "";
if (!is_string($baslik)) {
    yanit(422, ["hata" => "başlık metin olmalı"]);
}
$baslik = trim($baslik);
if ($baslik === "" || mb_strlen($baslik) > 80) {
    yanit(422, ["hata" => "başlık 1-80 karakter olmalı"]);
}

$oncelik = $girdi["oncelik"] ?? "orta";
if (!in_array($oncelik, ["düşük", "orta", "yüksek", "kritik"], true)) {
    yanit(422, ["hata" => "geçersiz öncelik"]);
}

$pdo = new PDO("sqlite:" . __DIR__ . "/bilet.db");
$st = $pdo->prepare("INSERT INTO biletler (baslik, oncelik) VALUES (?, ?)");
$st->execute([$baslik, $oncelik]);

yanit(201, ["id" => (int)$pdo->lastInsertId(), "baslik" => $baslik, "oncelik" => $oncelik]);
```

### Okurken çıkardıkların
| Satır | Davranış |
|---|---|
| `json_decode(..., true)` | bozuk JSON, `null` ya da tek bir sayı gelirse dizi değildir → 400 |
| `$girdi["baslik"] ?? ""` | alan yoksa boş metin (ardından 422) |
| `is_string` | `"baslik": 42` gibi bir sayı reddedilir |
| `trim` + `mb_strlen` | baştaki ve sondaki boşluklar atılır; uzunluk **karakter** cinsinden (PH04) |
| `in_array(..., true)` | **sıkı** karşılaştırma: `"KRITIK"` ya da `0` kabul edilmez (PH03) |
| `prepare` + `execute` | değerler sorgudan ayrı gider (PH08) |
| `JSON_UNESCAPED_UNICODE` | Türkçe karakterler `ü` gibi kaçırılmadan yazılır |

> [!İPUCU]
> `in_array`'ın üçüncü argümanı (`true`) unutulursa karşılaştırma gevşek olur. PHP 8'de çoğu durumda yine doğru sonuç çıkar ama `true` gibi bir değer, boş olmayan her metne gevşek olarak eşittir: `in_array(true, ["orta"])` doğrudur. İzin listesi denetimlerinde `true` olmadan yazılmış bir `in_array` gördüğünde dur ve düşün.
:::

::: tahmin
PHP 8 ile çıktı:

```php
<?php
$girdi = json_decode('{"baslik":"  Disk dolu  ","oncelik":"KRITIK"}', true);
$baslik = trim((string)($girdi["baslik"] ?? ""));
$oncelik = $girdi["oncelik"] ?? "orta";
var_dump($baslik, in_array($oncelik, ["düşük", "orta", "yüksek", "kritik"], true));
```

```gercek
string(9) "Disk dolu"
bool(false)
```

???

`string(9) "Disk dolu"`: `trim` baştaki ve sondaki boşlukları atar; 9 bayt kalır. `bool(false)`: sıkı karşılaştırma büyük-küçük harfe duyarlıdır, `"KRITIK"` listedeki `"kritik"` ile aynı değildir; uç nokta bu isteği 422 ile reddeder.
:::

::: gorev 1 · Doğrulama
`dogrula(girdi)` fonksiyonunu yaz. `girdi`, JSON'dan çözülmüş **herhangi** bir Python değeridir. PHP betiğindeki denetimleri aynı sırayla uygulasın ve `(kod, hata, temiz)` döndürsün:

- `girdi` sözlük değilse: `(400, "geçersiz JSON", None)`
- başlık metin değilse: `(422, "başlık metin olmalı", None)`
- boşluklar atıldıktan sonra başlık boşsa ya da 80 karakterden uzunsa: `(422, "başlık 1-80 karakter olmalı", None)`
- öncelik izin listesinde değilse: `(422, "geçersiz öncelik", None)`
- geçerliyse: `(200, None, {"baslik": ..., "oncelik": ...})`

```starter
def dogrula(girdi):
    return 200, None, {"baslik": girdi.get("baslik"), "oncelik": girdi.get("oncelik", "orta")}
```

```test
need("dogrula")
eq(dogrula({"baslik": "  Disk dolu  ", "oncelik": "kritik"}), (200, None, {"baslik": "Disk dolu", "oncelik": "kritik"}), "geçerli")
eq(dogrula({"baslik": "Yedek gecikti"}), (200, None, {"baslik": "Yedek gecikti", "oncelik": "orta"}), "varsayılan öncelik")
eq(dogrula([1, 2]), (400, "geçersiz JSON", None), "dizi")
eq(dogrula(None), (400, "geçersiz JSON", None), "null")
eq(dogrula({"baslik": 42}), (422, "başlık metin olmalı", None), "sayı başlık")
eq(dogrula({"oncelik": "orta"}), (422, "başlık 1-80 karakter olmalı", None), "başlık yok")
eq(dogrula({"baslik": "   "}), (422, "başlık 1-80 karakter olmalı", None), "yalnızca boşluk")
eq(dogrula({"baslik": "ş" * 80}), (200, None, {"baslik": "ş" * 80, "oncelik": "orta"}), "80 karakter (160 bayt) geçerli")
eq(dogrula({"baslik": "x" * 81}), (422, "başlık 1-80 karakter olmalı", None), "81 karakter")
eq(dogrula({"baslik": "Disk", "oncelik": "KRITIK"}), (422, "geçersiz öncelik", None), "büyük harf")
eq(dogrula({"baslik": "Disk", "oncelik": True}), (422, "geçersiz öncelik", None), "bool öncelik")
```

```solution
IZINLI = ["düşük", "orta", "yüksek", "kritik"]


def dogrula(girdi):
    if not isinstance(girdi, dict):
        return 400, "geçersiz JSON", None
    baslik = girdi.get("baslik", "")
    if not isinstance(baslik, str):
        return 422, "başlık metin olmalı", None
    baslik = baslik.strip()
    if baslik == "" or len(baslik) > 80:
        return 422, "başlık 1-80 karakter olmalı", None
    oncelik = girdi.get("oncelik", "orta")
    if not (isinstance(oncelik, str) and oncelik in IZINLI):
        return 422, "geçersiz öncelik", None
    return 200, None, {"baslik": baslik, "oncelik": oncelik}
```

```hint
Sıra PHP'deki gibi: tür (400), başlık türü, başlık uzunluğu, öncelik. `mb_strlen` karakter saydığı için Python'da `len(metin)` doğrudur.
```

```hint
Sıkı `in_array` için önce türü denetle: `isinstance(oncelik, str) and oncelik in IZINLI`. Python'da `True in ["orta"]` zaten yanlıştır ama türü açıkça denetlemek PHP koduyla birebir eşleşir.
```
:::

::: gorev 2 · Kaydet
`kaydet(db, girdi)` fonksiyonunu yaz: önce `dogrula`; geçersizse `(kod, {"hata": mesaj})` döndürsün. Geçerliyse `biletler` tablosuna **parametreli** bir INSERT yapsın ve `(201, {"id": ..., "baslik": ..., "oncelik": ...})` döndürsün (`id`: eklenen satırın kimliği). Önceki görevin `dogrula` fonksiyonunu bu kodda da tanımla.

```starter
def kaydet(db, girdi):
    db.execute(f"INSERT INTO biletler (baslik, oncelik) VALUES ('{girdi['baslik']}', '{girdi.get('oncelik', 'orta')}')")
    return 201, {}
```

```test
import sqlite3
need("kaydet")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE biletler (id INTEGER PRIMARY KEY, baslik TEXT NOT NULL, oncelik TEXT NOT NULL)")
eq(kaydet(db, {"baslik": "Disk dolu", "oncelik": "kritik"}), (201, {"id": 1, "baslik": "Disk dolu", "oncelik": "kritik"}), "ilk bilet")
eq(kaydet(db, {"baslik": "Ali'nin bilgisayarı"}), (201, {"id": 2, "baslik": "Ali'nin bilgisayarı", "oncelik": "orta"}), "kesme işaretli başlık")
eq(kaydet(db, {"baslik": ""}), (422, {"hata": "başlık 1-80 karakter olmalı"}), "geçersiz istek kaydedilmez")
eq(db.execute("SELECT COUNT(*) FROM biletler").fetchone()[0], 2, "tabloda iki bilet")
eq(kaydet(db, {"baslik": "a" * 80})[0], 201, "tam 80 karakter kabul")
eq(kaydet(db, {"baslik": "a" * 81}), (422, {"hata": "başlık 1-80 karakter olmalı"}), "81 karakter ret")
eq(kaydet(db, {"baslik": "Disk", "oncelik": "acil"}), (422, {"hata": "geçersiz öncelik"}), "geçersiz öncelik kaydedilmez")
```

```solution
IZINLI = ["düşük", "orta", "yüksek", "kritik"]


def dogrula(girdi):
    if not isinstance(girdi, dict):
        return 400, "geçersiz JSON", None
    baslik = girdi.get("baslik", "")
    if not isinstance(baslik, str):
        return 422, "başlık metin olmalı", None
    baslik = baslik.strip()
    if baslik == "" or len(baslik) > 80:
        return 422, "başlık 1-80 karakter olmalı", None
    oncelik = girdi.get("oncelik", "orta")
    if not (isinstance(oncelik, str) and oncelik in IZINLI):
        return 422, "geçersiz öncelik", None
    return 200, None, {"baslik": baslik, "oncelik": oncelik}


def kaydet(db, girdi):
    kod, hata, temiz = dogrula(girdi)
    if hata:
        return kod, {"hata": hata}
    imlec = db.execute("INSERT INTO biletler (baslik, oncelik) VALUES (?, ?)", (temiz["baslik"], temiz["oncelik"]))
    db.commit()
    return 201, {"id": imlec.lastrowid, "baslik": temiz["baslik"], "oncelik": temiz["oncelik"]}
```

```hint
Başlangıç kodu doğrulama yapmıyor ve değerleri sorgu metnine ekliyor; kesme işaretli başlık sorguyu bozar. `?` yer tutucuları kullan.
```

```hint
Eklenen satırın kimliği: `imlec = db.execute(...)` ve `imlec.lastrowid` (PDO'daki `lastInsertId()`).
```
:::

::: gorev 3 · Uçtan uca
`istek_isle(db, govde_metni)` fonksiyonunu yaz: ham istek gövdesini (metin) alsın, JSON olarak çözmeyi denesin (bozuksa `girdi` `None` sayılsın, PHP'deki gibi), `kaydet`'i çağırsın ve `(kod, json_metni)` döndürsün. JSON metni PHP'deki `json_encode(..., JSON_UNESCAPED_UNICODE)` gibi olsun: boşluksuz ve Türkçe karakterler kaçırılmadan.

```starter
import json


def istek_isle(db, govde_metni):
    return 200, json.dumps(json.loads(govde_metni))
```

```test
import sqlite3
need("istek_isle")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE biletler (id INTEGER PRIMARY KEY, baslik TEXT NOT NULL, oncelik TEXT NOT NULL)")
eq(istek_isle(db, '{"baslik": "Güç kaynağı arızası", "oncelik": "yüksek"}'),
   (201, '{"id":1,"baslik":"Güç kaynağı arızası","oncelik":"yüksek"}'), "başarılı istek")
eq(istek_isle(db, "{bozuk"), (400, '{"hata":"geçersiz JSON"}'), "bozuk gövde")
eq(istek_isle(db, ""), (400, '{"hata":"geçersiz JSON"}'), "boş gövde")
eq(istek_isle(db, '{"baslik": "Disk", "oncelik": "acil"}'), (422, '{"hata":"geçersiz öncelik"}'), "geçersiz öncelik")
eq(istek_isle(db, '{"baslik": "' + "b" * 80 + '"}')[0], 201, "tam 80 karakter kabul")
eq(istek_isle(db, '{"baslik": "' + "b" * 81 + '"}'), (422, '{"hata":"başlık 1-80 karakter olmalı"}'), "81 karakter ret")
```

```solution
import json

IZINLI = ["düşük", "orta", "yüksek", "kritik"]


def dogrula(girdi):
    if not isinstance(girdi, dict):
        return 400, "geçersiz JSON", None
    baslik = girdi.get("baslik", "")
    if not isinstance(baslik, str):
        return 422, "başlık metin olmalı", None
    baslik = baslik.strip()
    if baslik == "" or len(baslik) > 80:
        return 422, "başlık 1-80 karakter olmalı", None
    oncelik = girdi.get("oncelik", "orta")
    if not (isinstance(oncelik, str) and oncelik in IZINLI):
        return 422, "geçersiz öncelik", None
    return 200, None, {"baslik": baslik, "oncelik": oncelik}


def kaydet(db, girdi):
    kod, hata, temiz = dogrula(girdi)
    if hata:
        return kod, {"hata": hata}
    imlec = db.execute("INSERT INTO biletler (baslik, oncelik) VALUES (?, ?)", (temiz["baslik"], temiz["oncelik"]))
    db.commit()
    return 201, {"id": imlec.lastrowid, "baslik": temiz["baslik"], "oncelik": temiz["oncelik"]}


def istek_isle(db, govde_metni):
    try:
        girdi = json.loads(govde_metni)
    except json.JSONDecodeError:
        girdi = None
    kod, govde = kaydet(db, girdi)
    return kod, json.dumps(govde, ensure_ascii=False, separators=(",", ":"))
```

```hint
PHP'nin `json_decode`'u bozuk metinde `null` döndürür; Python'da `JSONDecodeError`'ı yakalayıp `girdi = None` yap. `dogrula` gerisini halleder.
```

```hint
`json_encode(..., JSON_UNESCAPED_UNICODE)` karşılığı: `json.dumps(govde, ensure_ascii=False, separators=(",", ":"))`.
```
:::
