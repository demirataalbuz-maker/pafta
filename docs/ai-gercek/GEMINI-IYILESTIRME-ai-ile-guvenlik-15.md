# GEMINI İYİLEŞTİRME RAPORU — ai-ile-guvenlik-15

**Ders:** `tracks/ai-ile-guvenlik/lessons/ai-ile-guvenlik-15-cok-ajanli-mavi-mor-takim-is-akisi.md`  
**Başlık:** Çok Ajanlı Mavi/Mor Takım İş Akışı (Toplayıcı → Analist → Doğrulayıcı)  
**Yazar:** gemini  
**Tarih:** 2026-11-01  
**Mevcut Puan:** 89 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 770 kelimenin üzerine çıkarıldı.
  - Çok ajanlı güvenlik mimarilerinde görev ayrımı (`Separation of Duties - SoD`) ilkesi ayrıntılandırıldı.
  - Aracın altında ne olur (Toplayıcı, Analist, Hakem katmanlarının işlem döngüsü).
  - Saldırgan ne dener (Ajanlar arası istem enjeksiyonu / `Cross-Agent Prompt Injection`, sahte hipotez tetikleme).
  - Savunma neden kırılır (deterministik hakem yerine LLM onaylatma tuzağı, kanıt indeksi çapraz sorgusu eksikliği).
  - Sık yapılan geliştirici tuzakları (Python'da `bool` tipinin `int` alt sınıfı olması, yerinde nesne değiştirme / in-place mutation, boş dayanak kanıtı listeleri).
- **Purple Standart Tablosu:** 3 sütunlu standart tablo eklendi (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki `.json` dosyalarının sentetikliği, kurulum bloğunun geçiciliği ve gerçek deneyde yerel model (`qwen3`) ile çok ajanlı zincirin nasıl çalıştırıldığı açıklandı.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1 (Toplayıcı):** `# KUSURLU BAŞLANGIÇ KODU: Kanıt kayıtlarını kopyalamadan yerinde değiştiriyor ve ajanlar arası enjeksiyon kalıbını temizlemiyor!`
- **Görev 2 (Hakem):** `# KUSURLU BAŞLANGIÇ KODU: Kanıtların varlığını ve IP uyumunu denetlemeden yalnız komut çıkış koduna bakarak onaylıyor!`
- **Görev 3 (Uçtan Uca Hat):** `# KUSURLU BAŞLANGIÇ KODU: Hakem doğrulama kapısını işletmeden tüm hipotezleri onaylananlar listesine ekliyor ve temizlenen kanıt sayısını aktarmıyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı ve her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Görev Gerçek Deney test bloğuna `ast.walk(ast.parse(src))` analizi entegre edildi.
- `referans`, `toplayici_paketi_hazirla_referans`, `hakem_hipotez_dogrula_referans`, `cok_ajanli_hatti_yurut_referans`, `getattr`, `kanit_yaz` ve `*` (wildcard) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- 1 tahmin adımı, 4 çözüm ve 4 starter tam olarak doğrulandı. Canlı yerel model çağrısı (`qwen3:4b-instruct-2507-q4_K_M`) GPU kipinde başarıyla tamamlandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-ile-guvenlik-15:4 [ai-ile-guvenlik/python] uyuşuyor · 2 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-ile-guvenlik-15:5 «1 · Toplayıcı ajanın kanıt paketini hazırla ve ajanlar arası enjeksiyonu temizle» 1 mutant, 1 yakalandı
ai-ile-guvenlik-15:6 «2 · Analist hipotezini bağımsız hakem kurallarıyla doğrula» 3 mutant, 3 yakalandı
ai-ile-guvenlik-15:7 «3 · Çok ajanlı (Toplayıcı → Analist → Doğrulayıcı) hattı uçtan uca yürüt» 1 mutant, 1 yakalandı
toplam 5 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile referans alma): `fail → korunuyor`
- Sonda 3 (wildcard import ile referans alma): `fail → korunuyor`

---

## 3. Özet
`ai-ile-guvenlik-15` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 770+ kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
