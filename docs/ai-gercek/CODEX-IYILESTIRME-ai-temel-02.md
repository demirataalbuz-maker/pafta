# ai-temel-02 iyileştirme teslimi

Codex'in kendi uygulama kontrolleridir; bağımsız denetim ve puan claude-opus'a aittir.

İş emrinin tüm maddeleri:ilk araç/temsil/sınır tablosu ve NOT;ilk3sentetik/finalgerçek ayrımı;yaklaşık 929 sözcük anlatım;görünür embedding.json+README;mevcut ai_temel_veri.hazirla setup;aynı dosyayı okuyan ilk3starter/solution. İlk görev hamJSON dosyasını metin_yukle ile de gösterir. Starter1mod alıp kaynak satırları paylaşır;starter2ham nokta çarpımı döndürür;starter3en uzak satırı seçer. Üçü Run çalışır,Check reddeder. Kaynaklar elle hazırlanmış sentetik etiket/vektörlerdir;gerçek tokenizer kaydı değildir. Setup her çalıştırmada geçici veri/ kopyası kurar;kalıcılık yoktur. Kaynağı editörde aç veya yüklenen sözlüğü kodda değiştirip Run dene. Gizli testler ayrıdır.

Öğretim token/kelime ve girişembedding/bağlamsaltemsil ayrımı,kopya/alias hatası,kosinüs ve büyüklük,eşitlik kuralı,boşluk/tokenizasyon etkisi,ham/birim vektör ayrımı ve yakınlığın güvenlik/semantik kalite kanıtı olmamasını açıklar. Resmî PyTorchEmbedding belgesi kaynak gösterilir. Model veya kütüphane indirilmez;final kurulu SmolLM2 giriş katmanını kullanır. Retrieval/cümleembedding kalitesi ölçülmez;sohbet/eğitim/transformer ileri hesabı bu deney değildir.

Küçük sayısal görevlerde sonlu float temsilini aşmayan sayı sözleşmesi açıklaştırıldı. Eski norm hesabı1e300'de taşabiliyor,1e-300'de sıfıra yuvarlanabiliyordu. Yeni birim vektör hesabı en büyük mutlak bileşenle ölçekler ve math.hypot kullanır. NaN/inf/float temsilini aşan int ValueError ile reddedilir;bool kabul edilmez. Kosinüs altı ondalıkfloat,sıfırnormred,sıra/eşitlik,kopya ve nonmutation korunur.1e±300,matrisin değişmemesi,kimlik listesinin değişmemesi ve yinelenen satır kopyalarının birbirini değiştirmemesi eklenmiştir. Doğru testler zayıflatılmadı.

Yeni sandbox/ai_gercek_ai_temel_02.py modülü bağımsız referans_raporu ve Run gösterimini taşır. Testin önceden yerel olan referansı aynı ağırlık tablosundan index_select yoluyla seçer;öğrenci gerçek model embedding katmanını çağırır. Yeni guard referans_raporu/getattr/kanit_yaz ile AST takmaad/yıldız ithalini engeller;ihlalde modelden önce stop eder. Referansı import eden sonda hedef guardda reddedilir.

Gerçek katman no_grad altında çağrılıyor mu forward_pre_hook ile gözlenir;aynı sırada model.forward engellenerek transformer ileri hesabı yapılmadığı sınanır. Kancalar/patch finally ile bırakılır. Sırf doğru vektörleri doğrudan .weight tablosundan alıp katmanı çağırmayan anlamlı yanlış çözüm katman-yok.json'da hedef kontrolde reddedildi. Float32kosinüs çözümünün geçmesini önlemek için karşılaştırma atol1e-10/rtol1e-9 olarak float64sözleşmesine uygun sıkılaştırıldı;float32.json reddedilir. Boyut modelden okunur;576sabitlenmez.

Yedi gerçek metin vardır;16tokenüst sınırı gerçekten16token olan metinle sınanır,40tekrar sınırı aşar. Yinelenen her kimlik çiftinin eşitliği hâlâ tek tek hesaplanır;yalnız UI'daki aynı mesaj kalabalığını azaltmak için tüm çiftler tek allkontrolünde toplanır,tekrarlar>0koşulu korunur. Bu test kırpma değildir. Tamham vektörler/kosinüs matrisleri kanıtta,ekran ise boyut ve örnek bileşenleri gösterir. Kabul=all(sonuclar) korunur.

Run daha önce yalnız print yapıyor ve gerçek kanıt üretmiyordu. Yeni goster(fn) kurulu modele ve öğrenci fonksiyonuna gider,ham çıktıyı ve ayarları kabulfalse ile kaydeder. Ayrıca gerçek embedding çağrı sayısı,gradbayrağı ve transformerforward sayısını ölçüp gösterir;öğrenci kodu yanlışsa bunların her zaman doğru olduğu varsayılmaz. Model kimliği,sabit revizyon,ağırlıkSHA256,sürümler ve CPU bilgisi ortak kayıtla saklanır. Dışsunucu veya kalıcı süreç açılmaz;Ollama gerekmez.

Zorunlu kontroller (.ai-venv/Scripts/python.exe -X utf8):
- tools/validate.py ai-temel-02:izole PAFTA_DATA Desktop/pafta-t02-son-kabul-20261031;sonTEMİZ9:tahmin1,solution4,starter4. Kimlik-listesi nonmutation eklendikten sonra tekrar edildi.
- docs/denetim/araclar/tahmin.py . ai-temel-02:1tahmin,0şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-t02-20261031:yokluğu doğrulanmış yeni hedef;mevcut dosyalar silinmedi. Kopyada mutasyon.py <kopya> --en-cok1000 ai-temel-02:18+7+9=34mutant,0geçen. İlk3starter/solution/test/setup blokları sonkaynaklaaynı.
- kopya_sonda.py ai-temel ai-temel-02 "from sandbox.ai_gercek_ai_temel_02 import referans_raporu as gercek_embedding_raporu":fail/korunuyor.

Ekler outputs/iyilestirme-codex-ai-temel-02:kopya,bos,sabit,float32,katman-yok,eksik-model JSON sonuçlarıfail/kabul yok;üç normalrunner/setupRunok. Eksik model yalnız kendi çocuk ortamında olmayan model/revizyon ve local_files_only ile sınanır;indirme yoktur. Bu teslimde CLI+gerçekUI ile yeterli kapsam sağlanır;ayrı aynımodel HTTP deneyini tekrar etmeye gerek yoktur. UI sonuçları/kapanış son ekte kaydedilir.

Gerçek CLI kanıtı:C:\Users\demo12\Desktop\pafta-t02-son-kabul-20261031\ai-kanit\temel-02-embedding-1793438514164.json. ModelHuggingFaceTB/SmolLM2-135M@93efa2f097d58c2a74874c7e644dbc9b0cee75a2;7gerçekgirdi;boyutlar[576];tekrarlanan kimlikçifti122. İlk16tokenvakasıözel-tokeneklemedensınanır. Bunlar öğrenilmiş giriş tablosunun gerçek satırlarıdır;modelin metin üretmesi veya cümle anlamının doğrulanması değildir.

Değişen dosyalar:tracks/ai-temel/lessons/ai-temel-02-embeddingler-tokenlerin-vektor-uzayina-tasinmasi.md;yeni sandbox/ai_gercek_ai_temel_02.py;iki fixture dosyası;bu rapor;kuyruk/pano/devir/özet. Yeni indirme/kurulum,engine/web değişikliği,commit/push veya puan yazımı yok. Önceki görsel açıklar ve Temel16'da kaydedilen varsayılanOllama500sorunu bu CPU deneyiyle kapanmış sayılmaz.

SonUI eki:starter iki kez10/13fail,gerçek tablo referansı hesaplandığı için kabulfalse kayıt var. Kullanıcı devamı sonrası eski sekme erişilemedi;güncel sekmede referans yeniden20/20gerçek kabul gösterdi:temel-02-embedding-1793451578003.json. 7gerçek metin,16token,122tekrarlanan kimlikçifti. UI Run gerçek model/vektörleri ve temel-02-embedding-calistir-1793451643350.json kabulfalse kaydını gösterdi:embeddingçağrısı1,gradFalse,transformerforward0. KaynakçözümSHA256Runkanıtıylaaynı. grad-acik.json doğru sayıları üretse de no_grad sözleşmesini ihlal eden çözümün hedef kontrolde reddini gösterir.

Üç görünür görevUI Run ile hamJSONdosyasını ve starter kusurlarını gösterdi:paylaşılan satır,hamnoktaçarpımı2.0,yanlış enyakınsatır0. İlk3doğru çözümler/starter retleri sonvalidate içinde doğrulandı. Giriş tablosu ve NOT arayüzde görüldü. Son gerçek çıktıda kosinüs köşegeni1.0000000000000002 gibi yuvarlama farkı taşıyabilir;kuramsal[-1,1]ile sonbasamak aşımı ayrımı anlatımda düzeltildi. Bu yalnız metin değişikliğidir;kodblokları değişmedi.

Kapanış:kendi18800Pafta test sunucusu kapatıldı;dinleyenportyok. Bu CPU dersinde Ollama süreci/modeli başlatılmadı veya kapatılmadı. Temel16 varsayılanOllama500notu devir üreticisinde kalıcı hale getirildi;bu dersin geçmesi o açığı kapatmaz.
