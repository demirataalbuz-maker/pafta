# GEMINI İYİLEŞTİRME RAPORU — ai-savunma-17

**Ders:** `tracks/ai-savunma/lessons/ai-savunma-17-guvenli-belge-alma-ve-icerik-ayristirma.md`  
**Başlık:** Güvenli Belge Alma ve İçerik Ayrıştırma  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 79 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 897 kelimeye çıkarıldı.
  - RAG sistemlerinde Dolaylı Prompt Enjeksiyonu (Indirect Prompt Injection) tehdidi ve LLM'lerin veri ile talimatı ayırt edememe doğası detaylandırıldı.
  - "Modelim akıllıdır" varsayımının geçersizliği; savunmanın ilk kalesinin model değil belge alma ve ayrıştırma katmanı olduğu açıklandı.
  - Fail-closed politika tasarımı: `aktif_icerik: "reddet"`, `gizli_talimat: "karantina"`, pozitif boyut/blok sınırları.
  - Belge kabul denetimi ve çoklu ihlal raporlaması: Ad-tür uzantı uyuşmazlığı (`ad`), izinli türler (`tur`), boyut/blok sınırları (`boyut`, `blok`), aktif içerik (`aktif`).
  - Blok ayrıştırma, normalizasyon ve karantina: CRLF/CR -> LF dönüşümü, kontrol karakteri denetimi, `script`/`makro` ve `baglanti` bloklarının tecridi, `casefold()` ile bilinen enjeksiyon kalıplarının tespiti ve karantinada metnin mutlak boşaltılması (`metin: ""`).
  - Saldırgan taktikleri: Çift/sahte uzantılar, NUL baytı enjeksiyonları, büyük/küçük harf ve sıfır genişlikli boşluk manipülasyonları.
  - Geliştirici tuzakları: Modele güvenip ham metni bağlama beslemek, karantina kararına rağmen metni taşımak, çoklu ihlallerde ilk hatada durup diğerlerini gizlemek, in-place liste mutasyonları.
- **Purple Standart Tablosu:** 3 sütunlu standart format eklendi (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki sentetik veriler, kalıcılık olmaması ve 4. görevdeki yerel Ollama modeliyle yapılan canlı özetleme sırasında enjeksiyon karantinası deneyi açıkça belirtildi.

### B. Görünür Fixture ve Setup Blokları
- `tracks/ai-savunma/fixtures/ai-savunma-17/README.md` ve `tracks/ai-savunma/fixtures/ai-savunma-17/veri/belgeler.json` oluşturuldu.
- Görev 1, Görev 2 ve Görev 3'e `sandbox.ai_savunma_veri.hazirla("ai-savunma-17")` çağıran ````setup```` blokları eklendi.
- Görev starter'ları `veri/belgeler.json` dosyasını okuyarak kullanıcıya doğrudan çalıştırılabilir örnek sağladı.

### C. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: şema doğrulaması yapmaz, aktif içerik ve gizli talimat kurallarını fail-closed doğrulamaz.`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: tüm belgeleri doğrudan kabul eder, ihlal nedenlerini denetlemez ve sıralama yapmaz.`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: aktif içerik ve gizli talimatları karantinaya almaz, metni temizlemeden doğrudan geçirir.`
- **Görev Gerçek Deney:** `# KUSURLU BAŞLANGIÇ KODU: aktif içerik ve gizli talimatları karantinaya almaz, tüm blokları güvenli sayar.`
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
- Canlı yerel Ollama modeli üzerinden güvenli metin özetleme ve enjeksiyon karantinası deneyi başarıyla tamamlandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-savunma-17:2 [ai-savunma/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-savunma-17:3 «1 · Fail-closed belge alma politikasını doğrula» 11 mutant, 11 yakalandı
ai-savunma-17:5 «2 · Belge alma kararlarını raporla» 29 mutant, 29 yakalandı
ai-savunma-17:7 «3 · Ayrıştırılmış blokları güvenli metne ayıkla» 16 mutant, 16 yakalandı
toplam 56 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (wildcard import): `error → korunuyor`
- Sonda 2 (doğrudan referans ithali): `error → korunuyor`
- Sonda 3 (getattr ile dinamik referans): `error → korunuyor`

---

## 3. Özet
`ai-savunma-17` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 897 kelimelik derin anlatım, fixture + setup blokları, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
