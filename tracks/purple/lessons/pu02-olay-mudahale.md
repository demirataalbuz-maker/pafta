---
id: pu02
title: Olay Müdahalesi · Zaman Çizelgesi ve Playbook
summary: Olay müdahalesinin adımları (doğrula, kapsamla, sınırla, temizle, ders çıkar); farklı saat dilimi ve biçimlerdeki kaynakları tek UTC zaman çizelgesinde birleştirmek; cihaz ve hesap üzerinden kapsamlamak; olay türüne göre playbook seçmek ve bağımlılıklara göre sıralamak; sınırlama ve temizleme önkoşullarını atomik durum geçişleriyle uygulamak; kanıtları değiştirmeden kopyalamak, SHA-256 manifestosu üretmek ve bütünlüğü doğrulamak. Python, yerel ve zararsız sentetik kayıtlar.
---

::: anlat Bir olayın ilk saati
Bir alarm geldi: "pc-ayse'de şüpheli bir dosya indirildi". Olay müdahalesi (incident response) bu noktada bir sırayla ilerler:

| Adım | Soru |
|---|---|
| Doğrula | Gerçekten bir olay mı, yanlış alarm mı? |
| Kapsamla | Hangi cihazlar ve hesaplar etkilendi, ne zamandan beri? |
| Sınırla | Yayılmayı nasıl durdururuz (cihazı ağdan ayırmak, hesabı kilitlemek)? |
| Temizle ve geri dön | Kalıcılık izlerini kaldırmak, sistemi güvenle geri açmak |
| Ders çıkar | Hangi tespit eksikti, neyi değiştiriyoruz? |

Önce **zaman çizelgesi** ve **kapsam** ile başlıyoruz; ardından aynı olay verisi üzerinde playbook kararlarını, sınırlama ve temizleme adımlarını uygulayacağız. Kayıtlar farklı ekiplerden, farklı biçimlerde gelir:

| Kaynak | Dosya | Zaman biçimi |
|---|---|---|
| Windows güvenlik günlüğü dökümü | `guvenlik.csv` (`;` ayraçlı) | `19.10.2026 12:03:40`, **İstanbul yerel saati** (UTC+3) |
| Web vekil sunucusu | `proxy.jsonl` (satır başına bir JSON) | `2026-10-19T09:02:10Z`, UTC |
| Uç nokta ajanı (EDR) | `edr.json` (JSON dizisi) | `1792400550`, epoch saniyesi (UTC) |

Cihaz ve hesap adları da kaynaktan kaynağa farklı yazılır: `PC-AYSE`, `pc-ayse`, `Pc-Ayse`. Karşılaştırmadan önce hepsini küçük harfe çevir.

> [!TUZAK] Saat dilimini yazmayan zaman damgası
> `datetime.strptime` saat dilimi olmayan ("naive") bir zaman üretir. Yerel saatle UTC'yi naive zamanlar olarak karşılaştırırsan sıralama üç saat kayar ve "önce indirildi, sonra çalıştı" sırası tersine dönebilir. Her kaynağı önce kendi diliminde **farkında** (aware) bir zamana çevir (`.replace(tzinfo=...)`), sonra UTC'ye (`.astimezone(timezone.utc)`).

```python norun
import datetime as dt
IST = dt.timezone(dt.timedelta(hours=3))
yerel = dt.datetime.strptime("19.10.2026 12:03:40", "%d.%m.%Y %H:%M:%S").replace(tzinfo=IST)
yerel.astimezone(dt.timezone.utc)          # 2026-10-19 09:03:40+00:00
dt.datetime.fromtimestamp(1792400550, dt.timezone.utc)   # epoch → UTC; ikinci argümansız yerel saat olur
```
:::

::: tahmin
Bu kod ne yazar?

```python
import datetime as dt
IST = dt.timezone(dt.timedelta(hours=3))
a = dt.datetime.strptime("19.10.2026 12:03:40", "%d.%m.%Y %H:%M:%S").replace(tzinfo=IST)
b = dt.datetime.strptime("2026-10-19T09:04:05Z", "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
print(a < b, a.astimezone(dt.timezone.utc).strftime("%H:%M:%S"))
```

???

**`True 09:03:40`**

```
True 09:03:40
```

Yerel saat 12:03:40, UTC'de 09:03:40'tır; vekil sunucudaki 09:04:05'ten **önce**. İki zaman da farkında olduğu için Python karşılaştırırken dilimleri hesaba katar. `.replace(tzinfo=IST)` yazılmasaydı `a` naive kalırdı ve naive ile farkında bir zamanı karşılaştırmak `TypeError` verirdi. Bu iyi bir hata: sessizce yanlış sıralamaktan iyidir.
:::

::: gorev 1 · Tek zaman çizelgesi
`zaman_cizelgesi()` fonksiyonunu yaz: üç dosyadaki bütün kayıtları tek bir listede, `(utc_zaman, kaynak, cihaz, kullanici, aciklama)` demetleri olarak döndür.

- `utc_zaman`: `"YYYY-AA-GG SS:DD:ss"` biçiminde UTC metni.
- `kaynak`: `"guvenlik"`, `"proxy"` ya da `"edr"`.
- `cihaz` ve `kullanici` küçük harfle.
- `aciklama`: güvenlik kaydında `"<olay> <aciklama>"` (ör. `"4688 yeni süreç: fatura.exe"`), proxy'de `url`, EDR'de `olay`.
- Zamana göre artan; aynı saniyedeki kayıtlar kaynak adına göre.

```starter
import csv
import json


def zaman_cizelgesi():
    olaylar = []
    for r in csv.DictReader(open("guvenlik.csv", encoding="utf-8", newline=""), delimiter=";"):
        olaylar.append((r["zaman"], "guvenlik", r["bilgisayar"], r["kullanici"], r["aciklama"]))
    return sorted(olaylar)


for olay in zaman_cizelgesi():
    print(*olay, sep=" | ")
```

```test
need("zaman_cizelgesi")
c = zaman_cizelgesi()
eq(len(c), 13, "üç kaynaktan on üç kayıt")
eq([o[:2] for o in c[:5]], [("2026-10-19 08:50:00", "guvenlik"), ("2026-10-19 09:02:10", "proxy"), ("2026-10-19 09:02:30", "edr"),
                            ("2026-10-19 09:03:40", "guvenlik"), ("2026-10-19 09:04:05", "proxy")],
   "yerel saat UTC'ye çevrildi: 12:03:40 → 09:03:40, indirmeden (09:02:10) sonra")
eq(c[2], ("2026-10-19 09:02:30", "edr", "pc-ayse", "ayse", "dosya oluşturuldu: fatura.zip"), "EDR kaydı: epoch → UTC, adlar küçük harf")
eq(c[3][4], "4688 yeni süreç: fatura.exe", "güvenlik açıklaması olay numarasıyla")
eq(sorted({o[2] for o in c}), ["pc-ayse", "pc-can", "pc-mert", "srv-dosya", "srv-yedek"], "beş cihaz, tek yazımla")
eq([o[1:3] for o in c if o[0] == "2026-10-19 09:10:00"], [("edr", "srv-dosya"), ("proxy", "pc-ayse")],
   "aynı saniyedeki iki kayıt kaynak adına göre: edr, proxy")
```

```solution
import csv
import datetime as dt
import json

UTC = dt.timezone.utc
IST = dt.timezone(dt.timedelta(hours=3))


def zaman_cizelgesi():
    olaylar = []
    for r in csv.DictReader(open("guvenlik.csv", encoding="utf-8", newline=""), delimiter=";"):
        t = dt.datetime.strptime(r["zaman"], "%d.%m.%Y %H:%M:%S").replace(tzinfo=IST).astimezone(UTC)
        olaylar.append((t, "guvenlik", r["bilgisayar"].lower(), r["kullanici"].lower(), f'{r["olay"]} {r["aciklama"]}'))
    for satir in open("proxy.jsonl", encoding="utf-8"):
        k = json.loads(satir)
        t = dt.datetime.strptime(k["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        olaylar.append((t, "proxy", k["cihaz"].lower(), k["kullanici"].lower(), k["url"]))
    for k in json.load(open("edr.json", encoding="utf-8")):
        t = dt.datetime.fromtimestamp(k["zaman"], UTC)
        olaylar.append((t, "edr", k["cihaz"].lower(), k["kullanici"].lower(), k["olay"]))
    olaylar.sort(key=lambda o: (o[0], o[1]))
    return [(o[0].strftime("%Y-%m-%d %H:%M:%S"),) + o[1:] for o in olaylar]


for olay in zaman_cizelgesi():
    print(*olay, sep=" | ")
```

```hint
Üç dönüşüm: CSV için `strptime(..., "%d.%m.%Y %H:%M:%S").replace(tzinfo=IST).astimezone(UTC)`, proxy için `strptime(..., "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)`, EDR için `datetime.fromtimestamp(saniye, UTC)`. Sıralamayı metne çevirmeden önce zaman nesneleri üzerinde yap.
```

```setup
import json
open("guvenlik.csv", "w", encoding="utf-8", newline="").write(
    "zaman;olay;bilgisayar;kullanici;aciklama\n"
    "19.10.2026 11:50:00;4624;PC-CAN;ayse;etkileşimli oturum\n"
    "19.10.2026 12:03:40;4688;PC-AYSE;ayse;yeni süreç: fatura.exe\n"
    "19.10.2026 12:07:15;4624;SRV-DOSYA;ayse;ağ oturumu, kaynak PC-AYSE\n"
    "19.10.2026 12:09:02;4624;SRV-DOSYA;yedek_svc;ağ oturumu, kaynak SRV-DOSYA\n"
    "19.10.2026 12:15:30;4624;SRV-YEDEK;yedek_svc;ağ oturumu, kaynak SRV-DOSYA\n"
    "19.10.2026 12:20:00;4624;PC-CAN;can;etkileşimli oturum\n")
with open("proxy.jsonl", "w", encoding="utf-8") as f:
    for k in [{"ts": "2026-10-19T09:02:10Z", "cihaz": "pc-ayse", "kullanici": "ayse", "url": "http://dosya.example/fatura.zip"},
              {"ts": "2026-10-19T09:04:05Z", "cihaz": "pc-ayse", "kullanici": "ayse", "url": "http://guncelle.example/k"},
              {"ts": "2026-10-19T09:10:00Z", "cihaz": "pc-ayse", "kullanici": "ayse", "url": "http://guncelle.example/k2"},
              {"ts": "2026-10-19T09:21:00Z", "cihaz": "pc-can", "kullanici": "can", "url": "http://haber.example/"}]:
        f.write(json.dumps(k, ensure_ascii=False) + "\n")
json.dump([{"zaman": 1792400550, "cihaz": "Pc-Ayse", "kullanici": "AYSE", "olay": "dosya oluşturuldu: fatura.zip"},
           {"zaman": 1792401000, "cihaz": "srv-dosya", "kullanici": "yedek_svc", "olay": "yeni hizmet kuruldu"},
           {"zaman": 1792401200, "cihaz": "PC-MERT", "kullanici": "mert", "olay": "dosya oluşturuldu: rapor.docx"}],
          open("edr.json", "w", encoding="utf-8"), ensure_ascii=False)
```
:::

::: gorev 2 · Kapsamı bulmak
`kapsamla(cizelge, cihaz, baslangic)` fonksiyonunu yaz: başlangıç cihazından yola çıkıp olaya karışan **bütün** cihazları ve hesapları bul.

- Bir kayıt, cihazını ve hesabını birbirine bağlar. Kapsamdaki bir cihazda görülen hesap kapsama girer; kapsamdaki bir hesabın görüldüğü cihaz kapsama girer. Yeni bir şey eklenmeyene kadar sürdür.
- Yalnız `baslangic`'tan (UTC metni) **itibaren** olan kayıtları kullan: olaydan önceki sıradan bir oturum kapsamı şişirmesin.
- Dönüş: `{"cihazlar": [...], "kullanicilar": [...]}`, ikisi de sıralı.

Görev 1'in `zaman_cizelgesi` fonksiyonu bu kodda da olmalı (kopyala).

```starter
def kapsamla(cizelge, cihaz, baslangic):
    kullanicilar = {o[3] for o in cizelge if o[2] == cihaz}
    return {"cihazlar": [cihaz], "kullanicilar": sorted(kullanicilar)}
```

```test
need("kapsamla"); need("zaman_cizelgesi")
c = zaman_cizelgesi()
eq(kapsamla(c, "pc-ayse", "2026-10-19 09:02:10"),
   {"cihazlar": ["pc-ayse", "srv-dosya", "srv-yedek"], "kullanicilar": ["ayse", "yedek_svc"]},
   "ayse → srv-dosya → yedek_svc → srv-yedek; can ve mert olaya karışmadı")
eq(kapsamla(c, "pc-ayse", "2026-10-19 08:00:00")["cihazlar"], ["pc-ayse", "pc-can", "srv-dosya", "srv-yedek"],
   "başlangıç geriye çekilirse 08:50'deki eski oturum pc-can'ı da içeri alır")
eq(kapsamla(c, "pc-mert", "2026-10-19 09:02:10"), {"cihazlar": ["pc-mert"], "kullanicilar": ["mert"]}, "ilgisiz cihaz kendi başına kalır")
eq(kapsamla(c, "pc-ayse", "2026-10-19 09:10:00"), {"cihazlar": ["pc-ayse"], "kullanicilar": ["ayse"]},
   "başlangıç anındaki kayıt dahildir (09:10:00); ayse'nin srv-dosya oturumu ondan önce olduğu için girmez")
eq(kapsamla(c, "pc-ayse", "2026-10-19 09:10:01"), {"cihazlar": ["pc-ayse"], "kullanicilar": []},
   "başlangıçtan sonra pc-ayse'de kayıt yoksa kapsam yalnız o cihazdır")
```

```solution
import csv
import datetime as dt
import json

UTC = dt.timezone.utc
IST = dt.timezone(dt.timedelta(hours=3))


def zaman_cizelgesi():
    olaylar = []
    for r in csv.DictReader(open("guvenlik.csv", encoding="utf-8", newline=""), delimiter=";"):
        t = dt.datetime.strptime(r["zaman"], "%d.%m.%Y %H:%M:%S").replace(tzinfo=IST).astimezone(UTC)
        olaylar.append((t, "guvenlik", r["bilgisayar"].lower(), r["kullanici"].lower(), f'{r["olay"]} {r["aciklama"]}'))
    for satir in open("proxy.jsonl", encoding="utf-8"):
        k = json.loads(satir)
        t = dt.datetime.strptime(k["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        olaylar.append((t, "proxy", k["cihaz"].lower(), k["kullanici"].lower(), k["url"]))
    for k in json.load(open("edr.json", encoding="utf-8")):
        t = dt.datetime.fromtimestamp(k["zaman"], UTC)
        olaylar.append((t, "edr", k["cihaz"].lower(), k["kullanici"].lower(), k["olay"]))
    olaylar.sort(key=lambda o: (o[0], o[1]))
    return [(o[0].strftime("%Y-%m-%d %H:%M:%S"),) + o[1:] for o in olaylar]


def kapsamla(cizelge, cihaz, baslangic):
    cihazlar, kullanicilar = {cihaz}, set()
    olaylar = [o for o in cizelge if o[0] >= baslangic]
    degisti = True
    while degisti:
        degisti = False
        for _, _, c, k, _ in olaylar:
            if (c in cihazlar or k in kullanicilar) and not (c in cihazlar and k in kullanicilar):
                cihazlar.add(c)
                kullanicilar.add(k)
                degisti = True
    return {"cihazlar": sorted(cihazlar), "kullanicilar": sorted(kullanicilar)}


print(kapsamla(zaman_cizelgesi(), "pc-ayse", "2026-10-19 09:02:10"))
```

```hint
İki küme tut (cihazlar, kullanıcılar) ve kayıtların üstünden, hiçbir küme büyümeyene kadar tekrar tekrar geç. Bir kaydın cihazı ya da hesabı kümelerden birindeyse ötekini de ekle.
```

```hint
Zaman metinleri `"YYYY-AA-GG SS:DD:ss"` biçiminde olduğu için metin karşılaştırması zaman sırasıyla aynıdır: `o[0] >= baslangic`.
```

```setup
import json
open("guvenlik.csv", "w", encoding="utf-8", newline="").write(
    "zaman;olay;bilgisayar;kullanici;aciklama\n"
    "19.10.2026 11:50:00;4624;PC-CAN;ayse;etkileşimli oturum\n"
    "19.10.2026 12:03:40;4688;PC-AYSE;ayse;yeni süreç: fatura.exe\n"
    "19.10.2026 12:07:15;4624;SRV-DOSYA;ayse;ağ oturumu, kaynak PC-AYSE\n"
    "19.10.2026 12:09:02;4624;SRV-DOSYA;yedek_svc;ağ oturumu, kaynak SRV-DOSYA\n"
    "19.10.2026 12:15:30;4624;SRV-YEDEK;yedek_svc;ağ oturumu, kaynak SRV-DOSYA\n"
    "19.10.2026 12:20:00;4624;PC-CAN;can;etkileşimli oturum\n")
with open("proxy.jsonl", "w", encoding="utf-8") as f:
    for k in [{"ts": "2026-10-19T09:02:10Z", "cihaz": "pc-ayse", "kullanici": "ayse", "url": "http://dosya.example/fatura.zip"},
              {"ts": "2026-10-19T09:04:05Z", "cihaz": "pc-ayse", "kullanici": "ayse", "url": "http://guncelle.example/k"},
              {"ts": "2026-10-19T09:10:00Z", "cihaz": "pc-ayse", "kullanici": "ayse", "url": "http://guncelle.example/k2"},
              {"ts": "2026-10-19T09:21:00Z", "cihaz": "pc-can", "kullanici": "can", "url": "http://haber.example/"}]:
        f.write(json.dumps(k, ensure_ascii=False) + "\n")
json.dump([{"zaman": 1792400550, "cihaz": "Pc-Ayse", "kullanici": "AYSE", "olay": "dosya oluşturuldu: fatura.zip"},
           {"zaman": 1792401000, "cihaz": "srv-dosya", "kullanici": "yedek_svc", "olay": "yeni hizmet kuruldu"},
           {"zaman": 1792401200, "cihaz": "PC-MERT", "kullanici": "mert", "olay": "dosya oluşturuldu: rapor.docx"}],
          open("edr.json", "w", encoding="utf-8"), ensure_ascii=False)
```
:::

::: anlat Playbook bir kontrol listesi değil, bağımlılık grafiğidir
**Playbook**, belirli bir olay türünde hangi kararların ve müdahale adımlarının uygulanacağını tanımlar. Adımları listede gördüğün sırayla körlemesine çalıştırmak yerine önkoşullarını denetle: kanıt toplanmadan sınırlama, sınırlama tamamlanmadan temizleme, temizlik doğrulanmadan geri açma yapılmaz. Bu dersin laboratuvarında bu sıra açık `gerektirir` bağımlılıklarıyla verilir; gerçek kurumun onay ve acil durum yolları ayrıca playbook'a işlenir.

**Sınırlama** (containment) yayılımı durdurur: cihazı izole etmek ve hesabı kilitlemek. **Temizleme** (eradication) zararlı dosya ve kalıcılığı kaldırır. Temizlik, sınırlamanın yerine geçmez; tek başına dosya silmek, başka cihazlara yayılım sürerken yalnız görünen izi ortadan kaldırır.

Kanıt da temizlenecek bir "artık" değildir. Özgün kayıtlar değiştirilmeden kopyalanır, her kopyanın SHA-256 özeti bir manifestoya yazılır ve sonraki doğrulamada bayt bayt bütünlük denetlenir. Aşağıdaki kodlar yalnız görevin geçici klasöründeki zararsız olay verisini ve durum sözlüklerini işler; gerçek ağ, hesap ya da sistem ayarını değiştirmez.
:::

::: gorev 3 · Doğru playbook'u ve adım sırasını seç
`playbook(playbooklar, olay)` fonksiyonunu yaz.

- `olay["yanlis_alarm"]` doğruysa `[]` döndür; olayı doğrulanmamışsa (`dogrulandi` yanlışsa) yalnız `["kanit-topla", "dogrula"]` döndür.
- Doğrulanmış olayda `tur` alanı eşleşen playbook'lardan `oncelik` değeri en küçük olanı seç. Eşleşme yoksa `ValueError` yükselt.
- Seçilen playbook'un `adimlar` listesindeki her adım `{"id": ..., "gerektirir": [...]}` biçiminde. Adım kimliklerini, her adımın bütün bağımlılıkları kendisinden önce gelecek biçimde döndür. Aynı anda hazır olan adımları kimliğe göre sırala.
- Bilinmeyen bağımlılık, yinelenen adım kimliği ya da bağımlılık döngüsü `ValueError` üretmeli; bozuk bir sırayı sessizce döndürme.

```starter
def playbook(playbooklar, olay):
    for p in playbooklar:
        if p["tur"] == olay["tur"]:
            return [a["id"] for a in p["adimlar"]]
    return []
```

```test
import json
need("playbook")
P = json.load(open("playbooklar.json", encoding="utf-8"))
eq(playbook(P, {"tur": "kotucul-yurutme", "dogrulandi": True}),
   ["kanit-topla", "agdan-ayir", "hesabi-kilitle", "kaliciligi-kaldir", "temizligi-dogrula", "geri-ac"],
   "öncelik 10 seçilir; kanıt → sınırlama → temizleme → doğrulama → geri açma")
eq(playbook(P, {"tur": "oltalama", "dogrulandi": True}),
   ["kanit-topla", "hesabi-kilitle", "oturumlari-iptal-et"],
   "oltalama playbook'u; oturum iptali hesap kilidinden sonra")
eq(playbook(P, {"tur": "oltalama", "dogrulandi": False}), ["kanit-topla", "dogrula"],
   "doğrulanmamış olayda henüz containment yok")
eq(playbook(P, {"tur": "oltalama", "dogrulandi": True, "yanlis_alarm": True}), [],
   "yanlış alarm müdahale zincirine girmez")
raises(ValueError, playbook, P, {"tur": "bilinmeyen", "dogrulandi": True}, msg="playbook eşleşmesi yok")
raises(ValueError, playbook, [{"tur": "x", "oncelik": 1, "adimlar": [{"id": "a", "gerektirir": ["yok"]}]}],
       {"tur": "x", "dogrulandi": True}, msg="bilinmeyen bağımlılık")
raises(ValueError, playbook, [{"tur": "x", "oncelik": 1, "adimlar": [{"id": "a", "gerektirir": ["b"]}, {"id": "b", "gerektirir": ["a"]}]}],
       {"tur": "x", "dogrulandi": True}, msg="döngü")
raises(ValueError, playbook, [{"tur": "x", "oncelik": 1, "adimlar": [{"id": "a"}, {"id": "a"}]}],
       {"tur": "x", "dogrulandi": True}, msg="yinelenen adım")
```

```solution
def playbook(playbooklar, olay):
    if olay.get("yanlis_alarm"):
        return []
    if not olay.get("dogrulandi"):
        return ["kanit-topla", "dogrula"]
    uygun = [p for p in playbooklar if p["tur"] == olay["tur"]]
    if not uygun:
        raise ValueError("Olay türüne uygun playbook yok")
    secilen = min(uygun, key=lambda p: p["oncelik"])
    adimlar = {a["id"]: a for a in secilen["adimlar"]}
    if len(adimlar) != len(secilen["adimlar"]):
        raise ValueError("Yinelenen adım kimliği")
    kalan = set(adimlar)
    sonuc = []
    while kalan:
        hazir = sorted(a for a in kalan if all(g in sonuc for g in adimlar[a].get("gerektirir", [])))
        if not hazir:
            raise ValueError("Bilinmeyen bağımlılık veya döngü")
        for ad in hazir:
            sonuc.append(ad)
            kalan.remove(ad)
    return sonuc


print(playbook(__import__("json").load(open("playbooklar.json", encoding="utf-8")),
               {"tur": "kotucul-yurutme", "dogrulandi": True}))
```

```hint
Önce karar kapılarını uygula. Sonra adımları kimlikten adım sözlüğüne eşle; her turda bağımlılıkları zaten `sonuc` içinde olan hazır adımları seç. Hazır adım kalmadığı hâlde `kalan` boş değilse grafik geçersizdir.
```

```setup
import json
P = [
    {"tur": "kotucul-yurutme", "oncelik": 20, "adimlar": [{"id": "yanlis-playbook"}]},
    {"tur": "kotucul-yurutme", "oncelik": 10, "adimlar": [
        {"id": "geri-ac", "gerektirir": ["temizligi-dogrula"]},
        {"id": "hesabi-kilitle", "gerektirir": ["kanit-topla"]},
        {"id": "kaliciligi-kaldir", "gerektirir": ["agdan-ayir", "hesabi-kilitle"]},
        {"id": "kanit-topla"},
        {"id": "temizligi-dogrula", "gerektirir": ["kaliciligi-kaldir"]},
        {"id": "agdan-ayir", "gerektirir": ["kanit-topla"]}
    ]},
    {"tur": "oltalama", "oncelik": 10, "adimlar": [
        {"id": "oturumlari-iptal-et", "gerektirir": ["hesabi-kilitle"]},
        {"id": "kanit-topla"},
        {"id": "hesabi-kilitle", "gerektirir": ["kanit-topla"]}
    ]}
]
json.dump(P, open("playbooklar.json", "w", encoding="utf-8"), ensure_ascii=False)
```
:::

::: gorev 4 · Sınırlama ve temizleme adımlarını güvenle uygula
`mudahale(durum, adimlar)` fonksiyonunu yaz: yerel olay durumunun **derin kopyası** üzerinde adımları sırayla uygula ve yeni durumu döndür. Girdi sözlüğü hiçbir durumda değişmemeli; bir adım geçersizse `ValueError` yükselip bütün işlem reddedilmeli.

Desteklenen adımlar ve kurallar:

- `kanit-topla`: `kanit_toplandi` alanını doğrular.
- `agdan-ayir:<cihaz>` ve `hesabi-kilitle:<hesap>`: yalnız kanıt toplandıktan sonra; var olan varlığın `izole` / `kilitli` alanını doğru yapar.
- `kaliciligi-kaldir:<ad>` ve `zararliyi-kaldir:<ad>`: **bütün** cihazlar izole ve **bütün** hesaplar kilitliyse ilgili listeden var olan öğeyi kaldırır.
- `temizligi-dogrula`: iki liste de boşsa `temizlik_dogrulandi` alanını doğru yapar.
- `geri-ac`: temizlik doğrulanmışsa yalnız cihaz izolasyonlarını kaldırır; hesap kilitlerini açmaz.

Bilinmeyen adım, cihaz, hesap veya listede olmayan kalıcılık/zararlı adı da `ValueError` üretir.

```starter
def mudahale(durum, adimlar):
    for adim in adimlar:
        if adim.startswith("agdan-ayir:"):
            durum["cihazlar"][adim.split(":")[1]]["izole"] = True
        elif adim.startswith("kaliciligi-kaldir:"):
            durum["kalicilik"].remove(adim.split(":")[1])
    return durum
```

```test
import copy
import json
need("mudahale")
D = json.load(open("olay.json", encoding="utf-8"))
O = copy.deepcopy(D)
PLAN = ["kanit-topla", "agdan-ayir:pc-ayse", "agdan-ayir:srv-dosya",
        "hesabi-kilitle:ayse", "hesabi-kilitle:yedek_svc",
        "kaliciligi-kaldir:GuncellemeKontrol", "kaliciligi-kaldir:guncelle.lnk",
        "zararliyi-kaldir:fatura.exe", "temizligi-dogrula", "geri-ac"]
Y = mudahale(D, PLAN)
eq(D, O, "başarılı çağrı bile girdiyi değiştirmez")
eq(Y["kanit_toplandi"], True, "kanıt adımı uygulandı")
eq((Y["kalicilik"], Y["zararlilar"], Y["temizlik_dogrulandi"]), ([], [], True), "temizlik tamam ve doğrulu")
eq({c: v["izole"] for c, v in Y["cihazlar"].items()}, {"pc-ayse": False, "srv-dosya": False}, "geri açma izolasyonu kaldırır")
eq({h: v["kilitli"] for h, v in Y["hesaplar"].items()}, {"ayse": True, "yedek_svc": True}, "hesaplar kilitli kalır")
for bozuk in (["agdan-ayir:pc-ayse"],
              ["kanit-topla", "kaliciligi-kaldir:guncelle.lnk"],
              ["kanit-topla", "agdan-ayir:pc-ayse", "agdan-ayir:srv-dosya", "hesabi-kilitle:ayse", "hesabi-kilitle:yedek_svc", "geri-ac"],
              ["kanit-topla", "agdan-ayir:olmayan"],
              ["kanit-topla", "zararliyi-kaldir:olmayan"],
              ["kanit-topla", "agdan-ayir:pc-ayse", "agdan-ayir:srv-dosya", "kaliciligi-kaldir:guncelle.lnk"],
              ["kanit-topla", "hesabi-kilitle:ayse", "hesabi-kilitle:yedek_svc", "zararliyi-kaldir:fatura.exe"],
              PLAN[:5] + ["kaliciligi-kaldir:GuncellemeKontrol", "kaliciligi-kaldir:guncelle.lnk", "temizligi-dogrula"],
              PLAN[:5] + ["zararliyi-kaldir:fatura.exe", "temizligi-dogrula"]):
    raises(ValueError, mudahale, D, bozuk, msg="geçersiz sıra veya hedef reddedilir: " + repr(bozuk))
    eq(D, O, "başarısız çağrıda da özgün durum korunur")
```

```solution
import copy
import json


def mudahale(durum, adimlar):
    yeni = copy.deepcopy(durum)
    for adim in adimlar:
        ad, _, hedef = adim.partition(":")
        if adim == "kanit-topla":
            yeni["kanit_toplandi"] = True
        elif ad in ("agdan-ayir", "hesabi-kilitle"):
            if not yeni["kanit_toplandi"]:
                raise ValueError("Önce kanıt toplanmalı")
            grup, alan, bayrak = (("cihazlar", "cihaz", "izole") if ad == "agdan-ayir"
                                  else ("hesaplar", "hesap", "kilitli"))
            if hedef not in yeni[grup]:
                raise ValueError("Bilinmeyen " + alan)
            yeni[grup][hedef][bayrak] = True
        elif ad in ("kaliciligi-kaldir", "zararliyi-kaldir"):
            if not all(c["izole"] for c in yeni["cihazlar"].values()) or not all(h["kilitli"] for h in yeni["hesaplar"].values()):
                raise ValueError("Temizlemeden önce bütün kapsam sınırlanmalı")
            liste = "kalicilik" if ad == "kaliciligi-kaldir" else "zararlilar"
            if hedef not in yeni[liste]:
                raise ValueError("Hedef listede yok")
            yeni[liste].remove(hedef)
        elif adim == "temizligi-dogrula":
            if yeni["kalicilik"] or yeni["zararlilar"]:
                raise ValueError("Temizlik tamamlanmadı")
            yeni["temizlik_dogrulandi"] = True
        elif adim == "geri-ac":
            if not yeni["temizlik_dogrulandi"]:
                raise ValueError("Önce temizlik doğrulanmalı")
            for cihaz in yeni["cihazlar"].values():
                cihaz["izole"] = False
        else:
            raise ValueError("Bilinmeyen müdahale adımı")
    return yeni


D = json.load(open("olay.json", encoding="utf-8"))
print(mudahale(D, ["kanit-topla", "agdan-ayir:pc-ayse"]))
```

```hint
`copy.deepcopy(durum)` ile başla. Her `elif` dalında önce önkoşulu ve hedefin varlığını denetle, sonra yalnız kopyayı değiştir. Böylece hata yükseldiğinde çağıranın elindeki özgün durum aynı kalır.
```

```setup
import json
D = {
    "cihazlar": {"pc-ayse": {"izole": False}, "srv-dosya": {"izole": False}},
    "hesaplar": {"ayse": {"kilitli": False}, "yedek_svc": {"kilitli": False}},
    "kalicilik": ["GuncellemeKontrol", "guncelle.lnk"],
    "zararlilar": ["fatura.exe"],
    "kanit_toplandi": False,
    "temizlik_dogrulandi": False
}
json.dump(D, open("olay.json", "w", encoding="utf-8"), ensure_ascii=False)
```
:::

::: gorev 5 · Kanıtı değiştirmeden paketle ve doğrula
İki fonksiyon yaz:

- `kanit_paketle(kaynak, hedef)`: `kaynak` klasörünün altındaki **bütün dosyaları** göreli yollarını koruyarak `hedef` klasörüne kopyalar. Kaynak dosyaları silmez, taşımaz veya değiştirmez. `hedef/manifest.json` içine `{"dosyalar": [{"yol": <POSIX göreli yolu>, "boyut": <bayt>, "sha256": <küçük harf özet>}, ...]}` yazar; kayıtlar yola göre sıralıdır. Manifesto sözlüğünü döndürür. Zamana veya rastgele değere bağlı alan ekleme.
- `kanit_dogrula(hedef)`: manifestodaki her dosyanın varlığını, bayt boyutunu ve SHA-256 özetini denetler. Hepsi doğruysa `True`, eksik ya da değişmiş dosyada `ValueError` yükseltir.

Manifesto güvenilir bir sınır değildir: `yol` yalnız `/` ayraçlı, temiz bir **göreli POSIX yolu** olmalı. Mutlak yolu, `.` / `..` parçalarını, boş parçayı, ters eğik çizgiyi, sürücü veya UNC adını reddet. Sonra symlink'leri çözümle ve hedefin hâlâ paket kökünün altında olduğunu denetle; `hedef / "../disarida.txt"` ya da dışarıyı gösteren bir symlink kanıt doğrulamak için kullanılamaz.

```starter
import os
import shutil


def kanit_paketle(kaynak, hedef):
    shutil.copytree(kaynak, hedef, dirs_exist_ok=True)
    return {"dosyalar": []}


def kanit_dogrula(hedef):
    return os.path.isdir(hedef)
```

```test
import copy
import hashlib
import json
import os
need("kanit_paketle"); need("kanit_dogrula")

def anlik(kok):
    return {os.path.relpath(os.path.join(k, a), kok).replace(os.sep, "/"): open(os.path.join(k, a), "rb").read()
            for k, _, dosyalar in os.walk(kok) for a in dosyalar}

def manifest_yaz(manifest):
    json.dump(manifest, open("kanit_paketi/manifest.json", "w", encoding="utf-8"), ensure_ascii=False)

once = anlik("kanit_kaynagi")
M = kanit_paketle("kanit_kaynagi", "kanit_paketi")
eq(anlik("kanit_kaynagi"), once, "kaynak kanıtların baytları ve dosya listesi değişmedi")
eq([d["yol"] for d in M["dosyalar"]], ["edr.json", "guvenlik.csv", "notlar/olay.txt"], "alt klasör dahil, yola göre sıralı")
eq(M["dosyalar"][1], {"yol": "guvenlik.csv", "boyut": len(once["guvenlik.csv"]),
                      "sha256": "113eca34ead7a2d46209c6139d6e09451cd7cb573f2c6ff1902d9abafa613134"},
   "gerçek boyut ve SHA-256")
eq(json.load(open("kanit_paketi/manifest.json", encoding="utf-8")), M, "manifesto diske yazıldı")
eq(kanit_dogrula("kanit_paketi"), True, "değişmemiş paket doğrulanır")
M2 = kanit_paketle("kanit_kaynagi", "ikinci_paket")
eq(M2, M, "iki çalıştırmada deterministik manifesto")
open("kanit_paketi/edr.json", "ab").write(b" ")
raises(ValueError, kanit_dogrula, "kanit_paketi", msg="değişen kanıt reddedilir")
os.remove("kanit_paketi/guvenlik.csv")
raises(ValueError, kanit_dogrula, "kanit_paketi", msg="silinen kanıt reddedilir")

veri = once["edr.json"]
open("disarida.txt", "wb").write(veri)
B = copy.deepcopy(M)
B["dosyalar"][0] = {"yol": "../disarida.txt", "boyut": len(veri), "sha256": hashlib.sha256(veri).hexdigest()}
B["dosyalar"] = B["dosyalar"][:1]  # başka bir eksik dosya, traversal kontrolünü gizlemesin
manifest_yaz(B)
raises(ValueError, kanit_dogrula, "kanit_paketi", msg="var olan ve özeti doğru paket dışı dosya bile reddedilir")
for kotu in (os.path.abspath("disarida.txt").replace(os.sep, "/"), "C:disarida.txt",
             "\\\\sunucu\\paylasim\\disarida.txt", "notlar/../../disarida.txt", "notlar\\..\\disarida.txt"):
    B["dosyalar"][0]["yol"] = kotu
    manifest_yaz(B)
    raises(ValueError, kanit_dogrula, "kanit_paketi", msg="mutlak, sürücü/UNC veya .. yolu reddedilir: " + repr(kotu))
try:
    os.symlink(os.path.abspath("disarida.txt"), "kanit_paketi/bagli.txt")
except (OSError, NotImplementedError):
    ok(True, "bu ortam symlink kurmaya izin vermiyor; yol ve traversal kontrolleri yine çalıştı")
else:
    B["dosyalar"][0]["yol"] = "bagli.txt"
    manifest_yaz(B)
    raises(ValueError, kanit_dogrula, "kanit_paketi", msg="paket dışını gösteren symlink reddedilir")

P = "ucuncu_paket"
M3 = kanit_paketle("kanit_kaynagi", P)
def yaz3(m):
    json.dump(m, open(P + "/manifest.json", "w", encoding="utf-8"), ensure_ascii=False)
icerik = open(P + "/edr.json", "rb").read()
open(P + "/edr.json", "wb").write(bytes([icerik[0] ^ 1]) + icerik[1:])
raises(ValueError, kanit_dogrula, P, msg="aynı boyutta değişen bayt özetten yakalanır")
open(P + "/edr.json", "wb").write(icerik)
eq(kanit_dogrula(P), True, "geri yüklenen dosya yine doğrulanır")
yanlis = copy.deepcopy(M3); yanlis["dosyalar"][0]["boyut"] += 1; yaz3(yanlis)
raises(ValueError, kanit_dogrula, P, msg="özet doğru ama boyut yanlış: reddedilir")
for yol in ("notlar\\olay.txt", "notlar/./olay.txt", "notlar//olay.txt", None, 5,
            os.path.abspath(P + "/notlar/olay.txt").replace(os.sep, "/"),
            (os.path.splitdrive(os.path.abspath(P))[0] or "C:") + "notlar/olay.txt"):
    m = copy.deepcopy(M3); m["dosyalar"] = [dict(M3["dosyalar"][2], yol=yol)]; yaz3(m)
    raises(ValueError, kanit_dogrula, P, msg="paket içini gösterse de biçimi bozuk yol reddedilir: " + repr(yol))
```

```solution
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil


def ozet(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(65536), b""):
            h.update(parca)
    return h.hexdigest()


def kanit_paketle(kaynak, hedef):
    os.makedirs(hedef, exist_ok=True)
    kayitlar = []
    for kok, _, dosyalar in os.walk(kaynak):
        for ad in dosyalar:
            tam = os.path.join(kok, ad)
            goreli = os.path.relpath(tam, kaynak).replace(os.sep, "/")
            kayitlar.append((goreli, tam))
    manifest = {"dosyalar": []}
    for goreli, tam in sorted(kayitlar):
        kopya = os.path.join(hedef, *goreli.split("/"))
        os.makedirs(os.path.dirname(kopya), exist_ok=True)
        shutil.copyfile(tam, kopya)
        manifest["dosyalar"].append({"yol": goreli, "boyut": os.path.getsize(kopya), "sha256": ozet(kopya)})
    with open(os.path.join(hedef, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return manifest


def kanit_yolu(hedef, goreli):
    if not isinstance(goreli, str) or not goreli or "\\" in goreli or "\0" in goreli:
        raise ValueError("Geçersiz kanıt yolu")
    parcalar = goreli.split("/")
    if (PurePosixPath(goreli).is_absolute() or PureWindowsPath(goreli).drive
            or any(p in ("", ".", "..") for p in parcalar)):
        raise ValueError("Kanıt yolu temiz bir göreli POSIX yolu olmalı")
    try:
        kok = Path(hedef).resolve(strict=True)
        yol = kok.joinpath(*parcalar).resolve(strict=True)
        yol.relative_to(kok)
    except (OSError, RuntimeError, ValueError) as e:
        raise ValueError("Kanıt eksik veya yolu paket dışına çıkıyor") from e
    if not yol.is_file():
        raise ValueError("Kanıt normal bir dosya olmalı")
    return yol


def kanit_dogrula(hedef):
    with open(os.path.join(hedef, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    for kayit in manifest["dosyalar"]:
        yol = kanit_yolu(hedef, kayit["yol"])
        if yol.stat().st_size != kayit["boyut"] or ozet(yol) != kayit["sha256"]:
            raise ValueError("Kanıt bütünlüğü bozuk: " + kayit["yol"])
    return True


M = kanit_paketle("kanit_kaynagi", "kanit_paketi")
print(kanit_dogrula("kanit_paketi"), len(M["dosyalar"]))
```

```hint
Önce `os.walk` ile `(göreli_yol, tam_yol)` çiftlerini toplayıp sırala. `shutil.copyfile` içeriği kopyalar; `shutil.move` veya `os.remove` kullanma. Doğrulamada `PurePosixPath` / `PureWindowsPath` ile yol biçimini reddet; ardından `Path.resolve(strict=True)` ve `relative_to(paket_koku)` ile symlink dahil kök sınırını denetle.
```

```setup
import os
os.makedirs("kanit_kaynagi/notlar", exist_ok=True)
open("kanit_kaynagi/guvenlik.csv", "wb").write(
    b"zaman;olay;bilgisayar\r\n19.10.2026 12:03:40;4688;PC-AYSE\r\n")
open("kanit_kaynagi/edr.json", "wb").write(
    b'[{"zaman":1792400550,"olay":"dosya olusturuldu"}]\n')
open("kanit_kaynagi/notlar/olay.txt", "wb").write(
    "İlk gözlem: fatura.exe; kanıt saatleri UTC'ye çevrildi.\n".encode("utf-8"))
```
:::
