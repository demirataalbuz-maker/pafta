# ai-saldiri-03 iyileştirme teslimi

Codex kendi uygulama kontrollerini yaptı; denetim ve puan claude-opus'a aittir.

İş emrinin tamamı uygulandı: ilk anlatımda gerçek araç/dersteki kullanım/ölçüm sınırı tablosu ve NOT; fixtures/ai-saldiri-03 altında README ve veri/hiyerarsi.json; ilk üç görevin setup bloğunda mevcut ai_saldiri_veri.hazirla; dosyayı okuyan ve ham veriyi/sonucu yazdıran üç gerçekçi kusurlu starter. Dosya sentetik örnektir, gerçek model çıktısı değildir; geçici çalışma kopyası sonraki çalıştırmada yenilenir. Gizli testler bu dosyayı ezberlemeye dayanmaz.

İlk görev rolün içerikten yükseltilemeyeceğini ve geçersiz rol türünü; ikinci görev eylem/kapsam ayrımını ve geçersiz alanları; üçüncü görev en yüksek rol, aynı rolde yasak önceliği, son kazanan kural izi ve belirsiz durumu sınar. İlk mutasyon 28 değişimden birini geçirdi: karar işlevinin göreli otorite sıralamasında 3→4 eşdeğerdi. İlk log korundu. Karar çözümünde açık rol sırası kullanıldı; bağlamın sözleşmesindeki sayısal 3/2/1/0 otoriteler korunur. Son mutasyon 7+11+6=24, sıfır geçen. Doğru test zayıflatılmadı.

Gerçek deney testinde referans importu, takma ad/yıldız importu ve kanit_yaz kopyaları guard ile durur. Kabul bütün kontrollerin all sonucudur; bütün model çağrılarının hatasız olması ve beklenen toplam adedin tamamlanması gerekir. Modelin yüksek uyum göstermesi geçme şartı değildir. Saf öğrenci sözleşmeleri başarısızsa deney koşulmaz ve artık gerçek çağrı kanıtı da yazılmaz. Bu son ayrım gerçek ekran testinde bulunan yanıltıcı etiketi giderir; engine/web değiştirilmedi.

Dört zorunlu kontrol (.ai-venv/Scripts/python.exe -X utf8):
- tools/validate.py ai-saldiri-03: TEMİZ, 10 kontrol (örnek1, tahmin1, çözüm4, starter4); son izole PAFTA_DATA Desktop/pafta-s03-kabul-son-20261030.
- docs/denetim/araclar/tahmin.py . ai-saldiri-03: 1 tahmin, sıfır şüpheli.
- kirp_gercek.py ile oluşturulmuş Desktop/pafta-mutasyon-s03-v2-20261030 kopyasında mutasyon.py --en-cok 1000 ai-saldiri-03: 24 mutant, sıfır geçen. Bu kopyadan sonraki tek ders değişikliği son gerçek-test bloğunun kanıt-yazma koşuludur; ilk üç görev aynıdır.
- kopya_sonda.py ai-saldiri ai-saldiri-03 "from sandbox.ai_gercek_ai_saldiri_03 import referans_karar as karar_ver, referans_ozet as uyum_ozeti": fail, korunuyor. kopya-sonucu.json guard mesajını ve kabul yokluğunu ayrıca doğrular.

Ek olumsuz çözümler (boş, sabit, format dışını paydadan atan) reddedildi. Eksik modele yalnız kendi çocuk süreç ortamında erişilemeyen loopback portu ve olmayan exe ile bakıldı: hata, kabul yok. İlk üç görev Run çıktısı normal runner/setup üzerinden dosyayı gösterdi. Kanıtlar outputs/iyilestirme-codex-ai-saldiri-03 altında.

Gerçek ders ekranı kabulü bu derste yapıldı: kendi 127.0.0.1:18800 sunucum, izole outputs/iyilestirme-codex-20261030/ui-data. Başlangıç Check 7/9 ile reddedildi ve 'Gerçek deney kanıtı yok' gösterdi. Görünür Çözümü göster → Tezgaha al → Kontrol et akışı 13/13 geçti. UI kanıtı saldiri-hiyerarsi-1793362466474.json: iki model, 28 çağrı, sıfır taşıma hatası. Qwen kontrol1.0/çatışma0.8; Llama kontrol0.25/çatışma0.7. Llama kontrolü tam olmadığı için bu sonuç hiyerarşi uyumunun kanıtı sayılmaz. Çalıştır 14 gerçek çağrı ve ham yanıtları gösterdi; saldiri-hiyerarsi-calistir-1793362490344.json kabul=false, yalnız deneme olarak etiketlendi. Birinci dosyalı görevin Run çıktısı ayrıca UI'da görüldü; ikinci/üçüncü görevin ayrı görsel kabulü yapılmadı, CLI doğrulandı.

Developer rolü bu Ollama deneyinde [developer] etiketli system mesajına eşlenir; doğal API developer rolü ölçülmüş sayılmaz. Sonuçlar bu vaka/ayar/yerel modellere aittir; genel model güvenliği puanı değildir. Önceki gerçek tekrarlar değişken çıktı verdi; sabit yanıt metni beklenmez.

Yalnız kendi test sunucum kapatıldı. Kullanıcının Ollama sunucusu/WSL/Docker kapatılmadı. İndirme/kurulum, commit/push veya puan yazımı yapılmadı. Önceki derslerde raporlanan görsel kabul eksikleri bu dersin testiyle kapanmış sayılmaz.
