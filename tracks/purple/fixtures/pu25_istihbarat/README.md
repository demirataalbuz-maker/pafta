# pu25 · Görünür Örnekler

- `ornekler.json` **sentetiktir**: CTID öykünme planı biçiminde elle yazılmış bir plan ayrıntısı ve altı adım. Komut alanları `(komut çıkarıldı)` ile değiştirilmiştir.
- `telemetri.json`: Varsayımsal, izole bir Windows değerlendirme VM'inin hangi tekniği hangi kayıtla görebileceğini anlatan **elle yazılmış** eşleme (`telemetri`) ve test ortamının sınırları (`ortam`). Bu bir ölçüm değil, bir **varsayımdır**; Dalga C'de VM kurulunca ölçülecektir.
- `attack.json` her çalıştırmada çalışma klasörüne kopyalanan MITRE ATT&CK Enterprise 19.2 özetidir.

Setup her Çalıştır/Kontrol Et adımında eksik dosyaları kopyalar; **kalıcılık yoktur**. Son görev `.deps` altındaki, sha256'sı doğrulanmış gerçek CTID APT29 planını yalnız okur; hiçbir komut çalıştırılmaz.
