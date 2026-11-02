# GEMINI İYİLEŞTİRME RAPORU — ai-ile-guvenlik-14

**Ders:** `tracks/ai-ile-guvenlik/lessons/ai-ile-guvenlik-14-yikici-eylemlerde-insan-onayi-ve-imzali-kapi.md`  
**Başlık:** Yıkıcı Eylemlerde İnsan Onayı (HITL) ve İmzalı Görev Kapısı  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 86 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 908 kelimeye çıkarıldı.
  - Güvenlik operasyonlarında olay müdahale (IR) ve SOAR sistemlerinde LLM kullanımı incelendi; `ip_engelle`, `hesap_kapat`, `guvenlik_duvari_kurali_yaz` gibi yıkıcı eylemlerin geri döndürülme maliyeti açıklandı.
  - Basit Boole onayının (`"onaylandi": true`) ölümcül tehlikesi: Parametre değiştirme (parameter tampering) ve şaşkın vekil (confused deputy) zafiyeti; analist saldırgan IP'si için onay verdiğinde modelin halüsinasyon, yarış durumu veya enjeksiyonla hedefi kurumsal ağ geçidiyle değiştirmesi riski detaylandırıldı.
  - Üç adımlı kriptografik HITL kapısı:
    1. Kanonik Görev İmzası (`gorev_imzasi_uret`): İstek kimliği, araç adı ve hedef parametresinin `f"{istek_id}:{arac}:{hedef}"` biçiminde `HMAC-SHA256` ile imzalanması.
    2. HITL Doğrulama Kapısı (`hitl_kapisi_dogrula`): Salt-okunur eylemlerin serbest bırakılması (`"salt_okunur_serbest"`), yıkıcı eylemlerde boş jeton tespiti (`"eksik_onay_jetonu"`) ve `hmac.compare_digest` ile sabit-zamanlı imza doğrulaması (`"imza_uyumsuz"` / `"imzali_onay_gecerli"`).
    3. Müdahale Kuyruğu Yürütücüsü (`mudahale_kuyrugu_yurut`): Yetkili eylemlerin `uygulanan_idleri` listesine, engellenenlerin nedenleriyle birlikte `reddedilenler` sözlüğüne yazılması.
  - Çıktı nasıl okunur: `uygulanan_idleri` ve `reddedilenler` denetim izi.
  - Saldırgan ne dener: Jeton yeniden kullanımı (token replay / cross-request replay), zamanlama saldırıları (timing attacks), onay yorgunluğu (approval fatigue).
  - Savunma neden kırılır ve sık yapılan geliştirici tuzakları: Parametreleri imzaya dahil etmemek, sabit-zamanlı karşılaştırma yapmamak (`==`), boşluk ve tip denetimlerini atlamak.
- **Purple Standart Tablosu:** 3 sütunlu standart format eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki sentetik veriler, kalıcılık olmaması ve 4. görevdeki yerel Ollama modeliyle yapılan canlı HITL kapısı deneyi açıkça belirtildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: hedef ve araç parametrelerini imzaya dahil etmeden boş imza döndürüyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: yıkıcı eylemlerde onay jetonu ve imza doğrulaması yapmadan her isteği doğrudan onaylıyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: tüm istekleri HITL kapısından geçirmeden doğrudan uygulanan listesine alıyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `gorev_imzasi_uret_referans`, `hitl_kapisi_dogrula_referans`, `mudahale_kuyrugu_yurut_referans`, `getattr`, `kanit_yaz`, `eval`, `exec` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı yerel Ollama modeli üzerinden HITL kapısı, HMAC-SHA256 doğrulaması ve hedef değiştirme engeli başarıyla doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-ile-guvenlik-14:3 [ai-ile-guvenlik/python] uyuşuyor · 1 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-ile-guvenlik-14:4 «1 · İstek kimliği, araç ve hedefe bağlı HMAC-SHA256 görev imzası üret» 1 mutant, 1 yakalandı
ai-ile-guvenlik-14:5 «2 · Müdahale isteğini HITL kapısında doğrula» 2 mutant, 2 yakalandı
ai-ile-guvenlik-14:6 «3 · Müdahale kuyruğunu imzalı HITL kapısından geçirerek yürüt» 1 mutant, 1 yakalandı
toplam 4 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (wildcard import): `fail → korunuyor`
- Sonda 3 (getattr ile dinamik referans): `fail → korunuyor`

---

## 3. Özet
`ai-ile-guvenlik-14` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 908 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
