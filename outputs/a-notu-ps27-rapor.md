# 14 · Gerçek FilterXml ve ToXml

27 Ekim 2026 · Codex

PS27'ye gerçek Get-WinEvent -FilterXml yazma görevi eklendi. EventID ve dahil Level eşiği, Oldest sırası, tek/çok/boş JSON listesi, adsız EventData alanları, Event namespace'i ve bozuk dosya hatasının eşleşme yoktan ayrımı sınanıyor. System ve EventData değerleri gerçek EventLogRecord.ToXml çıktısından namespace'li XPath ile çıkarılıyor. PS28'in mevcut 4104 okuma/parça birleştirme görevleri korunuyor; genel ham XML okuma köprüsü PS27'de kapanıyor.

Gerçek Windows PowerShell 5.1 üzerinde iki dosya yolu davranışı ölçüldü: FilterXml Path içinde file:// gerekir; XML doğru kaçırılsa da & içeren dosya adı query invalid üretir (%26 da çözmez). Ders bunu gizlemez. Kaynak, çalışma klasöründe GUID adlı EVTX kopyasıyla sorgulanır; finally içinde olay nesneleri Dispose edilir ve yalnız bu kopya silinir. Başarı, eşleşme yok ve bozuk dosya yollarının hepsinde temizlik ölçülür. Çalışma klasörü yolunun kendisi & içermemeli; native okuyucunun bu sınırı açıkça yazıldı. Orijinal kaynak ve canlı sistem kanalları değiştirilmez.

- Windows ve Git Bash: PS27/PS28 2 ders, 16 kontrol TEMİZ.
- `tools/test_powershell_filterxml.py`: gerçek referans geçti; 11 yanlış çözüm reddedildi, 0 geçen. Fail ve çalışma zamanı ÇıkışKodu/error JSON kanıtında ayrıdır.
- Sınanan mutantlar: eşit Level ucunu dışlama, AND/OR, sıra, EventID 0/65535 ve Level 0/5 uçları, yanlış namespace, Data kaybı, bozuk dosyayı gizleme, çalışma kopyasını sızdırma.
- Yeni paket kurulmadı; UTF-8/LF.

Öz değerlendirme: test 24, kapsam 24, derinlik 22, gerçeklik 15, yol 9 = 94/100 (A). Önceki bağımsız 87/100 korunur; bağımsız yeniden denetim yapılmadı. Bu genel Windows/EVTX kusursuzluğu iddiası değildir.
