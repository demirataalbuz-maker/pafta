# Unlearning doğrulaması — ai-savunma-39

2026-11-04. Kullanıcının yazılmamış AI derslerini Codex yazsın talebiyle plan-savunma-8 alındı. Aktif başka yazar başlangıcı yoktu. Yeni39dersi33'ten sonra kaydedildi; mevcut dersler korunur. Yazar kontrolleri tamam; puan verilmedi, Opus bekliyor.

## Gerçek araç ve kapsam
Kurulu torch2.14.1+cu130 CPU'da kullanıldı. Yeni paket/model/veri kurulmadı. Linear(12,2,bias=False),24parametre,zero init;12sentetik one-hotkimlik. Pretrained LLM değildir. Full12örnekle120SGDadımı;retain-onlyretrain8örnekle120adım;approximateunlearnfullkopyasından50gerçekbackward/step;unchangedfullkopyası. İki ayrı koşu39/391;zero init ve deterministikCPU nedeniyle seedçeşitliliği iddiası yok,tekrarlanabilirlik kontrolü. Retain veforget girdi sütunları bağımsız olduğu için gerçekLLMetkileşimi temsil edilmez.

Kayıp retainCE-alpha*forgetCE;studentfloatobjective ileactualtensorobjective heradım karşılaştırıldı. Herunlearningadımındagradientnormu pozitif ve kaydedildi. Full/unlearnhashfarklı,unchangedhashaynı;retrainforgetkimliklerinigörmedi. Herkoşudörtstate_dict .pt dosyası yazıldı,weights_onlyCPUileyenidenokunup tensorlarla birebir eşitlik kontrol edildi. Gerçek posteriorlar,NLL/accuracy/TV,weightsSHA,fulldata/settings/version/device/loglarreceipt'te. Başarıyı düşenforgetaccuracy'ye bağlayan test yok. Bu certifiedunlearning veya kişiselverisilmegarantisi değildir.

## Doğrulamalar
CLI validate:1ders9kontrol TEMİZ(4solution4starter1tahmin). Tahmin1/0şüpheli. Son gerçek referans75/75. UI75/75gerçekkabul;starterRET. Görünürunlearning/ornekJSONu değiştirildi/geriokundu;UIRun gerçek eğitim yaptı,kabulfalse. Çalışmakopyasıgeçici,kalıcılıkiddiasıyok.

Üç anlamlıyanlış(lossişareti,yanlışpartition,sahteTV),boş/sabitRET. Referansimport/attribute/getattr/inspectexec4kopyaRET;namespaceyamasiRET. Bunlardakabultrueyok. Eksikzorunlupythonruntime geçmedi,kabultrueyok;kurulum/kullanıcıdosyası silinmedi.

Resmîmutantüreticisi üçsafgörevde45mutasyonunhepsiniFAILyaptı,0PASS0timeout. İlk tur eksik tip/sınıf1/olasılıküst sınırı testlerini yakaladı;bunlar eklendi. Propernonemptyforgetsubsetkoşulu idsnonempty'yi zaten gerektirdiğinden fazladan redundantnotidsclausesadeleştirildi;sözleşmegevşetilmedi,boşidsret. Yeni testler simplex toleransını ve olasılık[0,1]sınırını ayrıölçer;NaN/bool/duplicate/extrakeyret.

Hedefli eskiSavunma26/33veGüvence07'nin modelçalıştırmayankontrolleriPASS; tamliste related-pure-regression.json. Bütünmüfredatın ağırmodeldeneyleri tekrarlanmadı. İkinciWindowsmasaüstü/diğerOSkabulüyok.

## Öğretim ve kaynaklar
İlkaraçtablosu,NOT,450+kelimeanlatım,3kusurlu başlangıç,görünürfixture,üçsözleşme,tahmin→çıktı→fark,hata vitrini,eşleme,kanıtıyorumlama,sınır var. Hata vitrinindeki kararlıyanlışposteriorlar açıkça sentetik;gerçekmodelçıktısıdiye sunulmaz. GerçekbulgularaşağıdakiJSON'da. ai-saldiri48,ai-savunma33,ai-guvence07 ile köprü kurulur. https://aclanthology.org/2024.acl-long.457/ yöntem/ölçüm bağlamı;bu çalışma birebir yenidenüretilmedi.

## Dosya ve teslim
Yeni lessonMD/sandboxmodülü/fixtureJSON+README;track'e1ID,durableplan→IDeşlemesi. Ortakengine/webdeğişmedi. KaynakSHAveCLI/UI/Runyolları outputs/yeni-ai-savunma-39/teslim.json içinde. Oklasörde reference,negatifler,mutasyonlar,missingruntime,regresyon sonuçları var. Gerçekağırlıkdosyaları ilgili receipt.media klasöründe. KendiUItestsunucusu kapatılır;ortak8798vekullanıcınınOllama/WSL/Dockerortamıyönetilmez. Commit/push yok.

## Son UI ölçümü (ilk koşu)
```json
{
  "retain": {
    "n": 8,
    "full_acc": 1.0,
    "full_nll": 0.053249247045673576,
    "unlearn_acc": 1.0,
    "unlearn_nll": 0.03242979214086955,
    "retrain_acc": 1.0,
    "retrain_nll": 0.03508522738363801,
    "unlearn_retrain_tv": 0.0025673136115074158
  },
  "forget": {
    "n": 4,
    "full_acc": 1.0,
    "full_nll": 0.053249247045673576,
    "unlearn_acc": 1.0,
    "unlearn_nll": 0.1358261115792093,
    "retrain_acc": 0.5,
    "retrain_nll": 0.6931471805599453,
    "unlearn_retrain_tv": 0.37299445271492004
  }
}
```
