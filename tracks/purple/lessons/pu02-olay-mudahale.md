---
id: pu02
title: Olay Müdahalesi · Zaman Çizelgesi ve Kapsam
summary: Olay müdahalesinin adımları (doğrula, kapsamla, sınırla, temizle, ders çıkar); farklı saat dilimi ve biçimlerdeki kaynakları (yerel saatli CSV, UTC ISO, epoch) tek UTC zaman çizelgesinde birleştirmek; cihaz ve hesap adlarını tek biçime getirmek; bir başlangıç noktasından cihaz ve hesap üzerinden ilişkili varlıkları bulmak (kapsamlama) ve olaydan önceki kayıtların kapsamı şişirmesi. Python, sentetik kayıtlar.
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

Bu paftanın konusu ilk iki adımın mutfağıdır: **zaman çizelgesi** ve **kapsam**. Kayıtlar farklı ekiplerden, farklı biçimlerde gelir:

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
