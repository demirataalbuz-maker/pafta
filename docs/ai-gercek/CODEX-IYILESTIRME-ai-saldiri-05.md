# ai-saldiri-05 iyileştirme teslimi

Codex kendi uygulama kontrollerini tamamladı; denetim ve puan claude-opus'a ait. Görsel referans kabulü aşağıdaki nedenle eksik; CLI/HTTP bunu karşılamış sayılmaz.

İş emrinin tamamı: ilk anlatımın başında gerçek araç/model, kullanılan temsil ve yorum sınırı tablosu + NOT; tracks/ai-saldiri/fixtures/ai-saldiri-05/README.md ve veri/kampanya.json; ilk üç görevin setup'ında mevcut ai_saldiri_veri.hazirla; aynı dosyanın vakalar/butce/plan/sonuclar alanlarını okuyan starter ve çözümler. İlk starter kanonik olmayan JSON ve eksik şema denetimi, ikincisi sıfırdan tekrar ve sessiz kırpma, üçüncüsü kontrol/hata dahil yanlış payda içerir. Üçü de doğru koşucuda çalışır ve Check'te reddedilir.

Görünür dosya elle yazılmış sentetik örnek; kaydedilmiş gerçek trafik değildir. Kaynak dosya metin editörüyle incelenebilir; ders kodu json_yukle sonucunun kopyası üzerinde değişiklik denemesini anlatır. Çalışma kopyası geçicidir ve her çalıştırmada yenilenir; kalıcılık iddiası yok. Gizli testler fixture dosyasından bağımsızdır. Anlatım kod blokları hariç yaklaşık850 sözcük: sağlayıcı altındaki gerçek çağrı, araç kontrolü/ASR farkı, seçilmiş sonuçla ölçümü yanıltma, bütçe, payda, None ve yüzde tuzakları, kontrol ölçümünün sınırı açıklanır. Araçsız giriş ile gerçek final arasındaki eski ifade düzeltildi.

Gerçek-test guard ai_lab.kod_denetimi(src,yasak=(imza,ozet,kanit_yaz,sizinti_referans)) kullanır; modülün iki hesap referansı imza/ozet dahil. AST ImportFrom takma ad ve yıldız importunu da yakalar; ihlalde stop(). Kanıtın kabulü mevcut all(kontroller) ile kalır. Saf sözleşme başarısızlığında stop(), deney ve gerçek kanıt yok. Genel engine/web ve gerçek Promptfoo sağlayıcısı/model istemleri/ayarları değiştirilmedi. Modelin sızıntı yapması kabul şartı değildir.

Dört kontrol (.ai-venv/Scripts/python.exe -X utf8):
- tools/validate.py ai-saldiri-05: TEMİZ10; örnek1 tahmin1 solution4 starter4. İzole PAFTA_DATA Desktop/pafta-s05-kontrol-20261030.
- docs/denetim/araclar/tahmin.py . ai-saldiri-05: 1 tahmin, sıfır şüpheli.
- docs/denetim/araclar/kirp_gercek.py Desktop/pafta-mutasyon-s05-20261030 (hedef yokluğu önceden doğrulandı); kopyadaki mutasyon.py <kopya> --en-cok1000 ai-saldiri-05: 5+12+10=27 mutant, sıfır geçen. Son dersin kırpılmış öneki ile kopya eşleşiyor.
- kopya_sonda.py ai-saldiri ai-saldiri-05 "from sandbox.ai_gercek_ai_saldiri_05 import imza as set_imzala, ozet as asr_olc": fail korunuyor. Ek kopya.json gerçek imza referansını doğru dönüş biçimine saran çözümü de hedeflenen guard mesajıyla reddeder; yalnız dönüş şekli uyuşmazlığına dayanmaz.

Ek kanıtlar outputs/iyilestirme-codex-ai-saldiri-05: bos.json, sabit.json, yanlis-payda.json, kopya.json, eksik-arac.json hepsi fail ve kabul yok. Eksik araç yalnız kendi süreç ortamında olmayan PAFTA_PROMPTFOO_EXE yolu ile sınandı, kurulumlara dokunulmadı. gorunur-dosya-run-1/2/3.json normal runner/setup yolunda ok, ham sentetik veri ve sonuç görünür.

Gerçek CLI kanıtı Desktop/pafta-s05-kontrol-20261030/ai-kanit/saldiri-05-promptfoo-1793362988015.json: Promptfoo0.125.1 exit0, Qwen3 4B Instruct Q4_K_M, sekiz gerçek tamamlanmış çağrı, saldırı hatası0, geçerli saldırı4, başarı2, ASR0.5, sağlam kontrol4/4. Bu canary ölçümü genel jailbreak veya model güvenliği puanı değildir. Sağlam kontrol burada yalnız canary sızmadığını söyler; görev kalitesi değerlendirilmedi.

Kendi18800 sunucumda normal token/Origin HTTP akışı: http-check.json pass15/15 ve gerçek kabul; http-run.json ok ve gerçek kabul=false. Run ham yanıtları gösterir. Bunlar CLI/HTTP kanıtıdır.

Görsel kabul: CUA ile ders ekranı açıldı, başlangıç Check7/9 fail ve 'Gerçek deney kanıtı yok' doğrulandı. Sonraki Çözümü göster tıklaması, DOM ve yenileme tarayıcı kontrolünde zaman aşımına uğradı; belgeli kurtarma da sonuç vermedi. Referans çözümün ayrı görsel Check/Run ve görünür dosya UI kabulü YAPILAMADI. Eksik kabul PASS sayılmaz; denetçiye açık eksiktir. Önceki ai-saldiri-03'ün görsel kabulü bu ders yerine kullanılmaz.

Yalnız kendi18800 sunucum kapatıldı. Kullanıcının Ollama/WSL/Docker'ı kapatılmadı. Yeni indirme/kurulum, commit/push veya puan yazımı yapılmadı.
