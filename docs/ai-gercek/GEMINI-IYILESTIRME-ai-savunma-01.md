# GEMINI İYİLEŞTİRME RAPORU — ai-savunma-01

**Ders:** `tracks/ai-savunma/lessons/ai-savunma-01-yerel-llm-saldiri-yuzeyi-guven-sinirlari.md`  
**Başlık:** Yerel LLM Saldırı Yüzeyi ve Güven Sınırları  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 81 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 949 kelimeye çıkarıldı.
  - Yerel LLM kurulumlarında "localhost güvenlidir" yanılgısı ve Sıfır Güven (Zero Trust) ilkesi detaylandırıldı; fiziksel yakınlığın bir güvenlik sınırı teşkil etmediği açıklandı.
  - Güven bölgeleri (`dis`, `uygulama`, `model`, `arac`, `veri`) mimari rolleriyle tanımlandı; modelin istatistiksel ve olasılıksal yapısı nedeniyle asla güvenilir bir karar verici olamayacağı vurgulandı.
  - Yönlü bağlantılar ve sınır geçişi matematiği: Her akış bir `(kaynak, hedef, kanal)` üçlüsüdür; `bolgeler[kaynak] != bolgeler[hedef]` koşulu mutlak sınır geçişini belirler.
  - Saldırgan ne dener: Şaşkın vekil (confused deputy), dolaylı prompt enjeksiyonuyla model üzerinden araç tetikleme (`model -> arac`), bölge atlama (zone hopping), şema manipülasyonu ve yetkisiz veri erişimi.
  - Savunma neden kırılır ve geliştirici tuzakları: Akış yönünü karıştırmak (`api -> model` ile `model -> api` farkı), aynı bölge akışlarına kontrol atayarak sahte güvenlik algısı üretmek, kontrolsüz geçiş sayısını sıfırlamamak, girdileri yerinde değiştirip sözleşmeyi bozmak.
- **Purple Standart Tablosu:** 3 sütunlu standart format eklendi (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki sentetik veriler, kalıcılık olmaması ve 4. görevdeki yerel Ollama modeliyle yapılan canlı model->araç etkileşim deneyi açıkça belirtildi.

### B. Görünür Fixture ve Setup Blokları
- `tracks/ai-savunma/fixtures/ai-savunma-01/README.md` ve `tracks/ai-savunma/fixtures/ai-savunma-01/veri/mimari.json` oluşturuldu.
- Görev 1, Görev 2 ve Görev 3'e `sandbox.ai_savunma_veri.hazirla("ai-savunma-01")` çağıran ````setup```` blokları eklendi.
- Görev starter'ları `veri/mimari.json` dosyasını okuyarak kullanıcıya doğrudan çalıştırılabilir örnek sağladı.

### C. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: tüm bileşenleri ayrım gözetmeksizin uygulama bölgesine atar ve sıralama yapmaz.`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: bölge kontrolü yapmadan tüm bağlantıları sınır geçişi yok (False) olarak işaretler.`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: kontrolleri geçişlerle eşleştirmeden sabit sıfır kontrolsüz geçiş raporlar.`
- **Görev Gerçek Deney:** `# KUSURLU BAŞLANGIÇ KODU: bölgeleri karşılaştırmadan tüm canlı bağlantıları sınır geçişi yok (False) sayar.`
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
- Canlı yerel Ollama modeli üzerinden canlı araç çağırma (`topla`, `carp`) ve model→araç güven sınırı geçiş deneyi başarıyla tamamlandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-savunma-01:1 [ai-savunma/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-savunma-01:2 «1 · Bileşen envanterini güven bölgeleriyle normalize et» 5 mutant, 5 yakalandı
ai-savunma-01:4 «2 · Yönlü bağlantılardan güven sınırı geçişlerini çıkar» 6 mutant, 6 yakalandı
ai-savunma-01:6 «3 · Sınır geçişlerinin kontrol kapsamını hesapla» 8 mutant, 8 yakalandı
toplam 19 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile dinamik referans): `fail → korunuyor`
- Sonda 3 (importlib ile modül referansı): `fail → korunuyor`

---

## 3. Özet
`ai-savunma-01` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 949 kelimelik derin anlatım, fixture + setup blokları, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
