# S36 — gerçek model imzalama ve yerel keyless teslimi

2026-11-03 · Codex yazdı; bağımsız claude-opus denetimi bekleniyor. Puan verilmedi. Bu bütün müfredatın tamamlandığı anlamına gelmez.

## Sonuç
Referans gerçek CLI doğrulaması TEMİZ9; ders ekranı Check74/74 geçti. Run iki gerçek koşu yaptı ama kabul=false olarak gösterildi. Her koşuda gerçek torch Linear(4,2) model80 sentetik örnekte50adımCPU'da eğitildi,safetensors ağırlığı yüklenip eşitliği doğrulandı. Seed36ve37 ile ayrı model,anahtar,issuer tokenı ve Fulcio CA kökü kullanıldı;karar dizisi iki koşuda aynıydı. Accuracy alanı bu80 eğitim örneğinin doğruluğudur,ayrı test kümesi başarısı değildir.

| Gerçek verify vakası | İki koşudaki sonuç |
|---|---|
| Key-pair doğru artifact/doğru key | Geçti |
| Key-pair tek bayt tahrifat | Reddedildi |
| Key-pair başka public key | Reddedildi |
| Keyless doğru artifact/subject/issuer/root | Geçti |
| Keyless tek bayt tahrifat | Reddedildi |
| Keyless başka subject | Reddedildi |
| Keyless başka issuer | Reddedildi |
| Keyless başka root | Reddedildi |

Resmi Fulcio gerçekten sertifika verdi:her koşuda trustBundle ve signingCert HTTP200 kaydı var. Cosign önce özel trusted-root dosyasını oluşturdu,imza sırasında bu kökü kullandı;varsayılan base64 public sertifika PEM'e çözüldü. Keyless çağrıda --key verilmedi;ephemeral imza anahtarını cosign üretti. Gerçek leaf cert SAN email ve issuer extension'ı okunup öğrenci politikasına verildi. Private key,parola veya JWT tokenı kanıta yazılmadığı son3kanıtta ayrıca tarandı.

## Özel lab sınırı
Bu private test OIDC/Fulcio akışıdır. Test issuer gerçek kişinin kimliğini kanıtlamaz. CT/Rekor/timestamp hizmeti kurulmadı;private doğrulamadaki insecure-ignore-tlog ve insecure-ignore-sct seçenekleri açıkça kayıtta/derste anlatılır. Bu bir public Sigstore transparency veya timestamp kanıtı değildir. İmza da modelin zararsızlığını kanıtlamaz. Deprecated legacy bayrak uyarıları ham logda tutuldu;bu sürümdeki davranış doğrulandı,gelecek sürüm uyumu iddia edilmedi.

## Kaynak ve kurulum
Kullanıcı iki indirmeyi ayrı ayrı onayladı: resmi cosign v3.1.4 Windowsamd64(191066624bayt)ve resmi Fulcio v1.9.1Linuxamd64(50925712bayt). SHA256lar yayın metadatasıyla eşleşti. Toplam dosya boyutu241992336bayt;bu ağın toplam trafiği veya ölçülmüş fiziksel disk kullanımı değildir. Kurulum kayıtları outputs/s36-kurulum/kurulum.json ve fulcio-kurulum.json. Ücretli servis/hesap,SaaS veya yeni pip/venv/taban imajı indirmesi yok.

Runtime mevcut yerel pafta-ai-s51:mlflow-2.1.1 imajını kullanır;MLflow servisini çalıştırmaz. PAFTA_S36_IMAGE ile başka mevcut linux/amd64taban seçilebilir;kimliği inspect ile çözülüp sabitlenir,pull=never. Docker root salt okunur,UID10001,cap-dropALL,no-new-privileges,512MiB RAM/2CPU/128PID sınırları gerçek inspect kaydında doğrulandı. Bunlar ölçülmüş peak bellek değerleri değil sınır ayarlarıdır. /tmp yalnız bu lab binary'si için exec tmpfs;host dizini/socket mount yok. Container network=none,hosta Docker portu yayınlanmadı.

Windows'tan doğrudan internal Docker ağına bağlantı çalışmadığı için localhost HTTP geçidi sınırlı Fulcio API isteklerini docker exec stdin üzerinden container loopback'indeki gerçek servise iletir. Sahte cert cevabı üretmez. Yalnız kendi geçidi,containerID'si ve token dosyası kapatılır;mevcut DockerDesktop/WSL/diğer containerlar/model ve öğrenci verileri korunur. Her kabul kaydında temizlendi=true. Windows laptopta denendi;ikinci masaüstü/Linux kabulü yapılmadı.

## Kendi kontrollerim
- .ai-venv/Scripts/python.exe -X utf8 tools/validate.py ai-savunma-36 → TEMİZ9;outputs/yeni-ai-savunma-36/validate-son.txt.
- tahmin.py . ai-savunma-36 →1tahmin,0şüpheli.
- Gerçek adımı çıkarılmış kopyada mutasyon.py <kopya> --en-cok1000 ai-savunma-36 →20mutant,0geçen(4+6+10);mutasyon-son.txt.
- Boş/sabit,3anlamlı yanlış çözüm ve4kopya yolu(import/module/getattr/inspect+exec)reddedildi. İki binary kurulu durumdayken de reddedildikleri doğrulandı. Resmi kopya_sonda.py ile oracle importu fail/korunuyor;kopya-son.txt.
- İlk3görevde solution3/3pass,starter3/3fail;görünür dosya son Run6/6OK(gorunur-run-son-*.json). Gizli testler fixture'dan ayrı. Geçerli sentetik weight[2,4]/bias[2] örneği resmi safetensors yükleyicisiyle açıldı;eğitim çıktısı diye sunulmadı.
- Sekiz vakanın256bool sonuç kombinasyonu aynen korundu;yalnız kullanıcıya verilen yüzlerce tekrar satırı üç toplu kontrole çevrildi. Ölçütler azaltılmadı.
- Ders ekranı referans Check74/74gerçek kabul;Run gerçek ama kabulfalse. Önceki eksik Fulcio UI/CLI denemeleri fail olarak korundu. İlk başlangıç hataları(ro-roota cp,noexec tmpfs,metrics-host bayrağı,internal network,özel trust root,base64cert)giderildi;başarısız denemeler kabul sayılmadı.
- python -Xutf8 tools/test_sinav.py →12testOK. Bütün yolların regresyonu bu teslimde yeniden çalıştırılmadı.

## Değişen dosyalar
- tracks/ai-savunma/lessons/ai-savunma-36-model-imzalama-cosign.md
- tracks/ai-savunma/fixtures/ai-savunma-36/README.md ve veri/model.safetensors,manifest.json,policy.json,verify.json
- sandbox/ai_gercek_ai_savunma_36.py;sandbox/s36_private_fulcio.py;sandbox/s36_keyless/supervisor.py
- tools/ai_s36_kur.py;tools/ai_s36_fulcio_kur.py
- tracks/ai-savunma/track.json:yalnız20'den sonra36 eklendi,diğer ajan kayıtları korundu.
- Bu rapor,onay belgesi,tarihsel DEVAM raporunun durum bağlantısı,tracker ve puansız denetim kuyruğu.

Engine/web davranışı değiştirilmedi. Commit/push yok. Hata geçmişi ve fixture/lifecycle sağlık sondaları gerçek kabulden ayrı tutuldu. Son kabul ekranı C:/Users/demo12/Desktop/pafta-s36-ui-kabul-20261103.png.

## Genel görev devamı
19:13ortak pano kullanıcı kararıyla26sahipsiz plan Codex'e verildi. Kalıcı atama kaydı30Codex/7Claude olarak güncellendi;Claude7korundu. 37PLANbaşlığı37yazılmışders değildir:modüller/klasik konular alt derslere bölünecek,örtüşmeler iki kez sayılmayacak. S36teslimi bu genel hedefin tamamı değildir;diğer planlar sırayla ele alınacak. S47/S51 de Opus denetiminde.

## Gerçek kanıtlar / SHA256

- `C:\Users\demo12\Desktop\pafta-s36-gercek-kabul-son-20261103\ai-kanit\savunma36-kabul-1793722494372.json` · `2062c23f1ae580bb88c65941d9624cc51ea5dd3d4b13b8d4913c1b52f48e5052`

- `C:\Users\demo12\Documents\Pafta-AI-GercekLab\outputs\yeni-ai-savunma-36\ui-data\ai-kanit\savunma36-kabul-1793722508149.json` · `fdbc3c78c45517836167273c75a5e963f6f0e5bfc0171ed3dd78257703830710`

- `C:\Users\demo12\Documents\Pafta-AI-GercekLab\outputs\yeni-ai-savunma-36\ui-data\ai-kanit\savunma36-run-1793722687261.json` · `39ed81f5e4c85036374ea399f146c69d1bfbcebd31c8d94779346a91a7752d5f`
