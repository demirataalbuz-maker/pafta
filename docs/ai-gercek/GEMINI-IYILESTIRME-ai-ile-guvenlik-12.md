# GEMINI İYİLEŞTİRME RAPORU — ai-ile-guvenlik-12

**Ders:** `tracks/ai-ile-guvenlik/lessons/ai-ile-guvenlik-12-log-enjeksiyonuna-dayanikli-soc-triyaj-hatti.md`  
**Başlık:** Log Enjeksiyonuna Dayanıklı SOC Triyaj Hattı  
**Yazar:** gemini  
**Tarih:** 2026-11-02  
**Mevcut Puan:** 87 → **Hedef:** ≥ 90 (A Notu)  
**Denetçi:** claude-opus (bağımsız denetçi)

---

## 1. Yapılan İyileştirmeler (İş Emri & Standart Maddeleri)

### A. Giriş Anlatımı & Purple Standardı
- **Kelime Sayısı ve Teknik Derinlik:** Giriş anlatımı 944 kelimeye çıkarıldı.
  - SOC ve SIEM operasyonlarında LLM kullanımı, log kayıtlarının homojen telemetri olmadığı ve saldırganın kontrolündeki serbest metin alanları (`kullanici`, `yol`, `user_agent`) incelendi.
  - Üç katmanlı dayanıklı SOC savunma hattı:
    1. Enjeksiyon taraması ve alan karantinası (`log_enjeksiyonu_tara`): Enjeksiyon kalıplarının (`"talimatlari unut"`, `"ignore previous"`, `"sistem:"` vb.) taranması, eşleşen alanların `"[KARANTINA_METNI]"` ile maskelenmesi ve deterministik telemetri alanlarının (`olay_id`, `kaynak_ip`, `alarm_seviyesi`) korunması.
    2. Veri ayrımlı istem paketleme (`veri_ayrimli_istem_kur`): Karantinadan geçen kayıtların JSON formatında `<veri_blogu>...</veri_blogu>` etiketleri arasına sınırlandırılması.
    3. Deterministik alarm bastırma kilidi (`triyaj_karari_denetle`): `alarm_seviyesi == "yuksek"` veya `zehirli == True` olan olayların zorunlu alarm kabul edilmesi, modelin bastırma girişimlerinin (`"temiz"`) engellenip `engellenen_bastirmalar` ve `nihai_alarmlar` listelerine yazılması.
  - Çıktı nasıl okunur: `nihai_alarmlar`, `engellenen_bastirmalar` ve `zehirli_olaylar` analizi.
  - Saldırgan ne dener: Alarm bastırma ile gizlenme (stealth via suppression), biçim ve ayrıştırıcı çökertme, karantina atlatma denemeleri.
  - Savunma neden kırılır ve sık yapılan geliştirici tuzakları: Yalnızca kelime filtresine (heuristic) güvenmek, zehirleme girişimini normal saymak, adli bilişim kayıtlarında girdi mutasyonu (in-place mutation).
- **Purple Standart Tablosu:** 3 sütunlu standart format eksiksiz korundu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`).
- **Sentetik Sınır Uyarısı (`[!NOT]`):** İlk 3 görevdeki sentetik veriler, kalıcılık olmaması ve 4. görevdeki yerel Ollama modeliyle yapılan canlı SOC triyaj deneyi açıkça belirtildi.

### B. Kusurlu Başlangıç Kodları (KUSURLU BAŞLANGIÇ KODU)
- **Görev 1:** `# KUSURLU BAŞLANGIÇ KODU: serbest metin alanlarındaki enjeksiyon kalıplarını taramadan doğrudan kaydı temiz kabul ediyor!`
- **Görev 2:** `# KUSURLU BAŞLANGIÇ KODU: ham kayıtları karantinaya almadan ve <veri_blogu> etiketi olmadan birleştiriyor!`
- **Görev 3:** `# KUSURLU BAŞLANGIÇ KODU: modelin 'temiz' kararını deterministik olarak denetlemeden doğrudan kabul ediyor!`
- **Görev Gerçek Deney:** 3 fonksiyon için de kuralları ihlal eden gerçekçi kusurlu başlangıç kodları sağlandı; boş `return {}` bırakılmadı. Her starter testi geçemeyecek şekilde kurgulandı.

### C. AST Tabanlı Kopya Koruması
- Gerçek deney test adımına `ast.walk(ast.parse(src))` analizi eklendi.
- `log_enjeksiyonu_tara_referans`, `veri_ayrimli_istem_kur_referans`, `triyaj_karari_denetle_referans`, `getattr`, `kanit_yaz`, `eval`, `exec` ve wildcard (`*`) ithalleri engellendi.

---

## 2. Dört Zorunlu Kontrol Sonuçları

### 1) Validate (Tam Kontrol)
```
1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}
TEMİZ
```
- Canlı yerel Ollama modeli üzerinden log enjeksiyonu karantinası ve alarm bastırma engeli başarıyla doğrulandı.

### 2) Tahmin Denetimi (`tahmin.py`)
```
ai-ile-guvenlik-12:3 [ai-ile-guvenlik/python] uyuşuyor · 1 satır
1 tahmin, 0 şüpheli
```

### 3) Mutasyon Testi (`mutasyon.py`)
```
ai-ile-guvenlik-12:4 «1 · Güvenilmez log alanlarında dolaylı istem enjeksiyonunu tara ve karantinaya al» 3 mutant, 3 yakalandı
ai-ile-guvenlik-12:5 «2 · Karantinaya alınmış kayıtlarla veri ayrımlı SOC istemi kur» 1 mutant, 1 yakalandı
ai-ile-guvenlik-12:6 «3 · Modelin triyaj kararlarını deterministik alarm kapısıyla denetle» 5 mutant, 5 yakalandı
toplam 9 mutant, 0 geçen
```

### 4) Kopya Sondası (`kopya_sonda.py`)
- Sonda 1 (doğrudan referans ithali): `fail → korunuyor`
- Sonda 2 (wildcard import): `fail → korunuyor`
- Sonda 3 (getattr ile dinamik referans): `fail → korunuyor`

---

## 3. Özet
`ai-ile-guvenlik-12` dersi iş emrindeki tüm gereksinimleri (Purple tablosu, `[!NOT]`, 944 kelimelik derin anlatım, 4 kusurlu starter, AST kopya koruması) eksiksiz karşılamaktadır ve 4 denetim kontrolünün tamamını başarıyla geçmiştir. Bağımsız denetçi `claude-opus` incelemesine hazırdır.
