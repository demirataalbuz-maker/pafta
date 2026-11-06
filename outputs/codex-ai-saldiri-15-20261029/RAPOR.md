# ai-saldiri-15 — gerçek embedding ve bütçeli bağlam
Uygulayıcı kabulü; bağımsız denetim değil.29Ekim2026.

Değişen: ai-saldiri-15 ders sonuna anlat/gerçek görev index8;sandbox/ai_gercek_ai_saldiri_15.py;web/data/ai-saldiri-15-baglam.txt. Eski adımlar korundu. Kurulum/ortakmotor/commit/push yok.

Görünür sentetik dosya ve ayrı kalıcı öğrenci kopyası; sorgu ve belgeler kurulu all-minilm:22m ile gerçekten gömülür. Boyut/sonlu/sıfır olmayan vektör kontrolü yapılır; ham gömmeler öğrenci deney alanında JSON'a yazılır. Cosine benzerliği0..100tamsayıya taşınır; olasılık/güven puanı değildir. Manipüle kol dış kaynaktan gelen sahte skora güvenme kusurunu simgeler; sahte100 gerçekembedding skoru olarak sunulmaz. Öğrenci karakter bütçeli seçim ve farkını yapar; iki kol gerçekQwen yanıtına gider. Karakter bütçesi token bütçesi değildir. Kanıt kaybı/işaret aktarımı/modelin uyması farklı ölçümlerdir; saldırı başarısı geçme koşulu değil.

Hedef validate1ders/9kontrol TEMİZ. kabul.py/summary.json9/9: referansPASS;starter/boş/sabit+özgün sorgu kaybı,erkenbreak,tersfark mutantlarıFAIL. Test içinde eski mutantlar ve yeni sorgu/bütçeörnekleri. ÇalıştırOK/kabulfalse;eksikOllamaFAIL/kabul yok. Farklı süreç/dizinlerde kalıcılıkpersistence.jsonfixturekontrolüyle doğrulandı. Model/embedding sürüm-digest/cihaz/bellek,gerçekvektörler/skorlar,hamyanıtlar/hatalar kanıtta.

Gerçek referans bulgu: kanıt cosine0.6355→82,diğer0.0964→55,ekbelge0.6112→81. Kusurlu dışskor100ile temiz seçim[kanit,diger]94karakter,manipüle[zehir,diger]123karakter;135bütçede kanıtçıktı. Bu küçük veri seti bulgusudur; herretriever için evrenselsonuç değil.

Son UI ve grup regresyonu eklenecek. İkinci cihaz/bağımsız denetim yok.

UI Kontrol29/29: outputs/codex-kirmizi-seri-20261029/ui-data/ai-kanit/saldiri-15-baglam-1793280246858.json. İlk UI Çalıştır HTTP400 ile başarısızdı, gerçek kabul sayılmadı; ham hata gövdesi o ilk koşuda alınmadığı için kök neden kanıtlanmadı. Son kod embedding HTTPError gövdesini kabulfalse hata kanıtına yazar; 400 yeniden denenmez. Aynı veriyle ayrı sonraki UI Çalıştır saldiri-15-baglam-1793280711994.json, bütün kontrollertrue/kabulfalse,ham vektör dosyası/iki gerçek yanıt göründü. Bu yeniden deneme ilk hatanın kök nedeninin çözüldüğü anlamına gelmez. 14/15grup regresyonu2ders/19kontrol TEMİZ. Bağımsızdenetim bekliyor.
