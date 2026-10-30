---
id: ai-guvence-03
title: Tehdit Modelinden Deney Sorusuna
summary: Tehdit kartındaki varsayımları ölçüt, yön ve eşik içeren gözlemlenebilir bir deney sorusuna dönüştür.
timeout: 45
---

::: anlat Gerçek tehdit modelini bil, sentetik temsili ayırt et
Evasion, poisoning, gizlilik ve tedarik zinciri riskleri ancak etkilenen varlık, aktör ve varsayım açıklandığında sınanabilir hale gelir. Tehdit kartı bu bağlamı sabitler. Deney sorusu ise hangi ölçütün hangi yönde ve ne kadar değişmesinin beklendiğini belirtir.

| Katman | Gerçek ML tehdit modellemesi ne içerir? | Bu ders ne kullanır? | Ne söyleyemez? |
|---|---|---|---|
| Tehdit kartı | MITRE ATLAS / OWASP ML Top 10 eşlemesi, saldırgan bilgisi (beyaz/kara kutu), bütçe ve varlık | İlk 3 görevde `veri/tehdit_karti.json` sentetik kartı; son görevde canlı poisoning tehdit kartı | Kart şemasının geçerli olması tehdidin üretim ortamında gerçekten uygulanabilir olduğunu kanıtlamaz |
| Hipotez sınaması | Tekrarlı taban ve saldırı koşuları arasındaki yönlü etki büyüklüğü ($\Delta$) ve güven aralığı | İlk 3 görevde `veri/olcumler.json` sentetik kayıtları; son görevde 3 tohumlu gerçek `LogisticRegression` temiz/zehirli karşılaştırması | Üç tekrarda eşik aşımı istatistiksel nedensellik veya tüm veri dağılımları için genelleme sağlamaz |

> [!NOT]
> İlk üç görevde örnek dosyalar çalışma klasörünün `veri/` altına kopyalanır: `veri/tehdit_karti.json` ve `veri/olcumler.json` (tümü **sentetik**). Bu dosyaları kodundan okuyup inceleyebilirsin; ancak her çalıştırmada temiz kopya yeniden yazılır (**kalıcılık yoktur**). Kontrol adımı bu dosyalardan bağımsız gizli verilerle sınama yapar.
:::

::: anlat Ölçüt ve yön tehditle uyumlu olmalıdır
Evasion ve poisoning deneylerinde saldırı başarı oranı ile sınıflandırma ölçütleri, gizlilik deneylerinde sızıntı oranı izlenebilir. Her ölçüt her tehdit için anlamlı kabul edilmez. Artış sorusunda fark `deney-taban`, azalış sorusunda `taban-deney` olarak hesaplanır; böylece iki yönde de pozitif fark beklenen değişimi gösterir.

Tekrarlar ayrı ayrı raporlanır. Bütün tekrarların farkı eşiğe eşit veya üzerindeyse sonuç `desteklendi`, aksi halde `desteklenmedi` olur. Bu karar yalnız verilen fixture ve soru için geçerlidir; nedensellik veya genellenebilirlik kanıtı değildir.
:::

::: tahmin Deney farklarını tahmin et
Üç çıktı satırını yaz:

```python
print(round(0.6 - 0.4, 6))
print(round(0.6 - 0.45, 6))
print(all(d >= 0.1 for d in [0.2, 0.0]))
```

???

```cikti
0.2
0.15
False
```

İlk satır artış, ikinci satır azalış sorusundaki beklenen yönlü farktır.
:::

::: gorev 1 · Tehdit kartını doğrula
`tehdit_karti_dogrula(karti)` işlevini yaz. Kart tam olarak `id`, `kategori`, `varlik`, `aktor`, `varsayim` alanlarını taşısın. Kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren stringdir. Kategori `evasion`, `poisoning`, `gizlilik` veya `tedarik` olmalıdır.

Varlık, aktör ve varsayım başı/sonu boşluğu olmayan boş olmayan stringdir ve kontrol karakteri içeremez. Geçersiz veride `ValueError` yükselt. Alanları koruyan yeni sözlükle döndür ve girdiyi değiştirme.

```starter
from ai_guvence_veri import json_yukle

def tehdit_karti_dogrula(karti):
    # KUSURLU BAŞLANGIÇ KODU: kategori ve metin kurallarını denetlemeden girdi sözlüğünü döndürüyor!
    return karti

print("Örnek tehdit kartı:", tehdit_karti_dogrula(json_yukle("veri/tehdit_karti.json")))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-03")
```

```test
import copy
T = {"id": "t-1", "kategori": "evasion", "varlik": "yelkovan modeli", "aktor": "dis saldirgan", "varsayim": "yalniz test girdisini degistirir"}
def sozlesme(fn):
    try:
        once = copy.deepcopy(T)
        sonuc = fn(T)
        if sonuc != T or T != once or sonuc is T:
            return False
        if fn(dict(T, id="a" * 64, kategori="gizlilik"))["kategori"] != "gizlilik":
            return False
        for karti in [
            None, [], dict(T, ek=1), dict(T, id=""), dict(T, id="a b"), dict(T, id="a" * 65), dict(T, id=None),
            dict(T, kategori="bilinmeyen"), dict(T, kategori=None), dict(T, kategori=True),
            dict(T, varlik=""), dict(T, varlik=" x"), dict(T, varlik="a\0b"), dict(T, varlik=None),
            dict(T, aktor=""), dict(T, aktor="x "), dict(T, aktor="a\0b"), dict(T, aktor=None),
            dict(T, varsayim=""), dict(T, varsayim=" x"), dict(T, varsayim="a\0b"), dict(T, varsayim=None),
        ]:
            try:
                fn(karti)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(tehdit_karti_dogrula), "tehdit kartı şeması ve metin alanları korunmalı")
def m_kategori(karti):
    return tehdit_karti_dogrula(dict(karti, kategori="tedarik"))
def m_varlik(karti):
    return tehdit_karti_dogrula(dict(karti, varlik="baska varlik"))
def m_id(karti):
    return tehdit_karti_dogrula(dict(karti, id="baska-id"))
for ad, mutant in [("kategoriyi değiştiren", m_kategori), ("varlığı değiştiren", m_varlik), ("kimliği değiştiren", m_id)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def tehdit_karti_dogrula(karti):
    import re
    if not isinstance(karti, dict):
        raise ValueError("kart sözlük olmalı")
    if set(karti) != {"id", "kategori", "varlik", "aktor", "varsayim"}:
        raise ValueError("kart şeması geçersiz")
    if not isinstance(karti["id"], str):
        raise ValueError("kimlik string olmalı")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", karti["id"]):
        raise ValueError("kimlik geçersiz")
    if karti["kategori"] not in ("evasion", "poisoning", "gizlilik", "tedarik"):
        raise ValueError("kategori geçersiz")
    for alan in ("varlik", "aktor", "varsayim"):
        deger = karti[alan]
        if not isinstance(deger, str):
            raise ValueError("metin alanı string olmalı")
        if not deger or deger != deger.strip():
            raise ValueError("metin boşluk biçimi geçersiz")
        if any(ord(k) < 32 for k in deger):
            raise ValueError("metin kontrol karakteri içeremez")
    return {"id": karti["id"], "kategori": karti["kategori"], "varlik": karti["varlik"], "aktor": karti["aktor"], "varsayim": karti["varsayim"]}
```

```hint
Kimliği desenle, kategoriyi izin listesiyle denetle. Üç metin alanını aynı döngüde doğrulayıp yeni sözlük oluştur.
```
:::

::: gorev 2 · Ölçülebilir deney sorusu üret
`deney_sorusu_uret(karti, olcut, yon, esik)` işlevini yaz. Kart ilk görevdeki kuralları sağlasın. Ölçüt-kategori uyumu şöyledir: `evasion` için `asr`, `f1`; `poisoning` için `asr`, `f1`, `fpr`; `gizlilik` için `sizinti_orani`; `tedarik` için `fpr`, `asr`. Yön `artis` veya `azalis`, eşik bool olmayan sonlu sayı ve `0 <= esik <= 1` aralığında olmalıdır. Geçersiz veride `ValueError` yükselt.

`{"tehdit_id":ID,"olcut":OLCUT,"yon":YON,"esik":ESIK,"soru":METIN}` döndür. Soru metni tam olarak `ID + " icin " + OLCUT + " " + YON + " esigi " + format(esik, ".6f")` olsun. Girdiyi değiştirme.

```starter
from ai_guvence_veri import json_yukle

def deney_sorusu_uret(karti, olcut, yon, esik):
    # KUSURLU BAŞLANGIÇ KODU: kategori-ölçüt uyumunu denetlemiyor ve eşiği 6 ondalık basamakla biçimlendirmiyor!
    kimlik = karti.get("id", "") if isinstance(karti, dict) else ""
    return {"tehdit_id": kimlik, "olcut": olcut, "yon": yon, "esik": esik, "soru": f"{kimlik} icin {olcut} {yon} esigi {esik}"}

print("Örnek soru:", deney_sorusu_uret(json_yukle("veri/tehdit_karti.json"), "asr", "artis", 0.1))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-03")
```

```test
import copy
T = {"id": "t-1", "kategori": "evasion", "varlik": "yelkovan modeli", "aktor": "dis saldirgan", "varsayim": "yalniz test girdisini degistirir"}
BEKLENEN = {"tehdit_id": "t-1", "olcut": "asr", "yon": "artis", "esik": 0.1, "soru": "t-1 icin asr artis esigi 0.100000"}
def sozlesme(fn):
    try:
        once = copy.deepcopy(T)
        if fn(T, "asr", "artis", 0.1) != BEKLENEN or T != once:
            return False
        for kategori, olcut in [("evasion", "f1"), ("poisoning", "fpr"), ("gizlilik", "sizinti_orani"), ("tedarik", "asr")]:
            if fn(dict(T, kategori=kategori), olcut, "azalis", 0)["esik"] != 0:
                return False
        if fn(T, "asr", "artis", 1)["soru"].endswith("1.000000") is False:
            return False
        if fn(T, "asr", "artis", 1 / 3)["soru"].endswith("0.333333") is False:
            return False
        for karti, olcut, yon, esik in [
            (None, "asr", "artis", 0.1), (dict(T, ek=1), "asr", "artis", 0.1),
            (dict(T, id="a" * 65), "asr", "artis", 0.1), (dict(T, kategori="baska"), "asr", "artis", 0.1),
            (dict(T, varlik=""), "asr", "artis", 0.1), (dict(T, aktor=" x"), "asr", "artis", 0.1),
            (dict(T, varsayim="a\0b"), "asr", "artis", 0.1),
            (T, "fpr", "artis", 0.1), (T, "sizinti_orani", "artis", 0.1), (T, None, "artis", 0.1),
            (dict(T, kategori="gizlilik"), "asr", "artis", 0.1),
            (T, "asr", "sabit", 0.1), (T, "asr", None, 0.1),
            (T, "asr", "artis", None), (T, "asr", "artis", True), (T, "asr", "artis", "0.1"),
            (T, "asr", "artis", float("nan")), (T, "asr", "artis", float("inf")),
            (T, "asr", "artis", -0.1), (T, "asr", "artis", 1.1),
        ]:
            try:
                fn(karti, olcut, yon, esik)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(deney_sorusu_uret), "kategori-ölçüt uyumu, yön, eşik ve metin korunmalı")
def m_olcut(karti, olcut, yon, esik):
    return deney_sorusu_uret(karti, "f1", yon, esik)
def m_yon(karti, olcut, yon, esik):
    return deney_sorusu_uret(karti, olcut, "azalis", esik)
def m_esik(karti, olcut, yon, esik):
    return deney_sorusu_uret(karti, olcut, yon, 1)
for ad, mutant in [("ölçütü değiştiren", m_olcut), ("yönü değiştiren", m_yon), ("eşiği değiştiren", m_esik)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def deney_sorusu_uret(karti, olcut, yon, esik):
    import math
    import re
    if not isinstance(karti, dict):
        raise ValueError("kart sözlük olmalı")
    if set(karti) != {"id", "kategori", "varlik", "aktor", "varsayim"}:
        raise ValueError("kart şeması geçersiz")
    if not isinstance(karti["id"], str):
        raise ValueError("kimlik string olmalı")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", karti["id"]):
        raise ValueError("kimlik geçersiz")
    if karti["kategori"] not in ("evasion", "poisoning", "gizlilik", "tedarik"):
        raise ValueError("kategori geçersiz")
    for alan in ("varlik", "aktor", "varsayim"):
        deger = karti[alan]
        if not isinstance(deger, str):
            raise ValueError("metin alanı string olmalı")
        if not deger or deger != deger.strip():
            raise ValueError("metin boşluk biçimi geçersiz")
        if any(ord(k) < 32 for k in deger):
            raise ValueError("metin kontrol karakteri içeremez")
    uyum = {"evasion": ("asr", "f1"), "poisoning": ("asr", "f1", "fpr"), "gizlilik": ("sizinti_orani",), "tedarik": ("fpr", "asr")}
    if olcut not in uyum[karti["kategori"]]:
        raise ValueError("ölçüt tehdit kategorisiyle uyumsuz")
    if yon not in ("artis", "azalis"):
        raise ValueError("yön geçersiz")
    if isinstance(esik, bool) or not isinstance(esik, (int, float)):
        raise ValueError("eşik sayı olmalı")
    if not math.isfinite(esik):
        raise ValueError("eşik sonlu olmalı")
    if esik < 0 or esik > 1:
        raise ValueError("eşik aralık dışında")
    soru = karti["id"] + " icin " + olcut + " " + yon + " esigi " + format(esik, ".6f")
    return {"tehdit_id": karti["id"], "olcut": olcut, "yon": yon, "esik": esik, "soru": soru}
```

```hint
Önce kartı doğrula. Kategoriye göre izinli ölçütleri bir eşlemede tut; soru metnini alanları birleştirerek ve eşiği biçimlendirerek kur.
```
:::

::: gorev 3 · Deney sorusunu tekrarlı ölçümlerle değerlendir
`deney_sorusunu_degerlendir(soru, olcumler)` işlevini yaz. Soru tam olarak `tehdit_id`, `olcut`, `yon`, `esik`, `soru` alanlarını taşısın. Kimlik ilk görevdeki desene uysun; ölçüt `asr`, `f1`, `fpr` veya `sizinti_orani`, yön `artis` veya `azalis`, eşik bool olmayan sonlu sayı ve `[0,1]` aralığında olsun. Soru metni ikinci görevdeki biçimle birebir aynı olmalıdır.

Ölçümler boş olmayan listedir. Her kayıt tam olarak `tekrar`, `taban`, `deney` alanlarını taşısın. Tekrar bool olmayan pozitif tamsayı ve benzersiz, taban ile deney bool olmayan sonlu sayı ve `[0,1]` aralığında olsun. Geçersiz veride `ValueError` yükselt.

Artışta fark `deney-taban`, azalışta `taban-deney` olsun. `{"tehdit_id":ID,"karar":KARAR,"ortalama_delta":X,"bulgular":[{"tekrar":N,"delta":X},...]}` döndür. Bulguları tekrar numarasına göre sırala, farkları ve ortalamayı altı ondalık basamağa yuvarla. Bütün ham farklar eşiğe eşit veya büyükse karar `desteklendi`, aksi halde `desteklenmedi` olsun. Girdileri değiştirme.

```starter
from ai_guvence_veri import json_yukle

def deney_sorusunu_degerlendir(soru, olcumler):
    # KUSURLU BAŞLANGIÇ KODU: yalnız ilk ölçümün farkına bakıp tüm tekrarları kontrol etmiyor!
    ilk = (olcumler or [{}])[0]
    fark = round(ilk.get("deney", 0.0) - ilk.get("taban", 0.0), 6) if isinstance(ilk, dict) else 0.0
    return {"tehdit_id": soru.get("tehdit_id", "") if isinstance(soru, dict) else "", "karar": "desteklendi", "ortalama_delta": fark, "bulgular": []}

k = json_yukle("veri/tehdit_karti.json")
s = {"tehdit_id": k["id"], "olcut": "asr", "yon": "artis", "esik": 0.15, "soru": f"{k['id']} icin asr artis esigi 0.150000"}
print("Örnek değerlendirme:", deney_sorusunu_degerlendir(s, json_yukle("veri/olcumler.json")))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-03")
```

```test
import copy
S = {"tehdit_id": "t-1", "olcut": "asr", "yon": "artis", "esik": 0.1, "soru": "t-1 icin asr artis esigi 0.100000"}
O = [{"tekrar": 2, "taban": 0.4, "deney": 0.6}, {"tekrar": 1, "taban": 0.5, "deney": 0.5}]
BEKLENEN = {"tehdit_id": "t-1", "karar": "desteklenmedi", "ortalama_delta": 0.1, "bulgular": [{"tekrar": 1, "delta": 0.0}, {"tekrar": 2, "delta": 0.2}]}
def sozlesme(fn):
    try:
        sonce = copy.deepcopy(S)
        oonce = copy.deepcopy(O)
        if fn(S, O) != BEKLENEN or S != sonce or O != oonce:
            return False
        tam = [{"tekrar": 1, "taban": 0.5, "deney": 0.65}, {"tekrar": 2, "taban": 0.4, "deney": 0.55}]
        if fn(S, tam)["karar"] != "desteklendi" or fn(S, tam)["ortalama_delta"] != 0.15:
            return False
        azalis = {"tehdit_id": "t-1", "olcut": "fpr", "yon": "azalis", "esik": 0.25, "soru": "t-1 icin fpr azalis esigi 0.250000"}
        if fn(azalis, [{"tekrar": 1, "taban": 0.5, "deney": 0.25}])["karar"] != "desteklendi":
            return False
        sifir = dict(S, esik=0, soru="t-1 icin asr artis esigi 0.000000")
        if fn(sifir, [O[1]])["karar"] != "desteklendi":
            return False
        yuvarla = dict(S, esik=0, soru="t-1 icin asr artis esigi 0.000000")
        sonuc = fn(yuvarla, [{"tekrar": 1, "taban": 0, "deney": 1 / 3}, {"tekrar": 2, "taban": 0, "deney": 0}])
        if sonuc["bulgular"][0]["delta"] != 0.333333 or sonuc["ortalama_delta"] != 0.166667:
            return False
        bir = dict(S, esik=1, soru="t-1 icin asr artis esigi 1.000000")
        if fn(bir, [{"tekrar": 1, "taban": 0, "deney": 1}])["karar"] != "desteklendi":
            return False
        if fn(S, [{"tekrar": 1, "taban": 1, "deney": 1}])["bulgular"][0]["delta"] != 0:
            return False
        for soru, olcumler in [
            (None, O), (dict(S, ek=1), O),
            (dict(S, tehdit_id="a" * 65, soru="a" * 65 + " icin asr artis esigi 0.100000"), O), (dict(S, olcut="baska"), O),
            (dict(S, yon="sabit"), O), (dict(S, esik=True), O), (dict(S, esik="0.1"), O),
            (dict(S, esik=float("nan")), O),
            (dict(S, esik=-0.1, soru="t-1 icin asr artis esigi -0.100000"), O),
            (dict(S, esik=1.1, soru="t-1 icin asr artis esigi 1.100000"), O),
            (dict(S, soru="baska"), O), (S, None), (S, {}), (S, []), (S, [None]),
            (S, [dict(O[0], ek=1)]), (S, [dict(O[0], tekrar=0)]), (S, [dict(O[0], tekrar=True)]),
            (S, [dict(O[0], tekrar=1.0)]), (S, [O[0], O[0]]),
            (S, [dict(O[0], taban=True)]), (S, [dict(O[0], taban="0.4")]),
            (S, [dict(O[0], taban=float("nan"))]), (S, [dict(O[0], taban=-0.1)]), (S, [dict(O[0], taban=1.1)]),
            (S, [dict(O[0], deney=True)]), (S, [dict(O[0], deney="0.6")]),
            (S, [dict(O[0], deney=float("inf"))]), (S, [dict(O[0], deney=-0.1)]), (S, [dict(O[0], deney=1.1)]),
        ]:
            try:
                fn(soru, olcumler)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(deney_sorusunu_degerlendir), "yönlü fark, tekrar sırası, eşik ve karar korunmalı")
def m_olcum(soru, olcumler):
    return deney_sorusunu_degerlendir(soru, olcumler[:1])
def m_yon(soru, olcumler):
        yeni = dict(soru, yon="azalis")
        return deney_sorusunu_degerlendir(yeni, olcumler)
def m_taban(soru, olcumler):
    return deney_sorusunu_degerlendir(soru, [dict(x, taban=0) for x in olcumler])
for ad, mutant in [("ölçümleri silen", m_olcum), ("yönü değiştiren", m_yon), ("tabanı değiştiren", m_taban)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def deney_sorusunu_degerlendir(soru, olcumler):
    import math
    import re
    if not isinstance(soru, dict):
        raise ValueError("soru sözlük olmalı")
    if set(soru) != {"tehdit_id", "olcut", "yon", "esik", "soru"}:
        raise ValueError("soru şeması geçersiz")
    if not isinstance(soru["tehdit_id"], str):
        raise ValueError("kimlik string olmalı")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", soru["tehdit_id"]):
        raise ValueError("kimlik geçersiz")
    if soru["olcut"] not in ("asr", "f1", "fpr", "sizinti_orani"):
        raise ValueError("ölçüt geçersiz")
    if soru["yon"] not in ("artis", "azalis"):
        raise ValueError("yön geçersiz")
    esik = soru["esik"]
    if isinstance(esik, bool) or not isinstance(esik, (int, float)):
        raise ValueError("eşik sayı olmalı")
    if not math.isfinite(esik):
        raise ValueError("eşik sonlu olmalı")
    if esik < 0 or esik > 1:
        raise ValueError("eşik aralık dışında")
    beklenen_soru = soru["tehdit_id"] + " icin " + soru["olcut"] + " " + soru["yon"] + " esigi " + format(esik, ".6f")
    if soru["soru"] != beklenen_soru:
        raise ValueError("soru metni alanlarla uyuşmuyor")
    if not isinstance(olcumler, list):
        raise ValueError("ölçümler liste olmalı")
    if not olcumler:
        raise ValueError("ölçümler boş olamaz")
    gorulen = set()
    bulgular = []
    ham_farklar = []
    for olcum in olcumler:
        if not isinstance(olcum, dict):
            raise ValueError("ölçüm sözlük olmalı")
        if set(olcum) != {"tekrar", "taban", "deney"}:
            raise ValueError("ölçüm şeması geçersiz")
        tekrar = olcum["tekrar"]
        if isinstance(tekrar, bool) or not isinstance(tekrar, int):
            raise ValueError("tekrar tamsayı olmalı")
        if tekrar <= 0:
            raise ValueError("tekrar pozitif olmalı")
        if tekrar in gorulen:
            raise ValueError("tekrar yinelenemez")
        for alan in ("taban", "deney"):
            deger = olcum[alan]
            if isinstance(deger, bool) or not isinstance(deger, (int, float)):
                raise ValueError("ölçüm değeri sayı olmalı")
            if not math.isfinite(deger):
                raise ValueError("ölçüm değeri sonlu olmalı")
            if deger < 0 or deger > 1:
                raise ValueError("ölçüm değeri aralık dışında")
        fark = olcum["deney"] - olcum["taban"] if soru["yon"] == "artis" else olcum["taban"] - olcum["deney"]
        gorulen.add(tekrar)
        ham_farklar.append(fark)
        bulgular.append({"tekrar": tekrar, "delta": round(fark, 6)})
    bulgular.sort(key=lambda x: x["tekrar"])
    return {"tehdit_id": soru["tehdit_id"], "karar": "desteklendi" if all(f >= esik for f in ham_farklar) else "desteklenmedi", "ortalama_delta": round(sum(ham_farklar) / len(ham_farklar), 6), "bulgular": bulgular}
```

```hint
Her kaydı doğruladıktan sonra yöne göre ham farkı hesapla. Kararı yuvarlanmış görüntü değerlerinden değil, ham farklardan çıkar.
```
:::

::: anlat Canlı zehirleme (poisoning) deneyinde tehdit kartı ve hipotez değerlendirmesi
İlk üç görevde tehdit kartı doğrulamayı, deney sorusu üretmeyi ve tekrarlı fark değerlendirmesini sentetik dosyalar üzerinde kurdun. Şimdi aynı üç işlevi **gerçek `scikit-learn` (`LogisticRegression`) zehirleme deneyine** bağlıyoruz:

1. `tehdit-poisoning-01` tehdit kartı `tehdit_karti_dogrula` ile doğrulanır ve `deney_sorusu_uret` ile `"tehdit-poisoning-01 icin asr artis esigi 0.150000"` deney sorusuna dönüştürülür.
2. Üç farklı rastgelelik tohumunda hem temiz (`taban`) hem de eğitim verisinin %16'sı tetikleyiciyle çevrilmiş (`deney`) iki `LogisticRegression` modeli gerçekten eğitilir ve tetikleyicili test örneklerindeki saldırı başarı oranı (`asr`) ölçülür.
3. Üç tekrarın canlı `taban` ve `deney` ölçümleri `deney_sorusunu_degerlendir` ile değerlendirilip kanıt dosyasına kaydedilir.
:::

::: gorev Gerçek deney · Canlı sınıflandırıcı zehirleme deneyinde hipotez değerlendirmesi
Önceki üç görevde yazdığın `tehdit_karti_dogrula(karti)`, `deney_sorusu_uret(karti, olcut, yon, esik)` ve `deney_sorusunu_degerlendir(soru, olcumler)` işlevlerini burada birleştir.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 180
```

```starter
import math
import re
import ai_lab
from sandbox import ai_gercek_ai_guvence_03 as L

def tehdit_karti_dogrula(karti):
    # KUSURLU BAŞLANGIÇ KODU: doğrulama yapmadan girdi sözlüğünü döndürüyor!
    return karti

def deney_sorusu_uret(karti, olcut, yon, esik):
    return {}

def deney_sorusunu_degerlendir(soru, olcumler):
    return {}

if ai_lab.CALISTIR:
    L.goster(tehdit_karti_dogrula, deney_sorusu_uret, deney_sorusunu_degerlendir)
```

```test
import copy
import ai_lab
from sandbox import ai_gercek_ai_guvence_03 as L

checks = []
_base_ok = ok
def ok(kosul, mesaj):
    checks.append(bool(kosul))
    return _base_ok(kosul, mesaj)

for s in ai_lab.kod_denetimi(src, yasak=("tehdit_karti_dogrula_referans", "deney_sorusu_uret_referans", "deney_sorusunu_degerlendir_referans", "kanit_yaz")):
    ok(False, f"Güvenlik/kopya denetimi: {s}")
if not all(checks):
    stop()

def _sozlesme_kontrol():
    try:
        T = {"id": "t-1", "kategori": "evasion", "varlik": "yelkovan modeli", "aktor": "dis saldirgan", "varsayim": "yalniz test girdisini degistirir"}
        once = copy.deepcopy(T)
        st = tehdit_karti_dogrula(T)
        if st != T or T != once or st is T:
            return False
        for bt in [None, dict(T, ek=1), dict(T, kategori="x"), dict(T, varlik=" x")]:
            try:
                tehdit_karti_dogrula(bt)
                return False
            except ValueError:
                pass

        ss = deney_sorusu_uret(T, "asr", "artis", 0.1)
        if ss != {"tehdit_id": "t-1", "olcut": "asr", "yon": "artis", "esik": 0.1, "soru": "t-1 icin asr artis esigi 0.100000"}:
            return False
        for bo, by, be in [("fpr", "artis", 0.1), ("asr", "x", 0.1), ("asr", "artis", 1.2), ("asr", "artis", True)]:
            try:
                deney_sorusu_uret(T, bo, by, be)
                return False
            except ValueError:
                pass

        O = [{"tekrar": 2, "taban": 0.4, "deney": 0.6}, {"tekrar": 1, "taban": 0.5, "deney": 0.5}]
        sd = deney_sorusunu_degerlendir(ss, O)
        if sd != {"tehdit_id": "t-1", "karar": "desteklenmedi", "ortalama_delta": 0.1, "bulgular": [{"tekrar": 1, "delta": 0.0}, {"tekrar": 2, "delta": 0.2}]}:
            return False
        for bs, bol in [(dict(ss, soru="x"), O), (ss, []), (ss, [O[0], O[0]]), (ss, [dict(O[0], deney=1.2)])]:
            try:
                deney_sorusunu_degerlendir(bs, bol)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(_sozlesme_kontrol(), "tehdit_karti_dogrula, deney_sorusu_uret ve deney_sorusunu_degerlendir sözleşme kontrollerini geçmeli")
if not all(checks):
    stop()

try:
    rapor = L.deney(tehdit_karti_dogrula, deney_sorusu_uret, deney_sorusunu_degerlendir)
except ai_lab.GercekLabYok as e:
    ok(False, str(e))
    stop()
except Exception as e:
    ok(False, f"GERÇEK TEHDİT SORUSU DENEYİ YAPILAMADI: {type(e).__name__}: {e}")
    stop()

k = rapor["kontroller"]
ok(k["kart_uyumu"], f"tehdit_karti_dogrula canlı tehdit kartında referansla uyuşmalı: {rapor['kart']}")
ok(k["soru_uyumu"], f"deney_sorusu_uret canlı deney sorusunda referansla uyuşmalı: {rapor['soru']}")
ok(k["degerlendirme_uyumu"] and k["canli_fark_pozitif"], f"deney_sorusunu_degerlendir canlı ASR ölçümlerinde referansla uyuşmalı: {rapor['degerlendirme']}")

kabul = all(checks)
kanit_yolu = ai_lab.kanit_yaz("guvence-03-tehdit-sorusu", dict(rapor, kaynak="gercek", kabul=kabul))
o = rapor["ozet"]
print(f"GERÇEK TEHDİT SORUSU DENEYİ: karar={o['karar']} ortalama_delta={o['ortalama_delta']} kanıt={kanit_yolu}")
```

```solution
import math
import re
import ai_lab
from sandbox import ai_gercek_ai_guvence_03 as L

def tehdit_karti_dogrula(karti):
    if not isinstance(karti, dict) or set(karti) != {"id", "kategori", "varlik", "aktor", "varsayim"}:
        raise ValueError("kart şeması geçersiz")
    if not isinstance(karti["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", karti["id"]):
        raise ValueError("kimlik geçersiz")
    if karti["kategori"] not in ("evasion", "poisoning", "gizlilik", "tedarik"):
        raise ValueError("kategori geçersiz")
    for alan in ("varlik", "aktor", "varsayim"):
        deger = karti[alan]
        if not isinstance(deger, str) or not deger or deger != deger.strip() or any(ord(k) < 32 for k in deger):
            raise ValueError("metin alanı geçersiz")
    return {"id": karti["id"], "kategori": karti["kategori"], "varlik": karti["varlik"], "aktor": karti["aktor"], "varsayim": karti["varsayim"]}

def deney_sorusu_uret(karti, olcut, yon, esik):
    k = tehdit_karti_dogrula(karti)
    uyum = {"evasion": ("asr", "f1"), "poisoning": ("asr", "f1", "fpr"), "gizlilik": ("sizinti_orani",), "tedarik": ("fpr", "asr")}
    if olcut not in uyum[k["kategori"]] or yon not in ("artis", "azalis"):
        raise ValueError("ölçüt veya yön geçersiz")
    if isinstance(esik, bool) or not isinstance(esik, (int, float)) or not math.isfinite(esik) or esik < 0 or esik > 1:
        raise ValueError("eşik geçersiz")
    soru = k["id"] + " icin " + olcut + " " + yon + " esigi " + format(esik, ".6f")
    return {"tehdit_id": k["id"], "olcut": olcut, "yon": yon, "esik": esik, "soru": soru}

def deney_sorusunu_degerlendir(soru, olcumler):
    if not isinstance(soru, dict) or set(soru) != {"tehdit_id", "olcut", "yon", "esik", "soru"}:
        raise ValueError("soru şeması geçersiz")
    if not isinstance(soru["tehdit_id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", soru["tehdit_id"]):
        raise ValueError("kimlik geçersiz")
    if soru["olcut"] not in ("asr", "f1", "fpr", "sizinti_orani") or soru["yon"] not in ("artis", "azalis"):
        raise ValueError("ölçüt/yön geçersiz")
    esik = soru["esik"]
    if isinstance(esik, bool) or not isinstance(esik, (int, float)) or not math.isfinite(esik) or esik < 0 or esik > 1:
        raise ValueError("eşik geçersiz")
    beklenen_soru = soru["tehdit_id"] + " icin " + soru["olcut"] + " " + soru["yon"] + " esigi " + format(esik, ".6f")
    if soru["soru"] != beklenen_soru:
        raise ValueError("soru metni uyuşmuyor")
    if not isinstance(olcumler, list) or not olcumler:
        raise ValueError("ölçümler geçersiz")
    gorulen = set()
    bulgular = []
    ham_farklar = []
    for olcum in olcumler:
        if not isinstance(olcum, dict) or set(olcum) != {"tekrar", "taban", "deney"}:
            raise ValueError("ölçüm şeması geçersiz")
        tekrar = olcum["tekrar"]
        if isinstance(tekrar, bool) or not isinstance(tekrar, int) or tekrar <= 0 or tekrar in gorulen:
            raise ValueError("tekrar geçersiz")
        for alan in ("taban", "deney"):
            deger = olcum[alan]
            if isinstance(deger, bool) or not isinstance(deger, (int, float)) or not math.isfinite(deger) or deger < 0 or deger > 1:
                raise ValueError("değer geçersiz")
        fark = olcum["deney"] - olcum["taban"] if soru["yon"] == "artis" else olcum["taban"] - olcum["deney"]
        gorulen.add(tekrar)
        ham_farklar.append(fark)
        bulgular.append({"tekrar": tekrar, "delta": round(fark, 6)})
    bulgular.sort(key=lambda x: x["tekrar"])
    return {"tehdit_id": soru["tehdit_id"], "karar": "desteklendi" if all(f >= esik for f in ham_farklar) else "desteklenmedi", "ortalama_delta": round(sum(ham_farklar) / len(ham_farklar), 6), "bulgular": bulgular}

if ai_lab.CALISTIR:
    L.goster(tehdit_karti_dogrula, deney_sorusu_uret, deney_sorusunu_degerlendir)
```

```hint
Önceki üç görevde yazdığın `tehdit_karti_dogrula`, `deney_sorusu_uret` ve `deney_sorusunu_degerlendir` işlevlerini eksiksiz taşı; canlı deneyde 3 tekrarlı temiz/zehirli `LogisticRegression` modeli üzerinde sınanır.
```
:::
