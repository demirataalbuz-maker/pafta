# 37 · KQ22 gerçek Kusto kabulü

27 Ekim 2026 · Codex

Zaman penceresi sorguları gerçek Kusto’da çalışır. Account Name/UPNSuffix ve IP Address mapping’ine bağlanabilecek gerçek çıktı sütunlarını üreten görev eklendi. Kullanıcıda Sentinel çalışma alanı bulunmadığından gerçek Test with current data/Review portal kabulü yapılmadı; bu eksik açık kalır.

Microsoft Kusto Emulator ücretsiz yerel sorgu motorudur; Sentinel/Defender servisi değildir. Kullanıcı indirme/kurulumunu onayladı. Resmî dokümanda önerilen stable etiketi MCR'de bulunamadı; latest indirildi ve digest ile sabitlendi: mcr.microsoft.com/azuredataexplorer/kustainer-linux@sha256:093af777e866d79abfaa2cd1f6e10f9509e6eec6ebd229aecb87c9609f26f1e9. Gerçek ProductVersion: 2026.10.26.2230-2643-1299172-master. Konteyner yalnız 127.0.0.1:18780 HTTP açar; host klasörü bağlanmaz, müşteri verisi alınmaz. Kimlik doğrulaması/HTTPS yok; üretim kurulumuyla aynı sayılmaz. Benchmark yapılmadı.

Öğrenci KQL'i native engine tarafından değerlendirilir. Eski SQL hazırlığı yalnız typed datatable/let verisini üretir; sorgu çevirisi değildir. Tür uyarlaması ve datetime görünümü README'de açık; sayılar/dynamic/bool native kalır. _GetWatchlist yalnız fixture listelerini sorgulayan yerel yardımcıdır, Sentinel API hizmeti diye sunulmaz.

Kabul: bu madde için **10 davranış bozan mutant reddedildi, 0 geçen**. Birleşik tools/test_kusto_native.py toplam 10 referans ve 37 mutantı gerçek motorla ölçer; native syntax/yanlış OutputSchema/yönetim komutu reddi ayrıca kontrol edilir. KQL tam yol Windows ve Git Bash: **24 ders, 249 kontrol TEMİZ**. Kaynak/kurulum/port ve destek sınırları derste yazıldı. Bütün uygulama bu teslimde yeniden test edilmedi.

Öz değerlendirme: **89/100** (B). Bu bağımsız denetim notu değildir. Eski bağımsız puan korunur; panel başka ajanın 92/105–108 değişikliklerini içerdiğinden ortak dosya değiştirilmedi. Ayrı panel önerisi kaydedildi. 37 tamamlandı sayılmadı; gerçek Sentinel portal kabulü bekliyor.

Kaynaklar kontrol edildi:
- https://learn.microsoft.com/en-us/azure/data-explorer/kusto-emulator-overview
- https://learn.microsoft.com/en-us/azure/data-explorer/kusto-emulator-install
- https://learn.microsoft.com/en-us/kusto/query/mv-apply-operator
- https://learn.microsoft.com/en-us/kusto/query/bag-unpack-plugin
- https://learn.microsoft.com/en-us/azure/sentinel/map-data-fields-to-entities
- https://learn.microsoft.com/en-us/azure/sentinel/entities-reference
- https://learn.microsoft.com/en-us/azure/sentinel/detect-threats-custom
