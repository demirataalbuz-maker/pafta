# GEMINI İYİLEŞTİRME RAPORU — ai-guvence-09

**Ders:** `tracks/ai-guvence/lessons/ai-guvence-09-gcg-ve-autodan-ayrik-token-optimizasyonu.md`  
**Başlık:** GCG ve AutoDAN: Ayrık Token Optimizasyonu  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 81 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 890 kelimeye çıkarıldı.
  - Geleneksel sürekli girdi uzayları (görüntü/ses) ile dil modellerinin sonlu, ayrık token uzayları ($V$) arasındaki temel fark açıklandı; sürekli gradyanın doğrudan bir tokene dönüştürülememe sorunu incelendi.
  - GCG (Greedy Coordinate Gradients; Zou ve ark., 2023) algoritması: Gömme matrisi $E$ üzerinden hedef çıktı kaybı $\mathcal{L}$ için birinci derece Taylor açılımı ve $\text{skor}(v) = (e_v - e_i) \cdot \nabla_{e_i} \mathcal{L}$ formülüyle aday tokenların filtrelenmesi.
  - AutoDAN (Zhu ve ark., 2023) algoritması: Genetik arama, mutasyon, çaprazlama ve hiyerarşik optimizasyonla şaşkınlık (perplexity) filtrelerine takılmayan akıcı karşıt istemler türetme prensibi.
  - Arama izi (`arama_izini_ozetle`) ve model transfer analizi (`transfer_ozeti`): En iyi kayıp, kümülatif katı artan sorgu sayıları, model transfer başarı oranı (`basari / deneme`) ve ortalama genel yetenek puanı.
  - Saldırgan ne dener: Evrensel aktarılabilir sonekler (universal adversarial suffixes), otomatik jailbreak ve perplexity gizleme.
  - Savunma neden kırılır ve geliştirici tuzakları: Basit kelime filtrelerinin anlamsız dizileri kaçırması, skor eşitliğinde belirlenimli `(skor, token)` kuralının ihmali, sorgu artışının kontrol edilmemesi, transfer raporunda bool yerine sayı kullanılması.
- **Purple Standart Tablosu:** 3 sütunlu standart format eklendi (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki sentetik veriler, kalıcılık olmaması ve 4. görevdeki PyTorch ve SmolLM2-135M modeliyle yapılan canlı GCG koordinat gradyanı deneyi açıkça belirtildi.

### B. Görünür Fixture ve Setup Blokları
- `tracks/ai-guvence/fixtures/ai-guvence-09/README.md` ve `tracks/ai-guvence/fixtures/ai-guvence-09/veri/optimizasyon.json` oluşturuldu.
- Görev 1, Görev 2 ve Görev 3'e `sandbox.ai_guvence_veri.hazirla("ai-guvence-09")` çağıran ````setup```` blokları eklendi.
- Görev starter'ları `veri/optimizasyon.json` dosyasını okuyarak kullanıcıya doğrudan çalıştırılabilir örnek sağladı.

### C. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: adayları skora göre sıralamadan ilk bütçe kadar elemanı olduğu gibi döndürür.`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: yöntemleri gruplamadan sabit boş liste veya tek kayıt döndürür.`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: transfer oranını ve ortalama yeteneği hesaplamadan sabit sıfır döndürür.`
- **Görev Gerçek Deney:** 3 fonksiyon için de sözleşmeyi kasten bozan kusurlu başlangıç kodları sağlandı.
- 4 starter kodunun hiçbiri boş `return` değildir; sözleşmeyi kasten bozan başlangıç kodlarıdır ve testleri geçmez (`starter: 4`).

### D. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- Wildcard (`*`) importları, `referans` içeren isim/nitelikler, `getattr`, `eval`, `exec` çağrıları engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı yerel PyTorch ve SmolLM2-135M modeli üzerinde embedding gradyanı, backward() çağrısı, aday seçimi ve ileri geçiş kaybı ölçüm deneyi başarıyla tamamlandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-guvence-09:2 [ai-guvence/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-guvence-09:3 «1 · Ayrık adayları bütçeyle seç» 3 mutant, 3 yakalandı
ai-guvence-09:4 «2 · GCG ve AutoDAN arama izlerini özetle» 11 mutant, 11 yakalandı
ai-guvence-09:5 «3 · Transfer başarısını ve yeteneği raporla» 11 mutant, 11 yakalandı
toplam 25 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile dinamik referans): `fail → korunuyor`
- Sonda 3 (importlib ile modül referansı): `fail → korunuyor`

---

## 3. Özet
`ai-guvence-09` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 890 kelimelik derin anlatım, fixture + setup blokları, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
