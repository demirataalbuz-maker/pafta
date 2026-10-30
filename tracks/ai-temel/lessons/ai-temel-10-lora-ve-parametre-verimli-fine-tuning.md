---
id: ai-temel-10
title: "LoRA ve Parametre Verimli Fine-Tuning"
summary: Sentetik LoRA matris çarpımı, temel ağırlıkla birleştirme ve adaptör parametre maliyeti hesapla.
timeout: 45
---

::: anlat LoRA düşük ranklı bir fark öğrenir
LoRA temel ağırlığı dondurup güncellemeyi iki küçük matrisin çarpımıyla temsil eder. `B @ A` temel ağırlıkla aynı boyutta bir fark üretir; rank arttıkça adaptör kapasitesi ve parametre maliyeti artar. Ölçek katsayısı bu farkın etkisini ayarlar.

Bu derste Transformers, PEFT veya bitsandbytes çalıştırılmaz. İki çarpı iki sentetik matrisler, matris çarpımının boyutunu ve birleştirme sırasını görünür kılar. Gerçek projelerde hedef modül seçimi ayrıca deney gerektirir.
:::

::: anlat Birleştirme ile eğitim parametre sayısı farklıdır
Inference öncesinde LoRA farkı temel ağırlığa eklenebilir. Böylece ayrı adaptör çağrısı yerine tek birleşik ağırlık kullanılır. Temel ağırlığı değiştirmeden yeni fark döndürmek deneylerin tekrarlanmasını kolaylaştırır.

Eğitilen parametre sayısı rank çarpı giriş ve çıkış boyutlarının toplamıdır. Bu sayıyı temel matrisin parametre sayısıyla karşılaştırmak bellek tasarrufunu ölçmenin basit bir yoludur; toplam bellekte aktivasyon ve optimizer ayrıca hesaba katılır.
:::

::: tahmin LoRA farkını tahmin et
Üç çıktı satırını yaz:

```python
A = [[1, 0], [0, 1]]
B = [[2, 0], [0, 2]]
print([[2, 0], [0, 2]])
print([[3, 1], [1, 3]])
print(2 * (4 + 8))
```

???

```cikti
[[2, 0], [0, 2]]
[[3, 1], [1, 3]]
24
```

İlk satır birim A ile ölçekli B çarpımını, ikinci satır birim temel ağırlığa eklenen farkı, üçüncü satır rank-2 adaptör parametre sayısını gösterir.
:::

::: gorev 1 · İki matrislik LoRA farkını hesapla
`lora_fark(a, b, olcek)` işlevini yaz. a ve b iki satır iki sütunluk, bool olmayan sayı listeleridir. Ölçek bool olmayan, `0 < olcek <= 4` koşulundaki sayıdır. Geçersiz veride `ValueError` yükselt.

`olcek * (b @ a)` matrisini hesapla. Çıktı iki çarpı iki listedir ve her değer altı ondalığa yuvarlanır. Girdileri değiştirme.

```starter
def lora_fark(a, b, olcek):
    return []
```

```test
A = [[1, 2], [3, 4]]
B = [[0, 1], [1, 0]]
def sozlesme(fn):
    try:
        if fn(A, B, 1) != [[3.0, 4.0], [1.0, 2.0]] or fn([[1, 0], [0, 1]], [[2, 0], [0, 2]], 0.5) != [[1.0, 0.0], [0.0, 1.0]]:
            return False
        if fn(A, B, 4) != [[12.0, 16.0], [4.0, 8.0]] or fn(A, B, 1 / 3) != [[1.0, 1.333333], [0.333333, 0.666667]]:
            return False
        for args in [(None, B, 1), ([[1, 0]], B, 1), ([[1], [0, 1]], B, 1), ([[1, True], [0, 1]], B, 1), (A, None, 1), (A, B, 0), (A, B, 4.1), (A, B, True)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(lora_fark), "B@A sırası, ölçek ve matris şeması korunmalı")
def m_a(a, b, o):
    return lora_fark(list(reversed(a)), b, o)
def m_b(a, b, o):
    return lora_fark(a, list(reversed(b)), o)
def m_olcek(a, b, o):
    return lora_fark(a, b, o * 2)
for ad, mutant in [("A matrisini bozan", m_a), ("B matrisini bozan", m_b), ("ölçeği bozan", m_olcek)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def lora_fark(a, b, olcek):
    def matris(m):
        return isinstance(m, list) and len(m) == 2 and all(isinstance(s, list) and len(s) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in s) for s in m)
    if not matris(a) or not matris(b):
        raise ValueError("matris geçersiz")
    if not isinstance(olcek, (int, float)) or isinstance(olcek, bool) or not 0 < olcek <= 4:
        raise ValueError("ölçek geçersiz")
    return [[round(olcek * sum(b[i][k] * a[k][j] for k in range(2)), 6) for j in range(2)] for i in range(2)]
```

```hint
Çıktının `i,j` hücresinde B'nin i. satırıyla A'nın j. sütununu çarpıp topla.
```
:::

::: gorev 2 · LoRA farkını temel ağırlığa ekle
`agirlik_birlestir(temel, fark)` işlevini yaz. İki girdi de iki çarpı iki sayı matrisidir; bool ve diğer geçersiz verilerde `ValueError` yükselt.

Karşılıklı hücreleri toplayarak yeni matris döndür ve değerleri altı ondalığa yuvarla. Özellikle temel matrisi yerinde değiştirme.

```starter
def agirlik_birlestir(temel, fark):
    return []
```

```test
import copy
W = [[1, 0], [0, 1]]
D = [[0.5, 1], [-1, 2]]
def sozlesme(fn):
    try:
        once = copy.deepcopy(W)
        if fn(W, D) != [[1.5, 1.0], [-1.0, 3.0]] or W != once:
            return False
        if fn([[0, 0], [0, 0]], D) != [[0.5, 1.0], [-1.0, 2.0]] or fn(W, [[0, 0], [0, 0]]) != [[1.0, 0.0], [0.0, 1.0]] or fn(W, [[1 / 3, 0], [0, 0]]) != [[1.333333, 0.0], [0.0, 1.0]]:
            return False
        for args in [(None, D), ([[1, 0]], D), ([[1], [0, 1]], D), ([[1, True], [0, 1]], D), (W, None), (W, [[0, 0], [0]])]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(agirlik_birlestir), "hücre toplamı ve temel ağırlık kopyası korunmalı")
def m_temel(w, d):
    return agirlik_birlestir(list(reversed(w)), d)
def m_fark(w, d):
    return agirlik_birlestir(w, list(reversed(d)))
def m_boyut(w, d):
    return agirlik_birlestir(w + [[0, 0]], d + [[0, 0]])
for ad, mutant in [("temeli bozan", m_temel), ("farkı bozan", m_fark), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def agirlik_birlestir(temel, fark):
    def matris(m):
        return isinstance(m, list) and len(m) == 2 and all(isinstance(s, list) and len(s) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in s) for s in m)
    if not matris(temel) or not matris(fark):
        raise ValueError("matris geçersiz")
    return [[round(temel[i][j] + fark[i][j], 6) for j in range(2)] for i in range(2)]
```

```hint
İki iç liste üretiminde aynı `i,j` konumundaki değerleri topla; yeni satırlar oluştur.
```
:::

::: gorev 3 · Adaptör parametre maliyetini hesapla
`lora_maliyet(girdi, cikti, rank)` işlevini yaz. Girdi ve çıktı bool olmayan 2, 4 veya 8 tamsayısıdır. Rank bool olmayan 1–4 tamsayısıdır. Geçersiz veride `ValueError` yükselt.

Temel parametre sayısı `girdi*cikti`, eğitilen LoRA parametre sayısı `rank*(girdi+cikti)` olsun. `{"temel":T,"egitilen":E,"oran":R}` döndür; oran eğitilen/temel değeridir.

```starter
def lora_maliyet(girdi, cikti, rank):
    return {}
```

```test
def sozlesme(fn):
    try:
        if fn(4, 8, 2) != {"temel": 32, "egitilen": 24, "oran": 0.75} or fn(2, 2, 1) != {"temel": 4, "egitilen": 4, "oran": 1.0}:
            return False
        if fn(8, 8, 4) != {"temel": 64, "egitilen": 64, "oran": 1.0} or fn(8, 2, 3) != {"temel": 16, "egitilen": 30, "oran": 1.875}:
            return False
        for args in [(3, 4, 1), (4.0, 4, 1), (True, 4, 1), (4, 3, 1), (4, 4.0, 1), (4, True, 1), (4, 8, 0), (4, 8, 5), (4, 8, True), (4, 8, 1.0)]:
            try:
                fn(*args)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(lora_maliyet), "LoRA parametre sayısı, oran ve boyutlar korunmalı")
def m_girdi(g, c, r):
    return lora_maliyet(g * 2, c, r)
def m_cikti(g, c, r):
    return lora_maliyet(g, c * 2, r)
def m_rank(g, c, r):
    return lora_maliyet(g, c, 1)
for ad, mutant in [("girdiyi bozan", m_girdi), ("çıktıyı bozan", m_cikti), ("rankı bozan", m_rank)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def lora_maliyet(girdi, cikti, rank):
    if any(not isinstance(x, int) or isinstance(x, bool) or x not in (2, 4, 8) for x in (girdi, cikti)):
        raise ValueError("boyut geçersiz")
    if not isinstance(rank, int) or isinstance(rank, bool) or not 1 <= rank <= 4:
        raise ValueError("rank geçersiz")
    temel = girdi * cikti
    egitilen = rank * (girdi + cikti)
    return {"temel": temel, "egitilen": egitilen, "oran": egitilen / temel}
```

```hint
Temel sayıyı çarpım, eğitilen sayıyı rank ile boyut toplamının çarpımı olarak ayrı hesapla.
```
:::

::: anlat Gerçek modelde LoRA: 134 milyonun binde üçü
Yukarıdaki görevler 2×2 matrislerle LoRA'nın matematiğini gösterdi. Gerçek bir modelde LoRA, dondurulmuş bir `nn.Linear` katmanını sarar: çıktı `temel(x) + ölçek · x Aᵀ Bᵀ` olur. `A` küçük rastgele değerlerle, `B` sıfırla başlar; böylece adaptör takıldığı anda modelin davranışı değişmez ve eğitim yalnız `A` ile `B`'yi günceller. Ölçek çoğunlukla `alfa / rank`'tir.

Bu deneyde senin LoRA sınıfın SmolLM2-135M'nin 30 katmanındaki `q_proj` ve `v_proj` katmanlarına takılır ve modele CPU'da tek bir cümle öğretilir. Ölçülenler: kaç parametre eğitildi, hedef cümlenin kaybı ne kadar düştü, ilgisiz bir metnin kaybı ne kadar değişti ve birleştirilmiş ağırlığın adaptörlü modelle aynı çıktıyı verip vermediği.
:::

::: gorev Gerçek deney · Elle LoRA ile gerçek modelde ince ayar
`LoraDogrusal(torch.nn.Module)` sınıfını yaz: `LoraDogrusal(temel, rank, alfa)`.

- Doğrulama, aksi hâlde `ValueError`: `temel` bir `torch.nn.Linear`; `rank` bool olmayan int, 1 ile `min(giriş, çıkış)` arası; `alfa` bool olmayan, pozitif int/float.
- `temel`'i `self.temel` olarak sakla ve bütün parametrelerini dondur (`requires_grad=False`).
- `self.A = nn.Parameter(...)` biçimi `[rank, giriş]`, küçük rastgele değerler (ör. `randn * 0.01`); `self.B = nn.Parameter(...)` biçimi `[çıkış, rank]`, **sıfır**. Eğitilen parametreler yalnız bu ikisi olmalı.
- `self.olcek = alfa / rank`.
- `forward(x)`: `self.temel(x) + (x @ A.T @ B.T) * self.olcek`.
- `birlestir()`: `temel.weight + olcek · (B @ A)` tensörünü **yeni** tensör olarak döndür; temel ağırlığı değiştirme.

Test sınıfını gerçek `q_proj` (576→576) ve `v_proj` (576→192) katmanlarının kopyalarında sınar, sonra modelin bir kopyasında 40 adım gerçek eğitim yapar. Çalıştır düğmesi aynı deneyin ölçümlerini gösterir. Laboratuvardaki `referans_sinifi`/`lora_tak` işlevlerini ve PEFT'i kullanma.

```meta
motor: ai-gercek
gereksinim: torch
timeout: 300
```

```starter
import torch
import ai_lab

class LoraDogrusal(torch.nn.Module):
    def __init__(self, temel, rank, alfa):
        super().__init__()
        self.temel = temel

    def forward(self, x):
        return self.temel(x)

    def birlestir(self):
        return self.temel.weight

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_10 as deney
    deney.goster(LoraDogrusal)
```

```test
import copy
import random
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans_sinifi", "lora_tak", "getattr", "peft", "LoraConfig"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans LoRA/PEFT kullanılmamalı " + ", ".join(sorun))
Sinif = need("LoraDogrusal")
try:
    from sandbox import ai_gercek_ai_temel_10 as D
    tok, model, bilgi = ai_lab.dil_modeli()
    import torch
except ai_lab.GercekLabYok as e:
    kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
    stop()
rnd = random.Random()
katman = rnd.randrange(model.config.num_hidden_layers)
gercek_katmanlar = [model.model.layers[katman].self_attn.q_proj, model.model.layers[katman].self_attn.v_proj]
ayarlar = [(rnd.choice([2, 4, 8]), rnd.choice([8, 16, 32])) for _ in gercek_katmanlar]
def sozlesme(S):
    try:
        for orijinal, (r, alfa) in zip(gercek_katmanlar, ayarlar):
            lin = copy.deepcopy(orijinal)
            W0 = lin.weight.detach().clone()
            m = S(lin, r, alfa)
            if any(p.requires_grad for p in lin.parameters()):
                return False
            egitilen = [p for p in m.parameters() if p.requires_grad]
            if sum(p.numel() for p in egitilen) != r * (lin.in_features + lin.out_features):
                return False
            if tuple(m.A.shape) != (r, lin.in_features) or tuple(m.B.shape) != (lin.out_features, r):
                return False
            if m.B.abs().max().item() != 0 or m.A.abs().max().item() == 0 or abs(m.olcek - alfa / r) > 1e-12:
                return False
            x = torch.randn(3, 5, lin.in_features)
            with torch.no_grad():
                if (m(x) - lin(x)).abs().max().item() > 1e-6:
                    return False
                m.A.copy_(torch.randn_like(m.A) * 0.05)
                m.B.copy_(torch.randn_like(m.B) * 0.05)
                beklenen = lin(x) + (x @ m.A.T @ m.B.T) * (alfa / r)
                if (m(x) - beklenen).abs().max().item() > 1e-4:
                    return False
                W = m.birlestir()
                if not isinstance(W, torch.Tensor) or tuple(W.shape) != tuple(W0.shape):
                    return False
                if (W - (W0 + (alfa / r) * (m.B @ m.A))).abs().max().item() > 1e-5:
                    return False
                if not torch.equal(lin.weight, W0):
                    return False
                if (torch.nn.functional.linear(x, W) - m(x)).abs().max().item() > 1e-3:
                    return False
            m(x).sum().backward()
            if lin.weight.grad is not None or m.A.grad is None or m.B.grad is None:
                return False
        lin = copy.deepcopy(gercek_katmanlar[1])
        for arg in [(torch.nn.Conv1d(2, 2, 1), 2, 8), (None, 2, 8), (lin, 0, 8), (lin, 193, 8), (lin, True, 8), (lin, 2.0, 8),
                    (lin, 2, 0), (lin, 2, -1.0), (lin, 2, True)]:
            try:
                S(*arg)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(Sinif), "gerçek q_proj/v_proj: dondurulmuş temel, A/B biçimleri, B=0 başlangıç, alfa/rank ölçeği, ileri hesap ve birleştirme doğru")
for ad, kw in [("ölçek alfa (rank'a bölünmüyor)", {"olcek_tur": "alfa"}), ("B rastgele başlıyor", {"b_sifir": False}),
               ("temel dondurulmuyor", {"dondur": False}), ("birleştirme temel ağırlığı yerinde değiştiriyor", {"yerinde": True}),
               ("ileri hesapta ölçek unutulmuş", {"ileri_olcek": False})]:
    kontrol(not sozlesme(D.referans_sinifi(**kw)), "hatalı çözüm reddedilmeli: " + ad)
class Adaptorsuz(torch.nn.Module):
    def __init__(self, temel, rank, alfa):
        super().__init__()
        ok_ = isinstance(temel, torch.nn.Linear) and not isinstance(rank, bool) and isinstance(rank, int) \
            and 1 <= rank <= min(temel.in_features, temel.out_features) and not isinstance(alfa, bool) and alfa > 0
        if not ok_:
            raise ValueError("geçersiz")
        self.temel, self.olcek = temel, alfa / rank
        self.A = torch.nn.Parameter(torch.randn(rank, temel.in_features) * 0.01)
        self.B = torch.nn.Parameter(torch.zeros(temel.out_features, rank))
        for p in temel.parameters():
            p.requires_grad_(False)
    def forward(self, x):
        return self.temel(x)
    def birlestir(self):
        return self.temel.weight.detach().clone()
kontrol(not sozlesme(Adaptorsuz), "hatalı çözüm reddedilmeli: adaptör hesaba katılmıyor")
r = {}
if all(sonuclar):
    r = D.deney(Sinif)
    kontrol(r["egitilen_parametre"] == r["beklenen_egitilen"], f"gerçek model: yalnız LoRA parametreleri eğitiliyor ({r['egitilen_parametre']:,})")
    kontrol(abs(r["takinca_hedef_kayip"] - r["once"]["hedef"]) < 1e-4, "adaptör takılınca model davranışı değişmiyor (B=0)")
    kontrol(r["sonra"]["hedef"] < 0.5 * r["once"]["hedef"], f"gerçek eğitim hedef kaybını düşürdü ({r['once']['hedef']:.3f} → {r['sonra']['hedef']:.3f})")
    kontrol(r["temel_agirlik_degismedi"] and r["ortak_model_degismedi"], "temel ağırlıklar eğitim boyunca değişmedi")
    kontrol(r["birlesme_farki"] < 5e-3, f"birleşik ağırlıklı model adaptörlü modelle aynı çıktıyı veriyor (fark {r['birlesme_farki']:.1e})")
yol = ai_lab.kanit_yaz("temel-lora", {
    "kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-temel-10", "model_bilgisi": bilgi,
    "ayarlar": {"sinanan_katman": katman, "rank_alfa": ayarlar, "tolerans": {"birlesme": 5e-3}}, "deney": r})
if r:
    ok(True, f"GERÇEK ÇIKTI ({bilgi['model']}@{bilgi['revizyon'][:8]}): {r['egitilen_parametre']:,}/{r['toplam_parametre']:,} parametre "
             f"(%{100 * r['oran']:.2f}) eğitildi; hedef kayıp {r['once']['hedef']:.2f} → {r['sonra']['hedef']:.4f}, "
             f"ilgisiz metin kaybı {r['once']['kontrol']:.2f} → {r['sonra']['kontrol']:.2f}; "
             f"devam: {r['once']['uretim']!r} → {r['sonra']['uretim']!r}")
```

```solution
import torch
import ai_lab

class LoraDogrusal(torch.nn.Module):
    def __init__(self, temel, rank, alfa):
        super().__init__()
        if not isinstance(temel, torch.nn.Linear):
            raise ValueError("temel bir nn.Linear olmalı")
        if isinstance(rank, bool) or not isinstance(rank, int) or not 1 <= rank <= min(temel.in_features, temel.out_features):
            raise ValueError("rank geçersiz")
        if isinstance(alfa, bool) or not isinstance(alfa, (int, float)) or not alfa > 0:
            raise ValueError("alfa pozitif olmalı")
        self.temel = temel
        for p in temel.parameters():
            p.requires_grad_(False)
        self.A = torch.nn.Parameter(torch.randn(rank, temel.in_features) * 0.01)
        self.B = torch.nn.Parameter(torch.zeros(temel.out_features, rank))
        self.olcek = alfa / rank

    def forward(self, x):
        return self.temel(x) + (x @ self.A.T @ self.B.T) * self.olcek

    def birlestir(self):
        return self.temel.weight.detach() + self.olcek * (self.B @ self.A).detach()

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_10 as deney
    deney.goster(LoraDogrusal)
```

```hint
`B` sıfırla başladığı için `x @ A.T @ B.T` başlangıçta sıfırdır. Birleştirmede `B @ A` biçimi `[çıkış, giriş]` olur, yani `temel.weight` ile aynıdır; toplamı yeni bir tensör olarak döndür (`+=` kullanma).
```
:::
