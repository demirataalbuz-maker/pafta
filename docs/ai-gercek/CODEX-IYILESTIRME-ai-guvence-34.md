# ai-guvence-34 iyileştirme teslimi

Codex düzeltti; claude-opus denetimi bekleniyor. Puan verilmedi.

Değişenler: tracks/ai-guvence/lessons/ai-guvence-34-llm-uygulama-pentest-koprusu-ssrf-ve-yetki.md; tracks/ai-guvence/fixtures/ai-guvence-34/{README.md,veri/model_onerisi.txt,veri/yetki.json}; sandbox/ai_gercek_ai_guvence_34.py. engine/web davranışı değişmedi. Yeni paket/model indirme/kurulum, commit/push yok.

İlk anlatım başına gerçek araç/sentetik örnek/sınır tablosu ve NOT eklendi. Üç görev mevcut hazirla/setup ile görünür ham URL ve sahiplik dosyalarını okur; Çalıştır veriyi ve sonucu gösterir. Dosyalar elle yazılmış sentetik eğitim örnekleri, canlı yanıt kaydı değildir. Kopya geçici, sonraki çalıştırmada yenilenir; kalıcılık iddiası yok. Üç kusurlu starter noktalama/tekrar temizlememe, URL içinde alt dize arama ve kaynak sahibini denetlememe hatalarını taşır. Hepsi reddedilir.

Dersin deney kapsamı açık: son görev gerçek yerel model çağırır ama öneri URL'lerini getirmez, ağ etkisini veya oturumlu IDOR'u sınamaz. DNS çözümlemesi, rebinding ve her yönlendirmede hedef denetimi yapılmaz. Basit URL çıkarıcı bütün IPv6/parantez dilbilgisini koruyan üretim parser'ı değildir. IDOR'da kullanıcı adı girdidir; gerçek API'de doğrulanmış oturumdan gelmesi gerektiği anlatılır. Bu deney tam SSRF savunması kabulü diye sunulmaz.

Sınır testleri bin/bin bir izinli host, yanlış liste türü, iç host allow-list'te olsa bile ret, localhost alt alanları, bozuk URL, alt dize/userinfo ile host karışıklığı ve sahiplik alanlarının bozuk türlerini kapsar. Bozuk URL ayrıştırması, öğrenci referansı ve bağımsız kapı referansında çökme yerine geçersiz şema/host kararıyla reddedilir. IP bayraklarının aynı union davranışı, görev iki çözümünde any(tuple) ile açık yazılır; örtüşen bayraklar yeni bir politika oluşturmaz. Mevcut doğru testler korunur, zayıflatılmaz.

Son görevin sözleşmesi iç adresin allow-list'e yanlışlıkla eklenmesi hâlini doğrudan sınar. Referans import takma ad/yıldız dahil kopya koruması ve ihlalde stop eklenir. İki gerçek çağrının tamamı hatasız olmalı; önceden tek başarılı çağrı yeterliydi. Gerçek ham yanıtın URL/izin/engel listelerinin tamamı bağımsız referansla karşılaştırılır; önceki host içinde example.com alt dizesi denetiminin yerine tam sonuç karşılaştırması gelir. Modelin iç adres önermesi geçme koşulu değildir. Tam yanıt, istem, tohum, sıcaklık, token sınırı ve süre kaydedilir. İstem/model çağrı ayarları korunur. Tam deney Kontrol/Run kanıtına eklenir; kabul mevcut+ek kontrollerin all sonucu, Run ise kabul=false kalır.

Dört kontrol .ai-venv/Scripts/python.exe -X utf8 ile:
- tools/validate.py ai-guvence-34: TEMİZ, dokuz kontrol (bir tahmin, dört çözüm, dört başlangıç), gerçek model dahil; PAFTA_DATA Desktop/pafta-g34-son-kontrol-20261030.
- docs/denetim/araclar/tahmin.py . ai-guvence-34: bir tahmin, sıfır şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g34-20261030, kopyadaki mutasyon.py <kopya> --en-cok 1000 ai-guvence-34: 0+11+11=22 mutant, sıfır geçen. Araç ilk URL çıkarımında kuralına uygun mutant üretemez; mevcut elle yazılmış noktalama/tekrar mutantları ayrıca ders testinde reddedilir. Sonraki değişiklik yalnız kırpılan gerçek deney sözleşmesindedir; mutasyon-kapsam.json sınanan ilk üç görevin kopyayla birebir aynı olduğunu doğrular.
- kopya_sonda.py ai-guvence ai-guvence-34 "from sandbox.ai_gercek_ai_guvence_34 import referans_denetle as url_denetle": fail, korunuyor. kopya-sonucu.json hedeflenen Kendi URL denetimini guard mesajını ve kabul kanıtı yokluğunu doğrular.

Ek kontroller olumsuz-bos.json, olumsuz-sabit.json, olumsuz-ssrf-atlayan.json ve eksik-model.json: hepsi fail, kabul yok. Sonuncu yalnız kendi test sürecinde erişilemeyen loopback portu/var olmayan Ollama exe ile model yokluğunu sınar. SSRF-atlayan çözüm gerçek iç-adres kapısını kaldırır; allow-list içine yanlışlıkla giren özel adres vakaları bunu reddeder.

Gerçek kanıt Desktop/pafta-g34-son-kontrol-20261030/ai-kanit/guvence-ssrf-1793350178991.json. İki teknik hatasız model çağrısı, sabit kapıda üç engel ve bir izin. Sabit engeller loopback, metadata ve allow-list dışı host; izin https://docs.example.com/x. Model bu koşuda metadata hedefini farklı/bozuk biçimlerde de yazdı (169.254.169.25.html ve 169.254.169.25); kayıtlar ham hâliyle korunur, doğru metadata hedefini kesin istediği iddia edilmez. Modelden gelen izinli örnek https://docs.example.com/kilavuz. Hiçbir öneri URL'sine istek yapılmadı.

Görünür dosya kontrolleri normal runner/setup/Run üzerinden üç görevde ok: gorunur-dosya-run-1/2/3.json. Mevcut izole 18800 test sunucusunun normal token/Origin HTTP akışı: Kontrol pass (dokuz kontrol, gerçek kabul), Run ok (gerçek çağrı, kabul=false); http-check.json/http-run.json. CLI/HTTP görsel ders ekranı kabulü yerine sayılmaz. Work tarayıcı erişimi son denemede kapalı bildirildi; bu dersin görsel kabulü YAPILMADI, denetçiye açık eksiktir.

Mevcut sunucu veya kullanıcının Ollama süreci kapatılmadı. Yalnız mevcut yerel model kullanıldı.
