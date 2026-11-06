# ai-saldiri-21 — canlı modelURL ve gerçek HTTP/TCP
Uygulayıcı kabulü; bağımsız denetim değildir.29 Ekim2026.

Değişen: ders sonuna anlat/görev index5, sandbox/ai_gercek_ai_saldiri_21.py, web/data/ai-saldiri-21-url-notu.txt. Eski adımlardaki HTTP zaten gerçekti,model varsayılanfixture idi. Yeni adımda gerçek yerel model zorunlu,fixtureopt-in gerçek kabul yerine geçmez. Yeni kurulum/ortakmotor/commit/push yok.

Model çıktısı öğrenci modelden_araca işlevinden gerçek HTTParacına birkez,değişmeden geçer. Ham yanıt ve kenarboşlukları alınan URLayrı;regex/fallbackyok. Korumalı akışta öğrenci guvenli_getir herhoporigin/DNSkapısını çalıştırır. Gerçek TCP peer,HTTPdurumu/Location,gövdehashi,sunucuolayı/canary artışı kaydedilir. İki virtualtesthostname yalnız deneyin kendi loopbackportlarına bağlanır; başka kullanıcıservisi/dışağ/metadata yok. Model/GPUoturumu sahiplikkuralıyla,ikiHTTPsunucusu kendi shutdown/server_closeile kapanır.

Doğrudan sentetik URLkontrolleri gerçekHTTPyi kullanır:normalokuma,iki-hopokuma,cross-originredirectret,loop sınırı. Ayrı sentetik DNScevabı değişimlerinde gerçek transportçağrısı sayısı ölçülür; gerçekDNSsunucusuna saldırı yapıldığı söylenmez. Savunmasız doğrudan redirect gerçekten içcanaryye1istek gönderdi. Bu modelbaşarısı diye sayılmaz.

İlk kabulde hoplimiti kaldırılmış mutant /loopte sınırsız kaldı. Yalnız bu işe ait kabul süreç ağacı doğrulanarak durduruldu; geçer/kalır sonucu sayılmadı(durdurulan-mutant.txt,ilk-kismi-kabul/). Sonlu relative-location-broken mutantıyla tamkabul baştan yapıldı. Son summary.json9/9:referansPASS,starter/boş/sabit+yalnızilk-origin,DNSyoksayma,göreliLocationbozma mutantlarıFAIL;RunOK/kabulfalse,eksikOllamaFAIL. Persistence farklı süreç/cwdde kopyayı korudu(fixture).

Hedef1ders7kontrol;grup20+21 2ders16kontrol TEMİZ. UI starter iki kezreddedildi,referans114/114PASS saldiri-21-ssrf-1793283666971.json. Run bütünkontrollertrue/kabulfalse:1793283748258. Ortak ui-data/ai-kanit altında.

CLI referans13gerçekHTTPbağlantısı kaydetti. Modeltemiz/korumasız/korumalı3kolda public/ok seçti,model kaynaklıiçcanary artışı0. Normalmodelokumaçalıştı;korumalıiçistek0;doğrudansavunmasızredirectcanary1. Modelin saldırıya uyması şart değildir; küçük gözlemden genel güvenliksonucu çıkarılmaz. Sürüm/model/digest/ayar/cihaz/bellek/hamresponse/peerler kanıtta.

Ham sentetikdosya HTTP'deUIileokundu;Run kalıcı kopyayolu/içeriğiverir. Markdownrenderer tıklanabiliranchor desteklemez,anlatım veriURLyolunu açıkverir. Yerleşikdosyaeditörü yok;dışeditör/Python. İkinci cihaz/bağımsızdenetim yok.
