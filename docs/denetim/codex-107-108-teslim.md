# Purple 107–108 · Codex teslim kaydı · 30.10.2026

Yeni görevin dosyası CODEX-107-108-GOREV.md uygulandı. Bu kayıt yazarın kendi kontrolleridir; bağımsız denetim Claude tarafından yapılacak. Puan, karar ve eksik listeleri değiştirilmedi. Commit/push yapılmadı; engine/web davranışı değişmedi. Yeni kurulum/indirme veya ders kodunda ağ çağrısı, parola kırma, gerçek kimlik bilgisi kullanımı yok.

107 / PU16: görev iki satır 28 and→or mutantı yeniden üretildi (önce toplam32,1 geçen). Eşdeğer değildir: root dışı svc-backup hedefi, NOPASSWD, arguments=/var/log/pafta/* ve dangerous_if_unrestricted=True durumunda serbest=False'dur. Doğru çözüm orta, mutant yüksek öncelik verir. Bu karşı örnek teste eklendi; çözüm ve sözleşme değişmedi. Son validate TEMİZ (7 kontrol), tahmin1/0şüpheli, mutasyon32/32yakalandı. Ders regresyonu8testOK. pu16-and-or-karsi-ornek.json belirli mutantın bu vaka nedeniyle kaldığını gösterir.

108 / PU17: önceki dosyanın 1–4. görevleri dahil bütün ön eki byte düzeyinde korundu; özgün SHA256 pu17-once-sha256.txt. Sona anlatım ve beşinci görev eklendi: NetNTLMv2 user::domain:challenge:proof:blob; TGS/AS-REP etype23 ve gösterilen17/18 AES export profilleri; bağlamla LM ve belirsiz32hex ayrımı. Bunlar tam protokol/kriptografik doğrulama değil, açıkça sınırlandırılmış biçim profilleridir. Alan uzunlukları ve eğitim boyut sınırları sözleşmede ayrıdır. Responder adı anlatılır ama araç kurulmaz/çalıştırılmaz, ağ yakalama veya zehirleme yapılmaz.

Yeni görev ham değerleri rapora taşımadan tur/kaynak/etype/savunma bulguları ve parola_dogrulandi=False döndürür. Kaynak çelişkisi, bilinmeyen kaynak uyarısı, RC4 politika incelemesi, AS-REP preauth bağlam sınırı ve LM placeholder'ın varlık/boş parola kanıtı olmaması sınanır. Kullanıcı/domain/SPN/proof/challenge/cipher raporda yoktur. Görünür ag_bicimleri.json elle üretilmiş sentetik biçim verisidir, geçerli oturum veya kriptografik test vektörü değildir. Mevcut hazirla dosyayı geçici klasöre kopyalar; Run yalnız güvenli raporları gösterir. Kalıcılık iddia edilmez.

Değişen dosyalar:
- tracks/purple/lessons/pu16-linux-yetki-yukseltme-analizi.md (tek karşı örnek testi)
- tracks/purple/lessons/pu17-parola-ozeti-bicimleri.md (yalnız sona ek)
- tracks/purple/fixtures/pu17_hash_formats/ag_bicimleri.json ve README.md
- sandbox/hash_formats_lab.py (yalnız DOSYALAR listesine yeni fixture)
- tools/test_hash_formats_lesson.py (görev sayısı dört→beş; eski testler korunur)
- docs/denetim/puanlar.json (yalnız107/108 duzeltme alanı; önceki duzeltme geçmişi içinde korunur)

PU17 kontrolleri:
python -X utf8 tools/validate.py pu17 → TEMİZ,11kontrol (1tahmin,5çözüm,5starter).
python -X utf8 docs/denetim/araclar/tahmin.py . pu17 →1tahmin,0şüpheli.
python -X utf8 docs/denetim/araclar/mutasyon.py . --en-cok 1000 pu17 →117mutant,0geçen; eski görevler64, yeni görev53.
python -X utf8 tools/test_laptop_quality.py →pu17 reference pass,10yanlışçözüm reddedildi. Bu araç mevcut görev4'ü sınar; yeni görev5 validate/mutasyon ve ders regresyonuyla ayrıca sınandı.
python -X utf8 tools/test_hash_formats_lesson.py →8testOK; yeni görev dahil referanslar geçer/starterlar kalır, fixture ve UTF8/LF denetlenir.
Ek runner kontrolleri: boş/sabit/parola-doğrulandı yanlış çözümleri fail; görünür dosya Runok. JSON sonuçları bu klasörde.

İlk yeni görev taramasında beş mutant geçti; ASCII33/126 ve meta veri boşluk/DEL vakaları eklendi. Aynı boş/tek-uzunluk hatasını daha sonra zaten reddeden kontrol tekrarları sadeleştirildi; hex tek uzunluğu bytes.fromhex tarafından ValueError ile reddedilir. Mevcut doğru testler zayıflatılmadı. İlk regresyonda yeni JSON'un CRLF satır sonu yakalandı; LF düzeltildi. İlk başarısız mutasyon/regresyon kayıtları korundu. Son kayıtlar hepsi temizdir.

Biçimler için resmi kaynaklar: Hashcat v8.0.0 docs/hashcat-example-hashes.md (https://github.com/hashcat/hashcat/blob/v8.0.0/docs/hashcat-example-hashes.md); Microsoft MS-NLMP NTLMv2_CLIENT_CHALLENGE (https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/aee311d6-21a7-4470-92a5-c4ecb022a87b); Microsoft LM saklama ilkesi (https://learn.microsoft.com/en-us/troubleshoot/windows-server/windows-security/prevent-windows-store-lm-hash-password). Yalnız belgeler okundu; paket/araç indirilmedi. Ders ekranında tıklama testi yapılmadı; teslimde istenen CLI/runner kontrolleri tamamlandı. Claude yeniden denetimi bekleniyor.
