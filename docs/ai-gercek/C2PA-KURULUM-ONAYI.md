# C2PA / watermark dersi — indirme planı

2026-11-04. DURUM: Kullanıcıya ayrı onay sorusu gönderildi, yanıt bekleniyor. Henüz indirilmedi. Ders tamam veya PASS değildir. Plan: plan-savunma-6; yeni ders numarası gerçek dosya yazılırken rezerve edilecek.

Resmî kaynak https://github.com/contentauth/c2patool/releases/tag/v0.28.4 . Windows arşivi v0.28.4-x86_64-pc-windows-msvc.zip,10.998.290bayt,ücretsiz. Upstream GitHub asset SHA256:00e5bcfef95fcf913cc3d67825d7d50ea1eb1180c7fdbef746c9ce3b65e272f1. Dosya https://github.com/contentauth/c2patool/releases/download/v0.28.4/v0.28.4-x86_64-pc-windows-msvc.zip . Yalnız .deps altında ayrı klasöre hash doğrulanarak açılacak; PATH/Windowskurulumu veya mevcutvenv değişmeyecek. Ek paket/model/baseimage indirilmez.

Amaç: kendi sentetik PNG dosyasında gerçek C2PA manifest imzalama/okuma,imza bütünlüğü ile signer trust ayrımı,metadata kaldırma ve piksel değişikliği sonuçlarını ölçmek. Test anahtarı/kimliği yalnızyerel,üretimgüveni diye sunulmayacak. ÜcretliCA/hesap/dışkimlikservisi yok. MevcutPillow vecryptography kullanılabilir. Watermark eğitim örneği C2PA ile aynı güvenlik özelliği diye anlatılmayacak; algılama/dönüştürme sınırları ölçülecek. Onay gelene kadar canlı C2PA kabulü yapılamaz; gerçek gibi sunulan fixture veya sahte doğrulama yok.

Kabul: açılabilir öğrenciPNG/manifest,3kusurlu görev,tahmin,gerçek CLI/UI/Run,kopya/yanlışçözüm/mutasyon/bağımlılıkyok testleri. Ham stdout/stderr,exitcode,aracsürümü,dosyaSHA,ayar/girdi/cihaz kayıtları. Kendi süreçleri kapanır; kullanıcıdosyası/kurulum silinmez. Denetim ve puan Opus'ta.
