---
id: ai-guvence-05
title: Tekrarlanabilirlik ve Kanıt Paketi
summary: Deney manifestini ve dosya özetlerini doğrula; iki çalıştırmanın kanıt paketlerini karşılaştırıp farkları raporla.
timeout: 45
---

::: anlat Gerçek kanıt paketini bil, sentetik temsili ayırt et
Tekrarlanabilirlik çalışması veri ve model sürümünü, rastgelelik tohumunu, ortam bilgisini ve çıktı dosyalarının bütünlüğünü birlikte kaydeder. Tohum tek başına yeterli değildir; farklı veri, kütüphane veya çıktı özeti aynı tohumla bile farklı sonuç üretebilir.

| Katman | Gerçek tekrarlanabilirlik paketi ne içerir? | Bu ders ne kullanır? | Ne söyleyemez? |
|---|---|---|---|
| Ortam manifesti | Python/kütüphane sürümleri, kilit dosyası (lockfile), donanım/CUDA bilgisi ve rastgelelik tohumu | İlk 3 görevde `veri/manifest.json` sentetik manifesti; son görevde canlı `sys.version` ve `sklearn.__version__` manifesti | Aynı manifest farklı GPU mimarilerinde kayan nokta yuvarlama farklarını tamamen sıfırlamaz |
| Dosya bütünlüğü | Üretilen ağırlık ve metrik dosyalarının göreli yolu, bayt boyutu ve SHA-256 özeti | İlk 3 görevde `veri/dosyalar.json` sentetik özetleri; son görevde diskte üretilen gerçek `model_agirlik.json` ve `cikti/metrik.json` SHA-256 özetleri | Birebir aynı SHA-256 özeti deneyin yalnızca deterministik olarak tekrarlandığını kanıtlar; metodolojik doğruluğu kanıtlamaz |

> [!NOT]
> İlk üç görevde örnek dosyalar çalışma klasörünün `veri/` altına kopyalanır: `veri/manifest.json` ve `veri/dosyalar.json` (tümü **sentetik**). Bu dosyaları kodundan okuyup inceleyebilirsin; ancak her çalıştırmada temiz kopya yeniden yazılır (**kalıcılık yoktur**). Kontrol adımı bu dosyalardan bağımsız gizli verilerle sınama yapar.
:::

::: anlat Fark raporu yalnız özete bakmaz
Dosya yolu göreli ve normalize edilmiş olmalıdır; mutlak yol, üst dizine çıkış veya yinelenen yol kanıt paketini belirsizleştirir. SHA-256 alanı 64 küçük hexadecimal karakter, boyut ise sıfır veya pozitif tamsayıdır. Aynı özet fakat farklı boyut da değişiklik olarak raporlanır.

İki paket karşılaştırılırken eksik ve eklenen dosyalar yol kümesinin birleşimiyle bulunur. Hiç fark yoksa karar `tekrarlanabilir`, aksi halde `fark_var` olur. Bu karar yalnız verilen manifest ve dosya kayıtlarının eşleştiğini gösterir; bilimsel sonucun doğruluğunu kanıtlamaz.
:::

::: tahmin Kanıt farklarını tahmin et
Üç çıktı satırını yaz:

```python
print(len("a" * 64))
print(sorted({"model.json", "metrik.json"}))
print([p for p in ["a.txt", "b.txt"] if p not in {"a.txt"}])
```

???

```cikti
64
['metrik.json', 'model.json']
['b.txt']
```

Son satır beklenen pakette olup gözlemlenen pakette bulunmayan dosyayı gösterir.
:::

::: gorev 1 · Deney manifestini doğrula
`kanit_manifestu_dogrula(manifest)` işlevini yaz. Manifest tam olarak `id`, `veri_surumu`, `model_surumu`, `tohum`, `ortam` alanlarını taşısın. Kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren stringdir. Veri ve model sürümü başı/sonu boşluğu olmayan boş olmayan stringdir ve kontrol karakteri içeremez. Tohum bool olmayan, sıfır veya pozitif tamsayıdır.

Ortam tam olarak `python` ve `kutuphane` alanlarını içeren sözlüktür; iki değer de sürüm metinleriyle aynı string kurallarını sağlar. Geçersiz veride `ValueError` yükselt. Ortamın da kopyası olan yeni sözlükle döndür ve girdiyi değiştirme.

```starter
from ai_guvence_veri import json_yukle

def kanit_manifestu_dogrula(manifest):
    # KUSURLU BAŞLANGIÇ KODU: iç ortam sözlüğünü kopyalamadan ve alanları denetlemeden döndürüyor!
    return manifest

print("Örnek manifest:", kanit_manifestu_dogrula(json_yukle("veri/manifest.json")))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-05")
```

```test
import copy
M = {"id": "deney-1", "veri_surumu": "veri-v1", "model_surumu": "model-v1", "tohum": 0, "ortam": {"python": "3.12.0", "kutuphane": "sklearn-1.5"}}
def sozlesme(fn):
    try:
        once = copy.deepcopy(M)
        sonuc = fn(M)
        if sonuc != M or M != once or sonuc is M or sonuc["ortam"] is M["ortam"]:
            return False
        if fn(dict(M, id="a" * 64, tohum=42))["tohum"] != 42:
            return False
        bosluklu = {"id": "deney-2", "veri_surumu": "veri v1", "model_surumu": "model v1", "tohum": 0, "ortam": {"python": "python 3.12", "kutuphane": "sklearn 1.5"}}
        if fn(bosluklu) != bosluklu:
            return False
        for manifest in [
            None, [], dict(M, ek=1), dict(M, id=""), dict(M, id="a b"), dict(M, id="a" * 65), dict(M, id=None),
            dict(M, veri_surumu=""), dict(M, veri_surumu=" x"), dict(M, veri_surumu="a\0b"), dict(M, veri_surumu=None),
            dict(M, model_surumu=""), dict(M, model_surumu="x "), dict(M, model_surumu="a\0b"), dict(M, model_surumu=None),
            dict(M, tohum=-1), dict(M, tohum=True), dict(M, tohum=1.0), dict(M, tohum=None),
            dict(M, ortam=None), dict(M, ortam={}), dict(M, ortam=dict(M["ortam"], ek=1)),
            dict(M, ortam=dict(M["ortam"], python="")), dict(M, ortam=dict(M["ortam"], python=" x")),
            dict(M, ortam=dict(M["ortam"], python="a\0b")), dict(M, ortam=dict(M["ortam"], python=None)),
            dict(M, ortam=dict(M["ortam"], kutuphane="")), dict(M, ortam=dict(M["ortam"], kutuphane="x ")),
            dict(M, ortam=dict(M["ortam"], kutuphane="a\0b")), dict(M, ortam=dict(M["ortam"], kutuphane=None)),
        ]:
            try:
                fn(manifest)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kanit_manifestu_dogrula), "manifest, ortam ve tohum kuralları korunmalı")
def m_tohum(manifest):
    return kanit_manifestu_dogrula(dict(manifest, tohum=1))
def m_veri(manifest):
    return kanit_manifestu_dogrula(dict(manifest, veri_surumu="veri-v2"))
def m_ortam(manifest):
    return kanit_manifestu_dogrula(dict(manifest, ortam=dict(manifest["ortam"], python="3.11.0")))
for ad, mutant in [("tohumu değiştiren", m_tohum), ("veriyi değiştiren", m_veri), ("ortamı değiştiren", m_ortam)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kanit_manifestu_dogrula(manifest):
    import re
    if not isinstance(manifest, dict):
        raise ValueError("manifest sözlük olmalı")
    if set(manifest) != {"id", "veri_surumu", "model_surumu", "tohum", "ortam"}:
        raise ValueError("manifest şeması geçersiz")
    if not isinstance(manifest["id"], str):
        raise ValueError("kimlik string olmalı")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", manifest["id"]):
        raise ValueError("kimlik geçersiz")
    for alan in ("veri_surumu", "model_surumu"):
        deger = manifest[alan]
        if not isinstance(deger, str):
            raise ValueError("sürüm string olmalı")
        if not deger or deger != deger.strip():
            raise ValueError("sürüm boşluk biçimi geçersiz")
        if any(ord(k) < 32 for k in deger):
            raise ValueError("sürüm kontrol karakteri içeremez")
    if isinstance(manifest["tohum"], bool) or not isinstance(manifest["tohum"], int):
        raise ValueError("tohum tamsayı olmalı")
    if manifest["tohum"] < 0:
        raise ValueError("tohum negatif olamaz")
    ortam = manifest["ortam"]
    if not isinstance(ortam, dict) or set(ortam) != {"python", "kutuphane"}:
        raise ValueError("ortam şeması geçersiz")
    for alan in ("python", "kutuphane"):
        deger = ortam[alan]
        if not isinstance(deger, str):
            raise ValueError("ortam sürümü string olmalı")
        if not deger or deger != deger.strip():
            raise ValueError("ortam sürümü boşluk biçimi geçersiz")
        if any(ord(k) < 32 for k in deger):
            raise ValueError("ortam sürümü kontrol karakteri içeremez")
    return {"id": manifest["id"], "veri_surumu": manifest["veri_surumu"], "model_surumu": manifest["model_surumu"], "tohum": manifest["tohum"], "ortam": {"python": ortam["python"], "kutuphane": ortam["kutuphane"]}}
```

```hint
Metin doğrulamasını hem sürüm hem ortam alanlarına uygula. Ortam sözlüğünün şemasını ayrıca denetle ve kopyalayarak döndür.
```
:::

::: gorev 2 · Dosya kanıtlarını doğrula ve sırala
`dosya_kanitlarini_dogrula(dosyalar)` işlevini yaz. Dosyalar boş olmayan listedir. Her kayıt tam olarak `yol`, `sha256`, `boyut` alanlarını taşısın. Yol göreli, `/` ayraçlı, boş olmayan stringdir; boş veya `.` ya da `..` parçası, ters eğik çizgi, başta `/` ve kontrol karakteri içeremez. Yollar yinelenemez.

SHA-256 tam 64 küçük hexadecimal karakterlik stringdir. Boyut bool olmayan, sıfır veya pozitif tamsayıdır. Geçersiz veride `ValueError` yükselt. Kayıtları yola göre sıralayıp yeni sözlüklerle döndür ve girdiyi değiştirme.

```starter
from ai_guvence_veri import json_yukle

def dosya_kanitlarini_dogrula(dosyalar):
    # KUSURLU BAŞLANGIÇ KODU: yol geçişini (..) ve SHA-256 biçimini denetlemeden sıralamadan döndürüyor!
    return list(dosyalar) if isinstance(dosyalar, list) else []

print("Örnek dosya kanıtları:", dosya_kanitlarini_dogrula(json_yukle("veri/dosyalar.json")))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-05")
```

```test
import copy
D = [{"yol": "model.json", "sha256": "a" * 64, "boyut": 10}, {"yol": "cikti/metrik.json", "sha256": "b" * 64, "boyut": 0}]
BEKLENEN = [D[1], D[0]]
def sozlesme(fn):
    try:
        once = copy.deepcopy(D)
        sonuc = fn(D)
        if sonuc != BEKLENEN or D != once or any(sonuc[i] is D[i] for i in range(len(D))):
            return False
        if fn([dict(D[0], yol="cikti dosya/model.json")])[0]["yol"] != "cikti dosya/model.json":
            return False
        for dosyalar in [
            None, {}, [], [None], [dict(D[0], ek=1)],
            [dict(D[0], yol="")], [dict(D[0], yol=None)], [dict(D[0], yol="/model.json")],
            [dict(D[0], yol="../model.json")], [dict(D[0], yol="a/../b")], [dict(D[0], yol="a/./b")],
            [dict(D[0], yol="a//b")], [dict(D[0], yol="a\\b")], [dict(D[0], yol="a\0b")],
            [D[0], D[0]], [dict(D[0], sha256="a" * 63)], [dict(D[0], sha256="a" * 65)],
            [dict(D[0], sha256="A" * 64)], [dict(D[0], sha256="g" * 64)], [dict(D[0], sha256=None)],
            [dict(D[0], boyut=-1)], [dict(D[0], boyut=True)], [dict(D[0], boyut=1.0)], [dict(D[0], boyut=None)],
        ]:
            try:
                fn(dosyalar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(dosya_kanitlarini_dogrula), "yol, özet, boyut ve sıralama korunmalı")
def m_yol(dosyalar):
    return dosya_kanitlarini_dogrula([dict(x, yol="ortak.json") for x in dosyalar])
def m_ozet(dosyalar):
    return dosya_kanitlarini_dogrula([dict(x, sha256="c" * 64) for x in dosyalar])
def m_boyut(dosyalar):
    return dosya_kanitlarini_dogrula([dict(x, boyut=0) for x in dosyalar])
for ad, mutant in [("yolları eşitleyen", m_yol), ("özetleri değiştiren", m_ozet), ("boyutları silen", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def dosya_kanitlarini_dogrula(dosyalar):
    import re
    if not isinstance(dosyalar, list):
        raise ValueError("dosyalar liste olmalı")
    if not dosyalar:
        raise ValueError("dosyalar boş olamaz")
    yollar = set()
    sonuc = []
    for dosya in dosyalar:
        if not isinstance(dosya, dict):
            raise ValueError("dosya sözlük olmalı")
        if set(dosya) != {"yol", "sha256", "boyut"}:
            raise ValueError("dosya şeması geçersiz")
        yol = dosya["yol"]
        if not isinstance(yol, str):
            raise ValueError("yol string olmalı")
        if not yol:
            raise ValueError("yol boş olamaz")
        if yol.startswith("/"):
            raise ValueError("yol göreli olmalı")
        if "\\" in yol:
            raise ValueError("yol ayıracı geçersiz")
        if any(ord(k) < 32 for k in yol):
            raise ValueError("yol kontrol karakteri içeremez")
        if any(parca in ("", ".", "..") for parca in yol.split("/")):
            raise ValueError("yol normalize edilmemiş")
        if yol in yollar:
            raise ValueError("yol yinelenemez")
        if not isinstance(dosya["sha256"], str):
            raise ValueError("özet string olmalı")
        if not re.fullmatch(r"[0-9a-f]{64}", dosya["sha256"]):
            raise ValueError("SHA-256 geçersiz")
        boyut = dosya["boyut"]
        if isinstance(boyut, bool) or not isinstance(boyut, int):
            raise ValueError("boyut tamsayı olmalı")
        if boyut < 0:
            raise ValueError("boyut negatif olamaz")
        yollar.add(yol)
        sonuc.append({"yol": yol, "sha256": dosya["sha256"], "boyut": boyut})
    return sorted(sonuc, key=lambda x: x["yol"])
```

```hint
Yolu hem genel biçim hem parçalar yönünden denetle. Özet desenini ve boyut türünü ayrı doğrulayıp kayıtları kopyala.
```
:::

::: gorev 3 · İki kanıt paketinin farkını raporla
`kanit_fark_raporu(beklenen, gozlemlenen)` işlevini yaz. Beklenen paket ikinci görevdeki kuralları sağlayan boş olmayan listedir. Gözlemlenen paket aynı kayıt kurallarını sağlar fakat boş liste olabilir. Geçersiz veride `ValueError` yükselt.

Yol kümelerini karşılaştır. Beklenende olup gözlemlenende olmayan dosya `eksik`, yalnız gözlemlenende olan `eklenen`, iki tarafta olup özeti veya boyutu farklı olan `degisti` olsun. `{"karar":KARAR,"degisiklik_sayisi":N,"farklar":[FARK,...]}` döndür. Her fark `{"yol":YOL,"durum":DURUM,"beklenen":KAYIT_VEYA_NONE,"gozlemlenen":KAYIT_VEYA_NONE}` biçiminde ve yola göre sıralı olsun. Hiç fark yoksa karar `tekrarlanabilir`, aksi halde `fark_var` olur. Kayıtları kopyala ve girdileri değiştirme.

```starter
from ai_guvence_veri import json_yukle

def kanit_fark_raporu(beklenen, gozlemlenen):
    # KUSURLU BAŞLANGIÇ KODU: yalnız dosya sayılarını karşılaştırıp içerik/boyut farklarını gözden kaçırıyor!
    fark_yok = len(beklenen or []) == len(gozlemlenen or [])
    return {"karar": "tekrarlanabilir" if fark_yok else "fark_var", "degisiklik_sayisi": 0, "farklar": []}

ornek = json_yukle("veri/dosyalar.json")
print("Örnek fark raporu:", kanit_fark_raporu(ornek, ornek[:1]))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_guvence_veri import hazirla
hazirla("ai-guvence-05")
```

```test
import copy
B = [{"yol": "model.json", "sha256": "a" * 64, "boyut": 10}, {"yol": "metrik.json", "sha256": "b" * 64, "boyut": 20}]
G = list(reversed(B))
def sozlesme(fn):
    try:
        bonce = copy.deepcopy(B)
        gonce = copy.deepcopy(G)
        if fn(B, G) != {"karar": "tekrarlanabilir", "degisiklik_sayisi": 0, "farklar": []} or B != bonce or G != gonce:
            return False
        degisen = [{"yol": "model.json", "sha256": "c" * 64, "boyut": 10}, {"yol": "sonuc.txt", "sha256": "d" * 64, "boyut": 0}]
        sonuc = fn(B, degisen)
        if sonuc["karar"] != "fark_var" or sonuc["degisiklik_sayisi"] != 3:
            return False
        if [(x["yol"], x["durum"]) for x in sonuc["farklar"]] != [("metrik.json", "eksik"), ("model.json", "degisti"), ("sonuc.txt", "eklenen")]:
            return False
        if sonuc["farklar"][0]["beklenen"] != B[1] or sonuc["farklar"][0]["gozlemlenen"] is not None:
            return False
        if sonuc["farklar"][1]["beklenen"] != B[0] or sonuc["farklar"][1]["gozlemlenen"] != degisen[0]:
            return False
        if sonuc["farklar"][2]["beklenen"] is not None or sonuc["farklar"][2]["gozlemlenen"] != degisen[1]:
            return False
        boyut = fn(B, [B[0], dict(B[1], boyut=21)])
        if boyut["degisiklik_sayisi"] != 1 or boyut["farklar"][0]["durum"] != "degisti":
            return False
        if fn(B, [])["degisiklik_sayisi"] != 2:
            return False
        bosluklu = [{"yol": "cikti dosya/model.json", "sha256": "f" * 64, "boyut": 0}]
        if fn(bosluklu, bosluklu)["karar"] != "tekrarlanabilir":
            return False
        for beklenen, gozlemlenen in [
            (None, G), (B, None), ({}, G), (B, {}), ([], []), ([None], G), (B, [None]),
            ([dict(B[0], ek=1)], G), (B, [dict(B[0], ek=1)]),
            ([dict(B[0], yol="../x")], G), (B, [dict(B[0], yol="/x")]),
            ([dict(B[0], yol="a//b")], G), (B, [dict(B[0], yol="a\\b")]),
            ([B[0], B[0]], G), (B, [G[0], G[0]]),
            ([dict(B[0], sha256="a" * 63)], G), (B, [dict(B[0], sha256="A" * 64)]),
            ([dict(B[0], boyut=-1)], G), (B, [dict(B[0], boyut=True)]), (B, [dict(B[0], boyut=1.0)]),
        ]:
            try:
                fn(beklenen, gozlemlenen)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kanit_fark_raporu), "eksik, eklenen, değişen kayıtlar ve karar korunmalı")
def m_ozet(beklenen, gozlemlenen):
    return kanit_fark_raporu(beklenen, [dict(x, sha256="e" * 64) for x in gozlemlenen])
def m_sil(beklenen, gozlemlenen):
    return kanit_fark_raporu(beklenen, gozlemlenen[:1])
def m_boyut(beklenen, gozlemlenen):
    return kanit_fark_raporu(beklenen, [dict(x, boyut=0) for x in gozlemlenen])
for ad, mutant in [("özetleri değiştiren", m_ozet), ("dosyaları silen", m_sil), ("boyutları değiştiren", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kanit_fark_raporu(beklenen, gozlemlenen):
    import re
    def dogrula(dosyalar, bos_olabilir):
        if not isinstance(dosyalar, list):
            raise ValueError("dosyalar liste olmalı")
        if not dosyalar and not bos_olabilir:
            raise ValueError("beklenen paket boş olamaz")
        yollar = set()
        sonuc = {}
        for dosya in dosyalar:
            if not isinstance(dosya, dict):
                raise ValueError("dosya sözlük olmalı")
            if set(dosya) != {"yol", "sha256", "boyut"}:
                raise ValueError("dosya şeması geçersiz")
            yol = dosya["yol"]
            if not isinstance(yol, str):
                raise ValueError("yol string olmalı")
            if not yol:
                raise ValueError("yol boş olamaz")
            if yol.startswith("/"):
                raise ValueError("yol göreli olmalı")
            if "\\" in yol:
                raise ValueError("yol ayıracı geçersiz")
            if any(ord(k) < 32 for k in yol):
                raise ValueError("yol kontrol karakteri içeremez")
            if any(parca in ("", ".", "..") for parca in yol.split("/")):
                raise ValueError("yol normalize edilmemiş")
            if yol in yollar:
                raise ValueError("yol yinelenemez")
            if not isinstance(dosya["sha256"], str):
                raise ValueError("özet string olmalı")
            if not re.fullmatch(r"[0-9a-f]{64}", dosya["sha256"]):
                raise ValueError("SHA-256 geçersiz")
            boyut = dosya["boyut"]
            if isinstance(boyut, bool) or not isinstance(boyut, int):
                raise ValueError("boyut tamsayı olmalı")
            if boyut < 0:
                raise ValueError("boyut negatif olamaz")
            yollar.add(yol)
            sonuc[yol] = {"yol": yol, "sha256": dosya["sha256"], "boyut": boyut}
        return sonuc
    b = dogrula(beklenen, False)
    g = dogrula(gozlemlenen, True)
    farklar = []
    for yol in sorted(set(b) | set(g)):
        if yol not in g:
            durum = "eksik"
        elif yol not in b:
            durum = "eklenen"
        elif b[yol]["sha256"] != g[yol]["sha256"] or b[yol]["boyut"] != g[yol]["boyut"]:
            durum = "degisti"
        else:
            continue
        farklar.append({"yol": yol, "durum": durum, "beklenen": dict(b[yol]) if yol in b else None, "gozlemlenen": dict(g[yol]) if yol in g else None})
    return {"karar": "fark_var" if farklar else "tekrarlanabilir", "degisiklik_sayisi": len(farklar), "farklar": farklar}
```

```hint
İki paketi yol anahtarlı kopya sözlüklere çevir. Birleşim kümesini sıralı gez; eksik ve eklenen durumlarını değişiklikten önce ayır.
```
:::

::: anlat Disk üzerinde gerçek deney paketlerinin SHA-256 tekrarlanabilirlik denetimi
İlk üç görevde manifest doğrulamayı, dosya kanıtı sıralamayı ve iki paket arasındaki fark raporunu sentetik dosyalar üzerinde kurdun. Şimdi aynı üç işlevi **disk üzerinde gerçekten eğitilen `scikit-learn` (`LogisticRegression`) deney paketlerine** bağlıyoruz:

1. Geçerli Python ve `scikit-learn` sürümlerini içeren canlı manifest `kanit_manifestu_dogrula` ile doğrulanır.
2. Aynı tohumla (`tohum=42`) iki ayrı klasörde model eğitilip `model_agirlik.json` ve `cikti/metrik.json` dosyaları gerçekten diske yazılır; `hashlib.sha256` özetleri ve bayt boyutları `dosya_kanitlarini_dogrula` ve `kanit_fark_raporu` ile karşılaştırılarak `tekrarlanabilir` kararı doğrulanır.
3. Farklı tohumla (`tohum=99`), silinmiş metrik dosyası ve eklenmiş not dosyasıyla üretilen üçüncü klasör karşılaştırılarak `degisti`, `eksik` ve `eklenen` durumlarının üçü birden canlı dosyalarda yakalanır.
:::

::: gorev Gerçek deney · Canlı deney dosyalarında SHA-256 kanıt paketi ve fark doğrulaması
Önceki üç görevde yazdığın `kanit_manifestu_dogrula(manifest)`, `dosya_kanitlarini_dogrula(dosyalar)` ve `kanit_fark_raporu(beklenen, gozlemlenen)` işlevlerini burada birleştir.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 180
```

```starter
import re
import ai_lab
from sandbox import ai_gercek_ai_guvence_05 as L

def kanit_manifestu_dogrula(manifest):
    # KUSURLU BAŞLANGIÇ KODU: doğrulama yapmadan girdi sözlüğünü döndürüyor!
    return manifest

def dosya_kanitlarini_dogrula(dosyalar):
    return list(dosyalar) if isinstance(dosyalar, list) else []

def kanit_fark_raporu(beklenen, gozlemlenen):
    return {"karar": "tekrarlanabilir", "degisiklik_sayisi": 0, "farklar": []}

if ai_lab.CALISTIR:
    L.goster(kanit_manifestu_dogrula, dosya_kanitlarini_dogrula, kanit_fark_raporu)
```

```test
import copy
import ai_lab
from sandbox import ai_gercek_ai_guvence_05 as L

checks = []
_base_ok = ok
def ok(kosul, mesaj):
    checks.append(bool(kosul))
    return _base_ok(kosul, mesaj)

for s in ai_lab.kod_denetimi(src, yasak=("kanit_manifestu_dogrula_referans", "dosya_kanitlarini_dogrula_referans", "kanit_fark_raporu_referans", "kanit_yaz")):
    ok(False, f"Güvenlik/kopya denetimi: {s}")
if not all(checks):
    stop()

def _sozlesme_kontrol():
    try:
        M = {"id": "deney-1", "veri_surumu": "veri-v1", "model_surumu": "model-v1", "tohum": 0, "ortam": {"python": "3.12.0", "kutuphane": "sklearn-1.5"}}
        sm = kanit_manifestu_dogrula(M)
        if sm != M or sm is M or sm["ortam"] is M["ortam"]:
            return False
        for bm in [None, dict(M, ek=1), dict(M, tohum=True), dict(M, ortam={})]:
            try:
                kanit_manifestu_dogrula(bm)
                return False
            except ValueError:
                pass

        D = [{"yol": "model.json", "sha256": "a" * 64, "boyut": 10}, {"yol": "cikti/metrik.json", "sha256": "b" * 64, "boyut": 0}]
        if dosya_kanitlarini_dogrula(D) != [D[1], D[0]]:
            return False
        for bd in [None, [], [D[0], D[0]], [dict(D[0], yol="../x")], [dict(D[0], sha256="A" * 64)]]:
            try:
                dosya_kanitlarini_dogrula(bd)
                return False
            except ValueError:
                pass

        if kanit_fark_raporu(D, list(reversed(D))) != {"karar": "tekrarlanabilir", "degisiklik_sayisi": 0, "farklar": []}:
            return False
        deg = [{"yol": "model.json", "sha256": "c" * 64, "boyut": 10}, {"yol": "sonuc.txt", "sha256": "d" * 64, "boyut": 0}]
        sf = kanit_fark_raporu(D, deg)
        if sf["karar"] != "fark_var" or [(x["yol"], x["durum"]) for x in sf["farklar"]] != [("cikti/metrik.json", "eksik"), ("model.json", "degisti"), ("sonuc.txt", "eklenen")]:
            return False
        return True
    except Exception:
        return False

ok(_sozlesme_kontrol(), "kanit_manifestu_dogrula, dosya_kanitlarini_dogrula ve kanit_fark_raporu sözleşme kontrollerini geçmeli")
if not all(checks):
    stop()

try:
    rapor = L.deney(kanit_manifestu_dogrula, dosya_kanitlarini_dogrula, kanit_fark_raporu)
except ai_lab.GercekLabYok as e:
    ok(False, str(e))
    stop()
except Exception as e:
    ok(False, f"GERÇEK KANIT PAKETİ DENEYİ YAPILAMADI: {type(e).__name__}: {e}")
    stop()

k = rapor["kontroller"]
ok(k["manifest_uyumu"], f"kanit_manifestu_dogrula canlı manifestte referansla uyuşmalı: {rapor['manifest']}")
ok(k["dosya_kanit_uyumu"], f"dosya_kanitlarini_dogrula canlı SHA-256 dosya özetlerinde referansla uyuşmalı: {rapor['dosyalar']}")
ok(k["ayni_tohum_tekrarlanabilir"] and k["farkli_tohum_fark_var"], f"kanit_fark_raporu aynı tohumda 'tekrarlanabilir', farklı tohum/dosyada 3 farkla 'fark_var' üretmeli: {rapor['farkli_tohum_raporu']}")

kabul = all(checks)
kanit_yolu = ai_lab.kanit_yaz("guvence-05-kanit-paketi", dict(rapor, kaynak="gercek", kabul=kabul))
o = rapor["ozet"]
print(f"GERÇEK KANIT PAKETİ DENEYİ: ayni_tohum={o['ayni_tohum_karar']} farkli_tohum={o['farkli_tohum_karar']} ({o['farkli_tohum_degisiklik_sayisi']} fark) kanıt={kanit_yolu}")
```

```solution
import re
import ai_lab
from sandbox import ai_gercek_ai_guvence_05 as L

def kanit_manifestu_dogrula(manifest):
    if not isinstance(manifest, dict) or set(manifest) != {"id", "veri_surumu", "model_surumu", "tohum", "ortam"}:
        raise ValueError("manifest şeması geçersiz")
    if not isinstance(manifest["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", manifest["id"]):
        raise ValueError("kimlik geçersiz")
    for alan in ("veri_surumu", "model_surumu"):
        deger = manifest[alan]
        if not isinstance(deger, str) or not deger or deger != deger.strip() or any(ord(k) < 32 for k in deger):
            raise ValueError("sürüm geçersiz")
    if isinstance(manifest["tohum"], bool) or not isinstance(manifest["tohum"], int) or manifest["tohum"] < 0:
        raise ValueError("tohum geçersiz")
    ortam = manifest["ortam"]
    if not isinstance(ortam, dict) or set(ortam) != {"python", "kutuphane"}:
        raise ValueError("ortam şeması geçersiz")
    for alan in ("python", "kutuphane"):
        deger = ortam[alan]
        if not isinstance(deger, str) or not deger or deger != deger.strip() or any(ord(k) < 32 for k in deger):
            raise ValueError("ortam sürümü geçersiz")
    return {"id": manifest["id"], "veri_surumu": manifest["veri_surumu"], "model_surumu": manifest["model_surumu"], "tohum": manifest["tohum"], "ortam": {"python": ortam["python"], "kutuphane": ortam["kutuphane"]}}

def _dosya_dogrula(dosyalar, bos_olabilir=False):
    if not isinstance(dosyalar, list):
        raise ValueError("dosyalar liste olmalı")
    if not dosyalar and not bos_olabilir:
        raise ValueError("dosyalar boş olamaz")
    yollar = set()
    sonuc = []
    for dosya in dosyalar:
        if not isinstance(dosya, dict) or set(dosya) != {"yol", "sha256", "boyut"}:
            raise ValueError("dosya şeması geçersiz")
        yol = dosya["yol"]
        if not isinstance(yol, str) or not yol or yol.startswith("/") or "\\" in yol or any(ord(k) < 32 for k in yol) or any(parca in ("", ".", "..") for parca in yol.split("/")) or yol in yollar:
            raise ValueError("yol geçersiz")
        if not isinstance(dosya["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", dosya["sha256"]):
            raise ValueError("SHA-256 geçersiz")
        boyut = dosya["boyut"]
        if isinstance(boyut, bool) or not isinstance(boyut, int) or boyut < 0:
            raise ValueError("boyut geçersiz")
        yollar.add(yol)
        sonuc.append({"yol": yol, "sha256": dosya["sha256"], "boyut": boyut})
    return sorted(sonuc, key=lambda x: x["yol"])

def dosya_kanitlarini_dogrula(dosyalar):
    return _dosya_dogrula(dosyalar, False)

def kanit_fark_raporu(beklenen, gozlemlenen):
    b = {x["yol"]: x for x in _dosya_dogrula(beklenen, False)}
    g = {x["yol"]: x for x in _dosya_dogrula(gozlemlenen, True)}
    farklar = []
    for yol in sorted(set(b) | set(g)):
        if yol not in g:
            durum = "eksik"
        elif yol not in b:
            durum = "eklenen"
        elif b[yol]["sha256"] != g[yol]["sha256"] or b[yol]["boyut"] != g[yol]["boyut"]:
            durum = "degisti"
        else:
            continue
        farklar.append({"yol": yol, "durum": durum, "beklenen": dict(b[yol]) if yol in b else None, "gozlemlenen": dict(g[yol]) if yol in g else None})
    return {"karar": "fark_var" if farklar else "tekrarlanabilir", "degisiklik_sayisi": len(farklar), "farklar": farklar}

if ai_lab.CALISTIR:
    L.goster(kanit_manifestu_dogrula, dosya_kanitlarini_dogrula, kanit_fark_raporu)
```

```hint
Önceki üç görevde yazdığın `kanit_manifestu_dogrula`, `dosya_kanitlarini_dogrula` ve `kanit_fark_raporu` işlevlerini eksiksiz taşı; canlı deneyde diskte üretilen `model_agirlik.json` ve `cikti/metrik.json` dosyalarının gerçek SHA-256 özetleri karşılaştırılır.
```
:::
