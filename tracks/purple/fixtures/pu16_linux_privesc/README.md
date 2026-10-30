# PU16 sentetik Linux yetki kayıtları

`lab.json`, CPTS düzeyinde karar analizi için elle hazırlanmış kurgusal `find`, `stat`, `id`, `getcap`, `sudo -l`, `crontab`, systemd ve `PATH` çıktılarının yapılandırılmış karşılığıdır.

Bu kayıtlar canlı bir sistemden toplanmamıştır. Ders ve yardımcı modül SUID/SUDO istismarı yapmaz; komut çalıştırmaz; setuid, capability, sahiplik, izin, sudo, cron veya systemd yapılandırması değiştirmez.

Metin kanıtı alanları kararın dayanağını görünür tutar. Yapılandırılmış alanlar, metin ayrıştırma yerine kullanıcı/grup üyeliği, yazılabilirlik, komut argümanı, tetiklenme durumu ve capability ad alanı gibi sınırların sınanmasını sağlar.
