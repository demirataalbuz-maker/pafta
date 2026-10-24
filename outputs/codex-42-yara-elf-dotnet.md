# Madde 42 · YARA ELF / .NET teslimi

Kod commit'i: `89b0fd1`. Başlama kaydı: `5363e74`.

YR21 ve YR22, Başpehlivan rütbesine eklendi. Yol 22 ders, 6 rütbe;
yeni dersler toplam 2 gerçek tahmin ve 4 kural yazma görevi içerir.

- YR21: ELF makine/tür ayrımı; x86-64 ET_REL ile x86-32 ve ET_DYN
  tanıklarını ayırma; bölüm adı, boyutu ve yazma bayrağı.
- YR22: native PE / managed ayrımı; assembly adı, kapsayıcı major sürüm
  aralığı; namespace dahil sınıfın tam adı ve sınıf dizisinde dolaşma.
- 13 örnek Kali gcc 16.2.0 ve .NET SDK 8.0.425 ile gerçek kaynaklardan
  derlendi. Hiçbir örnek çalıştırılmadı. Base64 baytlar, kaynaklar, araç
  bilgisi ve SHA256 özetleri `tracks/yara/fixtures/formats.json` içindedir.
- Korpus üretici `tools/build_yara_format_fixtures.py`; öğrenci için
  derleyici kurulumu gerekmez. NuGet kaynakları kapalı; paket kurulmadı.
- Gerçek libyara ELF/dotnet modülleri kullanılır; davranış taklidi yoktur.

## Doğrulama

- Windows: `python -X utf8 tools/validate.py --yol yara` →
  **22 ders, 134 kontrol; TEMİZ**.
- Git Bash: aynı YARA doğrulaması → **22 ders, 134 kontrol; TEMİZ**.
- `python -X utf8 tools/test_yara_formats.py` → **4 test temiz**;
  17 semantik mutasyonun tamamı `fail` ile reddedildi. Değiştirilen kuralın
  derleme hatası vermesi başarı sayılmadı; gerçek olumsuz kontrol arandı.
- `python -X utf8 tools/test_yara_runtime.py` → **15 test temiz**.
- Yeni tahminler: YR21 `Nesne`, `Esik`; YR22 `PE`, `Managed`.
- Tam uygulama doğrulamaları Windows ve Git Bash'te başlatıldı; aynı
  bilgisayarda denetçinin ayrı tam taraması da çalıştığından ek yükü
  azaltmak için kendi iki genel taramam tamamlanmadan durduruldu.
  **Bütün uygulama için temiz sonucu iddia edilmiyor.** Yukarıdaki
  tamamlanmış sonuçlar YARA yolunu ve motorunu kapsar.

Sınır tanıkları: ELF 255/256/257 bayt; .NET major 1/2/3/4; aynı kısa sınıf
adının farklı namespace'i; sınıf döngüsünü any yerine all yapan bozuk kural
için Decoy sınıfı; yanlış dosya türü ve sıradan metin girdileri.

## Sınırlar

Örnekler eğitim korpusudur; bilinen malware ailesi tespiti iddiası yoktur.
Dosya veya assembly çalıştırma/yükleme yapılmaz. Dersler metadata üzerinden
kural yazmayı öğretir; bölüm/sınıf adından davranış kanıtı çıkarılmaz.
Üretici yeniden çalıştırıldığında derleyici sürümü baytları değiştirebilir;
derslerdeki base64 girdileri ve gerçek tahmin çıktıları da kontrol edilmelidir.

`DENETIM.md` ve `ASAMA2.md` değiştirilmedi. Push yapılmadı.
