# GEMINI İYİLEŞTİRME RAPORU — ai-guvence-10

**Ders:** `tracks/ai-guvence/lessons/ai-guvence-10-refusal-direction-removal-ve-abliteration-olcumu.md`  
**Başlık:** Refusal Direction Removal ve Abliteration Ölçümü  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 81 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 891 kelimeye çıkarıldı.
  - Mekanistik yorumlanabilirlik ve temsil mühendisliği (Representation Engineering; Zou ve ark., 2023; Arditi ve ark., 2024) temelleri incelendi; LLM güvenlik hizalamasında red davranışının (refusal direction) residual stream içinde baskın doğrusal bir yön boyunca kodlandığı açıklandı.
  - Ortogonal projeksiyon matematiği: Yön vektörünün L2 normuna bölünerek birim vektöre ($\mathbf{u} = \mathbf{y} / \|\mathbf{y}\|_2$) dönüştürülmesi, iç çarpım ile skaler izdüşüm hesabı ve $\mathbf{x}_{\text{ablite}} = \mathbf{x} - (\mathbf{x} \cdot \mathbf{u}) \mathbf{u}$ formülüyle aktivasyonun refusal yönüne dik hale getirilmesi.
  - İki eksenli değerlendirme zorunluluğu: Güvenlik değişimi (`ablite - taban`) ve genel yetenek kaybı (`taban - ablite`). Tek başına red azalmasının modelin akıl yürütme ve olgusal tamamlama yeteneğini bozabileceği vurgulandı.
  - TransformerLens ve PyTorch kancaları (forward hooks): `(batch, seq, d_model)` tensorlerinin residual stream üzerinde model ağırlıklarını kalıcı olarak bozmadan dinamik olarak yön kaldırılması.
  - Saldırgan ne dener: Ağırlık seviyesinde sansürsüzleştirme (weight-level uncensoring), hassas katman tespiti (katman 14) ve güvenlik filtresi atlatma.
  - Savunma neden kırılır ve geliştirici tuzakları: Normalizasyonun unutulması, ara adımlarda erken yuvarlama yapılması, güvenlik ve yetenek formüllerindeki işaretlerin karıştırılması.
- **Purple Standart Tablosu:** 3 sütunlu standart format eklendi (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki sentetik veriler, kalıcılık olmaması ve 4. görevdeki PyTorch ve TransformerLens ile yerel Qwen2.5-0.5B-Instruct modeli üzerinde yapılan canlı katman 14 kancası deneyi açıkça belirtildi.

### B. Görünür Fixture ve Setup Blokları
- `tracks/ai-guvence/fixtures/ai-guvence-10/README.md` ve `tracks/ai-guvence/fixtures/ai-guvence-10/veri/abliteration.json` oluşturuldu.
- Görev 1, Görev 2 ve Görev 3'e `sandbox.ai_guvence_veri.hazirla("ai-guvence-10")` çağıran ````setup```` blokları eklendi.
- Görev starter'ları `veri/abliteration.json` dosyasını okuyarak kullanıcıya doğrudan çalıştırılabilir örnek sağladı.

### C. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: vektörü normalize etmeden sabit 1.0 koordinatları döndürür.`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: yön bileşenini çıkarmak yerine aktivasyon vektörünü olduğu gibi döndürür.`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: koşul ayrımı yapmadan sabit sıfır değişim ve kayıp döndürür.`
- **Görev Gerçek Deney:** 3 fonksiyon için de sözleşmeyi bozan kusurlu başlangıç kodları sağlandı.
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
- Canlı yerel PyTorch ve TransformerLens köprüsü üzerinden Qwen2.5-0.5B-Instruct katman 14 refusal yönü kancası ve abliteration karşılaştırma deneyi başarıyla tamamlandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-guvence-10:2 [ai-guvence/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-guvence-10:3 «1 · Yön vektörünü normalize et» 2 mutant, 2 yakalandı
ai-guvence-10:4 «2 · Aktivasyondan yön bileşenini çıkar» 3 mutant, 3 yakalandı
ai-guvence-10:5 «3 · Taban ve ablite koşullarını karşılaştır» 11 mutant, 11 yakalandı
toplam 16 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile dinamik referans): `fail → korunuyor`
- Sonda 3 (importlib ile modül referansı): `fail → korunuyor`

---

## 3. Özet
`ai-guvence-10` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 891 kelimelik derin anlatım, fixture + setup blokları, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
