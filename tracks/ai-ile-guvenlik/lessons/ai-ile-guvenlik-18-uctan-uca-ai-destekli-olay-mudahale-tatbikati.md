---
id: ai-ile-guvenlik-18
title: "Uçtan Uca Yerel AI Destekli Olay Müdahale ve Doğrulama Tatbikatı"
summary: Log anomalisi tespiti, enjeksiyon karantinası, kapsam kilidi ve HMAC-SHA256 imzalı insan onayını (HITL) tek bir tekrarlanabilir olay müdahale tatbikatında birleştir.
timeout: 300
---

::: anlat Gerçek biçimi bil, sentetik temsili ayırt et
`ai-ile-guvenlik` yolunun bu son dersinde önceki beş modülde öğrendiğimiz tüm güvenlik mühendisliği ilkelerini tek bir olay müdahale (`Incident Response`) tatbikatında birleştiriyoruz:
1. Log akışındaki dolaylı istem enjeksiyonu (`[SISTEM:`) karantinaya alınır (`Modül 4`),
2. Ham loglardan deterministik anomali korelasyonu (`401` + `/export` üzerinde `200`) çıkarılır (`Modül 1-2`),
3. Müdahale hedefi izinli IP kapsam kilidinden (`allowlist`) geçirilir (`Modül 3-5`),
4. Yıkıcı müdahale (`ip_karantina`) yalnızca kanıt satırları ve `HMAC-SHA256` insan onayı imzası doğrulandığında uygulanır (`Modül 5-6`).

| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |
|---|---|---|
| SIEM/SOAR olay müdahale hattını, deterministik korelasyon/onay kapılarını ve yerel Ollama (`qwen3`) olay komutanı özetini | İlk üç görevde `tatbikat_paketi.json` içindeki **sentetik** tatbikat verilerini; son görevde canlı `ai_lab.SohbetOturumu` ile uçtan uca olay müdahale deneyini | Yalnızca saldırgan IP adresini karantinaya almanın, çalınmış bir API jetonunu (`token`) iptal etmeden sızıntıyı tek başına sonlandırabileceğini söyleyemez |

> [!GÜVENLİK]
> **Kapsam ve dürüstlük sınırı:** İlk üç görevdeki `tatbikat_paketi.json` dosyası **sentetik** eğitim verisidir; yalnız yerel ve kanıtlı olay müdahale mühendisliği tatbikatı yürütülür ve dosyalar her çalıştırmada (`setup`) yeniden yüklenir.
:::

::: anlat Uçtan uca olay müdahale tatbikatının üç aşaması
Doğrulanabilir bir AI destekli olay müdahale hattı üç aşamada çalışır:

1. **Anomali Adayı ve Enjeksiyon Karantinası (`anomali_adaylarini_cikar`):** Ham loglar `olay_id` bazında indekslenirken `user_agent` içinde `"[sistem:"` geçen kayıtlar `"[KARANTINA]"` ile maskelenir. Aynı `kaynak_ip` altında hem başarısız giriş (`durum_kodu == 401`) hem de başarılı dışa aktarma (`durum_kodu == 200` ve `"export" in yol.lower()`) görülen IP adresleri `supheli_ipler` listesine alınır.
2. **Çok Katmanlı Müdahale Doğrulaması (`mudahale_adimini_dogrula`):** Her müdahale adımı sırasıyla üç kapıdan geçer:
   - **Kapsam Kilidi:** `hedef_ip` `politika["izinli_ipler"]` içinde değilse `"kapsam_disi"` döner.
   - **Kanıt Doğrulaması:** `kanit_olay_idleri` içindeki herhangi bir olay indekste yoksa veya `kaynak_ip != hedef_ip` ise `"kanit_gecersiz"` döner.
   - **HMAC-SHA256 HITL İmzası:** `f"{mudahale_id}:{eylem}:{hedef_ip}"` mesajının `gizli_anahtar` ile imzası `onay_imzasi` ile eşleşmiyorsa `"gecersiz_imza"` döner.
3. **Tatbikat Yürütücüsü (`olay_mudahale_tatbikati`):** Anomali çıkarımını ve müdahale doğrulama kapısını birleştirerek nihai tatbikat raporunu üretir.
:::

::: anlat Bulguyu sınırlı ve doğrulanabilir yaz: hiçbir adım diğerinin yerine geçmez
Geçerli bir operatör imzasına (`onay_imzasi`) sahip olmak, uydurma kanıt kimliğini (`ir-log-999`) veya kapsam dışı hedefi (`192.168.1.1`) meşrulaştırmaz. Kapsam kilidi, kanıt doğrulaması ve kriptografik insan onayı **birlikte** sağlanmalıdır.
:::

::: tahmin Anomali korelasyonu ve üçlü müdahale kapısını tahmin et
Aşağıdaki Python kodunun çıktısını tahmin et:

```python
loglar = [
    {"ip": "10.40.7.99", "kod": 401, "yol": "/api/login"},
    {"ip": "10.40.7.99", "kod": 200, "yol": "/api/token-export"},
]
basarisiz = any(x["kod"] == 401 for x in loglar)
sizinti = any(x["kod"] == 200 and "export" in x["yol"] for x in loglar)
print("supheli" if (basarisiz and sizinti) else "normal")
```

???

```cikti
supheli
```

Aynı kaynak IP adresinde hem `401` kimlik doğrulama hatası hem de `/api/token-export` üzerinde `200` başarılı erişim görüldüğü için IP `"supheli"` olarak işaretlenir.
:::

::: gorev 1 · Log akışından zehirli alanları temizle ve anomali adaylarını çıkar
`anomali_adaylarini_cikar(olay_loglari)` işlevini yaz.

Kurallar:
- `olay_loglari`: boş olmayan `list`; her öğesi tam olarak `{"olay_id", "kaynak_ip", "yol", "durum_kodu", "user_agent"}` anahtarlarına sahip `dict` olmalı ve `olay_id` değerleri benzersiz olmalıdır (aksi halde `ValueError` yükselt).
- Eğer `user_agent.lower()` içinde `"[sistem:"` geçiyorsa kopyalanan kayıtta `user_agent` değerini `"[KARANTINA]"` yap ve `zehirli_log_sayisi` sayacını artır.
- Kaynak IP bazında olayları grupla: aynı IP için en az bir kayıtta `durum_kodu == 401` **ve** en az bir kayıtta (`durum_kodu == 200` ve `"export" in yol.lower()`) koşulu sağlanıyorsa bu IP'yi `supheli_ipler` listesine ekle.
- `{"olay_indeksi": indeks, "supheli_ipler": sorted(supheli_ipler), "zehirli_log_sayisi": zehirli_log_sayisi}` sözlüğünü döndür.

```starter
from ai_ile_guvenlik_veri import json_yukle

paket = json_yukle("tatbikat_paketi.json")

def anomali_adaylarini_cikar(olay_loglari):
    # HATA: User-Agent karantinasını ve 401 + export korelasyonunu yapmıyor.
    return {
        "olay_indeksi": {},
        "supheli_ipler": [],
        "zehirli_log_sayisi": 0,
    }

print(anomali_adaylarini_cikar(paket["olay_loglari"]))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-18")
```

```test
need("anomali_adaylarini_cikar")
from ai_ile_guvenlik_veri import json_yukle

LOGLAR = json_yukle("tatbikat_paketi.json")["olay_loglari"]

def sozlesme(fn):
    try:
        r = fn(LOGLAR)
        if r["supheli_ipler"] != ["10.40.7.99"] or r["zehirli_log_sayisi"] != 1:
            return False
        if r["olay_indeksi"]["ir-log-1"]["user_agent"] != "[KARANTINA]":
            return False
        if LOGLAR[0]["user_agent"] == "[KARANTINA]":
            return False

        engelli_export = [
            dict(LOGLAR[0], olay_id="e1", kaynak_ip="10.40.9.1", durum_kodu=401),
            dict(LOGLAR[1], olay_id="e2", kaynak_ip="10.40.9.1", durum_kodu=403),
            dict(LOGLAR[1], olay_id="e3", kaynak_ip="10.40.9.2", durum_kodu=200),
        ]
        if fn(engelli_export)["supheli_ipler"] != []:
            return False

        for h in [
            None,
            123,
            [],
            [{}],
            [LOGLAR[0], LOGLAR[0]],
            [dict(LOGLAR[0], durum_kodu=True)],
        ]:
            try:
                fn(h)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(anomali_adaylarini_cikar), "anomali_adaylarini_cikar: zehirli user_agent alanını karantinaya alıp şüpheli IP korelasyonunu çıkarmalı")
ok(not sozlesme(lambda l: {"olay_indeksi": {}, "supheli_ipler": ["10.40.7.99"], "zehirli_log_sayisi": 0}), "mutasyon: indeks ve karantina sayısını atlayan işlev reddedilmeli")
```

```solution
from ai_gercek_ai_ile_guvenlik_18 import _log_kontrol

def anomali_adaylarini_cikar(olay_loglari):
    if not (isinstance(olay_loglari, list) and bool(olay_loglari)):
        raise ValueError("olay_loglari boş olmayan liste olmalı")

    indeks = {}
    ip_olaylari = {}
    zehirli = []

    for log in olay_loglari:
        _log_kontrol(log)
        oid = log["olay_id"]
        if oid in indeks:
            raise ValueError("tekrarlanan olay_id")
        kopya = dict(log)
        if "[sistem:" in log["user_agent"].lower():
            kopya["user_agent"] = "[KARANTINA]"
            zehirli.append(oid)
        indeks[oid] = kopya
        ip_olaylari.setdefault(log["kaynak_ip"], []).append(kopya)

    supheli_ipler = []
    for ip, liste in ip_olaylari.items():
        basarisiz_var = any(x["durum_kodu"] == 401 for x in liste)
        sizinti_var = any(all([x["durum_kodu"] == 200, "export" in x["yol"].lower()]) for x in liste)
        if all([basarisiz_var, sizinti_var]):
            supheli_ipler.append(ip)

    return {
        "olay_indeksi": indeks,
        "supheli_ipler": sorted(supheli_ipler),
        "zehirli_log_sayisi": len(zehirli),
    }
```

```hint
Her kaydı indekslerken `"[sistem:" in log["user_agent"].lower()` ise `"[KARANTINA]"` ata; IP bazında hem `401` hem de `200` + `"export"` koşulunu kontrol et.
```
:::

::: gorev 2 · Müdahale adımını kapsam, kanıt ve HMAC imzası ile doğrula
`mudahale_adimini_dogrula(mudahale, olay_indeksi, politika)` işlevini yaz.

Kurallar:
- `mudahale`, `olay_indeksi` ve `politika` geçerli şemada olmalıdır; aksi halde `ValueError` yükselt.
- Kontrolleri tam olarak şu sırayla uygula:
  1. `mudahale["hedef_ip"]` değeri `politika["izinli_ipler"]` içinde değilse `{"mudahale_id": mid, "onaylandi": False, "neden": "kapsam_disi"}` döndür.
  2. `kanit_olay_idleri` içindeki herhangi bir kimlik `olay_indeksi` içinde yoksa veya ilgili kaydın `kaynak_ip` değeri `hedef_ip` ile uyuşmuyorsa `{"mudahale_id": mid, "onaylandi": False, "neden": "kanit_gecersiz"}` döndür.
  3. `f"{mid}:{mudahale['eylem']}:{hedef_ip}"` mesajının `politika["gizli_anahtar"]` ile `HMAC-SHA256` (`hexdigest`) değeri `mudahale["onay_imzasi"]` ile eşleşmiyorsa (`hmac.compare_digest`) `{"mudahale_id": mid, "onaylandi": False, "neden": "gecersiz_imza"}` döndür.
  4. Tümü geçerse `{"mudahale_id": mid, "onaylandi": True, "neden": "tatbikat_onaylandi"}` döndür.

```starter
from ai_ile_guvenlik_veri import json_yukle

paket = json_yukle("tatbikat_paketi.json")
indeks = {x["olay_id"]: x for x in paket["olay_loglari"]}

def mudahale_adimini_dogrula(mudahale, olay_indeksi, politika):
    # HATA: Kapsam, kanıt ve imza kapılarını denetlemeden onaylıyor.
    return {
        "mudahale_id": mudahale.get("mudahale_id", ""),
        "onaylandi": True,
        "neden": "tatbikat_onaylandi",
    }

for m in paket["aday_mudahaleler"]:
    print(mudahale_adimini_dogrula(m, indeks, paket["politika"]))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-18")
```

```test
need("mudahale_adimini_dogrula")
from ai_ile_guvenlik_veri import json_yukle

PAKET = json_yukle("tatbikat_paketi.json")
INDEKS = {x["olay_id"]: x for x in PAKET["olay_loglari"]}
POLITIKA = PAKET["politika"]
ADAYLAR = PAKET["aday_mudahaleler"]

def sozlesme(fn):
    try:
        if fn(ADAYLAR[0], INDEKS, POLITIKA) != {"mudahale_id": "ir-1", "onaylandi": True, "neden": "tatbikat_onaylandi"}:
            return False
        if fn(ADAYLAR[1], INDEKS, POLITIKA) != {"mudahale_id": "ir-2", "onaylandi": False, "neden": "kanit_gecersiz"}:
            return False
        if fn(ADAYLAR[2], INDEKS, POLITIKA) != {"mudahale_id": "ir-3", "onaylandi": False, "neden": "kapsam_disi"}:
            return False
        if fn(ADAYLAR[3], INDEKS, POLITIKA) != {"mudahale_id": "ir-4", "onaylandi": False, "neden": "gecersiz_imza"}:
            return False

        yanlis_ip_kaniti = dict(ADAYLAR[0], kanit_olay_idleri=["ir-log-3"])
        if fn(yanlis_ip_kaniti, INDEKS, POLITIKA) != {"mudahale_id": "ir-1", "onaylandi": False, "neden": "kanit_gecersiz"}:
            return False

        for m_in, i_in, p_in in [
            (None, INDEKS, POLITIKA),
            ({}, INDEKS, POLITIKA),
            (ADAYLAR[0], None, POLITIKA),
            (ADAYLAR[0], {}, POLITIKA),
            (ADAYLAR[0], "sozluk_degil", POLITIKA),
            (ADAYLAR[0], INDEKS, None),
            (ADAYLAR[0], INDEKS, {}),
        ]:
            try:
                fn(m_in, i_in, p_in)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(mudahale_adimini_dogrula), "mudahale_adimini_dogrula: kapsam, kanıt ve HMAC imzası kapılarını doğru sırayla uygulamalı")
ok(not sozlesme(lambda m, i, p: {"mudahale_id": m["mudahale_id"], "onaylandi": True, "neden": "tatbikat_onaylandi"}), "mutasyon: her müdahaleyi onaylayan işlev reddedilmeli")
```

```solution
import hashlib
import hmac
from ai_gercek_ai_ile_guvenlik_18 import _mudahale_kontrol, _politika_kontrol

def mudahale_adimini_dogrula(mudahale, olay_indeksi, politika):
    _mudahale_kontrol(mudahale)
    if not (isinstance(olay_indeksi, dict) and bool(olay_indeksi)):
        raise ValueError("olay_indeksi boş olmayan sözlük olmalı")
    _politika_kontrol(politika)

    mid = mudahale["mudahale_id"]
    hedef_ip = mudahale["hedef_ip"]
    kanitlar = mudahale["kanit_olay_idleri"]

    if hedef_ip not in politika["izinli_ipler"]:
        return {"mudahale_id": mid, "onaylandi": False, "neden": "kapsam_disi"}

    if not all(oid in olay_indeksi and olay_indeksi[oid].get("kaynak_ip") == hedef_ip for oid in kanitlar):
        return {"mudahale_id": mid, "onaylandi": False, "neden": "kanit_gecersiz"}

    mesaj = f"{mid}:{mudahale['eylem']}:{hedef_ip}".encode("utf-8")
    beklenen = hmac.new(politika["gizli_anahtar"].encode("utf-8"), mesaj, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(mudahale["onay_imzasi"], beklenen):
        return {"mudahale_id": mid, "onaylandi": False, "neden": "gecersiz_imza"}

    return {"mudahale_id": mid, "onaylandi": True, "neden": "tatbikat_onaylandi"}
```

```hint
Önce `hedef_ip not in politika["izinli_ipler"]`, sonra `all(oid in olay_indeksi and olay_indeksi[oid].get("kaynak_ip") == hedef_ip ...)`, en son `hmac.compare_digest` kontrolünü uygula.
```
:::

::: gorev 3 · Uçtan uca olay müdahale tatbikatını yürüt
`olay_mudahale_tatbikati(paket)` işlevini yaz.

Kurallar:
- `paket`: tam olarak `{"olay_loglari", "politika", "aday_mudahaleler"}` anahtarlarına sahip `dict` olmalı, `aday_mudahaleler` boş olmayan `list` olmalı ve `mudahale_id` değerleri benzersiz olmalıdır (aksi halde `ValueError` yükselt).
- Önce `anomali_adaylarini_cikar(paket["olay_loglari"])` ile olay indeksini, şüpheli IP listesini ve zehirli log sayısını çıkar.
- Ardından `aday_mudahaleler` içindeki her adımı `mudahale_adimini_dogrula` ile değerlendir:
  - `onaylandi == True` olanları `uygulanan_mudahaleler` listesine ekle.
  - `onaylandi == False` olanları `reddedilen_mudahaleler[mudahale_id] = neden` olarak kaydet.
- `{"supheli_ipler": ..., "zehirli_log_sayisi": ..., "uygulanan_mudahaleler": sorted(...), "reddedilen_mudahaleler": ...}` sözlüğünü döndür.

```starter
from ai_ile_guvenlik_veri import json_yukle

paket = json_yukle("tatbikat_paketi.json")

def olay_mudahale_tatbikati(paket):
    # HATA: Anomali çıkarımı ve müdahale doğrulama adımlarını birleştirmiyor.
    return {
        "supheli_ipler": [],
        "zehirli_log_sayisi": 0,
        "uygulanan_mudahaleler": [],
        "reddedilen_mudahaleler": {},
    }

print(olay_mudahale_tatbikati(paket))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-18")
```

```test
need("olay_mudahale_tatbikati")
from ai_ile_guvenlik_veri import json_yukle

PAKET = json_yukle("tatbikat_paketi.json")

def sozlesme(fn):
    try:
        r = fn(PAKET)
        if r != {
            "supheli_ipler": ["10.40.7.99"],
            "zehirli_log_sayisi": 1,
            "uygulanan_mudahaleler": ["ir-1"],
            "reddedilen_mudahaleler": {
                "ir-2": "kanit_gecersiz",
                "ir-3": "kapsam_disi",
                "ir-4": "gecersiz_imza",
            },
        }:
            return False

        for h in [
            None,
            123,
            {},
            dict(PAKET, aday_mudahaleler=[]),
            dict(PAKET, aday_mudahaleler="liste_degil"),
            dict(PAKET, aday_mudahaleler=[PAKET["aday_mudahaleler"][0], PAKET["aday_mudahaleler"][0]]),
        ]:
            try:
                fn(h)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(olay_mudahale_tatbikati), "olay_mudahale_tatbikati: uçtan uca anomali tespiti ve doğrulamalı müdahale kapısını yürütmeli")
ok(not sozlesme(lambda p: {"supheli_ipler": ["10.40.7.99"], "zehirli_log_sayisi": 1, "uygulanan_mudahaleler": ["ir-1"], "reddedilen_mudahaleler": {}}), "mutasyon: reddedilen müdahaleleri silen işlev reddedilmeli")
```

```solution
from ai_gercek_ai_ile_guvenlik_18 import (
    anomali_adaylarini_cikar_referans as _anomali,
    mudahale_adimini_dogrula_referans as _dogrula,
)

def olay_mudahale_tatbikati(paket):
    if not (isinstance(paket, dict) and set(paket.keys()) == {"olay_loglari", "politika", "aday_mudahaleler"}):
        raise ValueError("paket şeması geçersiz")
    adaylar = paket["aday_mudahaleler"]
    if not (isinstance(adaylar, list) and bool(adaylar)):
        raise ValueError("aday_mudahaleler boş olmayan liste olmalı")

    anomali = _anomali(paket["olay_loglari"])
    indeks = anomali["olay_indeksi"]
    politika = paket["politika"]

    uygulanan = []
    reddedilen = {}
    gorulen = set()

    for m in adaylar:
        sonuc = _dogrula(m, indeks, politika)
        mid = sonuc["mudahale_id"]
        if mid in gorulen:
            raise ValueError("tekrarlanan mudahale_id")
        gorulen.add(mid)
        if sonuc["onaylandi"]:
            uygulanan.append(mid)
        else:
            reddedilen[mid] = sonuc["neden"]

    return {
        "supheli_ipler": anomali["supheli_ipler"],
        "zehirli_log_sayisi": anomali["zehirli_log_sayisi"],
        "uygulanan_mudahaleler": sorted(uygulanan),
        "reddedilen_mudahaleler": reddedilen,
    }
```

```hint
Önce `anomali_adaylarini_cikar` ile indeksi hazırla, ardından her müdahale adayını doğrulayıp `uygulanan_mudahaleler` ve `reddedilen_mudahaleler` içine ayır.
```
:::

::: gorev Gerçek deney · Yerel modelle uçtan uca AI destekli olay müdahale ve doğrulama tatbikatı
Önceki üç görevde yazdığın `anomali_adaylarini_cikar`, `mudahale_adimini_dogrula` ve `olay_mudahale_tatbikati` işlevlerini bu adımda birleştir.

Canlı deneyde:
1. Zehirli `user_agent` alanı karantinaya alınmış olay indeksi yerel Ollama modeline (`ai_lab.SohbetOturumu`) sunularak sızıntı yapan kaynak IP özetletilir.
2. Dört müdahale adayı (`ir-1..ir-4`) kapsam kilidi, kanıt eşleşmesi ve HMAC-SHA256 insan onayı kapısından geçirilir.
3. Yalnızca kanıtlı, kapsam içi ve geçerli imzalı `ir-1` müdahalesinin uygulandığı doğrulanır.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def anomali_adaylarini_cikar(olay_loglari):
    return {}

def mudahale_adimini_dogrula(mudahale, olay_indeksi, politika):
    return {}

def olay_mudahale_tatbikati(paket):
    return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_ile_guvenlik_18 as deney
    deney.goster(anomali_adaylarini_cikar, mudahale_adimini_dogrula, olay_mudahale_tatbikati)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-18")
```

```test
import ai_lab
from sandbox import ai_gercek_ai_ile_guvenlik_18 as D

checks = []
_base_ok = ok
def ok(kosul, mesaj):
    checks.append(bool(kosul))
    return _base_ok(kosul, mesaj)

for ad in ("anomali_adaylarini_cikar", "mudahale_adimini_dogrula", "olay_mudahale_tatbikati"):
    need(ad)

sorun = ai_lab.kod_denetimi(
    src,
    ("anomali_adaylarini_cikar_referans", "mudahale_adimini_dogrula_referans", "olay_mudahale_tatbikati_referans"),
)
ok(not sorun, "laboratuvar yamalanmamalı, referans işlevler çağrılmamalı")

def _on_sozlesme():
    try:
        for l_in in (None, [], [D.TATBIKAT_PAKETI["olay_loglari"][0], D.TATBIKAT_PAKETI["olay_loglari"][0]]):
            try:
                anomali_adaylarini_cikar(l_in)
                return False
            except ValueError:
                pass
        for m_in, i_in in [(None, {"ir-log-1": D.TATBIKAT_PAKETI["olay_loglari"][0]}), (D.TATBIKAT_PAKETI["aday_mudahaleler"][0], {})]:
            try:
                mudahale_adimini_dogrula(m_in, i_in, D.TATBIKAT_PAKETI["politika"])
                return False
            except ValueError:
                pass
        for p_in in (None, {}, dict(D.TATBIKAT_PAKETI, aday_mudahaleler=[])):
            try:
                olay_mudahale_tatbikati(p_in)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(_on_sozlesme(), "sentetik ön kontrol: anomali korelasyonu, kapsam kilidi ve HITL imza kuralları tam")

if not all(checks):
    stop()

try:
    r = D.deney(anomali_adaylarini_cikar, mudahale_adimini_dogrula, olay_mudahale_tatbikati)
except Exception as e:
    ok(False, f"GERÇEK OLAY MÜDAHALE TATBİKATI YAPILAMADI: {type(e).__name__}: {e}")
    stop()

for ad, deger in r["kontroller"].items():
    ok(deger, "gerçek deney: " + ad)

ai_lab.kanit_yaz("ile-guvenlik-18-tatbikat", {
    "kaynak": "gercek",
    "kabul": all(checks),
    "ders": "ai-ile-guvenlik-18",
    "ortam": r["ortam"],
    "ayarlar": r["ayarlar"],
    "deney": r,
    "ozet": r["ozet"],
})
o = r["ozet"]
ok(
    True,
    f"BULGU ({o['model']}): supheli_ipler={o['supheli_ipler']}, uygulanan={o['uygulanan']}, reddedilen={o['reddedilen']}.",
)
```

```solution
import hashlib
import hmac
import ai_lab
from sandbox.ai_gercek_ai_ile_guvenlik_18 import _log_kontrol, _mudahale_kontrol, _politika_kontrol

def anomali_adaylarini_cikar(olay_loglari):
    if not (isinstance(olay_loglari, list) and bool(olay_loglari)):
        raise ValueError("olay_loglari boş olmayan liste olmalı")

    indeks = {}
    ip_olaylari = {}
    zehirli = []

    for log in olay_loglari:
        _log_kontrol(log)
        oid = log["olay_id"]
        if oid in indeks:
            raise ValueError("tekrarlanan olay_id")
        kopya = dict(log)
        if "[sistem:" in log["user_agent"].lower():
            kopya["user_agent"] = "[KARANTINA]"
            zehirli.append(oid)
        indeks[oid] = kopya
        ip_olaylari.setdefault(log["kaynak_ip"], []).append(kopya)

    supheli_ipler = []
    for ip, liste in ip_olaylari.items():
        basarisiz_var = any(x["durum_kodu"] == 401 for x in liste)
        sizinti_var = any(all([x["durum_kodu"] == 200, "export" in x["yol"].lower()]) for x in liste)
        if all([basarisiz_var, sizinti_var]):
            supheli_ipler.append(ip)

    return {
        "olay_indeksi": indeks,
        "supheli_ipler": sorted(supheli_ipler),
        "zehirli_log_sayisi": len(zehirli),
    }

def mudahale_adimini_dogrula(mudahale, olay_indeksi, politika):
    _mudahale_kontrol(mudahale)
    if not (isinstance(olay_indeksi, dict) and bool(olay_indeksi)):
        raise ValueError("olay_indeksi boş olmayan sözlük olmalı")
    _politika_kontrol(politika)

    mid = mudahale["mudahale_id"]
    hedef_ip = mudahale["hedef_ip"]
    kanitlar = mudahale["kanit_olay_idleri"]

    if hedef_ip not in politika["izinli_ipler"]:
        return {"mudahale_id": mid, "onaylandi": False, "neden": "kapsam_disi"}

    if not all(oid in olay_indeksi and olay_indeksi[oid].get("kaynak_ip") == hedef_ip for oid in kanitlar):
        return {"mudahale_id": mid, "onaylandi": False, "neden": "kanit_gecersiz"}

    mesaj = f"{mid}:{mudahale['eylem']}:{hedef_ip}".encode("utf-8")
    beklenen = hmac.new(politika["gizli_anahtar"].encode("utf-8"), mesaj, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(mudahale["onay_imzasi"], beklenen):
        return {"mudahale_id": mid, "onaylandi": False, "neden": "gecersiz_imza"}

    return {"mudahale_id": mid, "onaylandi": True, "neden": "tatbikat_onaylandi"}

def olay_mudahale_tatbikati(paket):
    if not (isinstance(paket, dict) and set(paket.keys()) == {"olay_loglari", "politika", "aday_mudahaleler"}):
        raise ValueError("paket şeması geçersiz")
    adaylar = paket["aday_mudahaleler"]
    if not (isinstance(adaylar, list) and bool(adaylar)):
        raise ValueError("aday_mudahaleler boş olmayan liste olmalı")

    anomali = anomali_adaylarini_cikar(paket["olay_loglari"])
    indeks = anomali["olay_indeksi"]
    politika = paket["politika"]

    uygulanan = []
    reddedilen = {}
    gorulen = set()

    for m in adaylar:
        sonuc = mudahale_adimini_dogrula(m, indeks, politika)
        mid = sonuc["mudahale_id"]
        if mid in gorulen:
            raise ValueError("tekrarlanan mudahale_id")
        gorulen.add(mid)
        if sonuc["onaylandi"]:
            uygulanan.append(mid)
        else:
            reddedilen[mid] = sonuc["neden"]

    return {
        "supheli_ipler": anomali["supheli_ipler"],
        "zehirli_log_sayisi": anomali["zehirli_log_sayisi"],
        "uygulanan_mudahaleler": sorted(uygulanan),
        "reddedilen_mudahaleler": reddedilen,
    }

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_ile_guvenlik_18 as deney
    deney.goster(anomali_adaylarini_cikar, mudahale_adimini_dogrula, olay_mudahale_tatbikati)
```

```hint
Önceki üç görevdeki `anomali_adaylarini_cikar`, `mudahale_adimini_dogrula` ve `olay_mudahale_tatbikati` işlevlerini birleştir.
```
:::
