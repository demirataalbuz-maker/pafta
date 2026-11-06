# S36 — ONAYLANDI ve KURULDU

2026-11-03:Kullanıcı Cosign191MB ve Fulcio51MB indirmelerini ayrı ayrı onayladı. İki binary indirildi ve yayın SHA256'sıyla doğrulandı. Gerçek key-pair+private keyless CLI ve ders ekranı kabulü geçti. Ayrıntı CODEX-YENI-ai-savunma-36.md. Kurulum kaydı tek başına deney kabulü sayılmaz.

| Araç | Resmî kaynak | Dosya boyutu | SHA256 |
|---|---|---|---|
| cosign v3.1.4 Windowsamd64 | https://github.com/sigstore/cosign/releases/download/v3.1.4/cosign-windows-amd64.exe | 191066624 | cbe953787074611f1334cbf37dc1cf953995bb8c45398eb4fc7bb781d29c1f2a |
| Fulcio v1.9.1 Linuxamd64 | https://github.com/sigstore/fulcio/releases/download/v1.9.1/fulcio-linux-amd64 | 50925712 | d851e6fcc33bad57a08435e41fe082d8cc466f99c57d2fae156e82941f84ea31 |

Her ikisi ücretsiz Apache-2.0. Yalnız proje .deps altına kuruldu;PATH/OS trust store değiştirilmedi. Yeni paket veya taban imajı indirilmedi. Mevcut Docker imajı kullanıldı;MLflow servisi başlatılmaz. Fulcio Linux binary bu container içinde çalışır,Windows'ta doğrudan yürütülmez. Installerlar tools/ai_s36_kur.py ve ai_s36_fulcio_kur.py;--kontrol indirme yapmaz,--indir yalnız açık onayla çalışır;ders düğmesi kurulum/pull yapmaz.

Son runtime network=none,ro-root,nonroot,cap-dropALL,NNP ve kaynak limitlidir. Dosyalar yalnız tmpfs'e aktarılır;host mount/port yok. Cosignlocalhost HTTP isteği kendi docker-exec geçidiyle gerçek Fulcio'ya taşınır. Private lab OIDC kullanılır,dış kimlik servisine veri gönderilmez. PublicCT/Rekor/timestamp güvencesi yok;atlanan adımlar derste ve ham komutlarda açık. Root yalnız deney dosyasından pinlenir,Windows sertifika deposuna eklenmez. Yalnız kendi container/geçit/token kaynakları kapanır,kullanıcı kaynakları ve kurulumlar kalır.

Kaynaklar:https://github.com/sigstore/cosign/releases/tag/v3.1.4 , https://github.com/sigstore/fulcio/releases/tag/v1.9.1 . Toplam dosya boyutu241992336bayt;toplam ağ trafiği/physicaldisk/peakRAM ölçümü değildir. Ham kurulum kayıtları outputs/s36-kurulum/ altında.
