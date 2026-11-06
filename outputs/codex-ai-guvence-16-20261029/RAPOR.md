# ai-guvence-16 / kutu104 — Gizlilik tehdidi ve gerçek üyelik kanıtı
Uygulayıcı kabulü; bağımsız denetim değildir. Yeni kurulum/commit/push yok.

Değişen: tracks/ai-guvence/lessons/ai-guvence-16-*.md sonuna anlat/gerçekgörev index7;sandbox/ai_gercek_ai_guvence_16.py;web/data/ai-guvence-16-gizlilik.txt. Eski adımlar korundu.

Gerçek CPU-PyTorch MLP,24girdi/64gizli/2sınıf;100Adam adımıyla autograd eğitimi. Rastgele özellik/etiketler sentetiktir;loss/logits/olasılıklar gerçek eğitim/inference çıktısıdır. Her3tekrarda ayrıshadow vehedefmodel toplam6gerçekeğitim yapılır. Eşik yalnız shadow üyeliklerinden seçilir;hedef üyeliği eşik ayarlamaz. Öğrenci tehditmodeli gerçek erişimi tanımlar,gerçek hedefolasılıklarıyla üyelik kayıtlarını ölçer,0.5tabandoğruluk ve TPR-FPRavantajıyla raporlar. Pozitifavantaj/saldırıbaşarısı geçme şartı değildir.

ReferansCLI3tekrarda ortalama üyelik doğruluğu0.885417,taban0.5,avantaj0.770833buldu. UIÇalıştır(seed2026) ortalama0.765625,avantaj0.53125buldu. Test görülmemişrastgeleseed kullanır;çıktımetni veya sabitbaşarı karşılaştırılmaz. Bu küçük sentetik modelin gözlemidir;sohbetmodeli/gerçekkişiselveri gizliliğine genellenmez.

CLI9/9beklenensonuç:referansPASS;starter/boş/sabit+bilinmeyengüvenlikkapsamınıkabul,TPRyiavantajsayma,tabandoğruluğuyoksayma mutantlarıFAIL;RunOK/kabulfalse,eksikTorchyorumlayıcısıERROR(başarı değil). Hedefregresyon1ders9kontrol TEMİZ. persistence.jsonfarklısüreç/cwddeöğrenciayarının korunduğunu doğrular(fixturealtyapıkontrolü).

Ders ekranı başlangıçikikezreddedildi,referans19/19PASS:ui-data/ai-kanit/guvence-16-gizlilik-1793299753019.json. Run tümkontrollertrue/kabulfalse:guvence-16-gizlilik-1793299803584.json. İkisi outputs/codex-guvence-bos-20261029 altındadır. Kalıcıgirdi calisma/ai-guvence-16/gizlilik.json;dışeditör/Python ile değiştirilebilir. UIhenüzMarkdownlinkitıklanabilir yapmıyor;hamdosya sunucuda /data/ai-guvence-16-gizlilik.txt. Örnekler/etiketler/logits/olasılıklar/loss/versiyon/cihaz/ağırlıkhashleri gerçekJSONkanıtta;Run modelağırlıkları kendi deney klasöründe kalır. Testtempweights kapanınca temizlenir,kanıtJSONu kalır. TorchCPU,sunucuGPUmodeli kullanılmaz.

İkinci cihaz/bağımsızdenetim henüz yok. Bu kutunun tamamlanması diğer14kutunun bitmesi anlamına gelmez.
