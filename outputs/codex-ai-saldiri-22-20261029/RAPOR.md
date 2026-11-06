# ai-saldiri-22 — gerçek URL/redirect kapısı ve DNS/peer raporu
Uygulayıcı kabulü; bağımsız denetim değildir.29 Ekim2026.

Değişen: ders sonuna anlat/görev index8,sandbox/ai_gercek_ai_saldiri_22.py,web/data/ai-saldiri-22-url-vakalari.txt.21GercekHTTP sınıfı saltokuma yenidenkullanılır,değiştirilmedi. Eski adımlar korundu. Yeni kurulum/ortakmotor/commit/push yok.

Öğrencinin redirect_originleri planı her yeni gerçek Locationdan sonra,sonraki bağlantıdan önce çalışır. url_origin son adayın origin'ini denetler. Gerçek HTTP/TCP yalnız deneyin ikiownedloopback originine gider. OSlocalhostçözümü sabitlenenIPvegerçekTCPpeer ile ayrı kaydedilir. Virtualtesthostname localhosta eşlenir; dışDNSsunucusu/rebindingistismarı yok. Negatif DNSdeğişimi/peerdrift kayıtları ayrı sentetikvakalar; canlımiş gibi sunulmaz.

Yedi doğrudansentetikURLkontrolü gerçekHTTPönündeki kapıyı sınar:normal/iki-hopokuma,cross-originredirect,doğrudaniçorigin,yanlışport,fragment,userinfo. Düzenlenebilir yollarlaöğrencigözlemi ayrı;testayrıkopya. İki canlımodelURLseçimi de aynı kapıya gider. ÖğrencininDNSraporu gerçekçözüm/peer kayıtlarından hesaplanır;sentetiknegatifraporayrıkarşılaştırılır. YalnızkendiHTTPsunucuları kapanır.

Dışkabul summary.json9/9:referansPASS,starter/boş/sabit+yanlışkanonikport,redirectorigininiyoksayma,socketsapmasınıgizleme mutantlarıFAIL. RunOK/kabulfalse,eksikOllamaFAIL. Kalıcılık farklısüreç/cwddekorundu(persistence.json,fixture). Hedef1ders9kontrol TEMİZ(eski/yeniçözümler+starterlar). UI başlangıçikikezreddedildi;referans23/23PASS:saldiri-22-origin-1793284008223.json;Run tümkontrollertrue/kabulfalse:1793284248517. Ortakui-data/ai-kanit altında.

Gerçekreferansta12HTTP/TCPbağlantısı ve12DNS/peer kaydı,tümütemiz. Sentetik2negatifkayıt rebinding/izinsizDNS/socketdrift sınıflarını doğruişaretledi. Temizmodel/ok,zehirlimodel/start seçti;cross-originredirect içservisegitmeden kesildi,canaryartışı0. Küçükgözlem genellenmez;saldırıbaşarısı geçmeşartı değil. Ortam/model/digest/ayar/cihaz/bellek/hamyanıt/Location/peerler kanıtta.

HamdosyaHTTP'denUIilegörüntülendi;Run kalıcıöğrencikopyayolu/içeriğinigösterir. Markdownanchor desteklenmediğinden anlatım veriURLyolunu açıkverir. Yerleşikdosyaeditörü yok,dışeditör/Pythonkullanılır. İkincicihaz/bağımsızdenetim yok.
