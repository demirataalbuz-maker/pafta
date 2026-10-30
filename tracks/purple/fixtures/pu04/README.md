# PU04 sentetik bellek dışa aktarımları

Bu altı küçük CSV/JSON dosyası yalnız PU04 dersi ve testleri içindir. Gerçek bir
bellek imajından üretilmemişlerdir; alan biçimleri Volatility 3 ve MemProcFS
çıktılarından örneklenmiş, değerler elle yazılmıştır. IP adresleri RFC 5737
belgeleme bloklarındadır. Dosyalarda imaj, parola, bellek dökümü, kimlik bilgisi,
çalıştırılabilir dosya veya zararlı kod yoktur.

- `volatility_pslist.csv`: iki aracın ortak süreçleri ve aynı PID'nin daha eski bir
  süreçte kullanılmış olması.
- `volatility_netscan.csv`, `memprocfs_net.json`: yinelenen bağlantılar, eski PID
  örneği ve süreç tablosunda bulunmayan PID 9999.
- `volatility_malfind.csv`, `memprocfs_vads.json`: RWX + özel + dosyasız adaylar;
  salt okunur/çalıştırılabilir, paylaşılan ve dosya destekli karşı örnekler.

RWX bellek ve dış ağ bağlantısı bağımsız olarak zararlı kanıtı değildir. 900 PID'li
`svchost.exe` özellikle yanlış-pozitif kontrolüdür: bellek bölgesi aday olarak kalır ama
bağlantı gerekçesi almaz. 9999 ise yanlış ilişkilendirme kontrolüdür: süreç adı
uydurulmamalıdır.

Gerçek inceleme için `sandbox/memory_lab.py` araçları yalnız açık onayla ve kullanıcı
tarafından sağlanan yerel imajla çalıştırır. Eksik araç/imaj `atlandi`, kapalı gerçek
araç yolu `gereksinim-yok` döndürür; bunlar başarılı analiz anlamına gelmez.
