# ai-guvence-33 iyileştirme teslimi

Codex düzeltti; claude-opus denetimi bekleniyor. Puan verilmedi.

Değişenler: tracks/ai-guvence/lessons/ai-guvence-33-red-team-metodolojisi-ve-tekrarlanabilir-degerlendirme.md; tracks/ai-guvence/fixtures/ai-guvence-33/{README.md,veri/kapsam.json,veri/bulgular.json}; sandbox/ai_gercek_ai_guvence_33.py. Ortak engine/web davranışı değişmedi; yeni paket/model indirme veya kurulum yapılmadı. Commit/push yok.

İlk anlatım başına gerçek biçim/sentetik örnek/sınır tablosu ve NOT eklendi. Üç görev mevcut hazirla/setup ile görünür JSON okur ve Çalıştır çıktısında ham değerleri/sonuçları gösterir. Dosyalar elle yazılmış sentetik örnek, canlı kayıt değildir. Çalışma kopyası geçici; sonraki çalıştırmada yenilenir, kalıcılık iddia edilmez. Başlangıçlar artık gerçekçi kusurlu kapsam/şiddet/birleştirme uygulamalarıdır ve hepsi reddedilir. Gizli testler dosyadan bağımsızdır.

Etki × erişim anlatım çelişkisi, uygulanan etki + erişim kuralına göre düzeltildi. Puanlama öğretim amaçlıdır; evrensel güvenlik şiddeti standardı değildir. Tek koşunun kendi koşuluna karşı örnek olabileceği, fakat genel başarı oranını kanıtlamadığı açıklandı. Bu dersin tekrarlanabilirlik alanı yalnız bool kararların tutarlılığıdır; tam metinlerin eşitliği veya cihazlar arası yeniden üretilebilirlik değildir. Mevcut probe işaret-arama değerlendiricisi korunur ve sınırlılığı açıkça anlatılır: beklenen dizinin yanıtta bulunması tam anlamsal doğruluk kanıtı değildir. Genel model güvenliği iddiası yapılmaz.

Sınır testleri hedef/yasak için yüz öğeyi ve yüz bir öğeyi, izinlerin geçersiz tiplerini, şiddetin bütün kombinasyonlarını ve bozuk türlerini, bin bulgu sınırını, tüm komşu şiddetlerin sırasını ve girdi değişmezliğini kapsar. Bulgu şiddetinde liste/None gibi hashlenemeyen girdiler artık TypeError yerine sözleşmedeki ValueError ile reddedilir. Referans ordinal RANK aynı sırayı enumerate ile kurar. İzin eylemlerinin en çok yirmi olması ve dört izin türünden yinelenmesiz seçilmesi şartları birlikte en fazla dört geçerli öğe verir; doğrulayıcı üst sınırı len(IZIN) kullanır, hiçbir geçerli girdi dışlanmaz. Böylece ulaşılmaz yirmi sınırındaki eşdeğer sabit mutantı kaldırılır. Mevcut doğru testler zayıflatılmaz.

Gerçek testte ImportFrom takma ad/yıldız dahil referans/kanit_yaz koruması ve ihlalde stop eklenir. Sözleşme eşiğin sıfır/bir sınırları, NaN/sonsuzluk, bin/bin bir koşu ve yuvarlanmamış oranla eşik kararını da sınar. Gerçek deneyin mevcut istem/tohum/sıcaklık/tekrar sayısı ve probe ölçütü korunur. Modül her gerçek çağrının tam yanıtını, tohumunu, ayarlarını, süre/hata durumunu kaydeder; eski kısa örnek alanları da korunur. Teknik hata hâlâ eski kosular alanında False olarak yer alabilir ama cagrilar içinde ayrı hata kaydı vardır ve Kontrol bütün on beş çağrı hatasız değilse kabul vermez. Modelin probe'u geçememesi kabulü bozmaz, ölçülen bulgudur. Kabul mevcut ve ek kontrollerin all sonucudur. Tam deney Kontrol/Run kanıtına eklenir; Run kabul=false kalır.

Dört kontrol .ai-venv/Scripts/python.exe -X utf8 ile:
- tools/validate.py ai-guvence-33: TEMİZ, dokuz kontrol (bir tahmin, dört çözüm, dört başlangıç); gerçek model dahil. PAFTA_DATA Desktop/pafta-g33-kontrol-20261030.
- docs/denetim/araclar/tahmin.py . ai-guvence-33: bir tahmin, sıfır şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g33-20261030, kopyadaki mutasyon.py <kopya> --en-cok 1000 ai-guvence-33: 13+13+11=37 mutant, sıfır geçen.
- kopya_sonda.py ai-guvence ai-guvence-33 "from sandbox.ai_gercek_ai_guvence_33 import referans_ozet as tekrar_ozeti": fail, korunuyor. kopya-sonucu.json hedeflenen Kendi tekrar özetini guard mesajını ve kabul kanıtı yokluğunu doğrular.

Ek olumsuz kontroller olumsuz-bos.json, olumsuz-sabit.json, olumsuz-yanlis-tutarlilik.json ve eksik-model.json: hepsi fail, kabul yok. Sonuncu, yalnız o test sürecinde PAFTA_OLLAMA_HOST=127.0.0.1:9 ve var olmayan exe ayarıyla gerçek bağımlılık yokluğunu sınar; fixture gerçek diye sunulmaz.

Gerçek sonuç: qwen3:4b-instruct-2507-q4_K_M, üç probe × beş koşu = on beş teknik hatasız çağrı; aritmetik/başkent/talimat oranları 1.0/1.0/1.0, üç probe da bu bool ölçüte göre tutarlı. Kanıt Desktop/pafta-g33-kontrol-20261030/ai-kanit/guvence-metodoloji-1793348773948.json. Bu küçük kalite/probe deneyinin sonucu genel güvenlik kabulü değildir.

Görünür veri üç normal runner/setup/Run çağrısında okundu: gorunur-dosya-run-1/2/3.json. Mevcut izole 18800 test sunucusunun normal token/Origin akışıyla HTTP Kontrol pass (sekiz kontrol, gerçek kabul), Run ok (gerçek çağrı, kabul=false): http-check.json/http-run.json. Uygulama kanıtları outputs/iyilestirme-codex-20261030/ui-data/ai-kanit/guvence-metodoloji-1793348857191.json ve guvence-metodoloji-calistir-1793348895668.json. CLI/HTTP görsel ders ekranı kabulü yerine sayılmaz. Work tarayıcı kontrolü son erişim denemesinde kapalı bildirildi; bu dersin görsel kabulü YAPILMADI ve denetçiye açık eksiktir.

Mevcut sunucu/kullanıcının Ollama süreci kapatılmadı. Yalnız mevcut yerel model kullanıldı.
