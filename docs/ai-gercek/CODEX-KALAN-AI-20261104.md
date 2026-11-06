# Yazılmamış AI dersleri — güncel Codex devri

2026-11-04. Kullanıcı kalan yazılmamış AI derslerini Codex'in yazmasını açıkça istedi. Önce pano/atama/gerçek dosyalar kontrol edildi; diğer yazarın dört plan için aktif başlangıç kaydı yoktu. Eski Dalga3 raporundaki dörtbaşlıkclaude-yazar notu tarihsel oldu.

| Plan | Somut ders | Yazar kontrolleri | Durum |
|---|---|---|---|
| SOC–AI/Purple köprüsü | ai-ile-guvenlik-19 | UI76/76,CLI9TEMİZ,tahmin0,35mutant0geçen,4kopyaret | Opus denetimi bekliyor |
| Unlearning doğrulaması | ai-savunma-39 | UI75/75,CLI9TEMİZ,tahmin0,45mutant0geçen,4kopyaret | Opus denetimi bekliyor |
| Watermark/C2PA | Henüz yazılmadı | Gerçek C2PA aracı eksik | Ayrı indirme onayı soruldu,yanıt bekleniyor |
| Deepfake/ses tespiti | Henüz yazılmadı | NeuralTTS+insansesi verisi eksik | Ayrı toplu indirme onayı soruldu,yanıt bekleniyor |

## Tamamlanan iki ders
Üç kusurlu saf görev,450+kelime anlatım,araçtablosu,NOT,görünür düzenlenebilir geçici çalışmaJSONu,tahmin→fark,hata vitrini,eşleme,gerçekdeney,kanıt yorumlama,sınır. CLIveUIgerçekkabul;UIRun kabulfalse. Boş/sabit,3anlamlıyanlış,4referanskopyası,namespaceyamasi ve eksikbağımlılıkgeçmedi. 80mekanikmutantFAIL,0PASS0timeout. Hedefli18eskisafregresyonPASS;12sınavtesti12.469sOK. Bütünmüfredat yeniden sınandı denmiyor. Sadece buWindowslaptop;ikinci masaüstü kabulüyok. Yeniindirme/kurulum/ücretliAPI yok.

SOC19,kuruluOllamaile4gerçekçağrıdan sonra12SQLitealarmdefteri yazıpcommit/close/reopen/SELECTileölçer. Yanlış öneri faultprobe ayrısentetiketiketli. İki seeddeyalnızhighuser_agent saldırgan kontrolünde. UIrun'da4/4zorunluolaymodeltarafındanbastırıldı,hostgateherikikanıtta0korumalıbastırma. Bu kontrollülogprototipi;gerçekSIEMişletimivegenelLLMgüvenliğikanıtıdeğil.

Unlearning39,24parametreliCPUtorchsınıflandırıcı;full/unlearn/retrain/unchangedkarşılaştırması,100gerçekautogradadımı,ağırlıkdosyalarıyenidenokuma. PretrainedLLMdeğil. Buayarlardaforgetaccuracy1.0kalır,retrain0.5veposteriorTVyaklaşık0.373;unutmabaşarısıuydurulmadı. İki seed,sıfırinitnedeniyleaynıdinamiğiyineler;bağımsızbaşlangıççeşitliliğidiyeanlatılmaz.

Detaylı raporlar CODEX-YENI-ai-ile-guvenlik-19.md ve CODEX-YENI-ai-savunma-39.md. Her dersin outputs/yeni-<ID>/teslim.json dosyasında kaynakSHAveCLI/UI/Runreceiptyolları var. Screenshotlar Desktop/pafta-soc19-ui-kabul.png ve Desktop/pafta-unlearning39-ui-kabul.png. İki ders puansız iyileştirme kuyruğuna teslim edildi;puanıOpusverecek. Ortak8798panoHTTP200;yalnızkendiUItestsunucularıvegeçicisekmelerikapatıldı. KullanıcınınOllama/WSL/DockerDesktop'ı,öğrenciverilerivekurulumlarıkorundu. Commit/push yok.

## Devam edecek ajan
Onayları bu sohbetin yeni yanıtlarından kontrol et; geçmişSmolVLM/OCR/cosignonaylarıC2PA/Piperindirmesinikapsamaz. C2PA-KURULUM-ONAYI.md ve SES-TESPIT-KURULUM-ONAYI.md sabitresmîsürüm/boyut/hash/amaçlisteleridir. Henüz dosyaindirilmedi;onaygelmedenindirme. AGENTS.md ve YENI-AJAN-REHBERI.md'yi oku,panoacik/sonkayıtlar ve güncelatamalarıtekrar kontrol et. Yeni dersIDrezerve et;dosya/trackeklendiktensonratrackerileal. DersdosyalarıolmayanikiplanafakeID/puan/tamamdurumuyazma. EskiClaude-yazaratamasınıkullanıcıdevriylegüncelleme,gerçekyazımasahiplenirkenyapılır.

Onaygeldiğindeöncekurulumhash/boyutdoğrulaması;sonragerçekmedya/araçdeneyi,ayrıfixture,UIRun/Check ve4zorunlukontrol. C2PA:imzabütünlüğü ile signertrust ve içerikgerçekliği ayrı. Ses:hazırneuralTTS,kimseyesesklonlamayok;küçükinsansesiverisi/sesvespeakerdomainconfoundlarıdürüstölçülür. Kapsamdaralmasıgerekirsegeneldeepfakebaşarısıdiyeetiketleme. İki konununhenüzyazılmamışolmasınıgizleme.
