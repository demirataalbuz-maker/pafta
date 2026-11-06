# ai-saldiri-19 — gerçek SQLite nesne/kimlik yetkisi
Uygulayıcı kabulü; bağımsız denetim değildir. 29 Ekim2026.

Değişen: ders sonuna anlat/görev index8, sandbox/ai_gercek_ai_saldiri_19.py, web/data/ai-saldiri-19-istekler.txt. Eski görevler korundu; yeni kurulum/ortak motor değişikliği/commit/push yok.

Gerçek SQLite benim/ortak/yabanci nesnelerinde sunucunun sahiplik/paylaşım verisi kullanılır. Sentetik doğrulanmış oturum gerçek OAuth sağlayıcısı değildir. Öğrencinin kimlik ve nesne kapısı gerçek SELECT/UPDATE/DELETE önünde çalışır. Modelden/belgeden güvenilir silmeonayı alınmaz; doğrudan pozitif kontrolde nesne+işleme bağlı onay verilir. Silme yalnız deneyin kendi DBsatırındadır. Ağ/keyfi dosya işlemi yok.

kimlik_bagla mevcut sözleşmesinde sil olmadığı için adaptör bu fonksiyona yalnız kimlik kontrolü amacıyla oku verir; gerçek eylem aynen nesne_yetkiye gider. İkisi birlikte izin vermeli. Bu görev nesne/kimlik yetkisini ölçer; kullanıcı niyeti/amaç kapısının tüm ayrıntılarını kapsamaz(17dersi ayrı). Nesne sahipliğinin izin verdiği eylem, kullanıcı göreviyle aynı şey değildir.

On bir doğrudan sentetik kontrol gerçek diskte: meşru kendiokuma/yazma,paylaşılmışokuma,onaylıkendinesnesininsilinmesi; yabancınesne/paylaşılmışnesneyazma/kimlikuyuşmazlığı/doğrulanmamışoturum/yanlışya da eksikonay retleri. Native model temiz/korumalı/kapısız3kol; saldırının uyması şart değil. Ham çağrı,oturum,onay,ACL,karar,gerçek işlem,okunanveri/diskhashleri kaydedilir.

Dış kabul summary.json9/9: referansPASS,starter/boş/sabit+kimlikyoksayma,paylaşımıyazmayetkisiyapma,onayıyoksayma mutantlarıFAIL;RunOK/kabulfalse,eksikOllamaFAIL. Persistence farklı süreç/cwdde düzenlemeyi korudu(fixture). Grup18+19:2ders18kontrol TEMİZ. UI starter iki kezreddedildi. İlk referans25/27FAIL: saldiri-19-auth-1793282952846.json(ikiHTTP500); son referans27/27PASS:1793283087580. UI Run tümkontrollertrue/kabulfalse:1793283032639. Hepsi ortak ui-data/ai-kanit altında.

İlk CLIgrup da ikiHTTP500ileFAIL; ilk-validate-http500-fail.json ve ilk-validate-fail.log korundu. Daha sonraki CLI/UI geçmesi kök nedenin çözüldüğünü kanıtlamaz; ara sıra Ollama500 hâlâ bilinen sınırlamadır. Modüle sonraki hatalarda yanıtgövdesini de saklayan kayıt eklendi; ortak retry/transport değiştirilmedi. Hatalı koşular PASS sayılmadı.

Referans model3kolda da kendi nesnesini okudu;14vakanın karar/çalışması tutarlı,model kaynaklıbypass0. UIRun model bazı kolda araç seçmedi; gerçek yanıt ve çekimserlik kaydedildi,uydurma çağrı yok. Gerçekmeşruiş ve retler doğrudan disk kontrolleriyle kanıtlandı. Küçük örnek genel güvenlik iddiası değildir.

Ham istekdosyası HTTP'den görüntülendi,Run kalıcı kopya yolunu/içeriğini gösterir. Markdownlink ortak rendererda düzmetin; tıklanabilir değil. Ekranda dosyaeditörü yok; dışeditör/Python kullanılır. İkinci cihaz/bağımsız denetim yok.
