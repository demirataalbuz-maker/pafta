# AI54 — güvenlik ML dedektörü evasion teslimi

2026-11-03 · Codex yazdı, kendi kontrollerini yaptı; claude-opus denetimi bekliyor. Puan verilmedi. Dalga3 plan-saldiri-8'in somut dersi ai-saldiri-54. ai-saldiri-53 VLM dersi için Codex tarafından panoda rezerve; henüz yazılmış ders sayılmaz.

## Uygulama
Kurulu sklearn1.9.1 ile gerçek TfidfVectorizer(ngram1,2,norm=l2)+LogisticRegression(C4,max_iter300,seed54) fit edildi. Train48/test12 elle üretilmiş sentetik metin; birebir metin sızıntısı yok, fakat aynı dar sentetik kurgu: gerçek dünya bağımsız veri/genelleme iddiası yok. Hiç URL açılmaz/e-posta gönderilmez; adresler.invalid.

Öğrenci üç fonksiyon yazar: append-only/karakter bütçeli aday üretimi; callback ile query-bounded minimum-risk seçimi; doğru ASR ve kontrol false-positive raporu. Son gerçek görev üç fonksiyonu gerçek predict_proba üstünde çalıştırır. API yalnız black-box skor callback'i verir. Kaynak metin/URL korunur; bu phishing işlevini temsil eden dar lab vekilidir, gerçek kullanıcının algısını koruma kanıtı değildir.

Q1/3/4 için12test örneği,toplam36arama. Gerçek saldırı query96,ayrı değerlendirme72,ikinci model karşılaştırması24: maliyetler karıştırılmaz.168birincil model çağrısının tam input/skor/role audit'i kayıtta. Ağırlık/IDF/vocabulary hash'i,veri hash'i,model ayarları,sürümler/cihaz,train/test/adaylar/queryler/sonuçlar kanıtta. İkinci gerçek fit edilmiş model sabit6risk sözcüğü ve norm=None kullanır; yalnız mevcut benign suffix'lere karşı dar karşılaştırma. Genel sağlam savunma/LLM veya gradient iddiası yok.

## Gerçek sonuç
Bu koşuda başlangıçta6/6phishing yakalandı. Q1ASR0/6;Q3veQ4ASR6/6. Meşru6kontrolde önce/sonra false-positive0. Bu sayılar yalnız bu sentetik veri ve model içindir; saldırı başarısı PASS şartı değildir. Dar savunma modelinin önce/sonra skorları ayrıca kanıtta. Random model çıktısını sabit metne eşleyen test yok.

## Öğretim ve görünür dosyalar
dedektor/ornek.json,corpus.json,README.md setup ile geçici çalışma kopyasına gelir. Corpus48train/12test sentetik metnin okunabilir kopyasıdır; gerçek deney bağımsız veri kurucusundan fit eder. Kopyayı değiştirerek gizli kabul sonucu değişmez. Kopya yalnız bir çalıştırmada düzenlenebilir; kalıcılık iddiası yok. UI Run ile ornek.json okundu, ardından gerçek fit çalıştı. İlk tablo,NOT,3kusurlu starter,tahmin→çıktı→fark,yazılı hata vitrini,saldırı↔savunma eşlemesi,gerçek kanıtı yorumlama ve sınır cümlesi var.

## Kabul kontrolleri
- python -X utf8 tools/validate.py ai-saldiri-54 →1ders9kontrol TEMİZ(4solution,4starter,1tahmin).
- docs/denetim/araclar/tahmin.py . ai-saldiri-54 →1tahmin0şüpheli. İlk sandbox denemesi geçici klasör erişim hatasıydı; doğru izinli koşu geçti,ilk hata PASS sayılmadı.
- Resmî mutasyon.py KURALLAR/mutantlar üreteci aynen,3saf görevde seri:40üretilen0geçen. İlk koşuda7geçen vardı;0/1skor sınırları,son eşik,tuple/string tür kontrolleri eklenerek tamamı yakalandı. Testler zayıflatılmadı; gerçek final40mekanikmutasyona dahil edilmedi.
- Gerçek final: boş/sabit RET,karakter bütçesini yok sayma/en yüksek risk seçme/yanlış ASR paydası3/3RET,kopya import/attribute/getattr/inspect+exec4/4RET. Ret koşularında kabultruekanıt yok.
- ai_lab.kod_denetimi(src,ref_adaylar/ref_en_az_risk/ref_olcum_raporu/kanit_yaz,izin=()) çağrılıyor. Saf testlerin eq/raises sonuçları da kabulall(checks)'e katılıyor; başarısız ön kontrol gerçek kabul yazmıyor.
- UI Check65/65,gerçek kabul receipt'i. UI starter RET; Run gerçek fit + kabulfalse ve görünür JSON. Ekran görüntüsü Desktop/pafta-ai54-ui-kabul-20261103.png.
- Hedefli regresyon: mevcut AI47/49/51'in model çalıştırmayan görev/tahmin kontrolleri21/21. Bunların ağır gerçek model/CVE deneyleri veya tümAIyolu yeniden koşulmadı; böyle bir PASS iddiası yok.

## Dosya ve altyapı
Yeni ders/modül/fixtureler ve ai-saldiri/track.json'a yalnız54kaydı. Son görev motorai-gercek,gereksinimtorch mevcut koşucuda.ai-venv yorumlayıcısını seçmek içindir;gerçek araç sklearnCPU. web/app.js'te yalnız1satırdaki2sabit rozet metni düzeltildi: yanlış“torchmodeli”→“yerelPython deneyi”,yanıltıcı“fixtureyok”→“canlıölçüm”. Koşucu/API/motor/çalıştırma davranışı değiştirilmedi. CRLF korunarak byte düzeyinde dar metin değişimi yapıldı. Kurulum/indirme bu ders için yok. Kalıcı kanıtlar outputs/yeni-ai-saldiri-54 altında;teslim.json receipt yolları ve dosyaSHA256listesidir.

## Açık işler
VLM53 için kullanıcı SmolVLM256M rev7e3e67ed indirmesini ayrıca onayladı;indirme ayrı outputs/vlm53-kurulum kaydıyla sürüyor. Bu AI54kabulüne dahil değildir. Multimodal savunma ayrı Codex işidir; OCRaraç kararı/kurulum kabulü yapılmadı.7yeniAIdersten yalnız bu bir ders teslim ediliyor;diğerlerinin tamamlandığı iddia edilmez. İkinci masaüstü/Linux/macOSkabulü yok. Commit/push yok. Bağımsız denetimi ve puanı yalnız Opus verir.


## Ek kaynak koruması doğrulaması

2026-11-04: İçe aktarılan modülün namespace alanlarına yazma ve fonksiyon __globals__ erişimi ders içindeki AST kontrolüyle reddediliyor. M.deney yaması RET; kabultrue kanıt üretilmedi. Meşru referans aynı gerçek deneyle yeniden PASS oldu (53:67/67,54:65/65). Ortak ai_lab/engine/runner değişmedi. Yeni sonuç reference-guard-final.json ve modul-yama-ret.json; teslim.json yeni CLI receipt ve güncel kaynak hashlerini gösterir. Önceki UI ölçümü aynı çözüm/deney fonksiyonlarıyla yapılmıştı.
