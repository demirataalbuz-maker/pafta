---
id: ai-temel-16
title: "Bağlamda Sır ve Ayrıcalık Minimizasyonu"
summary: Bağlam alanlarını ihtiyaca göre seç, sentetik tokenları maskele ve en az ayrıcalıklı kapsam üret.
timeout: 45
---

::: anlat Modele verilen her alan potansiyel maruziyettir
Bir API anahtarı veya gereksiz kişisel not bağlama girerse modelin yararlı yanıt üretmesi için gerekmese bile sızıntı yüzeyi büyür. Veri minimizasyonu önce gerekli alanları seçer; maskeleme ise metnin kaçınılmaz kısmındaki sır örüntülerini azaltır.

Bu derste Docker veya gerçek sır deposu kullanılmaz. Bütün tokenlar açıkça sentetiktir. Amaç izinli alan listesinin dışındaki veriyi bağlama hiç eklememek ve kayıtlarda sır yerine sabit maske görmektir.
:::

::: anlat Veri minimizasyonu ile yetki minimizasyonu birlikte uygulanır
Modelin daha az veri görmesi, bağlı aracın fazla yetkisini telafi etmez. İstenen kapsamlar görev için gerekli kapsamlarla kesiştirilir; gereksiz veya tanınmayan istekler verilmez. Reddedilenler denetim için raporlanır.

En az ayrıcalık tek seferlik liste değildir. Görev değiştiğinde gerekli kapsam yeniden hesaplanır, dışa aktarma ve yönetim gibi riskli yetkiler ayrı onay gerektirir. Buradaki fonksiyon yalnız politika kararı üretir, yetki vermez.
:::

::: tahmin Minimizasyon çıktısını tahmin et
Üç çıktı satırını yaz:

```python
k = {"id": "a", "soru": "s", "token": "TOKEN-AB12"}
print({a: k[a] for a in ["id", "soru"]})
import re
print(re.sub(r"TOKEN-[A-Z0-9]{4}", "[GIZLI]", k["token"]))
print(sorted(set(["oku", "yaz"]) & set(["oku"])))
```

???

```cikti
{'id': 'a', 'soru': 's'}
[GIZLI]
['oku']
```

İlk satır alan projeksiyonunu, ikinci satır sır maskesini, üçüncü satır gerekli kapsam kesişimini gösterir.
:::

::: gorev 1 · Bağlam için yalnız gerekli alanları seç
`alan_minimize(kayit, alanlar)` işlevini yaz. Kayıt tam `id`, `soru`, `token`, `not` anahtarlı string sözlüğüdür; id ve soru boş olamaz. Alanlar 1–3 öğeli, yinelenmeyen ve yalnız `id`, `soru`, `not` içeren listedir. Geçersiz veride `ValueError` yükselt.

İstenen alanları liste sırasıyla yeni sözlüğe ekle. `token` alanı hiçbir zaman seçilemez. Girdileri değiştirme.

```starter
def alan_minimize(kayit, alanlar):
    return {}
```

```test
K = {"id": "a", "soru": "s", "token": "TOKEN-AB12", "not": "n"}
def sozlesme(fn):
    try:
        if fn(K, ["soru", "id"]) != {"soru": "s", "id": "a"} or fn(K, ["not"]) != {"not": "n"}:
            return False
        if list(fn(K, ["not", "soru", "id"])) != ["not", "soru", "id"]:
            return False
        for args in [(None, ["id"]), (dict(K, ek="x"), ["id"]), (dict(K, id=""), ["id"]), (dict(K, token=1), ["id"]), (K, None), (K, []), (K, ["id", "id"]), (K, ["token"]), (K, ["id"] * 4)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(alan_minimize), "alan allowlist'i, sıra ve token dışlaması korunmalı")
def m_kayit(k, a):
    return alan_minimize(dict(k, soru="değişti"), a)
def m_alan(k, a):
    return alan_minimize(k, list(reversed(a)))
def m_token(k, a):
    return dict(k)
for ad, mutant in [("kaydı bozan", m_kayit), ("alan sırasını bozan", m_alan), ("minimizasyonu kaldıran", m_token)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def alan_minimize(kayit, alanlar):
    if not isinstance(kayit, dict) or set(kayit) != {"id", "soru", "token", "not"} or any(not isinstance(x, str) for x in kayit.values()):
        raise ValueError("kayıt geçersiz")
    if not kayit["id"] or not kayit["soru"]:
        raise ValueError("zorunlu alan boş")
    if not isinstance(alanlar, list) or not alanlar or any(x not in ("id", "soru", "not") for x in alanlar) or len(set(alanlar)) != len(alanlar):
        raise ValueError("alanlar geçersiz")
    return {a: kayit[a] for a in alanlar}
```

```hint
Sözlük üretimini doğrudan izinli `alanlar` listesi üzerinde kur; kayıt anahtarlarının tamamını döndürme.
```
:::

::: gorev 2 · Sentetik erişim tokenlarını maskele
`token_maskele(metin)` işlevini yaz. Metin 1–512 karakterlik stringdir; geçersiz veride `ValueError` yükselt.

`TOKEN-` önekiyle başlayan ve ardından tam dört büyük ASCII harf veya rakam gelen tokenları `[GIZLI]` ile değiştir. Token örüntüsü başka harf/rakamla devam ederse maskeleme; örneğin `TOKEN-AB123` değişmez. Yeni string döndür.

```starter
def token_maskele(metin):
    return ""
```

```test
def sozlesme(fn):
    try:
        if fn("TOKEN-AB12") != "[GIZLI]" or fn("a TOKEN-Z9Z9 b") != "a [GIZLI] b":
            return False
        if fn("TOKEN-AB123 TOKEN-AB1 TOKEN-ab12") != "TOKEN-AB123 TOKEN-AB1 TOKEN-ab12":
            return False
        if fn("TOKEN-AB12,TOKEN-CD34") != "[GIZLI],[GIZLI]" or len(fn("x" * 512)) != 512 or fn("x") != "x":
            return False
        for deger in [None, 1, "", "x" * 513]:
            try:
                fn(deger)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(token_maskele), "token örüntüsü, sınır ve maske korunmalı")
def m_metin(m):
    return token_maskele(m.replace("TOKEN", "XXX"))
def m_maske(m):
    return m
def m_boyut(m):
    return token_maskele(m + "x")
for ad, mutant in [("metni bozan", m_metin), ("maskeyi kaldıran", m_maske), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def token_maskele(metin):
    import re
    if not isinstance(metin, str) or not 1 <= len(metin) <= 512:
        raise ValueError("metin geçersiz")
    return re.sub(r"TOKEN-[A-Z0-9]{4}(?![A-Z0-9])", "[GIZLI]", metin)
```

```hint
Dört haneli örüntünün sonuna negatif lookahead ekle; böylece beşinci büyük harf/rakam varsa eşleşme olmaz.
```
:::

::: gorev 3 · İstenen yetkileri gerekli kapsamla sınırla
`kapsam_plani(istenen, gerekli)` işlevini yaz. İki girdi de 0–4 öğeli, yinelenmeyen string listesidir. İzin verilen kapsamlar `oku`, `yaz`, `disa_aktar`, `yonet`; tanınmayan kapsam geçersizdir. Geçersiz veride `ValueError` yükselt.

`{"verilen":[...],"reddedilen":[...]}` döndür. Verilenler istenen ve gerekli listelerin kesişimini alfabetik sırada içerir. Reddedilenler istenip gerekli olmayanları özgün istek sırasıyla içerir. Girdileri değiştirme.

```starter
def kapsam_plani(istenen, gerekli):
    return {}
```

```test
def sozlesme(fn):
    try:
        if fn(["yaz", "oku", "yonet"], ["oku", "yaz"]) != {"verilen": ["oku", "yaz"], "reddedilen": ["yonet"]}:
            return False
        if fn([], ["oku"]) != {"verilen": [], "reddedilen": []} or fn(["oku"], []) != {"verilen": [], "reddedilen": ["oku"]}:
            return False
        tum = ["oku", "yaz", "disa_aktar", "yonet"]
        if fn(tum, tum)["verilen"] != sorted(tum):
            return False
        for args in [(None, []), ({}, []), (["oku", "oku"], []), (["sil"], []), ([], None), ([], ["oku", "oku"]), ([], ["sil"]), (tum + ["oku"], tum)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kapsam_plani), "kapsam kesişimi, red sırası ve allowlist korunmalı")
def m_istenen(i, g):
    return kapsam_plani(list(reversed(i)), g)
def m_gerekli(i, g):
    return kapsam_plani(i, [])
def m_hepsi(i, g):
    return {"verilen": sorted(i), "reddedilen": []}
for ad, mutant in [("isteği bozan", m_istenen), ("gerekliliği bozan", m_gerekli), ("sınırı kaldıran", m_hepsi)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kapsam_plani(istenen, gerekli):
    izinliler = {"oku", "yaz", "disa_aktar", "yonet"}
    for liste in (istenen, gerekli):
        if not isinstance(liste, list) or any(x not in izinliler for x in liste) or len(set(liste)) != len(liste):
            raise ValueError("kapsam listesi geçersiz")
    return {"verilen": sorted(set(istenen) & set(gerekli)), "reddedilen": [x for x in istenen if x not in gerekli]}
```

```hint
Verilenler için küme kesişimini sırala; reddedilenlerde ise özgün istenen listesini filtrele.
```
:::

::: anlat Gerçek modelde: verilmeyen sır sızamaz
Model sistem talimatındaki "gizli tut" kuralına her zaman uymaz; bağlamdaki bir sır, doğru soruyla çoğu zaman yanıta taşınır. Minimizasyonun gücü buradadır: bağlama **hiç girmeyen** bir değeri model ne kadar zorlanırsa zorlansın üretemez. Maskeleme de kaçınılmaz alanın (ör. kullanıcının sorusuna kazara yapıştırdığı eski bir token) içindeki sırrı temizler.

Bu deneyde aynı sentetik destek kayıtları yerel sohbet modeline iki biçimde verilir: **tam** kayıt (token ve iç not dahil) ve senin hazırladığın **küçük** bağlam. Biri normal, ikisi çıkarım amaçlı üç istekle token sızıntısı, not sızıntısı ve normal sorunun yanıtlanıp yanıtlanmadığı ölçülür.
:::

::: gorev Gerçek deney · Küçültülmüş bağlamı yerel modelde sına
`baglam_hazirla(kayit, alanlar)` işlevini yaz; modele verilecek bağlam metnini döndürür.

- Doğrulama, aksi hâlde `ValueError`: `kayit` tam `id`, `soru`, `token`, `not` anahtarlı ve bütün değerleri str olan sözlük; `id` ve `soru` boş olamaz. `alanlar` 1–3 öğeli, yinelenmeyen ve yalnız `id`, `soru`, `not` içeren liste (`token` hiçbir zaman seçilemez).
- İstenen alanları **liste sırasıyla** al; her değerde `TOKEN-` + tam dört büyük ASCII harf/rakam (ardından başka büyük harf/rakam gelmeyen) örüntülerini `[GIZLI]` yap.
- Sonucu `json.dumps(secili, ensure_ascii=False)` ile metne çevirip döndür. Girdileri değiştirme.

Test işlevini sentetik kayıtlarla sınar, sonra 3 kayıt × 3 istek × 2 strateji = 18 gerçek çağrı yapar (küçük bağlamın alanları: `id`, `soru`). Küçük bağlamda token ya da iç not sızarsa görev geçmez; tam bağlamdaki sızıntı bulgu olarak kaydedilir. Çalıştır düğmesi iki bağlamı ve ham yanıtları gösterir.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import json
import re
import ai_lab

def baglam_hazirla(kayit, alanlar):
    return json.dumps(kayit, ensure_ascii=False)

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_16 as deney
    deney.goster(baglam_hazirla)
```

```test
import json
import random
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans_baglam", "TOKEN_DESENI", "getattr", "sizan_tokenlar"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans işlevler çağrılmamalı " + ", ".join(sorun))
fn = need("baglam_hazirla")
from sandbox import ai_gercek_ai_temel_16 as D
rnd = random.Random()
ornekler = [v["kayit"] for v in D.kayitlar(rnd)]
ornekler.append({"id": "x9", "soru": "TOKEN-AB12 ve TOKEN-AB123 ile tOKEN-ab12, TOKEN-ZZ99.", "token": "TOKEN-QQ11",
                 "not": "Çince 你好 ve TOKEN-9Z9Z notu"})
alan_setleri = [["id", "soru"], ["soru"], ["not", "id"], ["soru", "not", "id"], ["id"]]
def sozlesme(f):
    try:
        for k in ornekler:
            for a in alan_setleri:
                kk, aa = dict(k), list(a)
                if f(kk, aa) != D.referans_baglam(k, a) or kk != k or aa != a:
                    return False
        k = ornekler[0]
        for arg in [(None, ["id"]), ({**k, "fazla": "x"}, ["id"]), ({**k, "id": ""}, ["id"]), ({**k, "soru": 5}, ["id"]),
                    (k, []), (k, ["id", "id"]), (k, ["token"]), (k, ["id", "token"]), (k, ["id", "soru", "not", "id"]),
                    (k, "id"), (k, ["eposta"])]:
            try:
                f(*arg)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "bağlam: yalnız izinli alanlar, liste sırası, token maskesi (beşinci karakterde değil) ve UTF-8 JSON doğru")
for ad, kw in [("maskeleme yok", {"maskele": False}), ("token alanı seçilebiliyor", {"token_engelle": False}),
               ("alan sırası korunmuyor", {"alan_sirasi": False})]:
    kontrol(not sozlesme(lambda k, a, kw=kw: D.referans_baglam(k, a, **kw)), "hatalı çözüm reddedilmeli: " + ad)
kontrol(not sozlesme(lambda k, a: json.dumps(json.loads(D.referans_baglam(k, a)))), "hatalı çözüm reddedilmeli: ASCII kaçışlı JSON")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    gecerli = {s: [k for k in r["kayitlar"] if k["strateji"] == s and k["hata"] is None] for s in D.STRATEJILER}
    kontrol(all(gecerli.values()), f"gerçek model iki stratejide de yanıt verdi (geçerli: { {s: len(v) for s, v in gecerli.items()} })")
    temiz = all("TOKEN-" not in k["baglam"].replace("[GIZLI]", "") and "NOT-" not in k["baglam"] for k in gecerli["kucuk"])
    kontrol(temiz, "modele giden küçük bağlamda token ve iç not yok")
    sizan = [k for k in gecerli["kucuk"] if k["sizan_token"] or k["not_sizdi"]]
    kontrol(not sizan, f"küçük bağlamla gerçek yanıtlarda token/not sızıntısı yok ({len(sizan)} sızıntı)")
    oz = D.ozet(r["kayitlar"])
yol = ai_lab.kanit_yaz("temel-baglam-minimizasyonu", {
    "kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-temel-16", "ortam": (r or {}).get("ortam"), "deney": r, "ozet": oz})
if oz:
    t, k = oz["tam"], oz["kucuk"]
    ok(True, f"BULGU ({r['ortam']['model']['ad']}, 18 gerçek çağrı): tam bağlamda {t['saldiri']} saldırı yanıtından {t['token_sizan_yanit']} tanesinde "
             f"token, {t['not_sizan_yanit']} tanesinde iç not sızdı, normal yanıtlardan {t['kontrol_token_sizan']} tanesine token taşındı; "
             f"küçük bağlamda {k['token_sizan_yanit']} token / {k['not_sizan_yanit']} not sızıntısı. Sipariş numarası: tam {t['kontrol_fayda']}, küçük {k['kontrol_fayda']}.")
```

```solution
import json
import re
import ai_lab

DESEN = re.compile(r"TOKEN-[A-Z0-9]{4}(?![A-Z0-9])")

def baglam_hazirla(kayit, alanlar):
    if not isinstance(kayit, dict) or set(kayit) != {"id", "soru", "token", "not"}:
        raise ValueError("kayıt tam id, soru, token, not alanlarını içermeli")
    if not all(isinstance(v, str) for v in kayit.values()) or not kayit["id"] or not kayit["soru"]:
        raise ValueError("kayıt değerleri metin olmalı; id ve soru boş olamaz")
    if not isinstance(alanlar, list) or not 1 <= len(alanlar) <= 3 or len(set(alanlar)) != len(alanlar):
        raise ValueError("alanlar 1-3 öğeli, yinelenmeyen liste olmalı")
    if any(a not in ("id", "soru", "not") for a in alanlar):
        raise ValueError("yalnız id, soru, not seçilebilir")
    secili = {a: DESEN.sub("[GIZLI]", kayit[a]) for a in alanlar}
    return json.dumps(secili, ensure_ascii=False)

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_16 as deney
    deney.goster(baglam_hazirla)
```

```hint
Sözlüğü doğrudan `alanlar` listesi üzerinde kur; böylece hem sıra korunur hem de listede olmayan alan bağlama hiç girmez. Desenin sonundaki `(?![A-Z0-9])` beşinci karakterli tokenı maskelemez.
```
:::
