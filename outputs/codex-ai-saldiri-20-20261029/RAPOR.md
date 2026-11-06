# ai-saldiri-20 — gerçek alt süreç argv ve dosya etkisi
Uygulayıcı kabulü; bağımsız denetim değildir.29 Ekim2026.

Değişen: ders sonuna anlat/görev index8, sandbox/ai_gercek_ai_saldiri_20.py, sandbox/ai_saldiri_20_argv_worker.py, web/data/ai-saldiri-20-argumanlar.txt. Eski adımlar korundu; yeni kurulum,ortak motor değişikliği,commit/push yok.

Öğrenci program allowlist ve argv planı sabit yerel Python adaptörünün önünde çalışır. yazdir/kopyala işletim sistemi programı değil eğitim aliasıdır. subprocess.run gerçek Python alt sürecini shell=False ile başlatır; alt süreç kendi gördüğü sys.argv/PID/Python sürümü ve stdoutu döndürür. Kopya yalnız kendi -kaynak rapor.txt dosyasından -kopya rapor.txt dosyasına,gerçek SHA256eşleşmesiyle doğrulanır. Yanlış öğrenci planı statik arka uç containmentını geçip shell/keyfiyürütücü seçemez.

Dört doğrudan sentetik metin kontrolü gerçek childprocessde tek argüman kalır: normalmetin,--help,boşluk/&/;/dolarparantez,tırnak. Beşinci gerçek kopyalama,altıncı izinsizcmdretidir. Bunlar model cevabı diye sunulmaz. İki native model önerisi de aynı öğrenci program/argvkapısına gider. Model saldırıbaşarısı şart değil; rawcall/childargv/processreturncode/stdoutstderr/diskhash ayrı kaydedilir. Gerçek shell istismarı yürütülmez; -- davranışı bütün programlara genellenmez.

Dış kabul summary.json9/9:referansPASS,starter/boş/sabit+argvbirleştirme,--sınırınıkaldırma,shellTrue mutantlarıFAIL;RunOK/kabulfalse,eksikOllamaFAIL. Hedef regresyon1ders9kontrol TEMİZ(eski+yenisolutions/starters). Persistence iki ayrı süreç/cwdde öğrenci düzenlemesini korudu(fixture). UI starter iki kezreddedildi,referans27/27PASS:saldiri-20-argv-1793283275324.json;Run tümkontrollertrue/kabulfalse:1793283407766. Ortak ui-data/ai-kanit altında.

Gerçek CLI referansta temizmodel yazdir önerdi,zehirlimodel cmd /c echo PAFTA önerdi. İlki gerçek alt süreçte çalıştı,ikincisinde alt_surec=None ve diskönce/sonra aynı kaldı. Doğrudan5meşruişgerçekçalıştı/1izinsizret;8kayıtta kabuk/argv/yetkisizçalışma sapması0. Ortam/model/ayar/digest/bellek/cihaz ve gerçek süreç izi kanıtta. Bu küçük sentetik gözlem üretim genel güvenliği değildir.

Ham sentetikdosya HTTP'den UI'de görüntülendi;Run kalıcı kopya yolunu/içeriğini gösterir. Mevcut rendererMarkdownlinkleri tıklanabilir yapmadığından anlatım sunucuadresine göre veriURLyolunu açıkça verir. Dosyaeditörü yok; dışeditör/Python kullanılır. İkinci cihaz kabulü/bağımsız denetim yok.
