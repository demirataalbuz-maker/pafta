# GEMINI İYİLEŞTİRME RAPORU — ai-ile-guvenlik-13

**Ders:** `tracks/ai-ile-guvenlik/lessons/ai-ile-guvenlik-13-salt-okunur-kesif-ajani-ve-kapsam-kilidi.md`  
**Başlık:** Salt-Okunur Keşif Ajanı ve Deterministik Kapsam Kilidi  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 87 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 969 kelimeye çıkarıldı.
  - Otonom güvenlik ajanlarında araç çağırma (tool-calling / function-calling) riskleri ve modele serbest araç yürütme yetkisi vermenin tehlikeleri açıklandı.
  - Üç katmanlı deterministik yürütme motoru:
    1. Salt-okunur araç beyaz listesi (tool allowlist) ve hedef kapsam kilidi (scope lock): `dosya_sil`, `komut_calistir` gibi yıkıcı araçların (`yasak_arac`) ve izinli hedefler dışındaki dış ağlara (`kapsam_disi_hedef`) sızıntının engellenmesi.
    2. Döngü kırıcı (circuit breaker) ve adım bütçesi (step budget): Tekrar döngülerinin (`tekrar_dongusu`) ve aşırı adım/kaynak tüketiminin (`butce_asimi`) kesilmesi.
    3. Uçtan uca yürütücü ve triyaj ayrımı (`kesif_ajani_calistir`): İzinli çağrıların yürütülmesi ve güvenlik duvarına takılanların `engellenenler` sözlüğünde denetim izine (audit log) kaydedilmesi.
  - Çıktı nasıl okunur: `calistirilan_idleri`, `engellenenler` ve `durdurma_nedeni` sonuçlarının SOC operasyonlarındaki karşılığı.
  - Saldırgan ne dener: Dolaylı istem enjeksiyonu (indirect prompt injection) ile hedef saptırma (scope escape / SSRF), yıkıcı araç tetikleme ve sonsuz döngü tuzakları (loop traps).
  - Savunma neden kırılır ve sık yapılan geliştirici tuzakları: İstem düzeyinde güvenlik yanılgısı (prompt-level guardrails), `bool` - `int` tip karışıklığı (`isinstance(True, int) == True`), engellenenleri sessizce yutma hatası ve girdi mutasyonu (in-place mutation).
- **Purple Standart Tablosu:** 3 sütunlu standart format eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki sentetik veriler, kalıcılık olmaması ve 4. görevdeki yerel Ollama modeliyle yapılan canlı araç çağırma deneyi açıkça belirtildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: araç ve hedef izin listesini kontrol etmeden her çağrıyı doğrudan onaylıyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: tekrar döngüsünü ve adım bütçesini kontrol etmeden tüm çağrıları çalıştırıyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: kapsam kilidini ve döngü kırıcıyı birleştirmeden boş sonuç döndürüyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `arac_cagrisi_dogrula_referans`, `dongu_kirici_kontrol_referans`, `kesif_ajani_calistir_referans`, `getattr`, `kanit_yaz`, `eval`, `exec` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı yerel Ollama modeli üzerinden araç çağırma ve yürütücü kapsam kilidi başarıyla doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-ile-guvenlik-13:3 [ai-ile-guvenlik/python] uyuşuyor · 1 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-ile-guvenlik-13:4 «1 · Araç çağrısını salt-okunur araç listesi ve hedef kapsamına göre doğrula» 0 mutant, 0 yakalandı
ai-ile-guvenlik-13:5 «2 · Tekrar döngüsünü ve adım bütçesini döngü kırıcı ile denetle» 4 mutant, 4 yakalandı
ai-ile-guvenlik-13:6 «3 · Kapsam kilidi ve döngü kırıcı ile keşif ajanını güvenli çalıştır» 1 mutant, 1 yakalandı
toplam 5 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (wildcard import): `fail → korunuyor`
- Sonda 3 (getattr ile dinamik referans): `fail → korunuyor`

---

## 3. Özet
`ai-ile-guvenlik-13` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 969 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
