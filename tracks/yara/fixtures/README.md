# ELF / .NET eğitim korpusu

`formats.json`, 13 zararsız derleyici çıktısının base64 baytlarını, SHA256
özetini, kaynak metnini ve kullanılan araç sürümünü içerir. Derlenen kod
çalıştırılmaz. Ders testleri `sandbox/yara_format_fixtures.py` ile korpusu
okur; gerçek libyara motoru baytları ayrıştırır. Öğrencide gcc, WSL veya
.NET SDK kurulu olması gerekmez; YARA yolunun mevcut bağımlılığı yeterlidir.

- ELF: Kali gcc 16.2.0; 255/256/257 bayt `.pafta` bölümü, başka bölüm adı,
  yazılabilir bölüm, 32 bit nesne ve 64 bit dinamik nesne tanıkları.
- .NET: SDK 8.0.425; net8.0 kitaplık, assembly major sürümleri 1/2/3/4,
  farklı assembly adı ve aynı kısa sınıf adının farklı namespace tanığı.
  Her kitaplıkta Marker yanında Decoy sınıfı vardır; dizinin tek elemanlı
  olduğunu varsayan kuralları ayırt eder.

Yazar için yeniden üretim:

```powershell
python -X utf8 tools/build_yara_format_fixtures.py
python -X utf8 tools/test_yara_formats.py
python -X utf8 tools/validate.py --yol yara
```

Üretim kurulu WSL dağıtımını `PAFTA_WSL_DISTRO` ortam değişkeninden okur
(varsayılan `kali-linux`); Linux çalışma dizini `/tmp` altında oluşturulur.
Windows tarafında kurulu .NET 8 SDK kullanılır. NuGet kaynakları kapalıdır;
eksik hedefleme paketi varsa işlem hata verir. Paket kurulum komutu yoktur.
Yeni derleyici sürümleri baytları değiştirebilir; yeniden üretim sonrası
derslerdeki base64 girdilerini ve gerçek tahmin çıktısını da güncelle.
