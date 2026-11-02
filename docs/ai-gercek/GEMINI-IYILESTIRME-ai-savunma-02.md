# GEMINI İYİLEŞTİRME RAPORU — ai-savunma-02

**Ders:** `tracks/ai-savunma/lessons/ai-savunma-02-birlesik-ai-risk-kontrol-cerceveleri.md`  
**Başlık:** Birleşik AI Risk ve Kontrol Çerçeveleri  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 80 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 894 kelimeye çıkarıldı.
  - Kurumsal yapay zekâ güvenliğinde farklı disiplinlerin (CISO, Red Team, Uyumluluk) odak noktaları açıklandı.
  - Üç temel çerçevenin rolleri netleştirildi:
    1. OWASP Top 10 for LLM: "Ne yanlış gidebilir?" (Risk boyutu: `LLM01`–`LLM10`).
    2. MITRE ATLAS: "Saldırgan bunu nasıl yapar?" (Saldırı tekniği boyutu: `AML.T` + 4 rakam, ör. `AML.T0051`, `AML.T0054`).
    3. NIST AI RMF: "Yönetişim hangi aşamadadır?" (Süreç boyutu: `GOVERN`, `MAP`, `MEASURE`, `MANAGE`).
  - Kontrol sahipliği ve matris mimarisi: Her kontrolün (`K-`) açık bir sahibi (`sahip`) ve ilişkili riskin NIST işlevine uygunluğu. Kontrolsüz risklerin (`kontrolsuz`) raporda açıkça gösterilmesinin sahte güvenlik yanılsamasını önleme rolü.
  - Test kanıtları ve güvence durum önceliği: `kontrolsuz` > `kritik` > `eksik_kanit` > `kapsali`. "Doğrulanmamış kontrol, mevcut olmayan kontroldür" ilkesi.
  - Saldırgan taktikleri: Kâğıt üzerinde uyum (paper compliance) açıkları, sorumluluk boşlukları (ownership gaps) ve canary/sistem prompt sızıntıları.
  - Geliştirici tuzakları: Kontrol varlığını kanıt sanmak, çoğunluk kuralıyla kritik riskleri gizlemek, `uygulanmadi` testine kanıt yazmak ve in-place liste mutasyonları.
- **Purple Standart Tablosu:** 3 sütunlu standart format eklendi (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki sentetik veriler, kalıcılık olmaması ve 4. görevdeki yerel Ollama modeliyle yapılan canlı canary sızıntı testi açıkça belirtildi.

### B. Görünür Fixture ve Setup Blokları
- `tracks/ai-savunma/fixtures/ai-savunma-02/README.md` ve `tracks/ai-savunma/fixtures/ai-savunma-02/veri/cerceve.json` oluşturuldu.
- Görev 1, Görev 2 ve Görev 3'e `sandbox.ai_savunma_veri.hazirla("ai-savunma-02")` çağıran ````setup```` blokları eklendi.
- Görev starter'ları `veri/cerceve.json` dosyasını okuyarak kullanıcıya doğrudan çalıştırılabilir örnek sağladı.

### C. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: şema doğrulaması yapmaz, ATLAS ve NIST listelerini alfabetik sıralamaz ve OWASP sırasını bozabilir.`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: kontrolleri risklerle eşleştirmez, kontrolsüz risk listesini boş döner ve sıralama yapmaz.`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: durum önceliklerini dikkate almaz, tüm riskleri kapsalı raporlar ve özet sayaçlarını sıfırlar.`
- **Görev Gerçek Deney:** `# KUSURLU BAŞLANGIÇ KODU: durum önceliklerini dikkate almaz, tüm riskleri kapsalı raporlar.`
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
- Canlı yerel Ollama modeli üzerinden canary enjeksiyonu ve sızıntı güvence deneyi başarıyla tamamlandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-savunma-02:1 [ai-savunma/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-savunma-02:2 «1 · Çoklu çerçeve eşlemelerini normalize et» 8 mutant, 8 yakalandı
ai-savunma-02:4 «2 · Sahipleri ve NIST işlevleri doğrulanmış kontrol matrisi kur» 9 mutant, 9 yakalandı
ai-savunma-02:6 «3 · Test kanıtlarından risk güvence durumunu üret» 14 mutant, 14 yakalandı
toplam 31 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (wildcard import): `error → korunuyor`
- Sonda 2 (doğrudan referans ithali): `error → korunuyor`
- Sonda 3 (getattr ile dinamik referans): `error → korunuyor`

---

## 3. Özet
`ai-savunma-02` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 894 kelimelik derin anlatım, fixture + setup blokları, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
