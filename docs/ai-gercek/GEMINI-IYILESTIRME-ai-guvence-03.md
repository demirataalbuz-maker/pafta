# GEMINI İYİLEŞTİRME RAPORU — ai-guvence-03

**Ders:** `tracks/ai-guvence/lessons/ai-guvence-03-tehdit-modelinden-deney-sorusuna.md`  
**Başlık:** Tehdit Modelinden Deney Sorusuna  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 89 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 887 kelimeye çıkarıldı.
  - Yapay zeka sistemlerinde soyut tehdit iddialarını somut tehdit kartlarına ve oradan matematiksel olarak ölçülebilir ampirik deney sorularına dönüştürme gereksinimi ayrıntılandırıldı.
  - MITRE ATLAS ve OWASP ML Top 10 çerçevesinde aktör, varlık ve varsayım eşlemeleri açıklandı.
  - Aracın altında ne olur: 4 adımlı hipotez değerlendirme döngüsü (tehdit kartı şeması ve izinli kategorilerin doğrulanması, kategori-ölçüt uyumuna dayalı deney sorusu üretimi, birden fazla bağımsız rastgelelik tohumuyla elde edilen taban/deney ölçümlerinin yönlü fark $\Delta$ hesabı ve tüm tekrarların eşiği aşmasını şart koşan katı karar mekanizması).
  - Çıktı nasıl okunur: Karar metni, ortalama delta etki büyüklüğü ve tekrara göre sıralı bulgular.
  - Saldırgan ne dener: Varyans ve tohum manipülasyonu ile kararsız saldırılar tasarlama, metrik maskeleme (genel doğruluğu yüksek tutup hedef alt kümede F1/ASR bozma), eşik altı mikro enjeksiyonlar.
  - Savunma neden kırılır: Kategori-ölçüt uyumsuzluğu (evasion'ı sızıntıyla, gizliliği FPR ile ölçme hatası), ortalama yanılgısı (flaw of averages), yön tanımlama karışıklığı.
  - Sık yapılan geliştirici tuzakları: Azalışta `taban - deney` yerine `deney - taban` yazarak negatif delta üretme, yuvarlanmış değerlerle karar verip kayan nokta sapmalarına düşme, soru metni format uyumsuzluğu, Python'da `bool` tipinin `int` alt sınıfı olması tuzağı.
- **Purple Standart Tablosu:** 3 sütunlu standart tablo eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** Standart `> [!NOT]` bloğunda sentetik veriler, temiz kopya yeniden yazımı ve canlı 3 tekrarlı `LogisticRegression` zehirleme deneyinin kapsamı açıkça ifade edildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: kategori ve metin kurallarını denetlemeden girdi sözlüğünü döndürüyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: kategori-ölçüt uyumunu denetlemiyor ve eşiği 6 ondalık basamakla biçimlendirmiyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: yalnız ilk ölçümün farkına bakıp tüm tekrarları kontrol etmiyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `referans`, `tehdit_karti_dogrula_referans`, `deney_sorusu_uret_referans`, `deney_sorusunu_degerlendir_referans`, `getattr`, `kanit_yaz`, `eval`, `exec` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı 3 tekrarlı temiz ve zehirli `LogisticRegression` modeli üzerinde ASR artış hipotezi hatasız doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-guvence-03:2 [ai-guvence/python] uyuşuyor · 3 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-guvence-03:3 «1 · Tehdit kartını doğrula» 6 mutant, 6 yakalandı
ai-guvence-03:4 «2 · Ölçülebilir deney sorusu üret» 11 mutant, 11 yakalandı
ai-guvence-03:5 «3 · Deney sorusunu tekrarlı ölçümlerle değerlendir» 20 mutant, 20 yakalandı
toplam 37 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (getattr ile referans alma): `fail → korunuyor`
- Sonda 3 (wildcard import ile referans alma): `fail → korunuyor`

---

## 3. Özet
`ai-guvence-03` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 887 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
