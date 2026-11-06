# Multimodal savunma — OCR kurulum onayı

Durum güncellemesi (2026-11-04): KULLANICI ONAYLADI ve KURULDU. Paket/index ağ planı39.756.840bayt,ek Docker katmanı128.336.723bayt. ImageIDsha256:d54c568dc43a4add16eb38cd9e6c1187a1904192bd14170ae9f5bb3790e45ed9. Tesseract5.3.0-2,English/osd; yeni taban imajı veya Python paketi yok. Gerçek paket/sürüm/binarySHA ve parent-image kaydı outputs/ocr38-kurulum/kurulum.json. Aşağıdaki onay-bekliyor paragrafı onay öncesi tarihsel plandır.

Durum: ONAY BEKLİYOR. Henüz paket indirilmedi veya kurulum yapılmadı. Dockerfile yalnız hazırlanmıştır. Kullanıcının SmolVLM onayı bu kurulumu kapsamaz.

Atanan iş: plan-savunma-7 (OCR/ses guardrail), hedef ders ai-savunma-38. Mevcut Windows PATH/.deps ve ilgili Docker imajlarında Tesseract bulunamadı; kapalı kullanıcı Kali dağıtımı başlatılmadı. Pillow, yerel Qwen2.5VL, Qwen3 ve faster-whisper-small zaten var. Yeni ASR/LLM modeli indirme planı yok.

Öneri: Resmî Debian Bookworm deposundan tesseract-ocr5.3.0-2,English dil verisi ve gerekli Debian kitaplıkları. Kaynak: https://packages.debian.org/bookworm/tesseract-ocr ve onun resmî deb.debian.org/security.debian.org depoları. Tesseract Apache2.0,ücretsiz;kitaplıkların kendi paket lisansları dpkg/copyright ile kaydedilir. Bu Debian paket sürümüdür;en yeni upstreamTesseract sürümü olduğu söylenmez.

Yaklaşık toplam ağ indirmesi: paket indeksleri ve bağımlılıklarla100MBbütçe. Ek Docker katmanı yaklaşık150–250MB;kesinaptboyut/kurulanpaket/sürümler/parentimageID/imageID gerçek kurulum çıktısında kaydedilecek. Önce apt planının gerçek boyutu kontrol edilecek;bütçe aşılırsa indirme yapılmadan tekrar onay istenecek. Yeni taban imajı çekilmez;yereldeki pafta-ai-s51:mlflow-2.2.1 yalnız başlangıç dosya sistemi. MLflow servisi çalıştırılmaz. Windows veya.ai-venv/.ai-araclar paketleri değiştirilmez.

Somut taslak: .deps/ocr38-build/Dockerfile. Sadece türetilmiş pafta-ocr38:tesseract-5.3.0-2 imajı üretilecek. Çalışırken networknone,saltokunurroot,UID10001,capdropall,no-new-privileges,tmpfs/tmp,bellek/PID sınırı;hostmount/port/socket yok. PNGstdin→Tesseractstdout;yalnız sentetik görseller. Her OCR çağrısının sürümü,inputhash/stdout/stderr/exitcode ve kendi container temizliği kaydedilir. Kullanıcı süreçleri/WSL/Docker Desktop kapatılmaz.

Amaç: Gerçek OCR + mevcut gerçek ASR'dan gelen güvenilmeyen metni yerel ajan akışına sokup yetkisiz dosya/araç etkisini engellemek;meşru görev ve sahte pozitifleri ayrıca ölçmek. Bir policy sözlüğünü kontrol etmek tek başına kabul sayılmayacak. Bu kurulum onayı başka paket/model/baseimage/dışservis kullanımını kapsamaz.
