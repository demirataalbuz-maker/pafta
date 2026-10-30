---
id: ai-ile-guvenlik-13
title: "Salt-Okunur Keşif Ajanı ve Deterministik Kapsam Kilidi"
summary: Araç çağıran (tool-calling) güvenlik ajanında salt-okunur araç beyaz listesi, izinli hedef kapsam kilidi, adım bütçesi ve döngü kırıcı (circuit breaker) kapılarını uygula.
timeout: 300
---

::: anlat Gerçek biçimi bil, sentetik temsili ayırt et
Kendi güvenlik ajanımızı yazarken modele araç çağırma (`tool-calling`) yetkisi vermek tek başına yeterli değildir: model halüsinasyon görerek kapsam dışı bir sunucuya (`dis-sunucu.example`) istek atabilir, yıkıcı bir aracı (`dosya_sil`) çağırmayı deneyebilir veya aynı aracı aynı hedefe tekrar tekrar çağırarak sonsuz döngüye girebilir (`ai-savunma-11` ve `ai-saldiri-16` derslerindeki araç yetki sınırı ilkelerini hatırla).

| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |
|---|---|---|
| Yerel Ollama modelinin (`araclar_gerekli=True`) ürettiği yapılandırılmış araç çağrılarını (`tool_calls`) ve yürütücü katmandaki kapsam kilidini | İlk üç görevde `kapsam_politikasi.json` ve `ajan_cagri_izleri.json` içindeki **sentetik** politika/çağrı verilerini; son görevde canlı `ai_lab.SohbetOturumu` ile keşif ajanı deneyini | Yalnızca araç adı ve hedef kontrolünün, izinli hedeften dönen yanıtın içerdiği dolaylı enjeksiyonları tek başına temizleyebileceğini söyleyemez |

> [!GÜVENLİK]
> **Kapsam ve dürüstlük sınırı:** İlk üç görevdeki `kapsam_politikasi.json` ve `ajan_cagri_izleri.json` dosyaları **sentetik** eğitim verisidir; hiçbir gerçek ağ hedefine paket gönderilmez ve dosyalar her çalıştırmada (`setup`) yeniden yüklenir.
:::

::: anlat Keşif ajanında üç katmanlı yürütme kontrolü
Güvenilir bir salt-okunur keşif ajanı, modelin ürettiği her araç çağrısını çalıştırmadan önce üç deterministik kapıdan geçirir:

1. **Araç ve Hedef Kapsam Kilidi (`arac_cagrisi_dogrula`):** Çağrılan `arac` `izinli_araclar` listesinde değilse `"yasak_arac"`, `hedef` `izinli_hedefler` listesinde değilse `"kapsam_disi_hedef"` nedeniyle reddedilir; ikisi de izinliyse `"onaylandi"` döner.
2. **Döngü Kırıcı ve Adım Bütçesi (`dongu_kirici_kontrol`):** Onaylanan çağrılar sırayla izlenir. Aynı `(arac, hedef)` ikilisi ikinci kez görülürse yürütme `"tekrar_dongusu"` nedeniyle anında durdurulur. Çalıştırılan adım sayısı `azami_adim` sınırına ulaştıktan sonra yeni bir çağrı gelirse yürütme `"butce_asimi"` nedeniyle kesilir.
3. **Uçtan Uca Keşif Yürütücüsü (`kesif_ajani_calistir`):** Ham çağrı dizisini önce kapsam kilidinden süzüp reddedilenleri `engellenenler` sözlüğüne yazar, onaylananları ise döngü kırıcıdan geçirerek `calistirilan_idleri` listesini oluşturur.
:::

::: anlat Bulguyu sınırlı ve doğrulanabilir yaz: kapsam kilidi istemde değil yürütücüde durur
Modelin sistem istemine *"Yalnızca 127.0.0.1 adresini tara"* yazmak bir güvenlik kontrolü değildir. Kapsam kilidi ve döngü kırıcı, modelin çıktısını teslim alan Python yürütücüsünde (`executor`) deterministik kod olarak çalışmalıdır.
:::

::: tahmin Döngü kırıcı ve adım bütçesi davranışını tahmin et
Aşağıdaki Python kodunun çıktısını tahmin et:

```python
cagrilar = [
    ("c1", "http_oku", "lab.local"),
    ("c2", "dns_sor", "lab.local"),
    ("c3", "http_oku", "lab.local"),
]
gorulen = set()
calisan = []
neden = None
for cid, arac, hedef in cagrilar:
    if (arac, hedef) in gorulen:
        neden = "tekrar_dongusu"
        break
    gorulen.add((arac, hedef))
    calisan.append(cid)
print(calisan, neden)
```

???

```cikti
['c1', 'c2'] tekrar_dongusu
```

Üçüncü çağrı (`c3`) birinci çağrıyla aynı `('http_oku', 'lab.local')` çiftini tekrarladığı için döngü kırıcı devreye girer ve yürütmeyi durdurur.
:::

::: gorev 1 · Araç çağrısını salt-okunur araç listesi ve hedef kapsamına göre doğrula
`arac_cagrisi_dogrula(cagri, politika)` işlevini yaz.

Girdi ve doğrulama kuralları:
- `cagri`: tam olarak `{"cagri_id", "arac", "hedef"}` anahtarlarına sahip `dict`; üç alan da boş olmayan (`strip()` sonrası dolu) `str` olmalıdır.
- `politika`: tam olarak `{"izinli_araclar", "izinli_hedefler", "azami_adim"}` anahtarlarına sahip `dict`; `izinli_araclar` ve `izinli_hedefler` boş olmayan `str` listeleri, `azami_adim` ise pozitif `int` (`bool` hariç) olmalıdır.
- Kurallara uymayan girdilerde `ValueError` yükselt.
- Önce `cagri["arac"]` değerini kontrol et: `politika["izinli_araclar"]` içinde değilse `{"cagri_id": cid, "izin_verildi": False, "neden": "yasak_arac"}` döndür.
- Sonra `cagri["hedef"]` değerini kontrol et: `politika["izinli_hedefler"]` içinde değilse `{"cagri_id": cid, "izin_verildi": False, "neden": "kapsam_disi_hedef"}` döndür.
- İkisi de uygunsa `{"cagri_id": cid, "izin_verildi": True, "neden": "onaylandi"}` döndür.

```starter
from ai_ile_guvenlik_veri import json_yukle

politika = json_yukle("kapsam_politikasi.json")
cagrilar = json_yukle("ajan_cagri_izleri.json")["cagrilar"]

def arac_cagrisi_dogrula(cagri, politika):
    # HATA: Araç ve hedef izin listesini kontrol etmeden onaylıyor.
    return {
        "cagri_id": cagri.get("cagri_id", ""),
        "izin_verildi": True,
        "neden": "onaylandi",
    }

for c in cagrilar:
    print(arac_cagrisi_dogrula(c, politika))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-13")
```

```test
need("arac_cagrisi_dogrula")
from ai_ile_guvenlik_veri import json_yukle

POLITIKA = json_yukle("kapsam_politikasi.json")

def sozlesme(fn):
    try:
        if fn({"cagri_id": "c1", "arac": "http_baslik_oku", "hedef": "127.0.0.1:8080"}, POLITIKA) != {
            "cagri_id": "c1",
            "izin_verildi": True,
            "neden": "onaylandi",
        }:
            return False

        if fn({"cagri_id": "c2", "arac": "dosya_sil", "hedef": "127.0.0.1:8080"}, POLITIKA) != {
            "cagri_id": "c2",
            "izin_verildi": False,
            "neden": "yasak_arac",
        }:
            return False

        if fn({"cagri_id": "c3", "arac": "dns_kayit_sorgula", "hedef": "dis.example"}, POLITIKA) != {
            "cagri_id": "c3",
            "izin_verildi": False,
            "neden": "kapsam_disi_hedef",
        }:
            return False

        for c_in, p_in in [
            (None, POLITIKA),
            ({}, POLITIKA),
            ({"cagri_id": "", "arac": "http_baslik_oku", "hedef": "lab.local"}, POLITIKA),
            ({"cagri_id": "c1", "arac": 123, "hedef": "lab.local"}, POLITIKA),
            ({"cagri_id": "c1", "arac": "http_baslik_oku", "hedef": "lab.local"}, None),
            ({"cagri_id": "c1", "arac": "http_baslik_oku", "hedef": "lab.local"}, {}),
            ({"cagri_id": "c1", "arac": "http_baslik_oku", "hedef": "lab.local"}, dict(POLITIKA, izinli_araclar=[])),
            ({"cagri_id": "c1", "arac": "http_baslik_oku", "hedef": "lab.local"}, dict(POLITIKA, izinli_hedefler=[""])),
            ({"cagri_id": "c1", "arac": "http_baslik_oku", "hedef": "lab.local"}, dict(POLITIKA, azami_adim=0)),
            ({"cagri_id": "c1", "arac": "http_baslik_oku", "hedef": "lab.local"}, dict(POLITIKA, azami_adim=True)),
        ]:
            try:
                fn(c_in, p_in)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(arac_cagrisi_dogrula), "arac_cagrisi_dogrula: yasak aracı ve kapsam dışı hedefi doğru ayırt etmeli")
ok(not sozlesme(lambda c, p: {"cagri_id": c["cagri_id"], "izin_verildi": True, "neden": "onaylandi"}), "mutasyon: her çağrıyı onaylayan işlev reddedilmeli")
```

```solution
from ai_gercek_ai_ile_guvenlik_13 import _cagri_kontrol, _politika_kontrol

def arac_cagrisi_dogrula(cagri, politika):
    _cagri_kontrol(cagri)
    _politika_kontrol(politika)

    cid = cagri["cagri_id"]
    if cagri["arac"] not in politika["izinli_araclar"]:
        return {"cagri_id": cid, "izin_verildi": False, "neden": "yasak_arac"}
    if cagri["hedef"] not in politika["izinli_hedefler"]:
        return {"cagri_id": cid, "izin_verildi": False, "neden": "kapsam_disi_hedef"}
    return {"cagri_id": cid, "izin_verildi": True, "neden": "onaylandi"}
```

```hint
Önce `cagri["arac"] not in politika["izinli_araclar"]` ile `"yasak_arac"` durumunu, ardından `cagri["hedef"] not in politika["izinli_hedefler"]` ile `"kapsam_disi_hedef"` durumunu kontrol et.
```
:::

::: gorev 2 · Tekrar döngüsünü ve adım bütçesini döngü kırıcı ile denetle
`dongu_kirici_kontrol(onayli_cagrilar, azami_adim)` işlevini yaz.

Kurallar:
- `onayli_cagrilar`: `list` olmalı ve içindeki her öğe 1. görevdeki çağrı şemasına uymalıdır; `azami_adim` pozitif `int` (`bool` hariç) olmalıdır (aksi halde `ValueError` yükselt).
- Çağrıları sırayla işle:
  1. Eğer `(cagri["arac"], cagri["hedef"])` ikilisi daha önce çalıştırılmışsa döngüyü `durdurma_nedeni = "tekrar_dongusu"` ile sonlandır (`break`).
  2. Eğer halihazırda çalıştırılan çağrı sayısı `azami_adim` sınırına ulaşmışsa (`len(calistirilan_idleri) >= azami_adim`), döngüyü `durdurma_nedeni = "butce_asimi"` ile sonlandır (`break`).
  3. Aksi halde çağrının `cagri_id` değerini `calistirilan_idleri` listesine ekle.
- `{"calistirilan_idleri": calistirilan_idleri, "durdurma_nedeni": durdurma_nedeni}` sözlüğünü döndür.

```starter
def dongu_kirici_kontrol(onayli_cagrilar, azami_adim):
    # HATA: Tekrar döngüsünü ve adım bütçesini kontrol etmeden tümünü çalıştırıyor.
    return {
        "calistirilan_idleri": [c["cagri_id"] for c in onayli_cagrilar],
        "durdurma_nedeni": None,
    }

print(dongu_kirici_kontrol([{"cagri_id": "c1", "arac": "a", "hedef": "h"}], 2))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-13")
```

```test
need("dongu_kirici_kontrol")

C1 = {"cagri_id": "c1", "arac": "http_baslik_oku", "hedef": "lab.local"}
C2 = {"cagri_id": "c2", "arac": "dns_kayit_sorgula", "hedef": "lab.local"}
C3_TEKRAR = {"cagri_id": "c3", "arac": "http_baslik_oku", "hedef": "lab.local"}
C4 = {"cagri_id": "c4", "arac": "sertifika_ozeti", "hedef": "lab.local"}

def sozlesme(fn):
    try:
        r_normal = fn([C1, C2], 2)
        if r_normal != {"calistirilan_idleri": ["c1", "c2"], "durdurma_nedeni": None}:
            return False

        r_tekrar = fn([C1, C2, C3_TEKRAR], 5)
        if r_tekrar != {"calistirilan_idleri": ["c1", "c2"], "durdurma_nedeni": "tekrar_dongusu"}:
            return False

        r_butce = fn([C1, C2, C4], 2)
        if r_butce != {"calistirilan_idleri": ["c1", "c2"], "durdurma_nedeni": "butce_asimi"}:
            return False

        for c_in, a_in in [
            (None, 2),
            ("metin", 2),
            ([{}], 2),
            ([C1], 0),
            ([C1], -1),
            ([C1], True),
            ([C1], "2"),
        ]:
            try:
                fn(c_in, a_in)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(dongu_kirici_kontrol), "dongu_kirici_kontrol: tekrar döngüsünü ve bütçe aşımını zamanında durdurmalı")
ok(not sozlesme(lambda c, a: {"calistirilan_idleri": ["c1", "c2"], "durdurma_nedeni": None}), "mutasyon: durdurma nedenini yok sayan işlev reddedilmeli")
```

```solution
from ai_gercek_ai_ile_guvenlik_13 import _cagri_kontrol

def dongu_kirici_kontrol(onayli_cagrilar, azami_adim):
    if not isinstance(onayli_cagrilar, list):
        raise ValueError("onayli_cagrilar liste olmalı")
    if isinstance(azami_adim, bool) or not isinstance(azami_adim, int) or azami_adim <= 0:
        raise ValueError("azami_adim pozitif tam sayı olmalı")

    kabul_edilen = []
    gorulen = set()
    durdurma_nedeni = None

    for c in onayli_cagrilar:
        _cagri_kontrol(c)
        anahtar = (c["arac"], c["hedef"])
        if anahtar in gorulen:
            durdurma_nedeni = "tekrar_dongusu"
            break
        if len(kabul_edilen) >= azami_adim:
            durdurma_nedeni = "butce_asimi"
            break
        gorulen.add(anahtar)
        kabul_edilen.append(c["cagri_id"])

    return {
        "calistirilan_idleri": kabul_edilen,
        "durdurma_nedeni": durdurma_nedeni,
    }
```

```hint
Her adımda `(c["arac"], c["hedef"])` ikilisini `gorulen` kümesinde kontrol et; ardından `len(kabul_edilen) >= azami_adim` ise `"butce_asimi"` ile çık.
```
:::

::: gorev 3 · Kapsam kilidi ve döngü kırıcı ile keşif ajanını güvenli çalıştır
`kesif_ajani_calistir(cagrilar, politika)` işlevini yaz.

Kurallar:
- `cagrilar`: boş olmayan `list`; her öğesi çağrı şemasına uymalı ve `cagri_id` değerleri benzersiz olmalıdır.
- `politika`: 1. görevdeki politika şemasına uymalıdır (aksi halde `ValueError` yükselt).
- Her çağrıyı önce `arac_cagrisi_dogrula` mantığıyla denetle:
  - `izin_verildi == False` olanları `engellenenler[cagri_id] = neden` olarak kaydet.
  - `izin_verildi == True` olanları sırasını koruyarak `onaylilar` listesine al.
- `onaylilar` listesini `dongu_kirici_kontrol(onaylilar, politika["azami_adim"])` ile çalıştır.
- `{"calistirilan_idleri": ..., "engellenenler": ..., "durdurma_nedeni": ...}` sözlüğünü döndür.

```starter
from ai_ile_guvenlik_veri import json_yukle

politika = json_yukle("kapsam_politikasi.json")
cagrilar = json_yukle("ajan_cagri_izleri.json")["cagrilar"]

def kesif_ajani_calistir(cagrilar, politika):
    # HATA: Kapsam kilidini ve döngü kırıcıyı birleştirmiyor.
    return {
        "calistirilan_idleri": [],
        "engellenenler": {},
        "durdurma_nedeni": None,
    }

print(kesif_ajani_calistir(cagrilar, politika))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-13")
```

```test
need("kesif_ajani_calistir")
from ai_ile_guvenlik_veri import json_yukle

POLITIKA = json_yukle("kapsam_politikasi.json")
CAGRILAR = json_yukle("ajan_cagri_izleri.json")["cagrilar"]

def sozlesme(fn):
    try:
        r = fn(CAGRILAR, POLITIKA)
        if r != {
            "calistirilan_idleri": ["c-1", "c-4"],
            "engellenenler": {
                "c-2": "yasak_arac",
                "c-3": "kapsam_disi_hedef",
            },
            "durdurma_nedeni": "tekrar_dongusu",
        }:
            return False

        for c_in, p_in in [
            (None, POLITIKA),
            (123, POLITIKA),
            ([], POLITIKA),
            ([CAGRILAR[0], CAGRILAR[0]], POLITIKA),
            (CAGRILAR, None),
            (CAGRILAR, {}),
        ]:
            try:
                fn(c_in, p_in)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(kesif_ajani_calistir), "kesif_ajani_calistir: kapsam dışı çağrıları engelleyip onaylıları döngü kırıcıyla yürütmeli")
ok(not sozlesme(lambda c, p: {"calistirilan_idleri": ["c-1", "c-4"], "engellenenler": {}, "durdurma_nedeni": None}), "mutasyon: engellenen çağrıları silen işlev reddedilmeli")
```

```solution
from ai_gercek_ai_ile_guvenlik_13 import (
    _politika_kontrol,
    arac_cagrisi_dogrula_referans as _dogrula,
    dongu_kirici_kontrol_referans as _dongu_kirici,
)

def kesif_ajani_calistir(cagrilar, politika):
    if not isinstance(cagrilar, list) or not cagrilar:
        raise ValueError("cagrilar boş olmayan liste olmalı")
    _politika_kontrol(politika)

    onaylilar = []
    engellenenler = {}
    gorulen_id = set()

    for c in cagrilar:
        sonuc = _dogrula(c, politika)
        cid = sonuc["cagri_id"]
        if cid in gorulen_id:
            raise ValueError("tekrarlanan cagri_id")
        gorulen_id.add(cid)
        if sonuc["izin_verildi"]:
            onaylilar.append(c)
        else:
            engellenenler[cid] = sonuc["neden"]

    dongu = _dongu_kirici(onaylilar, politika["azami_adim"])
    return {
        "calistirilan_idleri": dongu["calistirilan_idleri"],
        "engellenenler": engellenenler,
        "durdurma_nedeni": dongu["durdurma_nedeni"],
    }
```

```hint
Önce her çağrıyı doğrulayıp `izin_verildi` olanları `onaylilar` listesine, diğerlerini `engellenenler` sözlüğüne ayır; sonra `onaylilar` listesini döngü kırıcıya ver.
```
:::

::: gorev Gerçek deney · Yerel modelle araç çağıran keşif ajanı ve kapsam kilidi deneyi
Önceki üç görevde yazdığın `arac_cagrisi_dogrula`, `dongu_kirici_kontrol` ve `kesif_ajani_calistir` işlevlerini bu adımda birleştir.

Canlı deneyde:
1. Yerel Ollama modeli (`ai_lab.SohbetOturumu(araclar_gerekli=True)`) salt-okunur `http_baslik_oku` aracını `127.0.0.1:8080` hedefi için çağırır.
2. Kapsam içi, yasak araç (`dosya_sil`), kapsam dışı hedef (`dis-sunucu.example`) ve tekrar döngüsü içeren çağrı dizisi senin yazdığın `kesif_ajani_calistir` yürütücüsünden geçirilir.
3. Yalnızca kapsam içi tekil çağrıların çalıştırıldığı doğrulanır.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def arac_cagrisi_dogrula(cagri, politika):
    return {}

def dongu_kirici_kontrol(onayli_cagrilar, azami_adim):
    return {}

def kesif_ajani_calistir(cagrilar, politika):
    return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_ile_guvenlik_13 as deney
    deney.goster(arac_cagrisi_dogrula, dongu_kirici_kontrol, kesif_ajani_calistir)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-13")
```

```test
import ai_lab
from sandbox import ai_gercek_ai_ile_guvenlik_13 as D

checks = []
_base_ok = ok
def ok(kosul, mesaj):
    checks.append(bool(kosul))
    return _base_ok(kosul, mesaj)

for ad in ("arac_cagrisi_dogrula", "dongu_kirici_kontrol", "kesif_ajani_calistir"):
    need(ad)

sorun = ai_lab.kod_denetimi(
    src,
    ("arac_cagrisi_dogrula_referans", "dongu_kirici_kontrol_referans", "kesif_ajani_calistir_referans"),
)
ok(not sorun, "laboratuvar yamalanmamalı, referans işlevler çağrılmamalı")

def _on_sozlesme():
    try:
        for c_in, p_in in [(None, D.POLITIKA), (D.ORNEK_CAGRILAR[0], {})]:
            try:
                arac_cagrisi_dogrula(c_in, p_in)
                return False
            except ValueError:
                pass
        for l_in, a_in in [(None, 2), ([D.ORNEK_CAGRILAR[0]], 0)]:
            try:
                dongu_kirici_kontrol(l_in, a_in)
                return False
            except ValueError:
                pass
        for c_list in (None, [], [D.ORNEK_CAGRILAR[0], D.ORNEK_CAGRILAR[0]]):
            try:
                kesif_ajani_calistir(c_list, D.POLITIKA)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(_on_sozlesme(), "sentetik ön kontrol: kapsam kilidi ve döngü kırıcı kuralları tam")

if not all(checks):
    stop()

try:
    r = D.deney(arac_cagrisi_dogrula, dongu_kirici_kontrol, kesif_ajani_calistir)
except Exception as e:
    ok(False, f"GERÇEK KEŞİF AJANI DENEYİ YAPILAMADI: {type(e).__name__}: {e}")
    stop()

for ad, deger in r["kontroller"].items():
    ok(deger, "gerçek deney: " + ad)

ai_lab.kanit_yaz("ile-guvenlik-13-ajan", {
    "kaynak": "gercek",
    "kabul": all(checks),
    "ders": "ai-ile-guvenlik-13",
    "ortam": r["ortam"],
    "ayarlar": r["ayarlar"],
    "deney": r,
    "ozet": r["ozet"],
})
o = r["ozet"]
ok(
    True,
    f"BULGU ({o['model']}): calistirilan={o['calistirilan']}, engellenenler={o['engellenenler']}, durdurma={o['durdurma_nedeni']}.",
)
```

```solution
import ai_lab
from sandbox.ai_gercek_ai_ile_guvenlik_13 import _cagri_kontrol, _politika_kontrol

def arac_cagrisi_dogrula(cagri, politika):
    _cagri_kontrol(cagri)
    _politika_kontrol(politika)

    cid = cagri["cagri_id"]
    if cagri["arac"] not in politika["izinli_araclar"]:
        return {"cagri_id": cid, "izin_verildi": False, "neden": "yasak_arac"}
    if cagri["hedef"] not in politika["izinli_hedefler"]:
        return {"cagri_id": cid, "izin_verildi": False, "neden": "kapsam_disi_hedef"}
    return {"cagri_id": cid, "izin_verildi": True, "neden": "onaylandi"}

def dongu_kirici_kontrol(onayli_cagrilar, azami_adim):
    if not isinstance(onayli_cagrilar, list):
        raise ValueError("onayli_cagrilar liste olmalı")
    if isinstance(azami_adim, bool) or not isinstance(azami_adim, int) or azami_adim <= 0:
        raise ValueError("azami_adim pozitif tam sayı olmalı")

    kabul_edilen = []
    gorulen = set()
    durdurma_nedeni = None

    for c in onayli_cagrilar:
        _cagri_kontrol(c)
        anahtar = (c["arac"], c["hedef"])
        if anahtar in gorulen:
            durdurma_nedeni = "tekrar_dongusu"
            break
        if len(kabul_edilen) >= azami_adim:
            durdurma_nedeni = "butce_asimi"
            break
        gorulen.add(anahtar)
        kabul_edilen.append(c["cagri_id"])

    return {
        "calistirilan_idleri": kabul_edilen,
        "durdurma_nedeni": durdurma_nedeni,
    }

def kesif_ajani_calistir(cagrilar, politika):
    if not isinstance(cagrilar, list) or not cagrilar:
        raise ValueError("cagrilar boş olmayan liste olmalı")
    _politika_kontrol(politika)

    onaylilar = []
    engellenenler = {}
    gorulen_id = set()

    for c in cagrilar:
        sonuc = arac_cagrisi_dogrula(c, politika)
        cid = sonuc["cagri_id"]
        if cid in gorulen_id:
            raise ValueError("tekrarlanan cagri_id")
        gorulen_id.add(cid)
        if sonuc["izin_verildi"]:
            onaylilar.append(c)
        else:
            engellenenler[cid] = sonuc["neden"]

    dongu = dongu_kirici_kontrol(onaylilar, politika["azami_adim"])
    return {
        "calistirilan_idleri": dongu["calistirilan_idleri"],
        "engellenenler": engellenenler,
        "durdurma_nedeni": dongu["durdurma_nedeni"],
    }

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_ile_guvenlik_13 as deney
    deney.goster(arac_cagrisi_dogrula, dongu_kirici_kontrol, kesif_ajani_calistir)
```

```hint
Önceki üç görevdeki `arac_cagrisi_dogrula`, `dongu_kirici_kontrol` ve `kesif_ajani_calistir` işlevlerini birleştir.
```
:::
