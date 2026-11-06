# AI53 — VLM adversarial perturbation teslimi

2026-11-04 (03Kasım gecesi başlayan çalışma) · Codex yazdı,kendi kontrollerini yaptı. Opus denetimi bekliyor,puan verilmedi. plan-saldiri-7→ai-saldiri-53. Dalga3'te Codex'e verilen3AIişinden AI54ilebirlikte ikinci teslim;multimodal savunma38henüzbitmedi.

## Gerçek yöntem ve sınır
Onaylı HuggingFaceTB/SmolVLM-256M-Instruct rev7e3e67edbbed1bf9888184d9df282b700a323964,Apache2.0;13dosya517903046bayt resmîHub'dan tokenFalse ile indirildi. Model ağırlığı SHA25674dea5904032e5ae99a2e0eef5179e6ac0f1dedc3ab0c7c2a5d4d387c843203e upstreamLFSile doğrulandı ve ders kodunda sabitlendi. Paket/baseimage kurulmadı. .deps zaten gitignore'da. Kurulum çıktısı outputs/vlm53-kurulum/kurulum.json.

Gerçek pretrained VLM,gerçek image encoder ve decoder,piksel autograd kullanıldı. Model parametreleri donuk. İki sentetik512RGBgörsel için3targetedPGDadımı;epsilon0kontrolü ve8/255bütçesi,alpha2/255. Öğrenci projeksiyon fonksiyonu her adımda o anda hesaplanan gerçek gradient listesini alır;önceden hazırlanmış gradient yok. Normalize mean/std0.5modelin gerçek processor'ında doğrulanır;gradient bu normalize geçişinden de akar. CPU veya CUDA,torch2.14.1+cu130/transformers5.21.0;bu laptoptaCUDA.

Ölçüm bilinçli dar: tokenizer'da red/blue tek tokenları2382/4461. Softmax yalnız iki next-token logitinde;tamvocabulary olasılığı/kalibre renk sınıflandırması/serbest üretilmiş cevap değildir. Baseline'da daha az tercih edilen token hedef seçilir. Targeted loss logsumexp(iki logit)−hedeflogit. İlk sonda tamvocabulary objective ileblue logiti artsa da göreli redtercihi arttı;bu yanlış başarı örneği,hata vitrininde kabulfalse kaydıyla gösterilir. Son objective/ölçüm ikili tercih için tutarlı. Saldırı başarısı PASS şartı değildir.

## Sonuçlar ve gerçek dosyalar
CLIveUIkabulü gerçek4koşul,toplam12gradientadımı üretti. PNGdosyaları gerçekten yazılıp yenidenokundu;sonforward reloaded piksel üzerinde. Epsilon0grubunda2/2görsel aynıPNGbyte'larıyla kaldı ve hedeftercihi0/2. Attackgrubunda1/2ikili tercih değişti. ÖlçülenL-infinityyaklaşık6/255(3adım×2/255),izin8/255'in altında. UIkoşusunda PyTorch peakallocated2233939456bayt(~2.23GBdecimal);toplamVRAM/diğerkullanıcısüreçleri/CUDAreserved değildir. GPUbelleği için modellerin ağırlıkboyutundan genelleme yapılmadı.

Herkoşunun modelSHA/revizyon,sürümler,cihaz,prompt,processorayar,tokenID,önce/sonralogit/skor,gradientnormu,öğrenciprojeksiyonhatası,pikselbütçesi,PNGpath/hashvegrupözeti kanıtta. PNG'ler kalıcıPAFTA_DATA/ai-kanit-media/vlm53-UUIDaltında;JSONreceipttemporaryharnessdizinindenkalıcıarşive taşınır. KendiPythonharnessindenbaşkasüreçbaşlatılmaz;kullanıcıOllama/WSL/Docker Desktop/modeli kapatılmadı. KendiPythonmodeli del/gc/empty_cache,sonraharnessprocesskapanışıyla biter.

## Öğretim ve kontroller
İlk tablo/NOT,3kusurlustarter,syntheticvlm/ornek.json+README,hazirla,tahmin→gerçekçıktı→fark,hata vitrini,eşleme,gerçekkanıt/görseliyorumlama,sınır cümlesi var. Fixture çalışma kopyası aynı çağrıda değiştirilebilir;sonraki çalıştırmaya kalıcı değildir. Dosya hiçbir gerçekgradientkabulünün yerine geçmez. StudentPGD flatlistlerle yazılır;torchyalnızgerçekmodülde gerçekgradienthesaplar ve öğrenciadımını bağımsıztensorprojeksiyonuna karşısınar. Böylece normalPythongörevleri sistemyorumlayıcısında,.ai-venvgerçekadımda çalışır;engine/runnerdeğişmedi.

- python -X utf8 tools/validate.py ai-saldiri-53 →1ders9kontrol TEMİZ,4solution4starter1tahmin.
- tahmin.py . ai-saldiri-53 →1tahmin0şüpheli.
- Resmîmutasyon.pyKURALLAR/mutantlar üreteci3safgörevde:40üretilen0geçen. İlkkoşuda2geçen vardı;eps/alpha stringtipi/sonluluk ve tekil yenitercih testleri eklendi. Testler zayıflatılmadı;VLMgerçekadım mekanikmutasyonlarda çalıştırılmadı.
- Finalboş/sabitRET,gradientyönüters/xtmerkezliprojeksiyon/yanlışbaşarıpaydası3/3RET;import/attribute/getattr/inspect+exec kopya4/4RET. Safeq/raises/yakinsonuçlarıkabulall(checks)'ekatılıyor. Retkabultruekanıtı yok.
- Gerçekmodelyokken aynıreferansFAIL,kabultruekanıt yok;otomatikdownloadyok. YerelSHA/normalizeayaruyumsuzluğukoddatutulur.
- UIstarterRET,Check67/67gerçekkabul,RunfixtureJSONokuyupgerçekVLMçalıştırdıvekabulfalsegösterdi. ScreenshotDesktop/pafta-ai53-ui-kabul-20261103.png. UIgerçekmodeltestisırasındaCPU/GPUkontrolübaşarıylabitti.
- ÖncekiAI54çalışmasında49/51/47'nin21safkontrolügeçti;buVLMeklemesinden sonra bütünAIyoluağırregresyonuyenidenkoşulmadı. Yeni motor/engine/webdavranışı yok,yalnızai-saldiri/track.json'da53,12'densonrayerleşti.

## Tekrar üretim ve dosyalar
Yeni ders tracks/ai-saldiri/lessons/ai-saldiri-53-vlm-adversarial-perturbation.md,modül sandbox/ai_gercek_ai_saldiri_53.py,fixtures/ai-saldiri-53. PAFTA_VLM53_MODEL taşınmış onaylımodelklasörünüseçebilir;varsayılanROOT/.depsaltında kullanıcıyolu gömülmez. PAFTA_TORCH_CIHAZ=cpu CPUseçebilir. Yeni makinedemodel/venvkurulumu ayrıgerekliliktir;eksikmodelPASSolmaz.

outputs/yeni-ai-saldiri-53/teslim.json gerçekCLI/UI/RunreceiptyollarınıvefileSHA256listesini tutar. CLIreceipt ilkvalidate'lerden kendiLOCALAPPDATA/Pafta/ai-kanit kaydından korundu;solutionSHA256referansla eşleştirildi. İlkCLIvalidateiçinPAFTA_DATAizolasyonuseçilmemişti,yalnızkanıt/görsellerarşivlendi;progress.jsondeğiştirilmedi. Negatif/eksikmodelkontrollerioutputsaltındakikendiPAFTA_DATA'sında.UIayrıDesktoptestverisindeydi. Bu ayrım gizlenmedi.

## Açık işler
Yalnızbulaptopkabulü;masaüstü/Linux/macOSkabulüyok. Serbestgeneratedanswervebaşkamodel/genelVLMjailbreakiddiasıyok. MultimodalsavunmaOCR38kurulumukullanıcıtarafındanayrıcaonaylandı;kurulumsürüyor,AI53kabulünündahilideğil. Denetim/puanOpus'ta. Commit/pushyok.


## Ek kaynak koruması doğrulaması

2026-11-04: İçe aktarılan modülün namespace alanlarına yazma ve fonksiyon __globals__ erişimi ders içindeki AST kontrolüyle reddediliyor. M.deney yaması RET; kabultrue kanıt üretilmedi. Meşru referans aynı gerçek deneyle yeniden PASS oldu (53:67/67,54:65/65). Ortak ai_lab/engine/runner değişmedi. Yeni sonuç reference-guard-final.json ve modul-yama-ret.json; teslim.json yeni CLI receipt ve güncel kaynak hashlerini gösterir. Önceki UI ölçümü aynı çözüm/deney fonksiyonlarıyla yapılmıştı.


## PGD girdi sözleşmesi için ek kontrol
2026-11-04: İlk PGD karşılaştırması aynı tek eq içinde hem doğru adımı hem x0/xt/gradient listelerinin değişmediğini doğrulayacak şekilde güçlendirildi; kontrol sayısı67olarak kaldı. Meşru saf referans PASS, doğru çıktı üretip girdi gradientini yerinde değiştiren ek yanlış çözüm RET (pgd-pure-reference.json,input-mutation-ret.json). Referans fonksiyonu ve gerçek VLM deney kodu değişmedi; sourcehash teslim.json'da güncellendi. Bu kontrol40mekanikmutant toplamına ek bir anlamlı sözleşme sondasıdır.
