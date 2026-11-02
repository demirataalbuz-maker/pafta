# ai-temel-04 iyileştirme teslimi

Codex'in kendi uygulama kontrolleridir; bağımsız denetim ve puan claude-opus'a aittir.

İş emrinin tüm maddeleri: ilk araç/temsil/sınır tablosu ve NOT; ilk3sentetik/finalgerçek model ayrımı;yaklaşık839sözcük anlatım;görünür logitler.json+README;mevcut ai_temel_veri.hazirla setup;aynı dosyayı okuyan ilk3starter/solution;üç gerçekçi kusurlu başlangıç. İlk starter sıcaklığa bölmek yerine çarpar;ikinci küçük logitleri seçer;üçüncü top-p eşiğini aşan gerekli adayı dışarıda bırakır. Run çalışır,Check reddeder. İlk3testlere farklı değerlerde girdi değişmezliği eklenmiştir;önceki doğru testler korunmuştur.

Görünür tracks/ai-temel/fixtures/ai-temel-04/logitler.json elle hazırlanmış üç-token öğretim dağılımıdır;canlı model/tokenizer çıktısı değildir. Bağlam ve token etiketleri öğretim içindir. Üç görev aynı logitleri farklı sıcaklık,k,p değerleriyle işler. Kaynağı editörde aç veya kodda yüklenen sözlüğü değiştirip Run dene. Setup her çalıştırmada geçici veri/ kopyası kurar;kalıcılık yoktur. Gizli testler dosyadan ayrıdır. Örnek dosya yerel gerçek model yerine geçmez.

Anlatım logit/olasılık ayrımı,kararlı softmax,ilk görevdeki yuvarlamanın finale taşınmaması,top-k→yeniden normalize→top-p sırası,eşiği aşan aday,eşitlik politikası,greedy/sıcaklık0 ayrımı ve güvenlik ölçümündeki karıştırıcıları açıklar. Sıcaklık güvenlik filtresi veya kalite garantisi değildir. Transformers resmi üretim işlemcileri belgesi kaynak gösterilir. Genel tekrar cezası/yasak token/araç şeması bu dersin kapsamı değildir.

Final referans/hf_referans/son_logitler/getattr/uret/kanit_yaz ile AST takmaad/yıldız ithali denetlenir;ihlalde stop model çağrısından önce gelir. Eşit logitler,sınır sıcaklık/k/p ve tensor değişmezliği ayrıca sınanır. Gerçek ağırlıkların ileri hesapları ve yedi farklı istem/ayar sonucu korunur. Kanıta tam istem/token kimlikleri,ayarlar,logit boyutu/dtype/SHA256/üst10logit ve öğrenci aday/olasılık sonuçları eklenmiştir. Tam sözlük logit vektörü saklanmaz;özet ham vektörün yerine sunulmaz.

Gerçek üretimde seçilen token kimlikleri,her adım aday sayısı ve seçilen tokenın dağılımdaki olasılığı kaydedilir. Greedy seçim izindeki1.0deterministik seçim kütlesidir;model softmax olasılığı olduğu söylenmez. Üretim istemi,tohum7,12token bütçesi,dört ayar ve model/sürüm/cihaz bilgisi kayıttadır. Aynı süreçte/tohumda referans üretimle eşitlik algoritma kontrolüdür;metnin belirli bir cümle olması aranmaz. Kabul=all(sonuclar) korunmuştur;bağımlılık yokluğu kabul sayılmaz.

Zorunlu kontroller (.ai-venv/Scripts/python.exe -X utf8):
- tools/validate.py ai-temel-04:izole PAFTA_DATA Desktop/pafta-t04-kabul-20261031;TEMİZ9:tahmin1,solution4,starter4.
- docs/denetim/araclar/tahmin.py . ai-temel-04:1tahmin,0şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-t04-20261031:yokluğu doğrulanmış yeni hedef;var olan dosyalar silinmedi. Kopyadaki mutasyon.py <kopya> --en-cok1000 ai-temel-04:11+12+12=35mutant,0geçen. İlk3starter/solution/test/setup blokları kaynakla aynı.
- kopya_sonda.py ai-temel ai-temel-04 "from sandbox.ai_gercek_ai_temel_04 import referans as ornekleme_dagilimi":fail/korunuyor.

Ek çıktılar outputs/iyilestirme-codex-ai-temel-04:kopya,bos,sabit,sicaklik-yok,eksik-model JSON dosyaları fail/kabul yok. Anlamlı yanlış sonda diğer doğru kodu koruyup sıcaklığı formülden çıkarır. Eksik model yalnız kendi çocuk ortamında var olmayan model/revizyonla local_files_only yolunda sınanır;indirme yapılmaz. gorunur-dosya-run-1/2/3 normalrunner/setup ileok.

Gerçek kabul kanıtı:C:\Users\demo12\Desktop\pafta-t04-kabul-20261031\ai-kanit\temel-ornekleme-1793434027616.json. HF işlemcileri yedi gerçek istem/ayar kümesinde uyuştu. Aday boyutları:{'T=0.5, p=0.5': 1, 'T=0.5, p=0.9': 2, 'T=1.0, p=0.5': 1, 'T=1.0, p=0.9': 2, 'T=1.5, p=0.5': 4, 'T=1.5, p=0.9': 1210}. Bütün dört üretimde gerçek token seçimi vardır. Bunlar bu kurulu model/sürüm/cihaz koşularıdır;daha sıcak dağılımın her koşulda aynı etkiyi yapacağı veya daha doğru olacağı iddia edilmez. Üretim metinleri/kimlikleri tam kanıttadır. HTTP/UI ve kaynak kapanışı teslim ekindedir.

Değişen dosyalar:tracks/ai-temel/lessons/ai-temel-04-sampling-temperature-top-k-ve-top-p.md;sandbox/ai_gercek_ai_temel_04.py;iki fixture dosyası;bu rapor;kuyruk/pano/devir/özet. Yeni indirme/kurulum,engine/web davranış değişikliği,commit/push veya puan yazımı yok. Diğer derslerin eski görsel açıkları kapanmış sayılmaz.

HTTP/UI eki:http-check.json11/11gerçek kabul;http-run.jsonok/gerçek kabulfalse. UIstarter8/9fail;kabulfalse kanıtı vardır çünkü test önce gerçek logitleri modelden hesapladı ve ardından öğrenci sözleşmesi başarısız oldu. UIreferans11/11gerçek kabul:temel-ornekleme-1793434244780.json. HF7/7ve üretim eşitliği görüldü. UI Run/görünür örnekler ve sunucu kapanışı ayrıca son ekte doğrulanır.

SonUI eki:Run gerçek dört ayar üretimini ve temel-ornekleme-calistir-1793434303853.json kabulfalse kaydını gösterdi. Üç görünür dosya UI Run ile ham logitler ve starter kusurlarını gösterdi:ters sıcaklık etkisi,küçükten seçme,son gerekli adayı dışarıda bırakma. İlk3 doğru çözümler/starter retleri validate ile doğrulandı. Kendi18800 sunucusu kapanışı ayrıca kontrol edilir;önceki görsel açıklar sürer.

Kapanış:kendi18800 sunucusu kapandı;dinleyenportyok.Kullanıcı süreçleri kapatılmadı.
