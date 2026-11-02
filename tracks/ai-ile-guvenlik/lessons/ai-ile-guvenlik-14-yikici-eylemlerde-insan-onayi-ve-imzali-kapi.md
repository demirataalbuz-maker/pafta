---
id: ai-ile-guvenlik-14
title: "Yıkıcı Eylemlerde İnsan Onayı (HITL) ve İmzalı Görev Kapısı"
summary: Güvenlik ajanının IP engelleme veya hesap kapatma gibi yıkıcı eylemleri yalnızca parametreye bağlı HMAC-SHA256 insan onayı jetonu doğrulandığında çalıştırmasını sağla.
timeout: 300
---

::: anlat Gerçek biçimi bil, sentetik temsili ayırt et
Güvenlik operasyonlarında otomatik olay müdahale (Incident Response - IR) ve SOAR (Güvenlik Orkestrasyonu, Otomasyon ve Müdahale) platformları, bir tehdit algılandığında hızlı karşı tedbirler uygulayabilir. Günümüzde bu orkestrasyon kararları giderek daha fazla otonom büyük dil modeli (LLM) ajanlarına emanet edilmektedir.

Ancak bir güvenlik ajanına `ip_engelle`, `hesap_kapat`, `guvenlik_duvari_kurali_yaz` veya `servis_durdur` gibi durum değiştiren araçlar bağlandığında sistemin karşılaşacağı en ölümcül tehlike, **insan onay mekanizmasını yalnızca `"onaylandi": true` gibi bağlamsız bir Boole bayrağına bırakmaktır**.

### 1. Parametre Değiştirme ve "Şaşkın Vekil" (Confused Deputy) Tuzağı
Basit bir onay mekanizmasında insan analist meşru bir saldırgan IP adresi olan `10.20.9.88` için engelleme onayını tıklar. Ancak modelin otonom döngüsünde halüsinasyon, yarış durumu (race condition / TOCTOU) veya araya giren dolaylı bir istem enjeksiyonu meydana gelirse, ajan onay bayrağı (`onaylandi: true`) elindeyken parametreyi değiştirebilir: saldırgan IP'si yerine kurumsal ağ geçidi (`10.20.1.1`) veya etki alanı denetleyicisi (Domain Controller) hedefe yazılabilir. Yürütücü katman yalnızca bayrağa baktığı için meşru altyapıyı felç eder ve tüm şirketi çevrimdışı bırakır.

Bu nedenle güvenlik mühendisliğinde temel kural şudur: **Yıkıcı bir eylem için verilen insan onayı, eylemin hedef parametrelerine ve istek kimliğine kriptografik olarak sıkı sıkıya bağlı (parameter-bound HMAC token) olmak zorundadır.**

### 2. Aracın Altında Ne Olur: Kriptografik Parametreye Bağlı HITL Kapısı
Güvenilir bir Human-in-the-Loop (HITL) onay kapısı üç katmanlı bir mimariyle kurulur:
1. **Kanonik Görev İmzası (`gorev_imzasi_uret`):**
   - İnsan operatör onay verdiğinde, onay jetonu soyut bir izin dizesi olarak üretilmez. İstek kimliği, çağrılacak araç ve hedef parametresi deterministik kanonik bir dizgede birleştirilir: `f"{istek_id}:{arac}:{hedef}"`.
   - Bu kanonik mesaj, yalnızca yetkili operatör konsolu ve güvenlik yürütücüsü tarafından bilinen `gizli_anahtar` ile `HMAC-SHA256` algoritmasından geçirilerek 64 karakterlik onaltılık (`hexdigest`) özet üretilir.
2. **HITL Doğrulama Kapısı (`hitl_kapisi_dogrula`):**
   - **Salt-Okunur Eylemler:** `risk_sinifi == "salt_okunur"` olan sorgulama araçları durum değiştirmediği için onay jetonu aranmaksızın serbestçe yürütülür (`"salt_okunur_serbest"`).
   - **Yıkıcı Eylemler:** `risk_sinifi == "yikici"` olan eylemlerde `onay_jetonu` boşsa istek derhal `"eksik_onay_jetonu"` nedeniyle reddedilir.
   - Jeton mevcutsa, yürütücü anlık olarak istek parametrelerinden (`iid`, `arac`, `hedef`) beklenen HMAC özetini hesaplar ve gelen jeton ile `hmac.compare_digest` üzerinden karşılaştırır. İstek kimliği, araç adı veya hedef parametresinden tek bir karakter bile farklıysa imza tutmaz ve `"imza_uyumsuz"` kararıyla engellenir.
3. **Müdahale Kuyruğu Yürütücüsü (`mudahale_kuyrugu_yurut`):**
   - Gelen tüm müdahale istekleri sırayla HITL kapısından geçirilir. Onaylanan geçerli çağrılar `uygulanan_idleri` listesine, reddedilenler ise nedenleriyle birlikte `reddedilenler` sözlüğüne kaydedilir.

### 3. Çıktı Nasıl Okunur: HITL Denetim İzi
- `uygulanan_idleri`: Kriptografik onay kapısını başarıyla geçen ve fiilen yürütülen eylemlerin kimlikleri.
- `reddedilenler`: Güvenlik kapısına takılan eylemlerin kimlikleri ve engellenme nedenleri (`eksik_onay_jetonu`, `imza_uyumsuz`).

### 4. Saldırgan Neyi Dener? (Threat Vectors)
- **Jeton Yeniden Kullanımı ve Taşıma (Token Replay / Cross-Request Replay):** Saldırgan, meşru bir IP (`req-102: 10.20.9.88`) için üretilmiş onay jetonunu ağ trafiğinden veya loglardan ele geçirip kurumsal ağ geçidini hedefleyen başka bir isteğe (`req-104: 10.20.1.1`) yapıştırmayı dener. Kanonik mesajda `istek_id` ve `hedef` birlikte yer aldığından imza doğrulaması çöker.
- **Zamanlama Saldırıları (Timing Attacks):** Jeton karşılaştırmasında standart `==` operatörü kullanılırsa dizgeler baştan sona karakter karakter karşılaştırılır ve ilk uyuşmazlıkta durulur. Saldırgan mikrosaniyelik yanıt süresi farklarından jetonun karakterlerini tahmin edebilir. Savunmada `hmac.compare_digest` kullanılarak sabit-zamanlı (constant-time) güvenli karşılaştırma sağlanır.
- **Onay Yorgunluğu (Approval Fatigue):** Analistin ekranına yüzlerce sahte onay bildirimi göndererek analisti dikkatsizce rastgele onay vermeye teşvik etmek.

### 5. Savunma Neden Kırılır ve Sık Yapılan Geliştirici Hataları
- **Parametreleri İmzaya Dahil Etmemek:** Yalnızca `istek_id` alanını imzalamak, hedefin sonradan değiştirilmesini engelleyemez. Kanonik şablon mutlaka tüm kritik argümanları içermelidir.
- **Sabit-Zamanlı Karşılaştırmayı İhmal Etmek:** `==` kullanımı kriptografik doğrulamada kabul edilemez bir zafiyettir.
- **Boşluk ve Tip Denetimlerini Atlamak:** `strip()` yapılmaması veya parametrelerin `None` olabilmesi imza hesaplamasında `TypeError` veya sessiz güvenlik açıklarına yol açar.

| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |
|---|---|---|
| SOAR onay kuyruğunu, `hmac.new(..., hashlib.sha256)` ile parametreye bağlı görev imzasını ve yerel Ollama (`qwen3`) müdahale akışını | İlk üç görevde `mudahale_istekleri.json` içindeki **sentetik** müdahale isteklerini ve HMAC jetonlarını; son görevde canlı `ai_lab.SohbetOturumu` ile HITL kapısı deneyini | Yalnızca HMAC doğrulamasının, insan operatörün yanlış hedefi dikkatsizce onaylamasını (sosyal mühendislik / onay yorgunluğu) tek başına engelleyebileceğini söyleyemez |
| Parametreye bağlı kanonik görev imzası (`f"{istek_id}:{arac}:{hedef}"`) ve sabit-zamanlı doğrulama (`hmac.compare_digest`) | `gorev_imzasi_uret` ve `hitl_kapisi_dogrula` işlevleri | İmzalı onay jetonunun yetkisiz sızdırılması durumunda gizli anahtarın rotasyonunu veya çok faktörlü operatör doğrulamasını (MFA) tek başına çözebileceğini söyleyemez |
| Yıkıcı eylemlerde müdahale kuyruğu yürütücüsü ve triyaj ayrımı (`uygulanan_idleri` vs `reddedilenler`) | `mudahale_kuyrugu_yurut` ile onaylı ve engellenen çağrıların yönetimi | Kuyruk yürütücüsünün hedef sistemde uygulanan eylemin (örn. iptables kuralı) ağda beklenmeyen bir yan etki veya kesinti yaratmayacağını garanti ettiğini söyleyemez |

> [!NOT]
> **Kapsam ve dürüstlük sınırı:** İlk üç görevdeki `mudahale_istekleri.json` dosyası ve içindeki `gizli_anahtar` **sentetik** eğitim verisidir; hiçbir gerçek güvenlik duvarı veya kullanıcı hesabı üzerinde işlem yapılmaz ve dosyalar her çalıştırmada (`setup`) yeniden yüklenir (kalıcılık yoktur). Dördüncü görevde yerel Ollama modeliyle canlı HITL kapısı ve imza doğrulama deneyi yürütülür.
:::

::: anlat Parametreye bağlı imzalı HITL kapısı üç adımda çalışır
Yıkıcı araç çağrılarını koruyan **Human-in-the-Loop (`HITL`)** kapısı şöyle kurulur:

1. **Kanoniğe Bağlı Görev İmzası (`gorev_imzasi_uret`):** İstek kimliği, araç adı ve hedef parametresi `f"{istek_id}:{arac}:{hedef}"` dizgesinde birleştirilir ve operatörün `gizli_anahtar` değeriyle `HMAC-SHA256` (`hexdigest`) imzası üretilir.
2. **HITL Doğrulama Kapısı (`hitl_kapisi_dogrula`):**
   - `risk_sinifi == "salt_okunur"` olan çağrılar imza aranmadan `"salt_okunur_serbest"` gerekçesiyle onaylanır.
   - `risk_sinifi == "yikici"` olan çağrılarda `onay_jetonu` boşsa `"eksik_onay_jetonu"` ile reddedilir; doluysa beklenen imza ile `hmac.compare_digest` üzerinden karşılaştırılır. Hedef veya araç değiştirilmişse imza tutmaz ve `"imza_uyumsuz"` döner.
3. **Müdahale Kuyruğu Yürütücüsü (`mudahale_kuyrugu_yurut`):** Kuyruktaki her isteği sırayla HITL kapısından geçirir; onaylananları `uygulanan_idleri` listesine, reddedilenleri `reddedilenler` sözlüğüne yazar.
:::

::: anlat Bulguyu sınırlı ve doğrulanabilir yaz: başka isteğin jetonu yeni hedefe taşınamaz
Saldırgan veya hatalı ajan, `req-102` (`10.20.9.88` engelleme) için alınmış geçerli bir onay jetonunu kopyalayıp `req-104` (`10.20.1.1` engelleme) isteğine yapıştırdığında, kanonik mesaj içinde hem `istek_id` hem de `hedef` bulunduğu için imza doğrulaması deterministik olarak başarısız olur.
:::

::: tahmin Parametre değiştiğinde HMAC imza karşılaştırmasını tahmin et
Aşağıdaki Python kodunun çıktısını tahmin et:

```python
import hashlib, hmac

anahtar = b"sentetik-anahtar"
jeton = hmac.new(anahtar, b"req-1:ip_engelle:10.0.0.99", hashlib.sha256).hexdigest()
kontrol_ayni = hmac.compare_digest(
    jeton,
    hmac.new(anahtar, b"req-1:ip_engelle:10.0.0.99", hashlib.sha256).hexdigest(),
)
kontrol_degismis = hmac.compare_digest(
    jeton,
    hmac.new(anahtar, b"req-1:ip_engelle:10.0.0.1", hashlib.sha256).hexdigest(),
)
print(kontrol_ayni, kontrol_degismis)
```

???

```cikti
True False
```

Hedef IP `10.0.0.99` yerine `10.0.0.1` yapıldığında üretilen HMAC özeti tamamen değişir ve `compare_digest` `False` döndürür.
:::

::: gorev 1 · İstek kimliği, araç ve hedefe bağlı HMAC-SHA256 görev imzası üret
`gorev_imzasi_uret(istek_id, arac, hedef, gizli_anahtar)` işlevini yaz.

Kurallar:
- Dört parametrenin tamamı boş olmayan (`strip()` sonrası dolu) `str` olmalıdır; aksi halde `ValueError` yükselt.
- Kanonik mesajı tam olarak `f"{istek_id}:{arac}:{hedef}"` biçiminde oluştur.
- `hmac.new(gizli_anahtar.encode("utf-8"), mesaj.encode("utf-8"), hashlib.sha256).hexdigest()` değerini döndür.

```starter
import hashlib
import hmac
from ai_ile_guvenlik_veri import json_yukle

veri = json_yukle("mudahale_istekleri.json")

def gorev_imzasi_uret(istek_id, arac, hedef, gizli_anahtar):
    # KUSURLU BAŞLANGIÇ KODU: hedef ve araç parametrelerini imzaya dahil etmeden boş imza döndürüyor!
    return ""

print(gorev_imzasi_uret("req-102", "ip_engelle", "10.20.9.88", veri["gizli_anahtar"]))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-14")
```

```test
need("gorev_imzasi_uret")

def sozlesme(fn):
    try:
        imza1 = fn("req-102", "ip_engelle", "10.20.9.88", "pafta-hitl-sentetik-anahtar-2026")
        if imza1 != "c986fc70907fc102fc664569fadb84af530e3fd68c32ddb4d0b648da59136374":
            return False

        imza2 = fn("req-102", "ip_engelle", "10.20.1.1", "pafta-hitl-sentetik-anahtar-2026")
        if imza1 == imza2 or len(imza2) != 64:
            return False

        for args in [
            ("", "ip_engelle", "10.0.0.1", "k"),
            ("req-1", "   ", "10.0.0.1", "k"),
            ("req-1", "ip_engelle", None, "k"),
            ("req-1", "ip_engelle", "10.0.0.1", ""),
            (123, "ip_engelle", "10.0.0.1", "k"),
        ]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(gorev_imzasi_uret), "gorev_imzasi_uret: istek_id, arac ve hedefe bağlı HMAC-SHA256 imzası doğru")
ok(not sozlesme(lambda i, a, h, k: "c986fc70907fc102fc664569fadb84af530e3fd68c32ddb4d0b648da59136374"), "mutasyon: sabit imza döndüren işlev reddedilmeli")
```

```solution
import hashlib
import hmac

def gorev_imzasi_uret(istek_id, arac, hedef, gizli_anahtar):
    if not all(isinstance(x, str) and bool(x.strip()) for x in (istek_id, arac, hedef, gizli_anahtar)):
        raise ValueError("tüm parametreler boş olmayan string olmalı")
    mesaj = f"{istek_id}:{arac}:{hedef}".encode("utf-8")
    anahtar = gizli_anahtar.encode("utf-8")
    return hmac.new(anahtar, mesaj, hashlib.sha256).hexdigest()
```

```hint
`all(isinstance(x, str) and bool(x.strip()) for x in ...)` kontrolünden sonra `hmac.new(gizli_anahtar.encode("utf-8"), f"{istek_id}:{arac}:{hedef}".encode("utf-8"), hashlib.sha256).hexdigest()` hesapla.
```
:::

::: gorev 2 · Müdahale isteğini HITL kapısında doğrula
`hitl_kapisi_dogrula(istek, gizli_anahtar)` işlevini yaz.

Kurallar:
- `istek`: tam olarak `{"istek_id", "arac", "hedef", "risk_sinifi", "onay_jetonu"}` anahtarlarına sahip `dict`; `istek_id`, `arac`, `hedef` boş olmayan `str`, `risk_sinifi` `("salt_okunur", "yikici")` değerlerinden biri, `onay_jetonu` ise `str` olmalıdır.
- `gizli_anahtar`: boş olmayan (`strip()` sonrası dolu) `str` olmalıdır (aksi halde `ValueError` yükselt).
- Doğrulama sırası:
  1. `risk_sinifi == "salt_okunur"` ise `{"istek_id": iid, "izin_verildi": True, "neden": "salt_okunur_serbest"}` döndür.
  2. `risk_sinifi == "yikici"` ve `onay_jetonu.strip()` boşsa `{"istek_id": iid, "izin_verildi": False, "neden": "eksik_onay_jetonu"}` döndür.
  3. Beklenen HMAC-SHA256 imzasını hesapla; `hmac.compare_digest(jeton, beklenen)` `False` ise `{"istek_id": iid, "izin_verildi": False, "neden": "imza_uyumsuz"}` döndür.
  4. İmza eşleşiyorsa `{"istek_id": iid, "izin_verildi": True, "neden": "imzali_onay_gecerli"}` döndür.

```starter
from ai_ile_guvenlik_veri import json_yukle

veri = json_yukle("mudahale_istekleri.json")

def hitl_kapisi_dogrula(istek, gizli_anahtar):
    # KUSURLU BAŞLANGIÇ KODU: yıkıcı eylemlerde onay jetonu ve imza doğrulaması yapmadan her isteği doğrudan onaylıyor!
    return {
        "istek_id": istek.get("istek_id", ""),
        "izin_verildi": True,
        "neden": "imzali_onay_gecerli",
    }

for ist in veri["istekler"]:
    print(hitl_kapisi_dogrula(ist, veri["gizli_anahtar"]))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-14")
```

```test
need("hitl_kapisi_dogrula")
from ai_ile_guvenlik_veri import json_yukle

VERI = json_yukle("mudahale_istekleri.json")
ANAHTAR = VERI["gizli_anahtar"]
ISTEKLER = VERI["istekler"]

def sozlesme(fn):
    try:
        if fn(ISTEKLER[0], ANAHTAR) != {"istek_id": "req-101", "izin_verildi": True, "neden": "salt_okunur_serbest"}:
            return False
        if fn(ISTEKLER[1], ANAHTAR) != {"istek_id": "req-102", "izin_verildi": True, "neden": "imzali_onay_gecerli"}:
            return False
        if fn(ISTEKLER[2], ANAHTAR) != {"istek_id": "req-103", "izin_verildi": False, "neden": "eksik_onay_jetonu"}:
            return False
        if fn(ISTEKLER[3], ANAHTAR) != {"istek_id": "req-104", "izin_verildi": False, "neden": "imza_uyumsuz"}:
            return False

        for i_in, k_in in [
            (None, ANAHTAR),
            ({}, ANAHTAR),
            (dict(ISTEKLER[0], risk_sinifi="kritik"), ANAHTAR),
            (dict(ISTEKLER[0], onay_jetonu=None), ANAHTAR),
            (ISTEKLER[0], ""),
            (ISTEKLER[0], "   "),
            (ISTEKLER[0], None),
        ]:
            try:
                fn(i_in, k_in)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(hitl_kapisi_dogrula), "hitl_kapisi_dogrula: salt-okunur, eksik jeton ve imza uyumsuzluğu durumlarını doğru ayırmalı")
ok(not sozlesme(lambda i, k: {"istek_id": i["istek_id"], "izin_verildi": True, "neden": "imzali_onay_gecerli"}), "mutasyon: imzasız yıkıcı eylemi onaylayan işlev reddedilmeli")
```

```solution
import hmac
from ai_gercek_ai_ile_guvenlik_14 import _istek_kontrol, gorev_imzasi_uret_referans as _imza_uret

def hitl_kapisi_dogrula(istek, gizli_anahtar):
    _istek_kontrol(istek)
    if not (isinstance(gizli_anahtar, str) and bool(gizli_anahtar.strip())):
        raise ValueError("gizli_anahtar boş olmayan string olmalı")

    iid = istek["istek_id"]
    if istek["risk_sinifi"] == "salt_okunur":
        return {"istek_id": iid, "izin_verildi": True, "neden": "salt_okunur_serbest"}

    jeton = istek["onay_jetonu"].strip()
    if not jeton:
        return {"istek_id": iid, "izin_verildi": False, "neden": "eksik_onay_jetonu"}

    beklenen = _imza_uret(iid, istek["arac"], istek["hedef"], gizli_anahtar)
    if not hmac.compare_digest(jeton, beklenen):
        return {"istek_id": iid, "izin_verildi": False, "neden": "imza_uyumsuz"}

    return {"istek_id": iid, "izin_verildi": True, "neden": "imzali_onay_gecerli"}
```

```hint
`risk_sinifi == "salt_okunur"` ise doğrudan onayla; `"yikici"` ise önce boş jetonu (`"eksik_onay_jetonu"`), ardından `hmac.compare_digest(jeton, beklenen)` ile `"imza_uyumsuz"` durumunu kontrol et.
```
:::

::: gorev 3 · Müdahale kuyruğunu imzalı HITL kapısından geçirerek yürüt
`mudahale_kuyrugu_yurut(istekler, gizli_anahtar)` işlevini yaz.

Kurallar:
- `istekler`: boş olmayan `list`; her öğesi 2. görevdeki şemaya uymalı ve `istek_id` değerleri benzersiz olmalıdır.
- `gizli_anahtar`: boş olmayan (`strip()` sonrası dolu) `str` olmalıdır (aksi halde `ValueError` yükselt).
- Kuyruktaki her isteği `hitl_kapisi_dogrula` mantığıyla değerlendir:
  - `izin_verildi == True` olanların `istek_id` değerini sırasıyla `uygulanan_idleri` listesine ekle.
  - `izin_verildi == False` olanları `reddedilenler[istek_id] = neden` olarak kaydet.
- `{"uygulanan_idleri": uygulanan_idleri, "reddedilenler": reddedilenler}` sözlüğünü döndür.

```starter
from ai_ile_guvenlik_veri import json_yukle

veri = json_yukle("mudahale_istekleri.json")

def mudahale_kuyrugu_yurut(istekler, gizli_anahtar):
    # KUSURLU BAŞLANGIÇ KODU: tüm istekleri HITL kapısından geçirmeden doğrudan uygulanan listesine alıyor!
    return {
        "uygulanan_idleri": [i["istek_id"] for i in istekler],
        "reddedilenler": {},
    }

print(mudahale_kuyrugu_yurut(veri["istekler"], veri["gizli_anahtar"]))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-14")
```

```test
need("mudahale_kuyrugu_yurut")
from ai_ile_guvenlik_veri import json_yukle

VERI = json_yukle("mudahale_istekleri.json")
ANAHTAR = VERI["gizli_anahtar"]
ISTEKLER = VERI["istekler"]

def sozlesme(fn):
    try:
        r = fn(ISTEKLER, ANAHTAR)
        if r != {
            "uygulanan_idleri": ["req-101", "req-102"],
            "reddedilenler": {
                "req-103": "eksik_onay_jetonu",
                "req-104": "imza_uyumsuz",
            },
        }:
            return False

        for i_in, k_in in [
            (None, ANAHTAR),
            (123, ANAHTAR),
            ([], ANAHTAR),
            ([ISTEKLER[0], ISTEKLER[0]], ANAHTAR),
            (ISTEKLER, None),
            (ISTEKLER, ""),
            (ISTEKLER, "   "),
        ]:
            try:
                fn(i_in, k_in)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(sozlesme(mudahale_kuyrugu_yurut), "mudahale_kuyrugu_yurut: yalnızca salt-okunur ve geçerli imzalı yıkıcı istekleri uygulamalı")
ok(not sozlesme(lambda i, k: {"uygulanan_idleri": ["req-101", "req-102"], "reddedilenler": {}}), "mutasyon: reddedilenleri silen işlev reddedilmeli")
```

```solution
from ai_gercek_ai_ile_guvenlik_14 import hitl_kapisi_dogrula_referans as _kapi

def mudahale_kuyrugu_yurut(istekler, gizli_anahtar):
    if not (isinstance(istekler, list) and bool(istekler)):
        raise ValueError("istekler boş olmayan liste olmalı")

    uygulanan = []
    reddedilen = {}
    gorulen = set()

    for ist in istekler:
        sonuc = _kapi(ist, gizli_anahtar)
        iid = sonuc["istek_id"]
        if iid in gorulen:
            raise ValueError("tekrarlanan istek_id")
        gorulen.add(iid)
        if sonuc["izin_verildi"]:
            uygulanan.append(iid)
        else:
            reddedilen[iid] = sonuc["neden"]

    return {
        "uygulanan_idleri": uygulanan,
        "reddedilenler": reddedilen,
    }
```

```hint
Her isteği doğrulama işlevinden geçir; benzersiz `istek_id` kontrolü yap ve `izin_verildi` durumuna göre `uygulanan_idleri` veya `reddedilenler` içine ayır.
```
:::

::: gorev Gerçek deney · Yerel modelle yıkıcı eylemlerde insan onayı (HITL) ve imzalı kapı deneyi
Önceki üç görevde yazdığın `gorev_imzasi_uret`, `hitl_kapisi_dogrula` ve `mudahale_kuyrugu_yurut` işlevlerini bu adımda birleştir.

Canlı deneyde:
1. Yerel Ollama modeli (`ai_lab.SohbetOturumu`) parametreye bağlı insan onayı jetonunun neden hedef değiştirme saldırılarını önlediğini değerlendirir.
2. Salt-okunur (`req-101`), geçerli imzalı (`req-102`), onaysız (`req-103`) ve hedefi değiştirilmiş (`req-104`) müdahale kuyruğu senin yazdığın `mudahale_kuyrugu_yurut` kapısından geçirilir.
3. Onaysız ve değiştirilmiş parametreli yıkıcı çağrıların deterministik olarak reddedildiği kanıtlanır.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def gorev_imzasi_uret(istek_id, arac, hedef, gizli_anahtar):
    # KUSURLU BAŞLANGIÇ KODU: parametreleri imzalamadan boş dize döndürüyor!
    return ""

def hitl_kapisi_dogrula(istek, gizli_anahtar):
    # KUSURLU BAŞLANGIÇ KODU: onay jetonunu doğrulamadan her isteği onaylıyor!
    return {"istek_id": istek.get("istek_id", "") if isinstance(istek, dict) else "", "izin_verildi": True, "neden": "imzali_onay_gecerli"}

def mudahale_kuyrugu_yurut(istekler, gizli_anahtar):
    # KUSURLU BAŞLANGIÇ KODU: istekleri doğrulamadan doğrudan uyguluyor!
    return {"uygulanan_idleri": [i["istek_id"] for i in istekler if isinstance(i, dict)], "reddedilenler": {}}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_ile_guvenlik_14 as deney
    deney.goster(gorev_imzasi_uret, hitl_kapisi_dogrula, mudahale_kuyrugu_yurut)
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from ai_ile_guvenlik_veri import hazirla
hazirla("ai-ile-guvenlik-14")
```

```test
import copy
import ast
import ai_lab
from sandbox import ai_gercek_ai_ile_guvenlik_14 as D

checks = []
_base_ok = ok
def ok(kosul, mesaj):
    checks.append(bool(kosul))
    return _base_ok(kosul, mesaj)

for ad in ("gorev_imzasi_uret", "hitl_kapisi_dogrula", "mudahale_kuyrugu_yurut"):
    need(ad)

sorun = ai_lab.kod_denetimi(
    src,
    ("gorev_imzasi_uret_referans", "hitl_kapisi_dogrula_referans", "mudahale_kuyrugu_yurut_referans", "kanit_yaz"),
)
ok(not sorun, "laboratuvar yamalanmamalı, referans işlevler çağrılmamalı")
if not all(checks):
    stop()

try:
    _ag_tree = ast.parse(src)
    for _node in ast.walk(_ag_tree):
        if isinstance(_node, ast.ImportFrom):
            for _alias in _node.names:
                if _alias.name == "*":
                    ok(False, "Kopya/güvenlik ihlali: wildcard (*) import yasaktır")
        if isinstance(_node, ast.Name) and "referans" in _node.id.lower():
            ok(False, f"Kopya/güvenlik ihlali: 'referans' kullanımı tespit edildi: {_node.id}")
        if isinstance(_node, ast.Attribute) and "referans" in _node.attr.lower():
            ok(False, f"Kopya/güvenlik ihlali: 'referans' niteliği tespit edildi: {_node.attr}")
        if isinstance(_node, ast.Call) and isinstance(_node.func, ast.Name) and _node.func.id in ("getattr", "eval", "exec"):
            ok(False, f"Kopya/güvenlik ihlali: dinamik fonksiyon çağrısı yasaktır: {_node.func.id}")
except Exception as _e:
    ok(False, f"AST ayrıştırma hatası: {_e}")
if not all(checks):
    stop()

def _on_sozlesme():
    try:
        for args in [("", "a", "h", "k"), ("i", "a", "h", "")]:
            try:
                gorev_imzasi_uret(*args)
                return False
            except ValueError:
                pass
        for i_in, k_in in [(None, D.GIZLI_ANAHTAR), (D.ORNEK_ISTEKLER[0], "")]:
            try:
                hitl_kapisi_dogrula(i_in, k_in)
                return False
            except ValueError:
                pass
        for l_in in (None, [], [D.ORNEK_ISTEKLER[0], D.ORNEK_ISTEKLER[0]]):
            try:
                mudahale_kuyrugu_yurut(l_in, D.GIZLI_ANAHTAR)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(_on_sozlesme(), "sentetik ön kontrol: HMAC-SHA256 imza ve HITL kapısı kuralları tam")

if not all(checks):
    stop()

try:
    r = D.deney(gorev_imzasi_uret, hitl_kapisi_dogrula, mudahale_kuyrugu_yurut)
except Exception as e:
    ok(False, f"GERÇEK HITL KAPISI DENEYİ YAPILAMADI: {type(e).__name__}: {e}")
    stop()

for ad, deger in r["kontroller"].items():
    ok(deger, "gerçek deney: " + ad)

ai_lab.kanit_yaz("ile-guvenlik-14-hitl", {
    "kaynak": "gercek",
    "kabul": all(checks),
    "ders": "ai-ile-guvenlik-14",
    "ortam": r["ortam"],
    "ayarlar": r["ayarlar"],
    "deney": r,
    "ozet": r["ozet"],
})
o = r["ozet"]
ok(
    True,
    f"BULGU ({o['model']}): uygulanan={o['uygulanan']}, reddedilenler={o['reddedilenler']}.",
)
```

```solution
import hashlib
import hmac
import ai_lab
from sandbox.ai_gercek_ai_ile_guvenlik_14 import _istek_kontrol

def gorev_imzasi_uret(istek_id, arac, hedef, gizli_anahtar):
    if not all(isinstance(x, str) and bool(x.strip()) for x in (istek_id, arac, hedef, gizli_anahtar)):
        raise ValueError("tüm parametreler boş olmayan string olmalı")
    mesaj = f"{istek_id}:{arac}:{hedef}".encode("utf-8")
    anahtar = gizli_anahtar.encode("utf-8")
    return hmac.new(anahtar, mesaj, hashlib.sha256).hexdigest()

def hitl_kapisi_dogrula(istek, gizli_anahtar):
    _istek_kontrol(istek)
    if not (isinstance(gizli_anahtar, str) and bool(gizli_anahtar.strip())):
        raise ValueError("gizli_anahtar boş olmayan string olmalı")

    iid = istek["istek_id"]
    if istek["risk_sinifi"] == "salt_okunur":
        return {"istek_id": iid, "izin_verildi": True, "neden": "salt_okunur_serbest"}

    jeton = istek["onay_jetonu"].strip()
    if not jeton:
        return {"istek_id": iid, "izin_verildi": False, "neden": "eksik_onay_jetonu"}

    beklenen = gorev_imzasi_uret(iid, istek["arac"], istek["hedef"], gizli_anahtar)
    if not hmac.compare_digest(jeton, beklenen):
        return {"istek_id": iid, "izin_verildi": False, "neden": "imza_uyumsuz"}

    return {"istek_id": iid, "izin_verildi": True, "neden": "imzali_onay_gecerli"}

def mudahale_kuyrugu_yurut(istekler, gizli_anahtar):
    if not (isinstance(istekler, list) and bool(istekler)):
        raise ValueError("istekler boş olmayan liste olmalı")

    uygulanan = []
    reddedilen = {}
    gorulen = set()

    for ist in istekler:
        sonuc = hitl_kapisi_dogrula(ist, gizli_anahtar)
        iid = sonuc["istek_id"]
        if iid in gorulen:
            raise ValueError("tekrarlanan istek_id")
        gorulen.add(iid)
        if sonuc["izin_verildi"]:
            uygulanan.append(iid)
        else:
            reddedilen[iid] = sonuc["neden"]

    return {
        "uygulanan_idleri": uygulanan,
        "reddedilenler": reddedilen,
    }

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_ile_guvenlik_14 as deney
    deney.goster(gorev_imzasi_uret, hitl_kapisi_dogrula, mudahale_kuyrugu_yurut)
```

```hint
Önceki üç görevdeki `gorev_imzasi_uret`, `hitl_kapisi_dogrula` ve `mudahale_kuyrugu_yurut` işlevlerini birleştir.
```
:::
