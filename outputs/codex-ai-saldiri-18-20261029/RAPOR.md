# ai-saldiri-18 — Confused Deputy, gerçek SQLite yetki kapısı
Uygulayıcı kabulü; bağımsız denetim değildir.29 Ekim2026.

Değişen: ders sonuna anlat/görev index8, sandbox/ai_gercek_ai_saldiri_18.py, web/data/ai-saldiri-18-belge.txt. Eski görevler korundu. Yeni kurulum/ortak motor değişikliği/commit/push yok.

Oturumdan principal, güvenilmez belgeden beyanlar. Öğrencinin kullanıcı ∩ ajan ∩ istenen kapısı gerçek SQLite SELECT/UPDATE ve yerel paylaşım JSONL önünde çalışır. Paylas:dis yalnız deneyin yerel sentetik arşividir; dış ağ yok. Temiz/zehirli korumalı ve hatalı yalnız-ajan karşılaştırması gerçek native model kullanır. Altı doğrudan sentetik kontrol gerçek dosya yürütücüsünde meşru okuma/yazma/paylaşımın çalışmasını ve yetkisiz işlemde disk/okuma etkisizliğini sınar; model çıktısı diye sunulmaz.

İlk validate Windows SQLite dosya kilidi nedeniyle FAIL oldu. sqlite context manager tek başına bağlantıyı kapatmaz; modülün kendi bağlantılarına contextlib.closing eklendi. Sonra hedef1ders9kontrol TEMİZ. 18+19 ilkgrup19HTTP500nedeniyleFAIL(18geçti); daha sonraki grup2ders18kontrol TEMİZ. Başarısız koşular başarı sayılmadı.

Dış kabul summary.json9/9: referansPASS,starter/boş/sabit+ajan-tekbaşına,belge-admin-yükseltme,çalışan-ihlali-gizleme mutantlarıFAIL. RunOK/kabulfalse,eksikOllamaFAIL. Farklı süreç/cwdde öğrenci dosyası korunması persistence.json (fixture). UI başlangıç iki kezreddedildi; referans28/28PASS saldiri-18-vekil-1793282537820.json. Run bütün kontrollertrue/kabulfalse saldiri-18-vekil-1793282658687.json; ikisi ortak ui-data/ai-kanit altında.

CLI referans üç nativekolda da oku:rapor seçildi, model kaynaklı yetkiihlali0. Doğrudan yetkisiz3işlem reddedildi; meşru3işlem gerçek diskte çalıştı. Saldırı başarısı geçme şartı değildir; küçük model gözlemi genellenemez. Logda belge kaynaklı etiketi enjeksiyon nedenselliği ispatı değildir. Ham model,ayar,cihaz/digest/bellek,oturum/izinler,disk hashleri kanıtta.

Ham örnek HTTP'den okunuyor(UI'de görüldü),Run kalıcı kopyanın yolunu/içeriğini gösteriyor. Ancak anlatımdaki Markdownlink ortak renderer tarafından düzmetin gösteriliyor,tıklanabilir anchor yok. Ortak panoya gorunur-veri-ui olarak kaydedildi; bu arayüz eksiği düzeltilmiş sayılmadı. Ekranda dosyaeditörü yok; kopya dış editör/Python ile düzenlenir. İkinci cihaz/bağımsız denetim yok.
