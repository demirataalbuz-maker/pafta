# ai-temel-10 iyileştirme teslimi

Codex'in kendi uygulama kontrolleridir; bağımsız denetim ve puan claude-opus'a aittir.

İş emrinin tüm maddeleri: ilk tablo ve NOT;ilk3sentetik/finalgerçek model ayrımı;yaklaşık 934 sözcük anlatım;görünür lora.json+README;mevcut ai_temel_veri.hazirla setup;aynı dosyayı okuyan ilk3starter/solution;üç gerçekçi kusurlu başlangıç. Starter1A@B ters çarpımı,starter2temele yerinde ekleme,starter3yalnız giriş adaptörünü sayma hatasıdır. Üçü Run çalışır ama Check reddeder. Mevcut doğru testler korunur.

Görünür veri tracks/ai-temel/fixtures/ai-temel-10/lora.json:elle hazırlanmış sentetik A/B/temel matrisleri,ölçek,fark ve maliyet vakalarıdır;canlı eğitim kaydı değildir. İlk görev farkı,ikinci aynı farkın temel ile toplamını,üçüncü farklı boyut/rankların maliyetini işler. Farkın B@A/ölçek hesabıyla tutarlılığı ayrıca doğrulandı. Kaynağı editörle aç veya yüklenen sözlüğü kodda değiştirip Run dene. Setup her çalıştırmada geçici veri/ kopyası kurar;kalıcılık yoktur. Gizli testler ayrıdır. Önceki editörden işlev import etmek gerekmez. Adaptör ağırlıkları kalıcı dosyaya yazılmaz.

Anlatım sıra/biçim,alfa/rank,B=0başlangıç,A/B gradyan yolu,dondurma ile no_grad farkı,birleştirme yerinde değişim riski,rankın her boyutta tasarruf sağlamaması,parametre oranının toplam bellek olmaması ve tek cümle öğrenmenin genelleme göstermemesi konularını işler. Resmî HuggingFace LoRA kavram belgesi kaynak gösterilir. PEFT/bitsandbytes/QLoRA bu derste çalışmaz;final Transformers/torch ile elle yazılan sınıfı kullanır. Zararlı yük/backdoor eğitimi değildir;hedef cümle sentetiktir.

Final guard referans_sinifi/lora_tak/getattr/peft/LoraConfig/kanit_yaz ile AST takmaad/yıldız ithalini engeller;ihlalde modelden önce stop eder. Alfa sonlu pozitif olarak açıklaştırıldı;inf/nan reddi öğrenci ve referansta eşleşir. İlk iki küçük görevde bütün matris girdileri derin kopyayla değişmezlik açısından sınanır. Gerçek q/v boyutunda A matrisinin sabit doldurulmaması doğrudan denetlenir;sabitA sondası hedef sözleşmede reddedilir. Boyut1/2,bias bulunan Linear,rank üst sınırı,yeni tensör dönüşü ve girdi değişmezliği eklidir. Asıl eğitim ayarları,model,istemler ve40Adamadımı korunur. Kabul=all(sonuclar) kalır.

Önemli doğrulama düzeltmesi:önceden temel_agirlik_degismedi yalnız ilk2adaptörün temel ağırlığını,ortak_model_degismedi yalnız ilkq_proj ağırlığını özetliyordu;rapor bütün temel ağırlıklar için iddia taşıyordu. Artık deney kopyasının bütün temel named_parameters girdileri önce/sonra tamSHA256 ile karşılaştırılır. Ortak modelin bütün state_dict tensörleri de önce/sonra karşılaştırılır. Bu ağırlık/durum tensörleri denetimidir;Python nesnesinin bütün geçici nitelikleri için kanıt değildir. Yeni kontrol aynı eski kabul bayraklarını daha geniş kapsamda üretir,test zayıflatılmaz.

Kanıta hedef/kontrol/üretim girdileri ve tokenları,Adam adı,kırk adımın yuvarlanmamış kaybı ve temel/ortak önce-sonra özetleri eklidir. Eski seyir,önce/sonra kayıpları,üretilen metinler,birleşme farkı,parametre sayısı,rank/alfa,tohum/öğrenme oranı ve model bilgisi korunur. Tam adaptör ağırlıkları veya checkpoint kaydedilmez;bu ders kalıcı model dışa aktarımı değildir.

Zorunlu kontroller (.ai-venv/Scripts/python.exe -X utf8):
- tools/validate.py ai-temel-10:izole PAFTA_DATA Desktop/pafta-t10-son-kabul-20261031;TEMİZ9:tahmin1,solution4,starter4.
- docs/denetim/araclar/tahmin.py . ai-temel-10:1tahmin,0şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-t10-20261031:yokluğu doğrulanmış yeni hedef;mevcut dosyalar silinmedi. Kopyadaki mutasyon.py <kopya> --en-cok1000 ai-temel-10:19+13+11=43mutant,0geçen. İlk3starter/solution/test/setup blokları kaynakla aynı. Son nonmutation/sabitA kontrollerinden sonra validate,tahmin,mutasyon ve negatifler tekrar koşuldu.
- kopya_sonda.py ai-temel ai-temel-10 "from sandbox.ai_gercek_ai_temel_10 import referans_sinifi; LoraDogrusal=referans_sinifi()":fail/korunuyor.

Ek çıktılar outputs/iyilestirme-codex-ai-temel-10:kopya,bos,sabit,olcek-yok,eksik-model JSON dosyaları fail/kabul yok. Ölçek sondası diğer doğru kodu koruyup alfa/rank yerine alfa yapar. Eksik model yalnız çocuk ortamında var olmayan model/revizyon ve local_files_only ile sınanır;indirme yoktur. Üç gorunur-dosya-run normalrunner/setup ileok. HTTP/UI ve kapanış teslim ekindedir.

CLI gerçek kanıtı:C:\Users\demo12\Desktop\pafta-t10-son-kabul-20261031\ai-kanit\temel-lora-1793435893845.json. SmolLM2-135M sabit revizyon;460800/134515008parametre eğitildi. Hedef kayıp4.850737→0.000569;kontrol kaybı2.667660→6.719839;birleşmefarkı1.431e-04. B=0takma kaybı4.850737;temel/ortak bütün ölçülen tensör özetleri aynı. Kayıtlı temel parametre sayısı272;ortakstate_dict sayısı273. Kontrol metnindeki bozulma bulgu olarak korunur;genel performans veya güvenlik başarısı iddiası yapılmaz. Hedef kaybın düşmesi gerçek bu dar eğitim görevinin kabulüdür;sabit çıktı cümlesi aranmaz.

Değişen dosyalar:tracks/ai-temel/lessons/ai-temel-10-lora-ve-parametre-verimli-fine-tuning.md;sandbox/ai_gercek_ai_temel_10.py;iki fixture dosyası;bu rapor;kuyruk/pano/devir/özet. Yeni indirme/kurulum,engine/web davranış değişikliği,commit/push veya puan yazımı yok. Eski derslerin görsel açıkları kapanmış sayılmaz.

SonUIeki:starter7/8fail,kabulfalse kayıt;ilk referans14/14sonrasında nonmutation/sabitA ekleriyle sonreferans tekrar14/14gerçek kabul:temel-lora-1793436014049.json. Sonkanıtta40eğitimadımı,272temelparametrenin tamamı veortakstate_dict önce/sonraeşitliği doğrulandı.SabitAyanlışçözümü sabit-a.json ile hedef q/v sözleşmesinde reddedilir. Üç görünür dosyaUI Run hamA/B/ölçeği ve starter kusurlarını gösterdi:tersçarpım,temele yerinde ekleme,eksikparametre sayımı. İlk3referans/starter retleri sonvalidate içinde tekrar geçti. HTTP14/14 veHTTPRun önceki sonküçük testeklerinden önceydi;sonUIveCLI daha güçlü testleri geçti. UI Run/kapanış son ekte doğrulanır.

Son öğretim metninde sayı/kelime ve noktalama boşlukları düzeltildi;çalıştırılabilir bloklar değişmedi.Giriş tablosu ve NOT arayüzde gerçek/sentetik ayrımı ve kalıcılık sınırıyla ayrıca görüldü.

SonRun/kapanış eki:UI Run40adım gerçek eğitim,hedef/kontrol kayıpları,460800parametre ve temel-lora-calistir-1793436090071.json kabulfalse kaydını gösterdi.Son kaynak çözüm SHA256'sı bu UI kanıtıyla aynı;ilk3çalıştırılabilir bloklar sonmutasyon kopyasıyla aynı.Kendi18800sunucusu kapandı,dinleyenportyok.Kullanıcı süreçleri kapatılmadı.Devirde eski ai-temel-08 onay bekleme cümlesi mevcut kullanıcı kapsam onayı/teslimiyle güncellendi;eski UIaçıkları özellikle ai-guvence kimlikleriyle ayrıldı.
