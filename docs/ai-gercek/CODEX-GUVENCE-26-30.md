# Güvence26–30: uygulayıcı devir raporu

Beş dersin kodu ve CLI kabulü tamamlandı; UI ebeveyne ayrıldı. Bu yardımcı hiçbir tarayıcı/WindowsUI işlemi yapmadı ve hiçbir dersi denetime-hazir/bitti işaretlemedi. Gerçek adım tüm derslerde **7 (0tabanlı; ekrandaki8.adım)**. READY.json geçerli JSON dizisi, beş dersin rapor/CLI/kanıt/kalıcılık yollarını içerir. Parent UI kabulünü sırayla yapıp tracker durumunu kapatabilir.

## Son kabul

|Ders|CLI|Regresyon|Kapsam|
|---|---|---|---|
|26|9/9 beklenen sonuç|validate.log: dörtderste36TEMİZ|Gerçek autogradFGSM, aynıseed yeniden eğitim, yalnızlr değişen kol|
|27|9/9|aynı36TEMİZ|Gerçek eğitim/logit; ayrı kalibrasyon ve görülmemiştest;NLL/ECE|
|28|9/9|validate-28-optin-final.log:9TEMİZ|KuruluQwen4B/8B, gerçek8çağrı test ve ayrıca8Run;ortakSohbetOturumu|
|29|9/9 sonpaket|validate-29-30-final.log:18TEMİZ|Gerçek eğitim/FGSM→maskeli bildirimZIP,canary/hash doğrulama|
|30|9/9 sonpaket|aynı18TEMİZ|Üçgerçek eğitim, eşleşmişFGSM, öğrenci politikasına bağlı gerçek dosya etkisi, yayınZIP|

Toplam **45/45 beklenen senaryo**: her ders referansPASS, starter/boş/sabit/3anlamlımutantRED, RunOK ve eksikbağımlılıkFAIL. Bu45başarılısaldırı değildir. DörtCPUderste eksikseçiliyorumlayıcı BağımlılıkEksik;28de erişilemeyen gerçek yerelhizmetFAIL.28ek canlıolmayan kontrolleri ve gerçek/api/tags üzerinde eksikmodel/boyutbütçesireti ayrı raporlanır; model çıktısı diye sunulmaz. Son ana özet final-main-summary.json.29/30sonpaket tekrarından önceki cli-summary.json tarihsel; sonları cli-summary-29-30.json.

Kalıcılık: **5/5**, persistence.json. Her ders için iki bağımsızgerçekPython süreci, farklıcwd, göreliPAFTA_DATA proje köküne çözüldü ve öğrenci dosyasına eklenen düzenleme korundu. Başlangıçveçözüm CALISTIR/goster kancaları5/5:run-hooks.json. Başlangıçtamfonksiyonlar çalışır; deney yalnızçözümde değildir.

## 28: izin, modeller ve yeniden çalıştırma

Kullanıcı, daha sonra yalnız bizimizole kabul/UI alanında opt-intrue ile kurulu4B/8B kullanımını açıkça yetkilendirdi. Varsayılan web/data/ai-guvence-28-deney.txt hâlâ opt_infalse. Gerçeköğrencikopyasına dokunulmadı. Kabulkopyası outputs/codex-guvence-26-30-20261029/28-optin-data/calisma/ai-guvence-28/ayar.json içinde true.

Read-only/api/tags envanteri:28-installed-inventory.json. Küçük qwen3:4b-instruct-2507-q4_K_M=2497293803bayt,4.0B,Q4_K_M; büyükaday qwen3:8b=5225388164bayt,8.2B,Q4_K_M. Yeniindirme/kurulumyok,ücretli/uzakAPIyok. Gerçekoturumlar ortaklab.SohbetOturumu cihazsahipliği/kilidi ve temizlik akışını kullanır; başka süreç/Ollama/WSL/Docker durdurulmadı.

İlkreferansta8hamyanıt kaydedildi: heradaya2görev×2tekrar. İkisindekalite1.0,güvenlik1.0,üretilentoken10; küçükortalama1383.75ms,büyük3906.5ms. Tamcanlıkanıt28-live-reference.json içindeki ai_kanit.dosya alanında. Bunlar yalnız2sentetik aritmetik/enjeksiyon görevidir; genelüstünlük veya genelgüvenlikkanıtı değildir. Gecikmeyükleme/önbellek/sistemkoşullarındanetkilenir; tokenüretimsayısıdır,girdiaralığıdeğil.

İzole CLI, kenditestalanınıtrueyapar; öğrenci varsayılanını değiştirmez:

```powershell
python -X utf8 outputs/codex-guvence-26-30-20261029/28-live-kabul.py
```

Ebeveynin zatençalışan18800UIserverı outputs/codex-guvence-bos-20261029/ui-data kullanır. Yalnız buizoleUIverialanı için açıkonayıhazırlayan komut (projekökünde; serverrestartgerekmez):

```powershell
python -X utf8 -c "import os,json;os.environ['PAFTA_DATA']='outputs/codex-guvence-bos-20261029/ui-data';from sandbox import ai_gercek_ai_guvence_28 as m;p=m.calisma_dosyasi();c=m.izin_config(p);c['opt_in']=True;p.write_text(json.dumps(c,indent=2),encoding='utf-8');print(p)"
```

CPUistenirse serverıbaşlatan ortamda PAFTA_OLLAMA_CIHAZ=cpu; GPUkullanımı kilitlidir. Süre/araçhatası veya onayyokluğu PASSdeğildir. Defaultonaysız28validatebeklenenFAIL:validate-28-pending.log. Butarihsellog, sonizoleopt-inbaşarısını geçersizkılmaz.

## Veri, bilimsel kapsam ve dosyalar

26, [Goodfellow/Shlens/Szegedy2015 FGSM](https://arxiv.org/abs/1412.6572v3) yönteminin **sınırlı sentetik yenidenuygulamasıdır**. Makalenintamverikümesi/MNIST/maxout/model/sonuçlarının sadıkreplikasyonu DEĞİLDİR. Gerçekikiayrıeğitim aynıtörenselmakaleskoruyla karşılaştırılmaz; aynıkod/seedkontrollükollar velrfarkıölçülür. Değişenlrtekbaşınagenelnedensellikkanıtıdeğil.

27[Guovd.2017](https://proceedings.mlr.press/v70/guo17a.html) sıcaklıkyönteminin küçüksentetikuyarlaması; modeleğitim0:96,kalibrasyon96:144,test144:192. GridkalibrasyondaNLLile seçilir, testteECE/NLL/doğrulukraporlanır. Testteiyileşmekzorunludeğil.

29gerçekmodelkanıtınımaskelervegerçekyerelZIPyazar; hashler arşivyenidenokunarakdoğrulanır. Ham özelcanarykanıtıayrıklasörde, yayınpaketimaskelidir. Model-eğitim/sürüm/logitkaydıdahildir. Gerçekürünzafiyeti/CVEiddiasıvebildirimgönderimiyok.30öğrencikapısıgerçektahmindosyasınıbelirler; kapsama/izinliyanlışetkiölçülür. YayınZIPmodelkaydı/yenidenüretim/kodhashi/sınırlar/ölçümiçerir; ağdayayınlanmadı. SaldırıbaşarısıveyaolumlugüvenliksonucuPASSkoşuludeğildir.

Sentetikgörünürayarlar web/data/ai-guvence-NN-deney.txt; ekranda/data/ai-guvence-NN-deney.txt. Kalıcıayrıkopya PAFTA_DATA/calisma/ai-guvence-NN/ayar.json; Runmutlakgerçekyoluveiçeriğiyazdırır. Yerleşikdosyaeditörüyok, yerel editör kullanılır. Mevcutöğrencidüzenlemeleriüzerineyazılmaz.26/27/29/30Kontrolayrıgörülmemişayar kullanır;28kalıcıkopyasıonay/modelseçimiiçindir, beklenenyantıdeğiştirmez. Testtempdosyalarıtemizlenir; ağırlıkhash/hamlogit/eğitimiziJSONkanıttakalır. Runmodel/ZIP/etkid osyaları öğrencialanındakalır.

Değişendosyalarıntamlistesi outputs/codex-guvence-26-30-20261029/changed-files.json. Yalnız5dersmd,5özel sandboxmodülü,5webfixture,kendidevir/READYveçıktıklasörü. Eski dersadımları korundu. Ortakengine/webdavranışı/başkaajanşeridi değişmedi;14edokunulmadı. Yeniindirme/kurulum/commit/pushyok.

## Yeniden kabul ve kalan iş

```powershell
python -X utf8 outputs/codex-guvence-26-30-20261029/kabul.py
python -X utf8 outputs/codex-guvence-26-30-20261029/ek-kabul.py
python -X utf8 outputs/codex-guvence-26-30-20261029/28-preflight.py
python -X utf8 outputs/codex-guvence-26-30-20261029/28-live-kabul.py
python -X utf8 outputs/codex-guvence-26-30-20261029/28-missing-service.py
python -X utf8 tools/validate.py --yol ai-guvence ai-guvence-26 ai-guvence-27 ai-guvence-29 ai-guvence-30
```

28izoleregresyonuiçinPAFTA_DATA tamyolunu28-optin-dataolarakayarla,sonra validate.py --yol ai-guvence ai-guvence-28. Tümai-guvencebaşkalarınınaktifdersleriniçalıştırılmadı; yalnızatanandilimregresyonuyapıldı.

**Kalan kabul:** Parent:beşdersin gerçekders ekranında2starterKontrol→Çözümügöster→Kontrol/Çalıştırve görünürdosyaerişimini doğrulasın. Gerçekadım7,tümURLlerhttp://127.0.0.1:18800/#/ders/ai-guvence/ai-guvence-NN/7. UIebeveyninde; buyardımcı UIyapıldıiddiasındabulunmaz. TrackerUIsonrasına kadarebeveynkapatır. Bağımsızdenetimveikincicihazkabulübuçalışmadayapılmadı.
