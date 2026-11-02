# GEMINI İYİLEŞTİRME RAPORU — ai-guvence-08

**Ders:** `tracks/ai-guvence/lessons/ai-guvence-08-pgd-ile-saldiri-gucu-egrileri.md`  
**Başlık:** PGD ile Saldırı Gücü Eğrileri  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 89 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 932 kelimeye çıkarıldı.
  - Projected Gradient Descent (PGD) saldırısının temelleri, tek adımlı FGSM'e kıyasla kayıp yüzeyindeki yerel vadileri ve doğrusal olmayan dalgalanmaları aşabilme kabiliyeti ayrıntılandırıldı.
  - Aracın altında ne olur: 5 adımlı PGD değerlendirme döngüsü (girdi/bütçe doğrulama, yinelemeli gradyan tırmanışı, $[0, 1]$ geçerli girdi uzayı ve $[x_0 - \varepsilon, x_0 + \varepsilon]$ hiper-küpü çift kademeli projeksiyonu, adım bazlı $L_\infty$ iz takibi, epsilon ve adım sayısı boyunca model doğruluk eğrisini tabana göre çıkarma).
  - Çıktı nasıl okunur: Adım 0 taban doğruluğu (temiz model performansı), doğruluk kaybı (accuracy drop), doyum noktası (saturation) ve maksimum kayıp eşikleri.
  - Saldırgan ne dener: Yerel minimumları aşmak için küçük $\alpha$ adımlarıyla çoklu yineleme, $x_0$ etrafında rastgele başlatma (random restarts), kritik epsilon eşik tespiti.
  - Savunma neden kırılır: Gradyan maskelemesi (gradient masking / obfuscation) tuzakları, savunmanın yerel sırtlar oluşturmasına rağmen PGD'nin çok adımlı yapısıyla bunu aşması, tek metrik ($L_\infty$) yanılgısı ve diğer normlara taşınamama riski.
  - Sık yapılan geliştirici tuzakları: Projeksiyon sınırlarını güncel nokta yerine mutlaka ilk temiz örnek $x_0$ üzerinden hesaplama zorunluluğu, $[0, 1]$ aralığına kırpma ile bütçe projeksiyonunun sıralı/birlikte işletilmesi, `bool` tipinin `int` alt sınıfı olması tuzağı, taban adımı ($t=0$, $L_\infty=0$) eksikliği, float yuvarlama sapmaları için $1e-9$ toleransı.
- **Purple Standart Tablosu:** 3 sütunlu standart tablo eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** Standart `> [!NOT]` bloğunda sentetik veriler, temiz kopya yeniden yazımı ve canlı PyTorch MLP autograd deneyinin kapsamı açıkça ifade edildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: alpha <= epsilon şartını denetlemeden doğrudan girdi sözlüğünü döndürüyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: adımları uygulamadan ve projekte etmeden başlangıç vektörünü döndürüyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: taban doğruluğundan kayıp hesaplamadan ve özet üretmeden döndürüyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `referans`, `pgd_ayari_dogrula_referans`, `pgd_izini_uret_referans`, `pgd_egri_raporu_referans`, `getattr`, `kanit_yaz`, `eval`, `exec` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı `torch` autograd ve 64-32-4 MLP sınıflandırıcısı üzerinde çok adımlı PGD ve saldırı gücü eğrisi hatasız doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-guvence-08:2 [ai-guvence/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-guvence-08:3 «1 · PGD ayarını doğrula» 9 mutant, 9 yakalandı
ai-guvence-08:4 «2 · Çok adımlı PGD izini üret» 25 mutant, 25 yakalandı
ai-guvence-08:5 «3 · Epsilon-adım eğrilerini özetle» 14 mutant, 14 yakalandı
toplam 48 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile referans alma): `fail → korunuyor`
- Sonda 3 (wildcard import ile referans alma): `fail → korunuyor`

---

## 3. Özet
`ai-guvence-08` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 932 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
