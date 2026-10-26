# Test kusurları ve kod açıkları · Codex

Tarih: 26 Ekim 2026. Başlangıç HEAD: `34b7e06`. Teslim dalı: `codex/denetim-test-kod-aciklari`. Push/merge yapılmadı. C bölümü, puanlar ve Kimi'nin Purple dersleri değiştirilmedi. A bölümündeki derslerde çözüm/anlatım aynı kaldı; yalnız test blokları değişti (başlangıç ağacıyla otomatik karşılaştırıldı).

## A · Sonuç ve mutasyon kanıtı

Ham sayılar değiştirilmedi. Aşağıdaki "0 geçen" değerleri **hedef görev** içindir; bütün dersin sonucu farklıysa ayrıca yazıldı. Bağımsız mutasyon aracına filtre/istisna eklenmedi. Davranışı aynı kalan mutantları düşürmek için öğrencinin çözüm metnini ezberleten test yazılmadı.

| Açık no | Madde / hedef | Sonuç | Commit |
|---|---|---|---|
| 1 | md1 P75:11 | Gerçek wheel setine 0.10.0 eklendi, 0.9.0'a gerileme sınandı. Metin kıyaslayan özel bozuk çözüm reddedildi. Genel araçta **1 geçen**: `>`→`>=` aynı sürümü tekrar atıyor; eşdeğer, aşağıya bak. | 04dd2ec |
| 2 | md1 P75:5 | Öğrenci AST'sinde --no-index açıkça istenir. **1 mutant, 0 geçen**; --no-index kaldırılmış özel çözüm de reddedildi. | 04dd2ec |
| 3 | md11 BS35:5 | Gerçek scp/sshd korunup yalnız uzak hash cevabı test double ile yanlış/boş verildi; kod=1 ve uyuşmazlık istendi. stderr tanığı eklendi. **6 mutant, 0 geçen**; ders toplam **10 mutant, 0 geçen**. | a287146 |
| 4 | md83 JS13:3 | Gerçek Express route'undan expose true/false ve 399/400/499/500 matrisi. **14 mutant, 0 geçen**. Dersin diğer görevi JS13:4'te bir ayrı mutant geçiyor; kapsam dışı olarak saklandı. | dbe87c7 |
| 5 | md13 PS23:6 | Yalnız testte açılan loopback HTTP sunucusundan gerçek 200 yanıtı; stdout/stderr/çıkış kodu. **6 mutant, 0 geçen**; PS23+PS25 son koşusu toplam **33 mutant, 0 geçen**. | 94aefc9 |
| 6 | md22 CM23:3–5 | SystemRoot yalnız çocuk süreçte değiştirilerek whoami hatası; kaynak kodu değiştirmeden ikinci çağrıyı bozan geçici Windows .NET csc test aracı ve temiz stderr de sınandı. **4/6/14 mutant, her hedefte 0 geçen**. | 8ef380d + 4d6fd79 |
| 7 | md29 HT22:3 | 299/300/399/400, tam hop, bir fazla hop, varsayılan limit=3, Location ASCII uçları. **22 mutant, 0 geçen**; HT22:2 de **20 mutant, 0 geçen**. | 6906182 |
| 8 | md38 SP21:2/4 | Gerçek Splunk'ta UTC ve İstanbul gece yarısı/saniye/milisaniye kanıtları eklendi. **1+1 geçen** kaldı: bunlar saat değil MAX_TIMESTAMP_LOOKAHEAD 23→24 ve 19→20; sözleşmede tam minimum arama uzunluğu zorunlu değil. | 0b849ad |
| 9 | md45 SG19:2 | İddia edilen eşik, pipeline priority=100. Gerçek pySigma çevirisinde 100/101 aynı SPL; **1 geçen eşdeğer mutant**. Ders değiştirilmedi. Altyapı testinde birebir SPL eşitliği tanığı var. | 26cf766 (tanık) |
| 10 | md7 P79 | Başlangıç HEAD'de tam 2**64 için ValueError tanıkları zaten iki görevde vardı. Ek olarak 2**64+1 ve 2**65-1 sınandı; hedef ders temiz. **5 geçen**: üçü hata iletisi, ikisi daha sonraki MessageID eşitliğiyle yine reddedilen geniş guard. | 5c701c6 |
| 11 | md15 PS22:5/6 | Devralınan son iki grup, başka kimlik, boş/başarılı girdilerde stderr. PS22:6 **4 mutant, 0 geçen**. PS22:5 **1 geçen**, son grupta AND→OR daha önce karar vermemiş ACE'leri tekrar dolaştırıyor. Aynı maskeyle aynı stateless karar tekrarlandığından bu tekrarlar yeni karar üretmez; ham mutasyon sıfır gösterilmez. | 0f077f8 |
| 12 | md16 PS25:4 | Boş ve yalnız boşluk içeren yayıncı satırı, temiz stderr. **10 mutant, 0 geçen**. | 776ff68 |
| 13 | md62 AD21:2 | Gerçek CA şablonunda yalnız enrollment bit 1 açık/bit 2 kapalı tanığı; finally ile eski alanlar geri yüklendi. **2 mutant, 0 geçen**. | 709c13b |
| 14 | md69 CS13:3/4 | Kullanıcı/belge/işlem/gereksinim yanlış türleri, boş işlem, yanlış eşik/izinli tipi. **24+24 mutant, her hedefte 0 geçen**; ders toplam **48 mutant, 0 geçen**. | eb4d26d |
| 15 | md72 CS16:4 | U+FFFF tek ?, U+10000 iki ?. **1 mutant, 0 geçen**; diğer görev mutant üretmiyor. | e3c804d |

Özel yüksek öncelik bozuk çözümleri `codex-aciklar-yuksek-hedefler.json` içinde: lexical sürüm sırası, no-index yokluğu ve yanlış hash'i kabul eden çözümün üçü de fail. Bağımsız araç bunlardan bazılarını üretmediği için bu ek tanıklar gereklidir.

## Eşdeğer mutantlar neden zorla reddedilmedi?

- P75:11 en yüksek sürüm seçilirken `s > mevcut` yerine `s >= mevcut`: eşit sürümde aynı metin yeniden atanır. Öğrenciye strict `>` yazdırmak çıktı davranışını ölçmez.
- SP21'in iki sayısı **saat değil**, `MAX_TIMESTAMP_LOOKAHEAD` karakter sınırıdır. Mevcut TIME_PREFIX/TIME_FORMAT zaten doğru damgayı tarif eder; bir fazla karakter aynı timestamp'i üretir. Ürün belgesi tam minimumu tek geçerli cevap saymaz: [Splunk props.conf](https://help.splunk.com/en/splunk-enterprise/administer/admin-manual/10.6/configuration-file-reference/10.6.0-configuration-file-reference/props.conf).
- SG19 priority tespit eşiği değildir. Kullanılan `ProcessingPipeline +` birleştirmesi önceliği sıralamaz. Resmî kaynak da bunu açıklar: [pySigma ProcessingPipeline](https://sigmahq-pysigma.readthedocs.io/en/stable/_modules/sigma/processing/pipeline.html). `tools/test_sigma_splunk_runner.py` kurulu pySigma ile aynı SPL'i doğrular.
- P79'un `64`→`65` mutantlarının üçü yalnız ValueError mesajını değiştirir. Test sözleşmesi bu mesajı sabitlemez; AST tanıkları `codex-aciklar-esdeger-taniklar.json` içinde. Diğer iki mutant 64 bit dışındaki beklenen MessageID'yi guard'dan geçirse bile gerçek 64 bit başlıktaki MessageID ona eşit olamayacağı için yine ValueError verir.
- PS22:5 son Allow grubunu genişleten OR, önceki gruplarda zaten değerlendirilmiş ve karar vermemiş ACE'leri tekrar listeye ekler. Mevcut görev ilk karar veren ACE'de çıkar. Ham araçtaki tek geçiş saklandı; test açığının kesin kapandığı bu satır için iddia edilmez.

Bu satırlar denetçinin sınıflandırmasına sunulur; "hepsi 0 geçen" şeklinde yanıltıcı bir toplam verilmez.

## B · Kod ve altyapı

| No | İş | Kanıt / commit |
|---|---|---|
| 16 md63 | wslpath ve Linux Python çağrısı `--exec` ile doğrudan argv; kabuk tırnak çözümleme sorunu kaldırıldı. Kullanıcı verisine literal tırnak eklemek yerine kabuk devreden çıkarıldı. | `342500a`; `tools/test_ad_ldap_path.py` 2 test temiz, gerçek WSL'de boşluksuz/boşluklu/$ yollar çalıştı. |
| 17 md42 | EL13–EL18 karşılaştırması zaten NativeTests'te vardı. Yalnız o altı dersi seçen açık `--eql-predictions` opt-in seçeneği eklendi. | `0df3a47`; `python tools/test_elastic_lab.py --eql-predictions`: 6 yerel==gerçek ES karşılaştırması temiz. |
| 18 md45 | SigmaSplunkRunner mod/metadata dispatch, hata propagation, timeout/kill, pipeline priority eşdeğerliği ve opt-in gerçek Splunk. Yeni test runtime indirmez/başlatmaz. | `26cf766`; 4 unit + 1 native test temiz. |
| 20 md41 | Native Elastic işi başına 120 sn bütçe, 300 sn tavan, en fazla iki eşzamanlı native iş; yerel motorlar etkilenmez. EL20/EL21 meta bütçesi 120. | `b23011f`; 8 işçiyle iki tur, 12 native adım temiz; tam Elastic 27 ders/170 kontrol temiz. |

SP22 (19/md40), commit `973f247`: dispatch başlangıçları gerçek monotonic saatle aralanır; arama süresi her beklemeye yeniden eklenmez. SID'nin ilk 404 görünürlük yarışı en fazla 10 saniye beklenir; 401 ve diğer hatalar saklanmaz. Kısa gerçek-saat deneyinin dispatch gecikmesi/latans jitter'ı izin verilen zaman payını aşarsa yanlış bir tahmin yerine açık hata verilir. Alarm sayısı taklit edilmez. Eski başarısız tekrar kaydı saklandı; nihai sekiz tekrar ve commit aşağıdaki ek sonuçta belirtilir.

## Tam yol doğrulamaları

| Yol | Ders / kontrol | Sonuç |
|---|---|---|
| Python | 83 / 918 | TEMİZ (ilk yoğun koşuda üç eski ders timeout; sakin yükte tekrar temiz) |
| Bash | 35 / 338 | TEMİZ |
| PowerShell | 29 / 269 | TEMİZ (Windows PowerShell 5.1 modül yoluyla) |
| CMD | 25 / 146 | TEMİZ |
| HTTP | 24 / 175 | TEMİZ |
| JavaScript | 16 / 132 | TEMİZ |
| C# | 17 / 87 | TEMİZ |
| AD | 25 / 168 | TEMİZ |
| Elastic | 27 / 170 | TEMİZ |
| SPL | 23 / 226 | Son tam koşu TEMİZ |
| Sigma | 22 / 126 | TEMİZ |

İlk PowerShell denemesinde host'tan miras gelen PowerShell 7 modülleri Windows PowerShell 5.1 Security modülüyle çakıştı. Modül kurulmadı/değiştirilmedi; yalnız doğrulama komutunun ortamında PSModulePath Windows'un 5.1 modül dizinine alındı. İlk başarısız loglar da saklandı.

## Ortak klasörde dal değiştirme olayı

Kimi canlı oturumu checkout'u `is/kimi-rol-bosluklari` dalına geçirdi; ilk beş test commit'i yanlışlıkla o dalda oluştu. Bunlar Kimi dalı geri sarılmadan Codex dalına ayrı commitlerle kopyalandı. Sonraki commitler geçici index + commit-tree/update-ref kullanılarak **checkout değiştirmeden doğrudan Codex ref'ine** kaydedildi. Kimi'nin dosyaları veya çalışma index'i bu kayıt işlemine alınmadı. Main'e push/merge yok. Kimi dalındaki beş kopya commit: 2546ac8,65de3dd,48d829f,c9b73bd,f994291; Codex karşılıkları yukarıdaki tablodadır.

## SP22 nihai tekrar kabulü

`python tools/test_splunk_dispatch_timing.py --native --repeat 8`: dört altyapı testi temiz; iki gerçek tahminin her biri sekiz kez, toplam 16 kez aynı alarm/bastırma sonucunu verdi. İlk tahmin her seferinde tek alarm; ikinci tahmin her seferinde [1,0,1] alarm üretti. Ham sonuç: `codex-aciklar-sp22-final.txt`. Son tam SPL ve Sigma koşuları da TEMİZ: SPL 23 ders/226 kontrol, Sigma 22 ders/126 kontrol.

CMD ikinci çağrı testinin son hali: `codex-aciklar-cm23-native-double.txt` toplam **24 mutant, 0 geçen**; `codex-aciklar-validate-cmd-final.txt` **25 ders/146 kontrol TEMİZ**. Derleyici Windows ile kurulu .NET Framework csc.exe; yalnız geçici fixture üretir.

## Nihai teslim durumu

- 11 yolun son temiz çıktıları toplam **326 ders, 2755 kontrol**. SPL son koşusu `codex-aciklar-validate-spl-final.txt`, Sigma son koşusu `codex-aciklar-validate-sigma-final.txt`.
- B bölümündeki 16,17,18,19,20 için kod/altyapı kabulü tamamlandı. SP22 commit’i `973f247`.
- A bölümünde 2,3,4,5,6,7,12,13,14,15 hedeflerinde bağımsız aracın çıktısı 0 geçen. 11’in PS22:6 hedefi de 0 geçen.
- 1’de bildirilen lexical sürüm hatası özel bozuk çözümle yakalandı; kalan genel mutant eşdeğer atama. 8,9,10 ve 11/PS22:5 için ham sıfır iddia edilmez; kalan değişiklikler yukarıda tek tek açıklandı. Bu sınıflandırma denetçiye sunulur.
- A derslerinde çözüm/anlatım değişmedi; yalnız 13 ders dosyasının test blokları değişti. B’de EL20/EL21 süre meta’sı değişti.
- Paylaşılan checkout Kimi dalında bırakıldı. Teslimin tamamı `codex/denetim-test-kod-aciklari` ref’inde. Main’e push/merge yapılmadı.
