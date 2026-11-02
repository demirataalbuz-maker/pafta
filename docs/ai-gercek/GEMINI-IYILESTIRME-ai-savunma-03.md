# GEMINI İYİLEŞTİRME RAPORU — ai-savunma-03

**Ders:** `tracks/ai-savunma/lessons/ai-savunma-03-katmanli-savunma-referans-mimarisi.md`  
**Başlık:** Katmanlı Savunma Referans Mimarisi  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 83 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 893 kelimeye çıkarıldı.
  - LLM tabanlı sistemlerde tek bir kalkan/guardrail yanılgısı ve Savunma Derinliği (Defense-in-Depth) ile Sıfır Güven ilkeleri temellendirildi.
  - Beş katmanın (`girdi`, `model`, `cikti`, `arac`, `veri`) mimari sorumlulukları ve barındırdığı kontroller (`sema`, `boyut`, `icerik`, `sistem_promptu`, `model_sabitleme`, `cikti_semasi`, `dlp`, `yetki`, `onay`, `sandbox`, `kiraci`, `provenance`, `sorgu`) açıklandı.
  - Fail-closed prensibi: `kaldi` veya `hata` durumlarının kesinlikle `reddet` üretmesi, eksik gözlemlerde `eksik` kararı verilmesi ve yalnızca tüm kontroller başarılıysa `izin` çıkması detaylandırıldı.
  - Saldırgan taktikleri: Şaşkın vekil saldırılarıyla model üzerinden araç katmanını gasp etme, arıza enjeksiyonuyla filtreleri çökerterek fail-open geçişi zorlama, tek hata noktalarını (SPOF) hedef alma.
  - Geliştirici tuzakları: İstisnalarda sessiz geçişe izin verme (`pass` -> `izin`), mimari sıra ile alfabetik sıra karmaşası, in-place liste mutasyonları.
- **Purple Standart Tablosu:** 3 sütunlu standart format eklendi (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki sentetik veriler, kalıcılık olmaması ve 4. görevdeki yerel Ollama modeliyle yapılan canlı çıktı şeması fail-closed doğrulama deneyi açıkça belirtildi.

### B. Görünür Fixture ve Setup Blokları
- `tracks/ai-savunma/fixtures/ai-savunma-03/README.md` ve `tracks/ai-savunma/fixtures/ai-savunma-03/veri/savunma.json` oluşturuldu.
- Görev 1, Görev 2 ve Görev 3'e `sandbox.ai_savunma_veri.hazirla("ai-savunma-03")` çağıran ````setup```` blokları eklendi.
- Görev starter'ları `veri/savunma.json` dosyasını okuyarak kullanıcıya doğrudan çalıştırılabilir örnek sağladı.

### C. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: katmanları mimari sıraya koymaz, kontrolleri alfabetik sıralamaz ve şema doğrulaması yapmaz.`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: fail-closed kuralını çiğner, hata durumlarında izin verir ve neden detayını üretmez.`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: arızalı katmanları tek nokta olarak tespit etmez ve tüm senaryoları yedekli raporlar.`
- **Görev Gerçek Deney:** `# KUSURLU BAŞLANGIÇ KODU: fail-closed kuralını çiğner, her durumda izin verir.`
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
- Canlı yerel Ollama modeli üzerinden çıktı şeması guardrail deneyi ve fail-closed kararı başarıyla tamamlandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-savunma-03:1 [ai-savunma/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-savunma-03:2 «1 · Beş katmanlı mimariyi ve bağımsız kontrolleri doğrula» 3 mutant, 3 yakalandı
ai-savunma-03:4 «2 · Kontrol gözlemlerinden fail-closed istek kararı üret» 7 mutant, 7 yakalandı
ai-savunma-03:6 «3 · Kontrol arızası senaryolarında tek hata noktalarını bul» 9 mutant, 9 yakalandı
toplam 19 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (wildcard import): `error → korunuyor`
- Sonda 2 (doğrudan referans ithali): `error → korunuyor`
- Sonda 3 (getattr ile dinamik referans): `error → korunuyor`

---

## 3. Özet
`ai-savunma-03` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 893 kelimelik derin anlatım, fixture + setup blokları, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
