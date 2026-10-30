---
id: ai-savunma-09
title: PII Tespiti ve Çıktı DLP Kontrolleri
summary: Sentetik fixture üzerinde PII konumlarını bul, maskeleme ve redaksiyon uygula, kanal bazlı DLP kararları üret.
timeout: 45
---

::: anlat PII tespiti, redaksiyon ve DLP kararı farklı adımlardır
Kişisel veri tespiti metindeki varlığın türünü ve konumunu bulur. Maskeleme veya redaksiyon bu konumlara uygulanan dönüşümdür. DLP kararı ise verinin yanıt, log veya dış API kanalına hangi koşulda çıkabileceğini belirler. Bir varlığın bulunması bütün kanallarda aynı kararı gerektirmez.

Presidio ve LLM Guard gerçek sistemlerde tanıyıcı ve politika adımlarına bağlanabilir. Bu derste yalnız sentetik e-posta, dokümantasyon IP'si, geçerli Luhn örneği olan bilinen test kartı ve yapay telefon fixture'ı kullanılır. Dış servis veya gerçek kişi verisi yoktur; tespit raporu eşleşen değerin kendisini döndürmez.
:::

::: tahmin Maske son dört haneyi korur, redaksiyon türü gösterir
İki çıktı satırını yaz:

```python
deger = "4111111111111111"
print("*" * (len(deger) - 4) + deger[-4:])
print("[PII:kart]")
```

???

```cikti
************1111
[PII:kart]
```

Maskeleme dar bir görünürlük sağlar; redaksiyon ise değeri bütünüyle kaldırıp yalnız varlık türünü bırakır.
:::

::: gorev 1 · Sentetik PII varlıklarını değerlerini açığa çıkarmadan bul
`pii_varliklarini_bul(metin)` işlevini yaz. Metin NUL içermeyen string olmalı; boş string kabul edilir. Diğer durumlarda `ValueError` yükselt. Dört tanıyıcıyı uygula:

- `eposta`: ASCII harf, rakam ve `._%+-` içeren yerel kısım; `@`; nokta ile ayrılmış alan adı ve en az iki ASCII harfli son uzantı.
- `ipv4`: noktayla ayrılmış dört adet 1–3 haneli parça; her parçanın sayısal değeri 0–255 olmalı. Komşu rakam veya nokta içeren daha uzun sayıyı parçalama.
- `kart`: 13–19 rakamdan oluşan, rakamlar arasında en fazla bir boşluk veya tire bulunabilen ve Luhn toplamı geçerli dizi.
- `telefon`: tam `+90 555 123 45 67` biçimine uyan, `+90` sonrasında üç grup boşluklu yapay numara kalıbı; grup uzunlukları sırasıyla 3, 3, 2, 2 rakam.

Her eşleşme için `{"tur":TUR,"baslangic":B,"bitis":E}` döndür. `metin[B:E]` eşleşmenin tamamını vermelidir. Sonucu başlangıç, ardından `eposta`, `ipv4`, `kart`, `telefon` tür önceliğine göre sırala. Aynı türdeki eşleşmeleri yineleme; eşleşen metnin kendisini sonuca ekleme.

```starter
def pii_varliklarini_bul(metin):
    return []
```

```test
METIN = "E-posta ornek@example.test, IP 192.0.2.10, kart 4111 1111 1111 1111, tel +90 555 123 45 67"
PARCALAR = [("eposta", "ornek@example.test"), ("ipv4", "192.0.2.10"), ("kart", "4111 1111 1111 1111"), ("telefon", "+90 555 123 45 67")]
BEKLENEN = [{"tur": tur, "baslangic": METIN.index(deger), "bitis": METIN.index(deger) + len(deger)} for tur, deger in PARCALAR]
def sozlesme(fn):
    try:
        sonuc = fn(METIN)
        if sonuc != BEKLENEN or fn("") != [] or fn("Metin yok") != []:
            return False
        if any(set(x) != {"tur", "baslangic", "bitis"} for x in sonuc):
            return False
        if fn("a@b.co a@b.co") != [
            {"tur": "eposta", "baslangic": 0, "bitis": 6},
            {"tur": "eposta", "baslangic": 7, "bitis": 13},
        ]:
            return False
        if fn("255.255.255.255") != [{"tur": "ipv4", "baslangic": 0, "bitis": 15}]:
            return False
        if fn("1.2.3.4") != [{"tur": "ipv4", "baslangic": 0, "bitis": 7}]:
            return False
        for metin in ("256.0.0.1", "999.1.1.1", "0255.1.1.1", "1.1.1.0255", "1.2.3.4.5", "4111 1111 1111 1112", "1234", "a@b", "+90 555 123 4567"):
            if fn(metin) != []:
                return False
        if fn("4222222222222") != [{"tur": "kart", "baslangic": 0, "bitis": 13}]:
            return False
        if fn("4000000000000000006") != [{"tur": "kart", "baslangic": 0, "bitis": 19}]:
            return False
        if fn("40000000000000000002") != []:
            return False
        if fn("5555555555554444") != [{"tur": "kart", "baslangic": 0, "bitis": 16}]:
            return False
        if fn("4111-1111-1111-1111") != [{"tur": "kart", "baslangic": 0, "bitis": 19}]:
            return False
        for metin in (None, 1, [], "a\x00b"):
            try:
                fn(metin)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(pii_varliklarini_bul), "türler, ofsetler, IPv4 ve Luhn doğrulaması korunmalı")
def m_eposta(metin):
    return [x for x in pii_varliklarini_bul(metin) if x["tur"] != "eposta"]
def m_ip(metin):
    return [x for x in pii_varliklarini_bul(metin) if x["tur"] != "ipv4"]
def m_kart(metin):
    return [x for x in pii_varliklarini_bul(metin) if x["tur"] != "kart"]
for ad, mutant in [("e-postayı silen", m_eposta), ("IP kontrolünü silen", m_ip), ("kartı silen", m_kart)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def pii_varliklarini_bul(metin):
    import re
    if not isinstance(metin, str):
        raise ValueError("metin string olmalı")
    if "\x00" in metin:
        raise ValueError("metin NUL içeremez")
    bulunan = []
    for es in re.finditer(r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])", metin):
        bulunan.append((es.start(), es.end(), "eposta"))
    for es in re.finditer(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])", metin):
        if all(0 <= int(parca) <= 255 for parca in es.group().split(".")):
            bulunan.append((es.start(), es.end(), "ipv4"))
    for es in re.finditer(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)", metin):
        rakamlar = [int(c) for c in es.group() if c.isdigit()]
        toplam = 0
        for konum, rakam in enumerate(reversed(rakamlar)):
            if konum % 2 == 1:
                rakam *= 2
                if rakam >= 10:
                    rakam -= 9
            toplam += rakam
        if toplam % 10 == 0:
            bulunan.append((es.start(), es.end(), "kart"))
    for es in re.finditer(r"(?<!\d)\+90 \d{3} \d{3} \d{2} \d{2}(?!\d)", metin):
        bulunan.append((es.start(), es.end(), "telefon"))
    oncelik = {"eposta": "a", "ipv4": "b", "kart": "c", "telefon": "d"}
    sirali = sorted(bulunan, key=lambda x: (x[0], oncelik[x[2]]))
    return [{"tur": tur, "baslangic": baslangic, "bitis": bitis} for baslangic, bitis, tur in sirali]
```

```hint
Regex eşleşmelerinin `start()` ve `end()` değerlerini kullan. IPv4 parçalarını sayıya çevirip denetle; kartta yalnız rakamları alarak sağdan çift konumları ikiyle çarp.
```
:::

::: anlat Dönüşüm sondan uygulanırsa ofsetler korunur
Varlık konumları özgün metne aittir. Baştan başlayarak farklı uzunlukta redaksiyon metinleri eklemek sonraki ofsetleri kaydırır. Bu nedenle geçerli ve çakışmayan aralıklar başlangıca göre azalan sırayla işlenir.

Bu derste `maskele` yalnız son dört karakteri bırakır; dört veya daha kısa değerin tamamını yıldızlar. `redakte` değeri `[PII:tur]` ile değiştirir. `koru` metni aynen bırakır ve işlem sayısına eklenmez. Politika bütün varlık türlerini açıkça belirtmelidir.
:::

::: gorev 2 · Konumları doğrulanmış maskeleme ve redaksiyon uygula
`pii_donustur(metin, varliklar, politika)` işlevini yaz. Metin NUL içermeyen stringdir. Politika tam olarak `eposta`, `ipv4`, `kart`, `telefon` anahtarlarını taşısın; her değer `maskele`, `redakte` veya `koru` olmalıdır.

Varlıklar liste; her kayıt tam olarak `tur`, `baslangic`, `bitis` alanlarını taşısın. Tür politikada bulunmalı; ofsetler bool olmayan int olmalı ve `0 <= baslangic < bitis <= len(metin)` sağlanmalıdır. Aralıklar çakışamaz. Geçersiz veride `ValueError` yükselt.

Her aralığı türünün politika eylemine göre dönüştür. Maskelemede son dört karakter dışındaki her karakter `*` olur; değer en fazla dört karakterse tamamı maskelenir. Redaksiyon `[PII:TUR]`, koruma özgün değerdir. Dönüşümleri sondan başa uygula. `{"metin":YENI,"islem_sayisi":N}` döndür; `N` korunmayan varlık sayısıdır. Girdi listesini ve politika sözlüğünü değiştirme.

```starter
def pii_donustur(metin, varliklar, politika):
    return {"metin": "", "islem_sayisi": 0}
```

```test
import copy
METIN = "ornek@example.test 192.0.2.10 4111111111111111 +90 555 123 45 67"
PARCALAR = [("eposta", "ornek@example.test"), ("ipv4", "192.0.2.10"), ("kart", "4111111111111111"), ("telefon", "+90 555 123 45 67")]
V = [{"tur": tur, "baslangic": METIN.index(deger), "bitis": METIN.index(deger) + len(deger)} for tur, deger in PARCALAR]
P = {"eposta": "redakte", "ipv4": "koru", "kart": "maskele", "telefon": "redakte"}
BEKLENEN = "[PII:eposta] 192.0.2.10 ************1111 [PII:telefon]"
def sozlesme(fn):
    try:
        once = copy.deepcopy(V)
        ponce = dict(P)
        if fn(METIN, V, P) != {"metin": BEKLENEN, "islem_sayisi": 3} or V != once or P != ponce:
            return False
        if fn(METIN, list(reversed(V)), P) != {"metin": BEKLENEN, "islem_sayisi": 3}:
            return False
        if fn("abc", [{"tur": "eposta", "baslangic": 0, "bitis": 3}], dict(P, eposta="maskele")) != {"metin": "***", "islem_sayisi": 1}:
            return False
        for deger, beklenen in (("abcd", "****"), ("abcde", "*bcde"), ("abcdef", "**cdef")):
            if fn(deger, [{"tur": "eposta", "baslangic": 0, "bitis": len(deger)}], dict(P, eposta="maskele")) != {"metin": beklenen, "islem_sayisi": 1}:
                return False
        bitisik = [{"tur": "eposta", "baslangic": 0, "bitis": 3}, {"tur": "ipv4", "baslangic": 3, "bitis": 6}]
        if fn("abcdef", bitisik, dict(P, eposta="redakte", ipv4="redakte")) != {"metin": "[PII:eposta][PII:ipv4]", "islem_sayisi": 2}:
            return False
        if fn(METIN, [], P) != {"metin": METIN, "islem_sayisi": 0}:
            return False
        for args in [
            (None, V, P), ("a\x00b", [], P), (METIN, None, P), (METIN, {}, P),
            (METIN, V, None), (METIN, V, dict(P, ek="koru")),
            (METIN, V, {k: v for k, v in P.items() if k != "kart"}),
            (METIN, V, dict(P, kart="sil")), (METIN, [None], P),
            (METIN, [dict(V[0], ek=1)], P), (METIN, [dict(V[0], tur="diger")], P),
            (METIN, [dict(V[0], baslangic=True)], P), (METIN, [dict(V[0], baslangic=-1)], P),
            (METIN, [dict(V[0], baslangic=18)], P), (METIN, [dict(V[0], bitis=1000)], P),
            (METIN, [V[0], dict(V[1], baslangic=1)], P),
        ]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(pii_donustur), "aralık doğrulama, sondan dönüşüm, maske ve işlem sayısı korunmalı")
def m_maske(metin, varliklar, politika):
    sonuc = pii_donustur(metin, varliklar, politika)
    sonuc["metin"] = sonuc["metin"].replace("************1111", "4111111111111111")
    return sonuc
def m_redakte(metin, varliklar, politika):
    sonuc = pii_donustur(metin, varliklar, politika)
    sonuc["metin"] = sonuc["metin"].replace("[PII:eposta]", "ornek@example.test")
    return sonuc
def m_sayi(metin, varliklar, politika):
    sonuc = pii_donustur(metin, varliklar, politika)
    sonuc["islem_sayisi"] = 0
    return sonuc
for ad, mutant in [("maskeyi kaldıran", m_maske), ("redaksiyonu kaldıran", m_redakte), ("işlem sayısını silen", m_sayi)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def pii_donustur(metin, varliklar, politika):
    if not isinstance(metin, str) or "\x00" in metin:
        raise ValueError("metin geçersiz")
    turler = {"eposta", "ipv4", "kart", "telefon"}
    if not isinstance(politika, dict) or set(politika) != turler:
        raise ValueError("politika şeması geçersiz")
    if any(politika[t] not in ("maskele", "redakte", "koru") for t in turler):
        raise ValueError("politika eylemi geçersiz")
    if not isinstance(varliklar, list):
        raise ValueError("varlık listesi geçersiz")
    sirali = []
    for varlik in varliklar:
        if not isinstance(varlik, dict) or set(varlik) != {"tur", "baslangic", "bitis"}:
            raise ValueError("varlık şeması geçersiz")
        if varlik["tur"] not in turler:
            raise ValueError("varlık türü geçersiz")
        baslangic = varlik["baslangic"]
        bitis = varlik["bitis"]
        if type(baslangic) is not int or type(bitis) is not int:
            raise ValueError("ofsetler int olmalı")
        if baslangic < 0 or baslangic >= bitis or bitis > len(metin):
            raise ValueError("ofset aralığı geçersiz")
        sirali.append(varlik)
    sirali.sort(key=lambda x: (x["baslangic"], x["bitis"]))
    for onceki, sonraki in zip(sirali, sirali[1:]):
        if onceki["bitis"] > sonraki["baslangic"]:
            raise ValueError("varlık aralıkları çakışamaz")
    sonuc = metin
    islem = 0
    for varlik in reversed(sirali):
        eylem = politika[varlik["tur"]]
        if eylem == "koru":
            continue
        baslangic = varlik["baslangic"]
        bitis = varlik["bitis"]
        deger = metin[baslangic:bitis]
        if eylem == "maskele":
            yeni = "*" * max(0, len(deger) - 4) + deger[-4:]
            if len(deger) <= 4:
                yeni = "*" * len(deger)
        else:
            yeni = "[PII:" + varlik["tur"] + "]"
        sonuc = sonuc[:baslangic] + yeni + sonuc[bitis:]
        islem += 1
    return {"metin": sonuc, "islem_sayisi": islem}
```

```hint
Aralıkları önce artan sıraya getirip çakışmayı denetle, dönüşümde ters sırayla ilerle. Maske için kısa değer durumunu ayrı ele al; `koru` sayacı artırmasın.
```
:::

::: anlat DLP politikası kanala göre değişir
Bu dersin sabit politikasında log kanalına hiçbir PII çıkmaz. Dış API'ye kart göndermek durdurulur; e-posta veya telefon redakte edilir; yalnız IP varsa insan incelemesi gerekir. Yanıt kanalında kart redakte, e-posta ve telefon redakte, IP ise serbesttir.

Aynı toplam varlık sayısına sahip iki olay farklı türler taşıyorsa kararları da farklı olabilir. Rapor varlık türlerini `eposta`, `ipv4`, `kart`, `telefon` sırasıyla ve tekilleştirilmiş olarak gösterir; kişisel değerleri göstermez.
:::

::: gorev 3 · Kanal ve varlık türüne göre DLP karar raporu üret
`dlp_karar_raporu(olaylar)` işlevini yaz. Her olay tam olarak `id`, `kanal`, `varlik_turleri` alanlarını taşısın. Kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren benzersiz stringdir. Kanal `yanit`, `log` veya `dis_api`; varlık türleri dört bilinen türden oluşan yinelenmeyen bir liste olmalıdır. Geçersiz veride `ValueError` yükselt.

Türleri sabit sıraya göre sıralayıp şu politikayı uygula:

```text
log      + herhangi bir PII       -> durdur
dis_api  + kart                   -> durdur
dis_api  + eposta/telefon         -> redakte
dis_api  + yalnız ipv4            -> incele
yanit    + kart/eposta/telefon    -> redakte
yanit    + yalnız ipv4 veya boş   -> gecir
boş varlık (her kanal)            -> gecir
```

Her olay için `{"id":ID,"karar":KARAR,"varliklar":[TUR,...]}` döndür. Kimliğe göre sırala, boş girdide boş liste döndür ve girdiyi değiştirme.

```starter
def dlp_karar_raporu(olaylar):
    return []
```

```test
import copy
O = [
    {"id": "bos-1", "kanal": "log", "varlik_turleri": []},
    {"id": "log-1", "kanal": "log", "varlik_turleri": ["ipv4"]},
    {"id": "api-kart", "kanal": "dis_api", "varlik_turleri": ["kart", "eposta"]},
    {"id": "api-eposta", "kanal": "dis_api", "varlik_turleri": ["eposta"]},
    {"id": "api-ip", "kanal": "dis_api", "varlik_turleri": ["ipv4"]},
    {"id": "yanit-kart", "kanal": "yanit", "varlik_turleri": ["telefon", "kart"]},
    {"id": "yanit-ip", "kanal": "yanit", "varlik_turleri": ["ipv4"]},
]
BEKLENEN = [
    {"id": "api-eposta", "karar": "redakte", "varliklar": ["eposta"]},
    {"id": "api-ip", "karar": "incele", "varliklar": ["ipv4"]},
    {"id": "api-kart", "karar": "durdur", "varliklar": ["eposta", "kart"]},
    {"id": "bos-1", "karar": "gecir", "varliklar": []},
    {"id": "log-1", "karar": "durdur", "varliklar": ["ipv4"]},
    {"id": "yanit-ip", "karar": "gecir", "varliklar": ["ipv4"]},
    {"id": "yanit-kart", "karar": "redakte", "varliklar": ["kart", "telefon"]},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(O)
        if fn(O) != BEKLENEN or O != once or fn(list(reversed(O))) != BEKLENEN or fn([]) != []:
            return False
        if fn([dict(O[0], id="a" * 64)])[0]["id"] != "a" * 64:
            return False
        if fn([{"id": "tel", "kanal": "dis_api", "varlik_turleri": ["telefon"]}])[0]["karar"] != "redakte":
            return False
        for olaylar in [
            None, {}, [None], [dict(O[0], ek=1)], [dict(O[0], id="")],
            [dict(O[0], id="a" * 65)], [dict(O[0], id="a b")], [dict(O[0], kanal="diger")],
            [dict(O[0], varlik_turleri=None)], [dict(O[0], varlik_turleri="eposta")],
            [dict(O[0], varlik_turleri=["diger"])], [dict(O[0], varlik_turleri=["eposta", "eposta"])],
            [O[0], O[0]],
        ]:
            try:
                fn(olaylar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(dlp_karar_raporu), "kanal politikası, tür bazlı karar, sıralama ve şema korunmalı")
def m_kanal(olaylar):
    degisen = [dict(x, kanal="yanit") for x in olaylar]
    return dlp_karar_raporu(degisen)
def m_kart(olaylar):
    degisen = [dict(x, varlik_turleri=[t for t in x["varlik_turleri"] if t != "kart"]) for x in olaylar]
    return dlp_karar_raporu(degisen)
def m_log(olaylar):
    degisen = [dict(x, varlik_turleri=[]) for x in olaylar]
    return dlp_karar_raporu(degisen)
for ad, mutant in [("kanalı değiştiren", m_kanal), ("kart türünü silen", m_kart), ("bütün varlıkları silen", m_log)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def dlp_karar_raporu(olaylar):
    import re
    if not isinstance(olaylar, list):
        raise ValueError("olay listesi geçersiz")
    tur_sirasi = ["eposta", "ipv4", "kart", "telefon"]
    kimlikler = set()
    rapor = []
    for olay in olaylar:
        if not isinstance(olay, dict) or set(olay) != {"id", "kanal", "varlik_turleri"}:
            raise ValueError("olay şeması geçersiz")
        kimlik = olay["id"]
        if not isinstance(kimlik, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kimlik geçersiz")
        if kimlik in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kimlik)
        if olay["kanal"] not in ("yanit", "log", "dis_api"):
            raise ValueError("kanal geçersiz")
        turler = olay["varlik_turleri"]
        if not isinstance(turler, list):
            raise ValueError("varlık türleri liste olmalı")
        if len(set(turler)) != len(turler):
            raise ValueError("varlık türü yinelenemez")
        if any(t not in tur_sirasi for t in turler):
            raise ValueError("varlık türü geçersiz")
        sirali = [t for t in tur_sirasi if t in turler]
        kanal = olay["kanal"]
        if not sirali:
            karar = "gecir"
        elif kanal == "log":
            karar = "durdur"
        elif kanal == "dis_api" and "kart" in sirali:
            karar = "durdur"
        elif kanal == "dis_api" and any(t in ("eposta", "telefon") for t in sirali):
            karar = "redakte"
        elif kanal == "dis_api":
            karar = "incele"
        elif any(t in ("kart", "eposta", "telefon") for t in sirali):
            karar = "redakte"
        else:
            karar = "gecir"
        rapor.append({"id": kimlik, "karar": karar, "varliklar": sirali})
    return sorted(rapor, key=lambda x: x["id"])
```

```hint
Boş varlık durumunu önce ele al. Sonra log ve dış API kart yasağını uygula; yalnız IP ile diğer türlerin kararlarını ayır ve raporu sabit tür sırasıyla kur.
```
:::

::: anlat DLP gerçek çıktı üzerinde sınanır; desen temizliği değerle sınırlıdır
Çıktı DLP'si ancak bir modelin **gerçekten ürettiği** metin üzerinde çalıştığında anlam kazanır. Son görevde senin `pii_donustur` işlevin, gerçek yerel modelin sentetik bir kayıttan yankıladığı PII'yi kanal politikasına göre maskeler ve redakte eder. Sandbox önce çıktıdaki PII'yi bağımsız bulur (1. görev kuralları), dönüşümden sonra aynı tarayıcıyı yeniden koşar: kalan PII sayısı DLP'nin gerçekten işe yarayıp yaramadığını ölçer.

Gerçek bir ders daha vardır: desen temelli tespit, değerin biçimine bağlıdır. Model bir numarayı yeniden biçimlendirirse (örneğin telefon gruplarını değiştirirse) dar tanıyıcı onu kaçırabilir. Bu, PII tespitinin neden tek katman olmaması gerektiğini gösterir; kanal kararı (örneğin dış API'ye kart → durdur) ayrı bir güvenlik ağı olarak kalır.
:::

::: gorev Gerçek deney · Gerçek çıktıdaki PII'yi DLP ile temizle
`pii_donustur(metin, varliklar, politika)` işlevini yaz — kuralları ve çıktısı 2. görevdekiyle **aynıdır**. Deney gerçek modelin sentetik PII içeren çıktısını üretir, varlıkları gerçek metinden bulur ve senin dönüşümün bu gerçek PII'yi kanal politikasına göre maskeler/redakte eder; dönüşüm sonrası kalan PII ölçülür.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def pii_donustur(metin, varliklar, politika):
    return {"metin": "", "islem_sayisi": 0}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_09 as deney
    deney.goster(pii_donustur)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "referans_bul", "referans_dlp", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("pii_donustur")
from sandbox import ai_gercek_ai_savunma_09 as D
METIN = "ornek@example.test 192.0.2.10 4111111111111111 +90 555 123 45 67"
PARCALAR = [("eposta", "ornek@example.test"), ("ipv4", "192.0.2.10"), ("kart", "4111111111111111"), ("telefon", "+90 555 123 45 67")]
V = [{"tur": t, "baslangic": METIN.index(d), "bitis": METIN.index(d) + len(d)} for t, d in PARCALAR]
P = {"eposta": "redakte", "ipv4": "koru", "kart": "maskele", "telefon": "redakte"}
def sozlesme(f):
    try:
        if f(METIN, V, P) != {"metin": "[PII:eposta] 192.0.2.10 ************1111 [PII:telefon]", "islem_sayisi": 3}:
            return False
        if f(METIN, [], P) != {"metin": METIN, "islem_sayisi": 0}:
            return False
        for args in ((None, V, P), (METIN, None, P), (METIN, V, None), (METIN, V, dict(P, ek="koru")), (METIN, [dict(V[0], bitis=1000)], P)):
            try:
                f(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "aralık doğrulama, sondan dönüşüm, maske ve işlem sayısı korunmalı")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    kontrol(len(r["varliklar"]) >= 1, "gerçek model çıktısında en az bir PII bulundu")
    kontrol(r["donusum"]["islem_sayisi"] == sum(1 for v in r["varliklar"] if D.POLITIKA[v["tur"]] != "koru"),
            "korunmayan her gerçek PII dönüştürüldü")
    kontrol(len(r["kalan"]) == 0, f"DLP sonrası gerçek çıktıda kalan PII yok ({len(r['kalan'])})")
    oz = D.ozet(r)
yol = ai_lab.kanit_yaz("savunma-dlp", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-09",
                                       "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({r['ortam']['model']['ad']}): gerçek çıktıda {oz['ham_pii']} PII {oz['turler']} bulundu; "
             f"DLP {oz['islem_sayisi']} dönüşüm uyguladı, kalan PII {oz['kalan_pii']}; kanal '{oz['kanal']}' kararı {oz['dlp_karari']}. "
             f"PII gerçek model çıktısından geldi; desen temelli tespit değerin biçimine bağlıdır, kanal kararı ayrı güvenlik ağıdır.")
```

```solution
import ai_lab

def pii_donustur(metin, varliklar, politika):
    if not isinstance(metin, str) or "\x00" in metin:
        raise ValueError("metin geçersiz")
    turler = {"eposta", "ipv4", "kart", "telefon"}
    if not isinstance(politika, dict) or set(politika) != turler:
        raise ValueError("politika şeması geçersiz")
    if any(politika[t] not in ("maskele", "redakte", "koru") for t in turler):
        raise ValueError("politika eylemi geçersiz")
    if not isinstance(varliklar, list):
        raise ValueError("varlık listesi geçersiz")
    sirali = []
    for varlik in varliklar:
        if not isinstance(varlik, dict) or set(varlik) != {"tur", "baslangic", "bitis"}:
            raise ValueError("varlık şeması geçersiz")
        if varlik["tur"] not in turler:
            raise ValueError("varlık türü geçersiz")
        baslangic = varlik["baslangic"]
        bitis = varlik["bitis"]
        if type(baslangic) is not int or type(bitis) is not int:
            raise ValueError("ofsetler int olmalı")
        if baslangic < 0 or baslangic >= bitis or bitis > len(metin):
            raise ValueError("ofset aralığı geçersiz")
        sirali.append(varlik)
    sirali.sort(key=lambda x: (x["baslangic"], x["bitis"]))
    for onceki, sonraki in zip(sirali, sirali[1:]):
        if onceki["bitis"] > sonraki["baslangic"]:
            raise ValueError("varlık aralıkları çakışamaz")
    sonuc = metin
    islem = 0
    for varlik in reversed(sirali):
        eylem = politika[varlik["tur"]]
        if eylem == "koru":
            continue
        baslangic = varlik["baslangic"]
        bitis = varlik["bitis"]
        deger = metin[baslangic:bitis]
        if eylem == "maskele":
            yeni = "*" * max(0, len(deger) - 4) + deger[-4:]
            if len(deger) <= 4:
                yeni = "*" * len(deger)
        else:
            yeni = "[PII:" + varlik["tur"] + "]"
        sonuc = sonuc[:baslangic] + yeni + sonuc[bitis:]
        islem += 1
    return {"metin": sonuc, "islem_sayisi": islem}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_09 as deney
    deney.goster(pii_donustur)
```

```hint
Bu işlev 2. görevdeki `pii_donustur` ile birebir aynıdır; tek fark, metin ve varlıkların gerçek model çıktısından gelmesidir. Aralıkları sondan başa dönüştür, maske için kısa değeri ayrı ele al, `koru` sayacı artırmasın.
```
:::
