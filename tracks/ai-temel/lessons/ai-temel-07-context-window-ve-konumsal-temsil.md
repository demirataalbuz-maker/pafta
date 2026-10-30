---
id: ai-temel-07
title: "Context Window ve Konumsal Temsil"
summary: Token bütçesine göre ardışık bağlam seç, sinüzoidal konum üret ve düşen talimatları raporla.
timeout: 45
---

::: anlat Bağlam penceresi sınırlı bir bütçedir
Modele aynı anda sunulan token sayısı sınırlıdır. Bütçe dolunca eski mesajlar kırpılabilir; kırpma yalnız metni değil, güvenlik talimatlarını ve kanıtları da kapsam dışında bırakabilir. Bu yüzden hangi mesajların kaldığı açıkça ölçülmelidir.

Bu derste Transformers modeli açılmaz. Mesaj uzunlukları hazır sayılardır. Sondan başlayarak sığan ardışık mesajlar seçilir; sığmayan ilk eski mesajda durulur. Böylece bağlam her zaman özgün dizinin kesintisiz bir son parçasıdır.
:::

::: anlat Konum bilgisi sırayı temsil eder
Transformer token sırasını doğrudan bilmez; konumsal temsil bu bilgiyi ekler. Sinüzoidal kodlama farklı frekanslarda sinüs ve kosinüs değerleri kullanır. Biz iki boyutlu, sabit tabanlı küçük bir sürüm kullanacağız.

Konumsal vektör tokenın anlamını tek başına taşımaz. Ayrıca modern modeller farklı konum yöntemleri kullanabilir; buradaki amaç sıra ve pencere kavramlarını deterministik olarak sınamaktır.
:::

::: tahmin Bağlam seçimini tahmin et
Üç çıktı satırını yaz:

```python
print(["a", "b", "c", "d"][-2:])
import math
print([round(math.sin(0), 6), round(math.cos(0), 6)])
uzunluklar = [4, 3, 2]
print(sum(uzunluklar[1:]))
```

???

```cikti
['c', 'd']
[0.0, 1.0]
5
```

İlk satır son iki tokenı, ikinci satır sıfır konumunu, üçüncü satır son iki mesajın bütçesini gösterir.
:::

::: gorev 1 · Tokenları pencere sınırına göre kırp
`pencere_kirp(tokenlar, sinir)` işlevini yaz. Tokenlar 1–8 öğeli, boş olmayan string listesidir; sınır bool olmayan 1–8 tamsayısıdır. Geçersiz veride `ValueError` yükselt.

Son `sinir` tokenı özgün sırayla yeni listede döndür. Sınır mevcut uzunluktan büyükse bütün listeyi kopyala; girdiyi değiştirme.

```starter
def pencere_kirp(tokenlar, sinir):
    return []
```

```test
T = ["a", "b", "c", "d"]
def sozlesme(fn):
    try:
        if fn(T, 2) != ["c", "d"] or fn(T, 4) != T or fn(T, 8) != T or fn(T, 1) != ["d"]:
            return False
        sonuc = fn(T, 4)
        sonuc[0] = "x"
        if T[0] != "a" or fn(["a"], 1) != ["a"] or fn(["a"] * 8, 8) != ["a"] * 8:
            return False
        for args in [(None, 1), ([], 1), ([""], 1), ([1], 1), (T, 0), (T, 9), (T, True), (T, 1.0), (["a"] * 9, 1)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(pencere_kirp), "son tokenlar, kopya ve pencere sınırı korunmalı")
def m_token(t, s):
    return pencere_kirp(list(reversed(t)), s)
def m_sinir(t, s):
    return pencere_kirp(t, 1)
def m_boyut(t, s):
    return pencere_kirp(t + ["x"], s)
for ad, mutant in [("sırayı bozan", m_token), ("sınırı bozan", m_sinir), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def pencere_kirp(tokenlar, sinir):
    if not isinstance(tokenlar, list) or not 1 <= len(tokenlar) <= 8 or any(not isinstance(x, str) or not x for x in tokenlar):
        raise ValueError("tokenlar geçersiz")
    if not isinstance(sinir, int) or isinstance(sinir, bool) or not 1 <= sinir <= 8:
        raise ValueError("sınır geçersiz")
    return list(tokenlar[-sinir:])
```

```hint
Negatif dilim başlangıcı `tokenlar[-sinir:]` son öğeleri özgün sırayla verir.
```
:::

::: gorev 2 · İki boyutlu sinüzoidal konum üret
`konum_vektoru(pozisyon)` işlevini yaz. Pozisyon bool olmayan 0–127 tamsayısıdır; geçersiz veride `ValueError` yükselt.

`[sin(pozisyon), cos(pozisyon)]` değerlerini altı ondalığa yuvarlayarak döndür. Bu küçük fixture, sinüzoidal kodlamanın ilk iki boyutunu temsil eder.

```starter
def konum_vektoru(pozisyon):
    return []
```

```test
def sozlesme(fn):
    try:
        if fn(0) != [0.0, 1.0] or fn(1) != [0.841471, 0.540302] or fn(127) != [0.97263, 0.232359]:
            return False
        for deger in [None, True, 1.0, -1, 128]:
            try:
                fn(deger)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(konum_vektoru), "sinüs, kosinüs ve pozisyon sınırı korunmalı")
def m_pozisyon(p):
    return konum_vektoru(p + 1)
def m_sabit(p):
    return [0.0, 1.0]
for ad, mutant in [("pozisyonu kaydıran", m_pozisyon), ("sabit konum", m_sabit)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def konum_vektoru(pozisyon):
    import math
    if not isinstance(pozisyon, int) or isinstance(pozisyon, bool) or not 0 <= pozisyon < 128:
        raise ValueError("pozisyon geçersiz")
    return [round(math.sin(pozisyon), 6), round(math.cos(pozisyon), 6)]
```

```hint
Aynı pozisyonu `math.sin` ve `math.cos` işlevlerine verip iki sonucu ayrı yuvarla.
```
:::

::: gorev 3 · Bağlam bütçesine sığan mesajları raporla
`baglam_sec(mesajlar, butce)` işlevini yaz. Mesajlar 1–8 öğeli listedir; her mesaj tam `id`, `rol`, `uzunluk` anahtarlarına sahiptir. Kimlikler birbirinden farklı, boş olmayan stringler; rol `system` veya `user`; uzunluk bool olmayan 1–8 tamsayısıdır. Bütçe bool olmayan 1–16 tamsayısıdır. Geçersiz veride `ValueError` yükselt.

Sondan başa doğru mesajları toplam uzunluk bütçeyi aşmadan ekle. Sığmayan ilk mesajda dur. `{"secilen":[...],"dusen":[...]}` döndür; her iki kimlik listesi de özgün mesaj sırasındadır. Girdileri değiştirme.

```starter
def baglam_sec(mesajlar, butce):
    return {}
```

```test
M = [{"id": "s", "rol": "system", "uzunluk": 4}, {"id": "a", "rol": "user", "uzunluk": 3}, {"id": "b", "rol": "user", "uzunluk": 2}]
def sozlesme(fn):
    try:
        if fn(M, 5) != {"secilen": ["a", "b"], "dusen": ["s"]} or fn(M, 9) != {"secilen": ["s", "a", "b"], "dusen": []}:
            return False
        if fn(M, 2) != {"secilen": ["b"], "dusen": ["s", "a"]} or fn(M, 1) != {"secilen": [], "dusen": ["s", "a", "b"]} or fn(M, 16) != {"secilen": ["s", "a", "b"], "dusen": []}:
            return False
        tek = {"id": "t", "rol": "user", "uzunluk": 1}
        sekiz = [dict(tek, id=str(i), uzunluk=1) for i in range(8)]
        if fn([tek], 1) != {"secilen": ["t"], "dusen": []} or fn([dict(tek, uzunluk=8)], 8)["secilen"] != ["t"] or len(fn(sekiz, 16)["secilen"]) != 8:
            return False
        for args in [(None, 5), ([], 5), (sekiz + [dict(tek, id="9")], 16), (M, 0), (M, 17), (M, True), ([dict(M[0], id=1)], 5), ([dict(M[0], id="")], 5), ([dict(M[0], rol="tool")], 5), ([dict(M[0], rol=1)], 5), ([dict(M[0], ek=1)], 5), ([dict(M[0], uzunluk="4")], 5), ([dict(M[0], uzunluk=True)], 5), ([dict(M[0], uzunluk=0)], 5), ([dict(M[0], uzunluk=9)], 9), ([M[0], M[0]], 9)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(baglam_sec), "ardışık bağlam, bütçe ve düşen talimatlar korunmalı")
def m_mesaj(m, b):
    return baglam_sec(list(reversed(m)), b)
def m_butce(m, b):
    return baglam_sec(m, 16)
def m_boyut(m, b):
    return baglam_sec(m + [dict(m[-1], id="x")], b)
for ad, mutant in [("mesajları bozan", m_mesaj), ("bütçeyi bozan", m_butce), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def baglam_sec(mesajlar, butce):
    if not isinstance(mesajlar, list) or not 1 <= len(mesajlar) <= 8:
        raise ValueError("mesaj listesi geçersiz")
    if any(not isinstance(m, dict) or set(m) != {"id", "rol", "uzunluk"} for m in mesajlar):
        raise ValueError("mesaj şeması geçersiz")
    if any(not isinstance(m["id"], str) or not m["id"] or m["rol"] not in ("system", "user") or not isinstance(m["uzunluk"], int) or isinstance(m["uzunluk"], bool) or not 1 <= m["uzunluk"] <= 8 for m in mesajlar):
        raise ValueError("mesaj değeri geçersiz")
    if len({m["id"] for m in mesajlar}) != len(mesajlar):
        raise ValueError("kimlikler yinelenemez")
    if not isinstance(butce, int) or isinstance(butce, bool) or not 1 <= butce <= 16:
        raise ValueError("bütçe geçersiz")
    secilen = []
    toplam = 0
    for m in reversed(mesajlar):
        if toplam + m["uzunluk"] > butce:
            break
        secilen.append(m["id"])
        toplam += m["uzunluk"]
    secilen.reverse()
    return {"secilen": secilen, "dusen": [m["id"] for m in mesajlar if m["id"] not in secilen]}
```

```hint
Sondan gezerken toplam uzunluğu tut. Bütçe aşılırsa döngüyü kır; seçim listesini sonunda ters çevir.
```
:::

::: anlat Gerçek deney: pencereye metin değil token sığar
Önceki görevlerde mesaj uzunlukları hazır sayılardı. Şimdi kurulu küçük dil modelinin gerçek tokenizer'ı ve ileri hesabı kullanılacak. Deney metni ham kimliklere dönüştürür, sondaki tokenları korur, düşen token sayısını kaydeder ve kalan diziyle gerçek modelin sonraki-token logitlerini hesaplar. Sözcük veya karakter sayısıyla bütçe hesaplamak geçersizdir.

Bu deneyin bütçesi 1–32 tokendır; modelin gerçek `config.max_position_embeddings` sınırını ayrıca raporlarız. Kısa bütçe, laptopta hızlı ve tekrarlanabilir bir öğretim tercihidir; modelin bütün pencere kapasitesini veya uzun bağlam kalitesini sınadığımız anlamına gelmez. “Metni kestim, system talimatı güvende” gibi bir sonuç da çıkarılmaz; bu görev sohbet rolleri için koruma politikası uygulamaz.

Konumları kırpılmış girdide `0..N-1` olarak yeniden üretip modele açıkça `position_ids` ile vereceğiz. Bu modelin konum mekanizmasını kullanmak, önceki iki boyutlu sinüs tablosunu gerçek modelin mekanizması sanmak değildir. Dönen sayılar gerçek ağırlıklarla ileri hesaplanır. Test, yalnız raporlanan konumlara değil, modele gerçekte gönderilen tokenlara ve konumlara da bakar.
:::

::: gorev Gerçek deney · Token bütçesi, konumlar ve gerçek ileri hesap
`gercek_baglam_raporu(metin, butce)` işlevini yaz:

- `metin` boşluk dışı karakter içeren bir `str`, `butce` bool olmayan 1–32 aralığında `int` olsun. Aksi hâlde `ValueError` yükselt. Metni normalize etme veya kırpma.
- `tok, model, bilgi = ai_lab.dil_modeli()` ile kurulu modeli al. Gerçek model sınırını `int(model.config.max_position_embeddings)` ile oku. Bütçe bu sınırı da aşamaz.
- Özel token eklemeden elde edilen **tam** kimlik listesinin son `butce` tokenını koru. Başlangıç sayısı ile korunan sayıdan düşen sayıyı hesapla.
- `position_ids`, korunan token sayısına göre `[[0, 1, ..., N-1]]` olsun. `torch.no_grad()` içinde gerçek modeli bu kimlikler ve konumlarla, `use_cache=False` vererek çalıştır.
- Son konumun ham logitlerini double'a dönüştür. Tam şu sözlüğü döndür: `model_siniri`, `girdi_token_sayisi`, `dusen_token_sayisi`, `token_idleri`, `konumlar`, `en_olasi_id` (son logitlerin argmax'ı, int), `ornek_logitler` (son konumun sözlükteki ilk 8 tokenına ait float logitler).

`konumlar` düz bir int listesidir. Bütçe aşılırsa başı değil sonu koru, sırayı değiştirme. `ornek_logitler` ilk konumdan alınamaz. Teste ait referans işlevi çağırma. Model/bağımlılık yoksa bu adım geçmez; indirme yapmaz.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 240
```

```starter
import ai_lab

def gercek_baglam_raporu(metin, butce):
    return {}

if ai_lab.CALISTIR:
    for b in [2, 8]:
        print(gercek_baglam_raporu("The old instruction was removed; the latest note is green.", b))
```

```test
import copy
import random
import ai_lab

sonuclar = []
def kontrol(c, mesaj):
    sonuclar.append(bool(c))
    return ok(c, mesaj)
kontrol(not ai_lab.kod_denetimi(src), "laboratuvar yamalanmamalı")
fn = need("gercek_baglam_raporu")
try:
    import torch
    tok, model, bilgi = ai_lab.dil_modeli()
except (ImportError, ai_lab.GercekLabYok) as e:
    kontrol(False, "GERÇEK MODEL YOK: " + str(e))
    stop()

rng = random.SystemRandom()
metinler = ["The original rule is blue. The latest note is green.",
            "  İstanbul is a city; a model reads tokens, not words.",
            "A " + str(rng.randrange(1000,9999)) + " " + rng.choice(["river", "forest", "city"]) + " message with a final word."]
ayarlar = [(metinler[0], 1), (metinler[0], 4), (metinler[1], 8), (metinler[2], 32)]

def hesap(m, b, bas=False, ters=False, ilk=False, sifir=False):
    tum = tok(m, add_special_tokens=False)["input_ids"]
    ids = tum[:b] if bas else tum[-b:]
    if ters:
        ids = list(reversed(ids))
    konum = [0] * len(ids) if sifir else list(range(len(ids)))
    with torch.no_grad():
        logits = model(torch.tensor([ids]), position_ids=torch.tensor([konum]), use_cache=False).logits[0, 0 if ilk else -1].double()
    return {"model_siniri": int(model.config.max_position_embeddings), "girdi_token_sayisi": len(tum),
            "dusen_token_sayisi": len(tum)-len(ids), "token_idleri": ids, "konumlar": konum,
            "en_olasi_id": int(logits.argmax().item()), "ornek_logitler": logits[:8].tolist()}
beklenen = [hesap(m,b) for m,b in ayarlar]

def ayni(a,b):
    if not isinstance(a, dict) or set(a)!=set(b):
        return False
    for k in ["model_siniri", "girdi_token_sayisi", "dusen_token_sayisi", "en_olasi_id"]:
        if type(a[k]) is not int or a[k]!=b[k]:
            return False
    for k in ["token_idleri", "konumlar"]:
        if not isinstance(a[k], list) or any(type(i) is not int for i in a[k]) or a[k]!=b[k]:
            return False
    vals=a["ornek_logitler"]
    return isinstance(vals,list) and len(vals)==8 and all(type(x) is float for x in vals) and bool(torch.isfinite(torch.tensor(vals)).all()) and torch.allclose(torch.tensor(vals,dtype=torch.float64),torch.tensor(b["ornek_logitler"],dtype=torch.float64),atol=1e-4,rtol=1e-5)

def sozlesme(f):
    try:
        for (m,b),ref in zip(ayarlar,beklenen):
            cagrilar=[]
            def izle(modul, args, kwargs):
                ids = args[0] if args else kwargs.get("input_ids")
                pos = kwargs.get("position_ids")
                cagrilar.append({"ids": ids.detach().tolist() if isinstance(ids,torch.Tensor) else None,
                                 "konumlar": pos.detach().tolist() if isinstance(pos,torch.Tensor) else None,
                                 "use_cache": kwargs.get("use_cache")})
            handle=model.register_forward_pre_hook(izle, with_kwargs=True)
            try:
                a=f(m,b)
            finally:
                handle.remove()
            if not ayni(a,ref):
                return False
            hedef={"ids":[ref["token_idleri"]],"konumlar":[ref["konumlar"]],"use_cache":False}
            if hedef not in cagrilar:
                return False
        for args in [("",1),("   ",1),(None,1),(True,1),("hi",0),("hi",33),("hi",True),("hi",1.0)]:
            try:
                f(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

kontrol(sozlesme(fn), "gerçek ileri hesap: son token penceresi, gerçek position_ids ve son konum logitleri doğru")
def gecerli(hata=None):
    def f(m,b):
        if not isinstance(m,str) or not m.strip() or type(b) is not int or not 1<=b<=32:
            raise ValueError("girdi")
        return hesap(m,b,**(hata or {}))
    return f
sabit=copy.deepcopy(beklenen[0])
for ad,mutant in [("boş kod/işlev",None),("boş sözlük",lambda m,b:{}),
                  ("sabit gerçek sonuç",lambda m,b:copy.deepcopy(sabit)),
                  ("son yerine ilk tokenlar",gecerli({"bas":True})),
                  ("token sırasını ters çevirme",gecerli({"ters":True})),
                  ("ilk konumun logitleri",gecerli({"ilk":True})),
                  ("bütün konumları sıfırlama",gecerli({"sifir":True}))]:
    kontrol(not sozlesme(mutant), "hatalı çözüm reddedilmeli: "+ad)

ciktilar=[fn(m,b) for m,b in ayarlar] if all(sonuclar) else []
kontrol(any(d["dusen_token_sayisi"]>0 for d in ciktilar), "en az bir gerçek girdi bütçe yüzünden kırpıldı")
kontrol(any(d["dusen_token_sayisi"]==0 for d in ciktilar), "sığan gerçek girdi de sınandı")
ai_lab.kanit_yaz("temel-07-baglam",{
    "kaynak":"gercek","kabul":all(sonuclar),"model_bilgisi":bilgi,
    "ayarlar":{"girdiler":[list(a) for a in ayarlar],"deney_butce_ust_siniri":32,"use_cache":False},
    "ciktilar":ciktilar,"olculen":"gerçek tokenizasyon, konumlarla ileri hesap ve kısa pencere kırpması",
    "sinir":"tam context kapasitesi veya uzun bağlam doğruluğu kabulü yapılmadı",
    "temizlik":"CPU işlemi; kalıcı sunucu, model indirme ve dış süreç yok"})
for (m,b),d in zip(ayarlar,ciktilar):
    print("bütçe",b,"model sınırı",d["model_siniri"],"düşen",d["dusen_token_sayisi"],"tokenlar",d["token_idleri"],"konumlar",d["konumlar"],"sonraki kimlik",d["en_olasi_id"])
```

```solution
import ai_lab
import torch

def gercek_baglam_raporu(metin, butce):
    if not isinstance(metin,str) or not metin.strip() or type(butce) is not int or not 1<=butce<=32:
        raise ValueError("geçersiz metin veya bütçe")
    tok, model, _=ai_lab.dil_modeli()
    sinir=int(model.config.max_position_embeddings)
    if butce>sinir:
        raise ValueError("model sınırı aşılıyor")
    tum=tok(metin,add_special_tokens=False)["input_ids"]
    if not tum:
        raise ValueError("token yok")
    ids=tum[-butce:]
    konum=list(range(len(ids)))
    with torch.no_grad():
        logits=model(torch.tensor([ids]),position_ids=torch.tensor([konum]),use_cache=False).logits[0,-1].double()
    return {"model_siniri":sinir,"girdi_token_sayisi":len(tum),"dusen_token_sayisi":len(tum)-len(ids),
            "token_idleri":ids,"konumlar":konum,"en_olasi_id":int(logits.argmax().item()),
            "ornek_logitler":logits[:8].tolist()}

if ai_lab.CALISTIR:
    for b in [2,8]:
        print(gercek_baglam_raporu("The old instruction was removed; the latest note is green.",b))
```

```hint
Önce tam kimlik sayısını al, sonra `tum[-butce:]` uygula. Model girdisi `[1,N]`, konum tensörü de `[1,N]` olmalı. Sonraki token için son konum logitleri kullanılır; raporladığın konumların modele de gerçekten gitmesi gerekir.
```
:::
