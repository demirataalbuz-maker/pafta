# GEMINI İYİLEŞTİRME RAPORU — ai-guvence-11

**Ders:** `tracks/ai-guvence/lessons/ai-guvence-11-veri-kokeni-ve-supheli-kayit-profili.md`  
**Başlık:** Veri Kökeni ve Şüpheli Kayıt Profili  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 89 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 719 kelimeye derinleştirildi.
  - Veri kökeni (data provenance / lineage) kavramı, eğitim setine sızabilecek yetkisiz ve sentetik veri kirliliğinin siber güvenlikteki önemi ayrıntılandırıldı.
  - Aracın altında ne olur: 3 adımlı doğrulama döngüsü (kriptografik hash/HMAC doğrulama, referans dağılım ile gelen küme arasındaki sapmayı Toplam Varyasyon Uzaklığı - TVD ile ölçme, şüpheli/yetim kayıtları profilleme).
  - Çıktı nasıl okunur: Kategori bazlı frekans farkları, TVD skoru ($TVD \in [0, 1]$), şüpheli oran paydası (tüm geçerli/toplam kayıt sayısı üzerinden hesaplama) ve kaynak bazlı anomali dağılımı.
  - Saldırgan ne dener: Kriptografik doğrulama atlatma, veri enjeksiyonu (`data poisoning`), dağılımı referansa uydurarak gizlenme (`stealth distribution matching`), kimliği belirsiz veya sahte kaynak etiketleri enjekte etme.
  - Savunma neden kırılır: `hashlib.sha256` doğrulamalarında ham byte dönüşüm hataları, float yuvarlama sapmaları (`1e-6` toleransı), kategori kümesinde olmayan beklenmeyen etiketlerin sessizce yutulması.
  - Sık yapılan geliştirici tuzakları: TVD toplamında $\frac{1}{2}$ katsayısının unutulması, referans sözlükte olmayan kategorilerin paya eklenmemesi, oran hesabında paydanın sadece şüpheliler olarak alınıp `1.0` çıkması hatası, deterministik sıralama (`sorted(categories)`) yapılmaması.
- **Purple Standart Tablosu:** 3 sütunlu standart tablo eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** Standart `> [!NOT]` bloğunda sentetik veri sınırları, SHA-256 bütünlük kontrolü ve deterministik dağılım analizinin pratik kapsamı vurgulandı.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: eksik alanları denetlemiyor ve geçersiz hash'leri de geçerli sayıyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: TVD formülündeki 0.5 katsayısını unutuyor ve referansta olmayan kategorileri atlıyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: oran paydasını toplam yerine şüpheli sayısına bölüyor ve kaynak sayımını yanlış yapıyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `referans`, `kayit_kokeni_dogrula_referans`, `dagilim_sapmasi_referans`, `supheli_kayit_profili_referans`, `getattr`, `kanit_yaz`, `eval`, `exec` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Tüm starter ve solution adımları ile gerçek deney adımı hatasız doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-guvence-11:3 [ai-guvence/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-guvence-11:4 «1 · Kayıt kökenini doğrula» 16 mutant, 16 yakalandı
ai-guvence-11:5 «2 · Dağılım sapmasını ölç» 6 mutant, 6 yakalandı
ai-guvence-11:6 «3 · Şüpheli kayıt profili üret» 21 mutant, 21 yakalandı
toplam 43 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile referans alma): `fail → korunuyor`
- Sonda 3 (wildcard import ile referans alma): `fail → korunuyor`

---

## 3. Özet
`ai-guvence-11` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 719 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
