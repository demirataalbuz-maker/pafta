# PU15 sentetik Windows adli izleri

Bu klasördeki bütün kayıtlar elle üretilmiş, küçük ve sentetiktir. Gerçek bir makineden kanıt toplanmamıştır; hiçbir dosya ham Registry hive, Prefetch, MFT veya LNK değildir.

- `registry.json`: Hive, anahtar/değer alanları ve anahtara ait LastWriteTime için normalize kayıtlar.
- `prefetch.json`: Dosya adı, yürütülebilir ad, yol hash'i, sınırlı son çalıştırma listesi ve run count alanları.
- `mft.json`: `$STANDARD_INFORMATION` ve `$FILE_NAME` MACB zamanları ile `$DATA` resident/nonresident durumu.
- `lnk.json`: LNK hedefi, çalışma dizini, hedefin iç zamanları ve ayrı tutulan dış dosya zamanları.

JSON dosyaları gerçek biçimlerin yalnız ders için seçilmiş alanlarını temsil eder. `sandbox/windows_forensics_lab.py` ham yapıları ayrıştırmaz, canlı Registry'ye veya dosya sistemine tarama yapmaz, ağ/alt süreç kullanmaz ve paket kurmaz. Çelişkili değerler özellikle korunmuştur; bunlar zaman damgası kurcalamasının tek başına kanıtı değildir.
