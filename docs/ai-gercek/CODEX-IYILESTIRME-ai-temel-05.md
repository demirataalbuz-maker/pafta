# ai-temel-05 iyileştirme teslimi

Codex'in kendi uygulama kontrolleridir; bağımsız denetim ve puan claude-opus'a aittir.

İş emrinin tüm maddeleri uygulandı: ilk tablo ve NOT;ilk3sentetik/finalgerçek model ayrımı;yaklaşık834sözcük anlatım;görünür qkv.json+README;mevcut ai_temel_veri.hazirla setup;aynı dosyayı okuyan ilk3starter/solution;üç gerçekçi kusurlu başlangıç. Starter1satır yerine sütun projeksiyonu,starter2eksik ölçek,starter3Query/Key yerine basit Value ortalamasıdır. Üçü Run çalışır ama Check reddeder. İlk3testlerde farklı değerlerle girdi değişmezliği ayrıca denetlenir;mevcut doğru testler korunur.

Görünür veri tracks/ai-temel/fixtures/ai-temel-05/qkv.json içindedir. Elle hazırlanmış sentetik token temsilleri,Wq/Wk/Wv ve önceden hesaplanmış projekte değerlerdir;canlı model/tokenizer kaydı değildir. Birinci görev üç matrisle projeksiyon;ikinci ilk token Query'si ve üç Key ile skor;üçüncü aynı Q/K ve Value ile bağlam hesaplar. Fixture projekte alanının matrislerle tutarlılığı ayrıca doğrulandı. Kaynak editörde açılır veya dersteki yüklenen sözlük değiştirip Run denenir. Setup her çalıştırmada geçici veri/ kopyası kurar;kalıcılık yoktur. Gizli testler ayrıdır. Önceki editördeki işlevi import etmek gerekmez.

Anlatım projeksiyon yönü,logit/skor/olasılık ayrımı,ara yuvarlama tuzağı,Key ile Value değişiminin farkı,nedensel maskenin yetki denetimi olmaması ve dikkat ağırlığından nedensel/güvenlik sonucu çıkarılamaması konularını işler. PyTorch resmi scaled_dot_product_attention belgesi ölçek/maske/softmax/Value sırası için kaynak gösterilir. Hazır işlevi öğrenci yerine kullanmak kabul edilmez. İlk3 tekQuery ve sabit küçük boyut;final çok-token nedensel dikkat hesabıdır.

Final guard referans/kafa_girdileri/getattr/scaled_dot_product_attention/kanit_yaz ile AST takmaad/yıldız ithalini engeller;ihlalde modelden önce stop eder. T1/d1,küçük asimetrik vaka,tensor değişmezliği,sıfır kafa boyutu,Keysonsuz ve Valuenan ek sınamaları vardır. Gerçek davranış korunur:RoPE sonrası Q/K,gruplu sorguda eşlenen V ve modelin o_proj girdisi karşılaştırılır. Hooklar finally ile kaldırılır. Kabul=all(sonuclar) kalır;eksik model veya başarısız deney PASS sayılmaz.

Gerçek kanıt artık dört vaka için metin,tokenlar,katman/kafa,tam Q/K/V,model kafa bağlamı ve öğrenci dikkat/bağlam tensörlerini içerir. Run kanıtına aynı tek-kafa girdileri/çıktıları,metin ve sink katmanları eklenir;kabulfalse kalır. Gerçek model ağırlık özeti,revizyon,sürümler ve CPU aygıt bilgisi ortak kanıttadır. Sink ilk tokena dördüncü tokendan itibaren tüm kafalar üzerinden ortalama dikkattir;bütün modelin açıklaması değildir.

Zorunlu kontroller (.ai-venv/Scripts/python.exe -X utf8):
- tools/validate.py ai-temel-05:izole PAFTA_DATA Desktop/pafta-t05-kabul-20261031;TEMİZ9:tahmin1,solution4,starter4.
- docs/denetim/araclar/tahmin.py . ai-temel-05:1tahmin,0şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-t05-20261031:yokluğu doğrulanmış yeni hedef;mevcut dosyalar silinmedi. Kopyadaki mutasyon.py <kopya> --en-cok1000 ai-temel-05:11+13+19=43mutant,0geçen. İlk3starter/solution/test/setup blokları kaynakla aynı.
- kopya_sonda.py ai-temel ai-temel-05 "from sandbox.ai_gercek_ai_temel_05 import referans as nedensel_dikkat":fail/korunuyor.

Ek çıktılar outputs/iyilestirme-codex-ai-temel-05:kopya,bos,sabit,maske-yok,eksik-model JSON dosyaları fail/kabul yok. Maskesiz sonda diğer doğru kodu koruyup yalnız gelecek maskesini kaldırır. Eksik model yalnız çocuk ortamında var olmayan model/revizyon ve local_files_only ile sınanır;indirme yoktur. Üç gorunur-dosya-run sonucu normalrunner/setup ileok. Gerçek HTTP/UI ve kapanış teslim ekindedir.

CLI gerçek kabul kanıtı:C:\Users\demo12\Desktop\pafta-t05-kabul-20261031\ai-kanit\temel-dikkat-1793434548719.json. SmolLM2-135M sabit revizyon;dört gerçek kafa vakasında model çıktı farkları:[4.726616675831963e-07, 1.4396265290983479e-08, 2.6251362972296022e-08, 1.9959280450621009e-07];en büyükfark4.727e-07. Sink katman→oran:{'0': 0.2016, '3': 0.4057, '15': 0.706, '29': 0.6274}. Bu metin/model/katmanlara ait ölçümdür;dikkat temsili bir saldırı veya savunma başarısı iddiası değildir. Sabit model metni/saldırı başarısı PASS şartı yapılmaz.

Değişen dosyalar:tracks/ai-temel/lessons/ai-temel-05-attention-query-key-ve-value.md;sandbox/ai_gercek_ai_temel_05.py;iki fixture dosyası;bu rapor;kuyruk/pano/devir/özet. Yeni indirme/kurulum,engine/web davranış değişikliği,commit/push veya puan yazımı yok. Eski derslerin görsel açıkları bu teslimle kapanmış sayılmaz.

HTTPeki:http-check.json11/11gerçek kabul;http-run.jsonok/gerçek kabulfalse.TamQ/K/V ve çıktı kaydı kanıtta.

UIeki:starter8/9fail,gerçeklogit hesabı yapıldığı için kabulfalse kayıt var. İlk referans kontrolünün sekmesi kapandığından sonucu görülmedi ve UI kabul sayılmadı. Tek güncel sekmede tekrar edilen referans11/11gerçek kabul gösterdi:temel-dikkat-1793435006370.json. Modele fark4.7e-7ve sink özetleri görüldü. Üç görünür görev UI Run ile token/matrisleri ve starter kusurlarını gösterdi:sütun projeksiyonu,ölçeksiz skor[2,0,-2],basit ortalama bağlam[0,2]. Doğru çözümler/starter retleri validate içinde doğrulandı. Run ve kapanış son ekte doğrulanır.

SonRun/kapanış eki:UI Run gerçek dikkat haritası,4.73e-7model farkı,sink değerleri ve temel-dikkat-calistir-1793435045802.json kabulfalse kaydını gösterdi. Kendi18800sunucusu kapatıldı;dinleyenportyok.Kapanan ilksekme döneminde sunucu yanıt yazarken ConnectionAbortedError/WinError10053 kaydı görüldü;bu başarısız görüntüleme kabul sayılmadı.Sonteksekme UI11/11veRun ayrı doğrulandı;sunucu davranışı değiştirilmedi.Kullanıcı süreçleri kapatılmadı.
