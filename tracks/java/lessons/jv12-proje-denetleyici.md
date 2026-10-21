---
id: jv12
title: Proje · Bir Spring Web Hizmetini Baştan Sona Okumak
summary: Filtre, DTO doğrulaması ve JDBC veri katmanından oluşan bir Java web hizmetini satır satır okuyup uçtan uca Python ve SQLite ile kurmak.
---

::: anlat Proje tanımı: Üç katmanlı Java web hizmeti
Gerçek bir kaynak kodu incelemesinde (OSWE / CWEE) tek bir sınıfa bakmazsın; isteğin **Filtre (`Filter`) → Denetleyici (`Controller` + `record` DTO) → Veri Katmanı (`Repository` / JDBC)** boyunca nasıl aktığını takip edersin.

Aşağıda bir BT olay bildirim hizmetinin üç bileşeni verilmiştir. Her satırın hangi girdiyi kabul edip hangisini reddettiğini dikkatlice oku:

```java
package tr.pafta.servis;

import java.sql.*;
import java.util.*;

public class BildirimServisi {
    private static final Set<String> IZINLI_SEVIYELER = Set.of("DUSUK", "ORTA", "YUKSEK", "KRITIK");

    // 1. KATMAN: İstek Başlığı ve Zaman Penceresi Filtresi
    public static String filtreKontrol(Map<String, String> basliklar, long sunucuSaniye) {
        if (basliklar == null) return "401:BASLIK_YOK";
        String imza = basliklar.get("X-Servis-Anahtar");
        String zamanMetin = basliklar.get("X-Zaman");
        if (!"pafta-ic-servis-2026".equals(imza) || zamanMetin == null) {
            return "401:YETKISIZ";
        }
        try {
            long istekSaniye = Long.parseLong(zamanMetin.trim());
            if (Math.abs(sunucuSaniye - istekSaniye) > 300L) {
                return "401:ZAMAN_ASIMI";
            }
            return "OK";
        } catch (NumberFormatException e) {
            return "400:GECERSIZ_ZAMAN";
        }
    }

    // 2. KATMAN: İstek Gövdesi (DTO) Doğrulaması
    public static String govdeDogrula(Map<String, Object> govde) {
        if (govde == null) return "400:BOZUK_JSON";
        Object kaynakObj = govde.get("kaynak");
        Object seviyeObj = govde.get("seviye");
        Object kodObj = govde.get("kod");

        if (!(kaynakObj instanceof String kaynakStr)) return "422:KAYNAK_METIN_OLMALI";
        String kaynak = kaynakStr.trim();
        if (kaynak.length() < 3 || kaynak.length() > 40 || !kaynak.matches("[a-z0-9.-]+")) {
            return "422:GECERSIZ_KAYNAK";
        }

        String seviye = (seviyeObj instanceof String s) ? s.trim().toUpperCase(Locale.ROOT) : "ORTA";
        if (!IZINLI_SEVIYELER.contains(seviye)) {
            return "422:GECERSIZ_SEVIYE";
        }

        if (!(kodObj instanceof Integer kod) || kod < 100 || kod > 999) {
            return "422:GECERSIZ_KOD";
        }
        return "200:" + kaynak + "|" + seviye + "|" + kod;
    }
}
```

### İnceleme Notları
| Katman | Kritik Sınır |
|---|---|
| `Math.abs(sunucuSaniye - istekSaniye) > 300L` | Tam `±300` saniye fark **kabul edilir**; `301` saniye reddedilir |
| `kaynak.matches("[a-z0-9.-]+")` | `3..40` karakter ve yalnızca küçük harf, rakam, nokta, tire |
| `seviyeObj instanceof String` | `seviye` hiç verilmemişse veya `String` değilse varsayılan `"ORTA"` olur! |
| `kodObj instanceof Integer` | `100..999` aralığında tam sayı zorunludur (Python'da `bool`, `int` alt sınıfı olduğu için `isinstance(kod, bool)` ayrıca reddedilmelidir!) |
:::

::: tahmin
Java 21 ile çalıştırıldığında bu doğrulama testi ne yazdırır?

```java
import java.util.*;

public class Ornek {
    static final Set<String> SEVIYELER = Set.of("DUSUK", "ORTA", "YUKSEK", "KRITIK");

    static String kontrol(Object seviyeObj, long farkSaniye) {
        if (Math.abs(farkSaniye) > 300L) {
            return "401:ZAMAN_ASIMI";
        }
        String seviye = (seviyeObj instanceof String s) ? s.trim().toUpperCase(Locale.ROOT) : "ORTA";
        if (!SEVIYELER.contains(seviye)) {
            return "422:GECERSIZ_SEVIYE";
        }
        return "OK:" + seviye;
    }

    public static void main(String[] args) {
        System.out.println(kontrol("  kritik ", 300L));
        System.out.println(kontrol("  kritik ", -301L));
        System.out.println(kontrol(null, 0L));
        System.out.println(kontrol("ACIL", 10L));
    }
}
```

```gercek
OK:KRITIK
401:ZAMAN_ASIMI
OK:ORTA
422:GECERSIZ_SEVIYE
```

???

`OK:KRITIK`, `401:ZAMAN_ASIMI`, `OK:ORTA`, `422:GECERSIZ_SEVIYE`. İlk çağrıda `300L` fark `> 300L` olmadığı için geçer ve `"  kritik "` → `"KRITIK"` olur. İkinci çağrıda `Math.abs(-301L)` değeri `301` olduğu için `401:ZAMAN_ASIMI` döner. Üçüncü çağrıda `null` bir `String` olmadığı için varsayılan `"ORTA"` seçilir (`OK:ORTA`). Dördüncü çağrıda `"ACIL"` kümede bulunmadığı için `422:GECERSIZ_SEVIYE` döner.
:::

::: gorev 1 · Filtre ve zaman penceresi (`filtreKontrol`)
`BildirimServisi.filtreKontrol(basliklar, sunucu_saniye)` metodunu Python'da `filtre_kontrol(basliklar, sunucu_saniye)` olarak kur.

```starter
def filtre_kontrol(basliklar, sunucu_saniye):
    return "OK"
```

```test
need("filtre_kontrol")
eq(filtre_kontrol({"X-Servis-Anahtar": "pafta-ic-servis-2026", "X-Zaman": "1000"}, 1300), "OK", "tam +300 sn sınırda OK")
eq(filtre_kontrol({"X-Servis-Anahtar": "pafta-ic-servis-2026", "X-Zaman": "1300"}, 1000), "OK", "tam -300 sn sınırda OK")
eq(filtre_kontrol({"X-Servis-Anahtar": "pafta-ic-servis-2026", "X-Zaman": "1000"}, 1301), "401:ZAMAN_ASIMI", "+301 sn -> 401:ZAMAN_ASIMI")
eq(filtre_kontrol({"X-Servis-Anahtar": "pafta-ic-servis-2026", "X-Zaman": "1301"}, 1000), "401:ZAMAN_ASIMI", "-301 sn -> 401:ZAMAN_ASIMI")
eq(filtre_kontrol({"X-Servis-Anahtar": "yanlis", "X-Zaman": "1000"}, 1000), "401:YETKISIZ", "yanlış anahtar -> 401:YETKISIZ")
eq(filtre_kontrol({"X-Servis-Anahtar": "pafta-ic-servis-2026"}, 1000), "401:YETKISIZ", "X-Zaman eksik -> 401:YETKISIZ")
eq(filtre_kontrol({"X-Servis-Anahtar": "pafta-ic-servis-2026", "X-Zaman": "bin"}, 1000), "400:GECERSIZ_ZAMAN", "sayı olmayan zaman -> 400:GECERSIZ_ZAMAN")
eq(filtre_kontrol(None, 1000), "401:BASLIK_YOK", "None başlıklar -> 401:BASLIK_YOK")
```

```solution
import re

def filtre_kontrol(basliklar, sunucu_saniye):
    if basliklar is None:
        return "401:BASLIK_YOK"
    imza = basliklar.get("X-Servis-Anahtar")
    zaman_metin = basliklar.get("X-Zaman")
    if imza != "pafta-ic-servis-2026" or zaman_metin is None:
        return "401:YETKISIZ"
    temiz = str(zaman_metin).strip()
    if not re.fullmatch(r"[+-]?[0-9]+", temiz):
        return "400:GECERSIZ_ZAMAN"
    istek_saniye = int(temiz)
    if abs(sunucu_saniye - istek_saniye) > 300:
        return "401:ZAMAN_ASIMI"
    return "OK"
```

```hint
`abs(sunucu_saniye - istek_saniye) > 300` kontrolünde `300` kabul edilir, `301` reddedilir.
```
:::

::: gorev 2 · İstek gövdesi doğrulaması (`govdeDogrula`)
`BildirimServisi.govdeDogrula(govde)` metodunu Python'da `govde_dogrula(govde)` olarak kur.

```starter
def govde_dogrula(govde):
    return "200:web01|ORTA|200"
```

```test
need("govde_dogrula")
eq(govde_dogrula({"kaynak": "  srv-01.pafta.local ", "seviye": "yuksek", "kod": 100}),
   "200:srv-01.pafta.local|YUKSEK|100", "geçerli girdi ve alt sınır kod=100")
eq(govde_dogrula({"kaynak": "abc", "kod": 999}),
   "200:abc|ORTA|999", "alt sınır kaynak uzunluğu 3, eksik seviyede ORTA, üst sınır kod=999")
eq(govde_dogrula({"kaynak": "a" * 40, "seviye": 123, "kod": 500}),
   "200:" + ("a" * 40) + "|ORTA|500", "üst sınır kaynak uzunluğu 40; String olmayan seviyede varsayılan ORTA")
eq(govde_dogrula({"kaynak": "ab", "kod": 200}), "422:GECERSIZ_KAYNAK", "2 karakterli kaynak (< 3) reddedilmeli")
eq(govde_dogrula({"kaynak": "a" * 41, "kod": 200}), "422:GECERSIZ_KAYNAK", "41 karakterli kaynak (> 40) reddedilmeli")
eq(govde_dogrula({"kaynak": "SRV_01", "kod": 200}), "422:GECERSIZ_KAYNAK", "büyük harf veya alt çizgi içeren kaynak reddedilmeli")
eq(govde_dogrula({"kaynak": 42, "kod": 200}), "422:KAYNAK_METIN_OLMALI", "sayı kaynak -> 422:KAYNAK_METIN_OLMALI")
eq(govde_dogrula({"kaynak": "web01", "seviye": "ACIL", "kod": 200}), "422:GECERSIZ_SEVIYE", "geçersiz seviye")
eq(govde_dogrula({"kaynak": "web01", "kod": 99}), "422:GECERSIZ_KOD", "kod=99 (< 100) reddedilmeli")
eq(govde_dogrula({"kaynak": "web01", "kod": 1000}), "422:GECERSIZ_KOD", "kod=1000 (> 999) reddedilmeli")
eq(govde_dogrula({"kaynak": "web01", "kod": True}), "422:GECERSIZ_KOD", "bool değer Integer değildir -> 422:GECERSIZ_KOD")
eq(govde_dogrula({"kaynak": "web01", "kod": "200"}), "422:GECERSIZ_KOD", "metin kod Integer değildir -> 422:GECERSIZ_KOD")
eq(govde_dogrula(None), "400:BOZUK_JSON", "None gövde -> 400:BOZUK_JSON")
```

```solution
import re

IZINLI_SEVIYELER = {"DUSUK", "ORTA", "YUKSEK", "KRITIK"}

def govde_dogrula(govde):
    if not isinstance(govde, dict):
        return "400:BOZUK_JSON"
    kaynak_obj = govde.get("kaynak")
    seviye_obj = govde.get("seviye")
    kod_obj = govde.get("kod")

    if not isinstance(kaynak_obj, str):
        return "422:KAYNAK_METIN_OLMALI"
    kaynak = kaynak_obj.strip()
    if not (3 <= len(kaynak) <= 40) or not re.fullmatch(r"[a-z0-9.-]+", kaynak):
        return "422:GECERSIZ_KAYNAK"

    seviye = seviye_obj.strip().upper() if isinstance(seviye_obj, str) else "ORTA"
    if seviye not in IZINLI_SEVIYELER:
        return "422:GECERSIZ_SEVIYE"

    if type(kod_obj) is not int or not (100 <= kod_obj <= 999):
        return "422:GECERSIZ_KOD"
    return f"200:{kaynak}|{seviye}|{kod_obj}"
```

```hint
Python'da `isinstance(True, int)` `True` döndürür; Java'da ise `Boolean` bir `Integer` değildir. Bu yüzden `type(kod_obj) is not int` (veya `isinstance(kod_obj, bool) or not isinstance(kod_obj, int)`) kontrolünü kullan.
```
:::

::: gorev 3 · Uçtan uca bildirim uç noktası (Filtre + Doğrulama + SQLite)
İlk iki görevdeki filtre ve doğrulama adımlarını birleştirip geçerli bildirimi `bildirimler (id INTEGER PRIMARY KEY, kaynak TEXT, seviye TEXT, kod INTEGER)` tablosuna parametreli sorguyla kaydeden `bildirim_isle(db, basliklar, sunucu_saniye, govde)` fonksiyonunu yaz:
- Filtre `"OK"` dönmezse veritabanına dokunmadan `(durum_kodu, hata_kodu)` döndür (`(401, "ZAMAN_ASIMI")` gibi).
- Gövde doğrulaması `"200:..."` dönmezse veritabanına dokunmadan `(durum_kodu, hata_kodu)` döndür (`(422, "GECERSIZ_KOD")` gibi).
- Geçerliyse satırı tabloya ekle (`commit`) ve `(201, f"#{id}:{kaynak}:{seviye}:{kod}")` döndür.

```starter
def bildirim_isle(db, basliklar, sunucu_saniye, govde):
    return 201, "#1:web01:ORTA:200"
```

```test
import sqlite3
need("bildirim_isle")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE bildirimler (id INTEGER PRIMARY KEY, kaynak TEXT, seviye TEXT, kod INTEGER)")
baslik = {"X-Servis-Anahtar": "pafta-ic-servis-2026", "X-Zaman": "1000"}

eq(bildirim_isle(db, baslik, 1300, {"kaynak": "abc", "seviye": "kritik", "kod": 999}),
   (201, "#1:abc:KRITIK:999"), "ilk geçerli bildirim (fark=300, kaynak=3, kod=999) kaydedilmeli")
eq(bildirim_isle(db, baslik, 1301, {"kaynak": "web-01", "seviye": "kritik", "kod": 502}),
   (401, "ZAMAN_ASIMI"), "zaman aşımında (fark=301) 401 dönmeli ve kaydedilmemeli")
eq(bildirim_isle(db, None, 1000, {"kaynak": "web-01", "kod": 200}),
   (401, "BASLIK_YOK"), "None başlık -> 401 BASLIK_YOK")
eq(bildirim_isle(db, {"X-Servis-Anahtar": "yanlis", "X-Zaman": "1000"}, 1000, {"kaynak": "web-01", "kod": 200}),
   (401, "YETKISIZ"), "yanlış anahtar -> 401 YETKISIZ")
eq(bildirim_isle(db, {"X-Servis-Anahtar": "pafta-ic-servis-2026"}, 1000, {"kaynak": "web-01", "kod": 200}),
   (401, "YETKISIZ"), "eksik zaman -> 401 YETKISIZ")
eq(bildirim_isle(db, {"X-Servis-Anahtar": "pafta-ic-servis-2026", "X-Zaman": "bin"}, 1000, {"kaynak": "web-01", "kod": 200}),
   (400, "GECERSIZ_ZAMAN"), "sayısal olmayan zaman -> 400 GECERSIZ_ZAMAN")
eq(bildirim_isle(db, baslik, 1000, None),
   (400, "BOZUK_JSON"), "None gövde -> 400 BOZUK_JSON")
eq(bildirim_isle(db, baslik, 1000, {"kaynak": 123, "kod": 200}),
   (422, "KAYNAK_METIN_OLMALI"), "sayı kaynak -> 422 KAYNAK_METIN_OLMALI")
eq(bildirim_isle(db, baslik, 1000, {"kaynak": "ab", "kod": 200}),
   (422, "GECERSIZ_KAYNAK"), "2 karakterli kaynak -> 422 GECERSIZ_KAYNAK")
eq(bildirim_isle(db, baslik, 1000, {"kaynak": "a" * 41, "kod": 200}),
   (422, "GECERSIZ_KAYNAK"), "41 karakterli kaynak -> 422 GECERSIZ_KAYNAK")
eq(bildirim_isle(db, baslik, 1000, {"kaynak": "BUYUK", "kod": 200}),
   (422, "GECERSIZ_KAYNAK"), "büyük harfli kaynak -> 422 GECERSIZ_KAYNAK")
eq(bildirim_isle(db, baslik, 1000, {"kaynak": "web-01", "seviye": "YOK", "kod": 200}),
   (422, "GECERSIZ_SEVIYE"), "geçersiz seviye -> 422 GECERSIZ_SEVIYE")
eq(bildirim_isle(db, baslik, 1000, {"kaynak": "web-01", "seviye": "kritik", "kod": 99}),
   (422, "GECERSIZ_KOD"), "kod=99 (< 100) -> 422 GECERSIZ_KOD")
eq(bildirim_isle(db, baslik, 1000, {"kaynak": "web-01", "seviye": "kritik", "kod": 1000}),
   (422, "GECERSIZ_KOD"), "kod=1000 (> 999) -> 422 GECERSIZ_KOD")
eq(bildirim_isle(db, baslik, 1000, {"kaynak": "web-01", "seviye": "kritik", "kod": "200"}),
   (422, "GECERSIZ_KOD"), "metin kod -> 422 GECERSIZ_KOD")
eq(bildirim_isle(db, baslik, 700, {"kaynak": "a" * 40, "kod": 100}),
   (201, "#2:" + ("a" * 40) + ":ORTA:100"), "ikinci geçerli bildirim (fark=300, kaynak=40, kod=100) #2 olarak kaydedilmeli")
eq(db.execute("SELECT COUNT(*) FROM bildirimler").fetchone()[0], 2, "tabloda tam 2 kayıt olmalı")
```

```solution
import re

IZINLI_SEVIYELER = {"DUSUK", "ORTA", "YUKSEK", "KRITIK"}

def _filtre(basliklar, sunucu_saniye):
    if basliklar is None:
        return "401:BASLIK_YOK"
    imza = basliklar.get("X-Servis-Anahtar")
    zaman_metin = basliklar.get("X-Zaman")
    if imza != "pafta-ic-servis-2026" or zaman_metin is None:
        return "401:YETKISIZ"
    temiz = str(zaman_metin).strip()
    if not re.fullmatch(r"[+-]?[0-9]+", temiz):
        return "400:GECERSIZ_ZAMAN"
    if abs(sunucu_saniye - int(temiz)) > 300:
        return "401:ZAMAN_ASIMI"
    return "OK"

def _dogrula(govde):
    if not isinstance(govde, dict):
        return "400:BOZUK_JSON"
    kaynak_obj = govde.get("kaynak")
    seviye_obj = govde.get("seviye")
    kod_obj = govde.get("kod")
    if not isinstance(kaynak_obj, str):
        return "422:KAYNAK_METIN_OLMALI"
    kaynak = kaynak_obj.strip()
    if not (3 <= len(kaynak) <= 40) or not re.fullmatch(r"[a-z0-9.-]+", kaynak):
        return "422:GECERSIZ_KAYNAK"
    seviye = seviye_obj.strip().upper() if isinstance(seviye_obj, str) else "ORTA"
    if seviye not in IZINLI_SEVIYELER:
        return "422:GECERSIZ_SEVIYE"
    if type(kod_obj) is not int or not (100 <= kod_obj <= 999):
        return "422:GECERSIZ_KOD"
    return f"200:{kaynak}|{seviye}|{kod_obj}"

def bildirim_isle(db, basliklar, sunucu_saniye, govde):
    f = _filtre(basliklar, sunucu_saniye)
    if f != "OK":
        kod, mesaj = f.split(":", 1)
        return int(kod), mesaj
    d = _dogrula(govde)
    if not d.startswith("200:"):
        kod, mesaj = d.split(":", 1)
        return int(kod), mesaj
    kaynak, seviye, kod_str = d[4:].split("|")
    kod_int = int(kod_str)
    cur = db.execute(
        "INSERT INTO bildirimler (kaynak, seviye, kod) VALUES (?, ?, ?)",
        (kaynak, seviye, kod_int),
    )
    db.commit()
    return 201, f"#{cur.lastrowid}:{kaynak}:{seviye}:{kod_int}"
```

```hint
Önce filtre kontrolünü, sonra gövde doğrulamasını çağır; hata varsa `f.split(":", 1)` ile `(int(kod), mesaj)` döndür. Başarılıysa `INSERT INTO bildirimler (kaynak, seviye, kod) VALUES (?, ?, ?)` çalıştırıp `cur.lastrowid` ile yanıtı üret.
```
:::
