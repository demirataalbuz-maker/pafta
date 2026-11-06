> TARİHSEL HAZIRLIK KAYDI: Fulcio sonradan kullanıcı onayıyla kuruldu; gerçek kabul geçti. Güncel teslim: CODEX-YENI-ai-savunma-36.md. Aşağıdaki bekleme ifadeleri önceki durumu anlatır.

# S36 — devam/devir kaydı (teslim değildir)

2026-11-03 · Codex. Tam hedef atanan bütün derslerdir; S36 henüz tamamlanmadı. S47 ve S51 kendi gerçek kabul kanıtlarıyla ayrı denetime teslim edilmişti. Bu kayıt S36 için puan veya bağımsız denetim değildir.

Cosign v3.1.4 kullanıcı onayıyla kuruldu,191066624bayt ve yayın SHA256 doğrulandı. Gerçek torch Linear(4,2) model80sentetik örnek/50adım/seed36 ile eğitildi;safetensors kaydı yüklenip parametre eşitliği doğrulandı. Gerçek cosign ile doğru imza geçti,tahrifat ve başka key reddedildi. Bu key-pair alt kontrolüdür,keyless veya tam ders kabulü değildir (`keypair-on-sonda.json`:kabul=false).

Yeni ders `tracks/ai-savunma/lessons/ai-savunma-36-model-imzalama-cosign.md`:üç kusurlu başlangıç,görünür manifest/policy/verify ve açıkça yüklenebilir-model-olmayan sentetik bayt örneği;ilk tablo+NOT,tahmin/çalıştır/fark,hata vitrini,saldırı-savunma eşlemesi ve kapsam sınırı. Setup çalışma kopyası geçici;kalıcılık iddiası yok. Gerçek model dosyası finalde gerçekten üretilir.

Kontroller:
- İlk üç görevde referans3/3pass,starter3/3fail. Görünür dosya Run6/6ok (`pure-*.json`,`gorunur-run-*.json`).
- tahmin.py1tahmin/0şüpheli.
- Gerçek adımı kırpılmış yeni kopyada mutasyon20mutant/0geçen (4+6+10),`mutasyon-son.txt`. İlk rapor testindeki eksik liste parantezi düzeltildi;bozuk ilk tur kabul sayılmadı.
- Üç anlamlı yanlış çözüm ve import/module/getattr/inspect+exec dört kopya yolu reddedildi;boş/sabit ret. `kod_denetimi(...,izin=())` ve attribute-assignment guard kullanılır.
- TAM validate TEMİZ DEĞİL:9kontrolden1gerçek referans deneyi eksik Fulcio nedeniylefail. Sonuç `validate-onay-bekleyen-son.txt`. Üç saf çözüm ve dört starter doğru davranır. Bu fail PASS gibi sunulmadı.
- UI'da çalışma dosyaları gerçek Run ile okundu. Referans gerçek adım Check'i eksik Fulcio nedeniyle reddedildi;tam gerçek/UI kabul yok. Ön koşul eksikliğinin fixture/gerçek deney kanıtı yazması son kaynakta önlendi. Önceki altyapı kaydı gerçek model kabulü değildir.

Runtime kaynakları `sandbox/ai_gercek_ai_savunma_36.py`,`sandbox/s36_private_fulcio.py`,`sandbox/s36_keyless/supervisor.py`. İlk dosya iki bağımsız keypair+keyless koşusu,orijinal/tahrifat/başka key/subject/issuer/root ve gerçek CLI çıktılarını ölçmek üzere yazıldı. LocalFulcio kendi internal Docker ağı ve tam container ID'siyle;nonroot,read-only root,cap-drop,no-new-privileges,resource limits ve yalnız127.0.0.1host portuyla tasarlandı. Bu keyless kaynak henüz gerçek Fulcio'da ÇALIŞTIRILMADI;uyumluluk/sağlık/cert parsing/CLI bayrakları gerçek deneyde doğrulanmalı. Kod varlığı gerçek kabul değildir.

Fulcio v1.9.1Linuxamd64resmi51MBbinary ayrıca kullanıcı onayı BEKLİYOR. SHA256veURL `SAVUNMA-36-KURULUM-ONAYI.md`. İndirilmeyen installer `tools/ai_s36_fulcio_kur.py`;--kontrol eksik/exit2,otomatik indirme yok. Mevcut S51Dockerimajı yeniden kullanılacak,yeni taban/paket indirme planlanmıyor. Kullanıcının Cosign191MBonayı Fulcio'ya genişletilmedi.

Kalan zorunlu işler:Fulcio onayı/kurulumu;gerçek yerel OIDC+Fulcio sağlık/imza/sertifika/root/kimlik/issuer kontrollerini koşturup hataları gidermek;iki gerçek koşuda karar tutarlılığı ve yalnız kendi kaynak cleanup'ı;CLIvalidateTEMİZ;UIgerçekRun/Check;kendi kontrollerini tekrar doğrulayıp Opus'a teslim. CT/Rekor/timestamp kurulmaz:private-lab keyless ile publicSigstore şeffaflığı karıştırılmayacak. Token/privatekey kanıta yazılmayacak. Ders bu işler bitmeden denetime-hazır/bitti olmayacak.

Ortak track'te yalnız20'den sonra36 eklendi;32/33/34/35 korundu. Engine/web değiştirilmedi. Commit/push yok. Aktif bağımsız kurulum süreci yok. Paylaşılan pano8798sunucusu kullanıcı için açık bırakıldı;bu lab kabul sunucusundan ayrıdır.

Genel görev dağılımı:14:09kararındaki19/18dağılımın26öğe karşılığı eskiüreticide kaybolmuş. Kalıcı açık devir dosyası ve dolu sorumluları koruyan üretici/canlıJS düzeltmesi yapıldı (`yeni-dersler-atamalar.json`). Kesin11sorumlu,26belirsiz;kalan atamalar UYDURULMADI. Sadece bilinen47/49/51/36Codex;50/52/32/33veeskiClaudeatamaları korunur. Bu yüzden tüm37kalem tamamlandı iddiası yok.
