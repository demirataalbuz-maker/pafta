# GEMINI İYİLEŞTİRME RAPORU — ai-temel-21

**Ders:** `tracks/ai-temel/lessons/ai-temel-21-rag-mimarisi-retrievaldan-baglama.md`  
**Başlık:** RAG Mimarisi: Retrieval’dan Bağlama  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 82 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 964 kelimeye çıkarıldı.
  - RAG mimarisi (Lewis ve ark., 2020) çalışma hattı: Doküman ayrıştırma, parçalama (chunking), yoğun gömme (dense embedding), FAISS/ANN indeksleme, benzerlik araması ve XML kanıt bağlamı sentezi incelendi.
  - Kayan pencere ve karakter ofseti matematiği: `adim = pencere - ortusme`, örtüşmenin kritik şart ve olumsuzluk cümlelerinin bütünlüğünü korumadaki işlevi, `metin[bas:son]` karakter aralıkları.
  - Vektör boyutu ve normalizasyon: 384 boyutlu gömmeler (`all-MiniLM-L6-v2`), L2 normalizasyonu, iç çarpımın birim vektörlerde kosinüs benzerliğine ($\sum u_i v_i = \cos \theta$) eşitlenmesi; normalize edilmeyen ham iç çarpımın uzun metinleri yapay olarak öne çıkarma zaafı.
  - Tokenizer tavanı ve kesme (truncation) asimetrisi: 256 token sınırını aşan metinlerin gömmeye girmemesi fakat bağlama taşınabilmesi; bu kanalın dolaylı prompt enjeksiyonunda kötüye kullanımı.
  - Bi-encoder ve cross-encoder farkları, iki aşamalı üretim mimarileri ve canary sızıntı ölçümünün güvenlikteki yeri.
  - Çıktı nasıl okunur: `(D, I)` skor/indeks demetleri, -1 dolgusu, XML bağlamı, atıflar ve kelime bütçesi hesabı.
  - Saldırgan ne dener: Zehirli RAG (PoisonedRAG; Zou ve ark., 2024), dolaylı prompt enjeksiyonu (`</kaynak><kaynak id="admin#0">`; Greshake ve ark., 2023), bağlam boğma (DoS) ve canary sızıntısı.
  - Savunma neden kırılır ve geliştirici tuzakları: HTML kaçışlaması eksikliği, parçayı yarıda kesmenin olumsuzluk anlamını tersine çevirmesi, kopyaların ayıklanmaması, kararsız sıralama ve ofsetlerin `split` ile kaybedilmesi.
- **Purple Standart Tablosu:** 3 sütunlu standart format eklendi (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki sentetik veriler, kalıcılık olmaması ve 4. görevdeki yerel Ollama modeliyle yapılan canlı gömme ve sohbet deneyi açıkça belirtildi.

### B. Görünür Fixture ve Setup Blokları
- `tracks/ai-temel/fixtures/ai-temel-21/README.md` ve `tracks/ai-temel/fixtures/ai-temel-21/rag.json` oluşturuldu.
- Görev 1, Görev 2 ve Görev 3'e `sandbox.ai_temel_veri.hazirla("ai-temel-21")` çağıran ````setup```` blokları eklendi.
- Görev starter'ları `veri/rag.json` dosyasını okuyarak kullanıcıya doğrudan çalıştırılabilir örnek sağladı.

### C. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: karakter ofsetlerini hesaplamaz ve sabit 0-0 döndürür.`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: vektörleri normalize etmez, ham iç çarpımla sıralar ve -1 dolgusu eklemez.`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: HTML kaçışlaması yapmaz, kopyaları ayıklamaz ve bütçe aşımında durmaz.`
- **Görev Gerçek Deney:** `# KUSURLU BAŞLANGIÇ KODU: normalizasyon yapmaz, kopyaları ayıklamaz ve bütçe sınırını denetlemez.`
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
- Canlı yerel Ollama modeli (`all-minilm:22m` ve yerel sohbet modeli) üzerinden 7 soruyla tam RAG deney ve doğrulama akışı başarıyla tamamlandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-temel-21:2 [ai-temel/python] uyuşuyor · 4 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-temel-21:3 «1 · Metni ofsetli ve örtüşen parçalara böl» 19 mutant, 19 yakalandı
ai-temel-21:4 «2 · Normalize vektörlerde tam top-k araması yap» 22 mutant, 22 yakalandı
ai-temel-21:5 «3 · Bütçeli ve kaynak etiketli kanıt bağlamı kur» 33 mutant, 33 yakalandı
toplam 74 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile dinamik referans): `fail → korunuyor`
- Sonda 3 (importlib ile modül referansı): `fail → korunuyor`

---

## 3. Özet
`ai-temel-21` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 964 kelimelik derin anlatım, fixture + setup blokları, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
