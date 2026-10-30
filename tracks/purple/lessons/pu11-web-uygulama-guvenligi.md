---
id: pu11
title: Web Uygulama Güvenliği · Kanıtla ve Savun
summary: Yalnız 127.0.0.1 üzerindeki resetlenebilir sentetik laboratuvarla IDOR ve API nesne yetkilendirmesi; gerçek HTTP durumları ile kalıcı durum kanıtı; bellek içi SQLite'ta parametreli sorgu ve sıralama allowlist'i; textContent/innerHTML farkı, opt-in gerçek tarayıcı canary'si ve güvenli DOM modeli; komut çalıştırmadan allowlist + argv planı.
timeout: 20
---

::: anlat Saldırı iddiası değil, savunma kanıtı
Bir web bulgusu "çalışıyor gibi" görünmesiyle kanıtlanmaz. **IDOR**'da nesne kimliğini değiştirmek isteği göndermek değildir; sunucunun başka kullanıcının nesnesine erişime izin vermesi gerekir. Savunmada ise her istekte hem oturum hem **nesne sahipliği** denetlenir. API yanıtındaki `200`, `401`, `403`, `404` gerçek HTTP durumlarıdır; yazma denemesinden sonra kaydın gerçekten değişip değişmediğine ayrıca bakılır.

| Konu | Bu dersteki savunma | Yanıltıcı kısayol |
|---|---|---|
| IDOR / API | Oturum + nesne sahibi; reddedilen yazmada durum değişmemeli | Kimliği gizlemek ya da yalnız arayüzde düğmeyi kapatmak |
| SQLi | Değeri `?` parametresiyle bağlamak; sıralama adını allowlist ile seçmek | Tırnak kaçamaklarını elle temizlemek |
| XSS | Güvenilmeyen metni `textContent` ile DOM'a koymak | Güvenilmeyen metni `innerHTML`e basmak |
| Komut enjeksiyonu | İşlem ve hedefi allowlist'le seçip argv öğelerini ayrı tutmak | Kullanıcı metnini kabuk komutuna birleştirmek |

```python norun
# Parametre SQL metninin parçası değil, ayrı bir değerdir.
db.execute("SELECT id FROM notlar WHERE govde = ?", (metin,))
# Güvenli DOM sink'i metni markup olarak derlemez.
element.textContent = metin
# Bu bir plandır; çalıştırılmaz.
argv = ["pafta-durum", "--format", "json", "--hedef", "web01"]
```

> [!NOT] Laboratuvar sınırı
> `web_security_lab.py` mevcut HTTP labından bağımsızdır ve yalnız **127.0.0.1** üzerinde dinler. Hesaplar `ayse` ve `can`, parola `pafta-demo`; bütün kayıtlar sentetiktir. Reset veriyi ve oturumları başlangıca döndürür. SQL yalnız bellek içi SQLite'tır. Dış ağ, cookie çalma, exfiltration ve reverse shell yoktur. Komut görevindeki program adları hayalidir ve **hiçbir komut çalıştırılmaz**.

Gerçek tarayıcı deneyi ayrıca opt-in'dir: yalnız `PAFTA_WEB_BROWSER=1` verildiğinde kurulu Edge/Chromium ile `window.__paftaCanary` ölçülür. Canary tek bir JavaScript atamasıdır; veri okumaz veya göndermez. Tarayıcı yoksa ya da opt-in yoksa test açıkça **skip** olur; bu, güvenli DOM modeli görevini atlamak anlamına gelmez.
:::

::: tahmin
Ayşe oturumuyla kendi 1 numaralı belgesini okuma, Can'ın 2 numaralı belgesini okuma ve oturumsuz 1 numaralı belgeyi okuma istekleri hangi gerçek HTTP durumlarını verir?

```python
from web_security_lab import WebSecurityLab

with WebSecurityLab() as lab:
    ayse = lab.login("ayse")
    print(lab.request("GET", "/api/documents/1", cookie=ayse)["status"],
          lab.request("GET", "/api/documents/2", cookie=ayse)["status"],
          lab.request("GET", "/api/documents/1")["status"])
```

???

**`200 403 401`**

```
200 403 401
```

Oturum kimliği doğru olsa da nesne Ayşe'ye ait değilse ikinci istek `403` olur. Cookie hiç yoksa kimlik doğrulama nesne denetiminden önce gerekir ve `401` döner. Bu üç sonuç sunucu üzerinden yapılan gerçek TCP HTTP isteklerinden gelir.

```setup
import sys
from pathlib import Path
_sandbox = str(Path(sys.modules["__main__"].__file__).resolve().parent)
if _sandbox not in sys.path:
    sys.path.insert(0, _sandbox)
```
:::

::: gorev 1 · IDOR ve API: durum kodu ile kalıcı durumu birlikte ölç
`incele(lab)` fonksiyonunu yaz. Verilen `WebSecurityLab` üzerinde sırayla:

1. Ayşe oturumu aç; oturumsuz `GET /api/documents/1` isteği yap.
2. Ayşe ile kendi belgesini `GET` ile oku; Can'ın 2 numaralı belgesini `GET` ile okumayı dene.
3. Ayşe'nin 1 numaralı belgesini `PATCH` ile başlığı **`PU05 kalıcı`** olacak şekilde değiştir.
4. Ayşe oturumuyla Can'ın belgesine `PATCH {"title": "değişmemeli"}` gönder.

Şu sözlüğü döndür: `{"oturumsuz": ..., "kendi_oku": ..., "baskasini_oku": ..., "kendi_yaz": ..., "baskasini_yaz": ..., "kaydedilen": ..., "revizyon_artisi": ...}`. Durumlar ilgili gerçek yanıtlardan, `kaydedilen` işlem sonrası `lab.snapshot()["documents"][1]["title"]` değerinden, revizyon artışı da önce/sonra snapshot farkından gelsin.

```starter
def incele(lab):
    ayse = lab.login("ayse")
    kendi = lab.request("GET", "/api/documents/1", cookie=ayse)
    return {"oturumsuz": 200, "kendi_oku": kendi["status"],
            "baskasini_oku": 200, "kendi_yaz": 200, "baskasini_yaz": 200,
            "kaydedilen": "değişmedi", "revizyon_artisi": 0}
```

```test
need("incele")
from web_security_lab import WebSecurityLab
with WebSecurityLab() as lab:
    sonuc = incele(lab)
    eq(sonuc, {"oturumsuz": 401, "kendi_oku": 200, "baskasini_oku": 403,
               "kendi_yaz": 200, "baskasini_yaz": 403, "kaydedilen": "PU05 kalıcı",
               "revizyon_artisi": 1},
       "gerçek HTTP: oturumsuz 401, başkasının nesnesi 403; yalnız sahip PATCH'i 200")
    son = lab.snapshot()
    eq(son["documents"][1]["title"], "PU05 kalıcı", "başarılı API yazması sunucuda kalıcı")
    eq(son["documents"][2]["title"], "Can taslağı", "403 dönen yazma Can'ın kaydını değiştirmedi")
    eq(son["revision"], 1, "yalnız başarılı bir yazma revizyonu artırdı")
```

```solution
def incele(lab):
    once = lab.snapshot()
    ayse = lab.login("ayse")
    oturumsuz = lab.request("GET", "/api/documents/1")
    kendi = lab.request("GET", "/api/documents/1", cookie=ayse)
    baska_oku = lab.request("GET", "/api/documents/2", cookie=ayse)
    kendi_yaz = lab.request("PATCH", "/api/documents/1", {"title": "PU05 kalıcı"}, cookie=ayse)
    baska_yaz = lab.request("PATCH", "/api/documents/2", {"title": "değişmemeli"}, cookie=ayse)
    sonra = lab.snapshot()
    return {"oturumsuz": oturumsuz["status"], "kendi_oku": kendi["status"],
            "baskasini_oku": baska_oku["status"], "kendi_yaz": kendi_yaz["status"],
            "baskasini_yaz": baska_yaz["status"],
            "kaydedilen": sonra["documents"][1]["title"],
            "revizyon_artisi": sonra["revision"] - once["revision"]}
```

```hint
Her isteğin yanıtını ayrı değişkende tut. PATCH isteklerinde `cookie=ayse` ve veri sözlüğünü birlikte ver; sonucu yanıttan tahmin etmek yerine ikinci `lab.snapshot()` ile ölç.
```

```setup
import sys
from pathlib import Path
_sandbox = str(Path(sys.modules["__main__"].__file__).resolve().parent)
if _sandbox not in sys.path:
    sys.path.insert(0, _sandbox)
```
:::

::: gorev 2 · SQLi: değeri bağla, sıralamayı allowlist'le seç
`ara(db, metin, siralama="yeni")` fonksiyonunu yaz. Bellek içi SQLite'taki `notlar(id, yazar, govde, zaman)` tablosunda `govde = metin` eşleşmelerini `(id, yazar, govde)` demetleri olarak döndür.

- Metin için **parametreli sorgu** kullan. `' OR 1=1 --` yalnız literal bir arama değeri olmalı; SQL'e dönüşmemeli.
- `siralama`: `"yeni"` → zaman azalan, `"eski"` → zaman artan, `"yazar"` → yazar artan ve eşitlikte id artan.
- Başka bir sıralama adı `ValueError` vermeli. Kullanıcıdan gelen adı SQL metnine birleştirme; izinli adları önceden yazılmış ORDER BY ifadelerine eşle.

```starter
def ara(db, metin, siralama="yeni"):
    sql = "SELECT id, yazar, govde FROM notlar WHERE govde = '" + metin + "' ORDER BY zaman DESC"
    return db.execute(sql).fetchall()
```

```test
need("ara")
from web_security_lab import memory_database
db = memory_database()
eq(ara(db, "O'Reilly kaydı"), [(2, "can", "O'Reilly kaydı")], "tırnak verisi SQL sözdizimi değildir")
eq(ara(db, "' OR 1=1 --"), [], "SQLi metni bütün satırları döndürmez; literal değer olarak bağlanır")
eq([r[0] for r in ara(db, "", "eski")], [], "boş metinli kayıt yok")
eq([r[0] for r in ara(db, "Normal not", "eski")], [1], "normal literal eşleşme")
for deger, beklenen in (("yeni", [3, 2, 1]), ("eski", [1, 2, 3]), ("yazar", [1, 3, 2])):
    db2 = memory_database()
    db2.execute("UPDATE notlar SET govde = 'aynı'")
    eq([r[0] for r in ara(db2, "aynı", deger)], beklenen, f"{deger}: yalnız izinli sıralama")
    db2.close()
raises(ValueError, ara, db, "Normal not", "zaman DESC; DROP TABLE notlar", msg="sıralama alanı allowlist dışı")
eq(db.execute("SELECT count(*) FROM notlar").fetchone()[0], 3, "tablo değişmedi ve hâlâ bellek içi fixture'da")
db.close()
```

```solution
def ara(db, metin, siralama="yeni"):
    siralar = {
        "yeni": "zaman DESC",
        "eski": "zaman ASC",
        "yazar": "yazar ASC, id ASC",
    }
    if siralama not in siralar:
        raise ValueError("izinli sıralama: yeni, eski, yazar")
    sql = "SELECT id, yazar, govde FROM notlar WHERE govde = ? ORDER BY " + siralar[siralama]
    return db.execute(sql, (metin,)).fetchall()
```

```hint
`db.execute(sql, (metin,))` değeri SQL metninden ayrı taşır. ORDER BY için `siralar[siralama]` kullanmadan önce anahtarın allowlist'te olduğunu denetle; `siralar.get(siralama, kullanici_degeri)` yazma.
```

```setup
import sys
from pathlib import Path
_sandbox = str(Path(sys.modules["__main__"].__file__).resolve().parent)
if _sandbox not in sys.path:
    sys.path.insert(0, _sandbox)
```
:::

::: gorev 3 · XSS: güvenli DOM sink'ini seç
`notu_yaz(dom, metin)` fonksiyonunu yaz. Verilen `DOMModel` nesnesinde kullanıcı notunu **metin düğümü** olarak eklemek için `dom.text(metin)` çağır. Bu model gerçek tarayıcıdaki `textContent` davranışını temsil eder; `dom.html` ise `innerHTML` benzeri güvensiz sink'tir.

Girdi markup içerse bile metin olarak kalmalı, modelin canary'si değişmemeli ve serileştirmede `<` / `>` kaçamaklanmalı. HTML'i önceden elle kaçamaklayıp sonra `text` çağırma: bu çifte kaçamaklama olur ve görünen metni bozar.

```starter
def notu_yaz(dom, metin):
    dom.html(metin)
```

```test
need("notu_yaz")
from web_security_lab import CANARY, DOMModel
dom = DOMModel()
notu_yaz(dom, CANARY)
eq(dom.nodes, [("text", CANARY)], "girdi tek bir literal metin düğümü")
ok(not dom.canary, "zararsız canary metin olarak yazılınca çalışmaz")
eq(dom.serialized(), "&lt;script&gt;window.__paftaCanary=1&lt;/script&gt;", "serileştirmede markup değil kaçamaklı metin")
ok("<script>" not in dom.serialized(), "girdiden yeni script elementi oluşmaz")
ikinci = DOMModel()
notu_yaz(ikinci, "<b>A & B</b>")
eq(ikinci.serialized(), "&lt;b&gt;A &amp; B&lt;/b&gt;", "HTML ve & görünür metin olarak korunur; çifte kaçamaklama yok")
```

```solution
def notu_yaz(dom, metin):
    dom.text(metin)
```

```hint
Gerçek DOM karşılığı `element.textContent = metin`; buradaki karşılığı yalnız `dom.text(metin)`. `html.escape` eklemek gerekmez; model metin sink'inde doğru bağlamı zaten uygular.
```

```setup
import sys
from pathlib import Path
_sandbox = str(Path(sys.modules["__main__"].__file__).resolve().parent)
if _sandbox not in sys.path:
    sys.path.insert(0, _sandbox)
```
:::

::: gorev 4 · Komut enjeksiyonu: çalıştırma, planı doğrula
`planla(islem, hedef)` fonksiyonunu yaz. `COMMAND_PLANS` içindeki izinli işlemi bul; hedef o işlemin `hedefler` listesinde değilse `ValueError` ver. Geçerliyse planın `argv` öğelerini yeni bir **listeye** kopyalayıp sonuna hedefi ayrı bir argv öğesi olarak ekle ve döndür.

Bu fonksiyon komut **çalıştırmaz**, kabuk metni üretmez. Örneğin `("durum", "web01")` sonucu `["pafta-durum", "--format", "json", "--hedef", "web01"]` olur. `web01;whoami`, `$(whoami)`, boşlukla eklenen ikinci argüman ve `/etc` izinli hedef değildir. Ana makinede bunların hiçbiri yürütülmez; yalnız reddedilmeleri test edilir.

```starter
def planla(islem, hedef):
    return islem + " " + hedef
```

```test
need("planla")
from copy import deepcopy
from web_security_lab import COMMAND_PLANS
once = deepcopy(COMMAND_PLANS)
eq(planla("durum", "web01"), ["pafta-durum", "--format", "json", "--hedef", "web01"], "ayrı argv öğeleri; kabuk metni değil")
eq(planla("liste", "/lab/raporlar"), ["pafta-liste", "--dizin", "/lab/raporlar"], "ikinci izinli plan")
for islem, hedef in (("durum", "web01;whoami"), ("durum", "$(whoami)"),
                     ("durum", "web01 --verbose"), ("liste", "/etc"),
                     ("bilinmeyen", "web01")):
    raises(ValueError, planla, islem, hedef, msg=f"allowlist dışı reddedilir: {islem!r}, {hedef!r}")
eq(COMMAND_PLANS, once, "döndürülen liste ortak argv planını değiştirmez")
```

```solution
from web_security_lab import COMMAND_PLANS

def planla(islem, hedef):
    plan = COMMAND_PLANS.get(islem)
    if plan is None or hedef not in plan["hedefler"]:
        raise ValueError("izinli işlem ve hedef gerekli")
    return list(plan["argv"]) + [hedef]
```

```hint
Önce `plan = COMMAND_PLANS.get(islem)`, sonra `plan is None or hedef not in plan["hedefler"]`. Sonuç `list(plan["argv"]) + [hedef]`; `" ".join(...)` kabuk metni üretir ve argv ayrımını kaybeder.
```

```setup
import sys
from pathlib import Path
_sandbox = str(Path(sys.modules["__main__"].__file__).resolve().parent)
if _sandbox not in sys.path:
    sys.path.insert(0, _sandbox)
```
:::
