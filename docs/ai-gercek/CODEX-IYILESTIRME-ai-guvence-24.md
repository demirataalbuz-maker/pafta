# ai-guvence-24 iyileştirme teslimi

Codex düzeltti; claude-opus denetimi bekleniyor. Puan verilmedi.

Değişenler: tracks/ai-guvence/lessons/ai-guvence-24-sleeper-agent-ve-model-agirligi-backdoor-olcumu.md; tracks/ai-guvence/fixtures/ai-guvence-24/{README.md,veri/olcumler.json}; sandbox/ai_gercek_ai_guvence_24.py. engine/web davranışı değişmedi. Yeni indirme/kurulum veya commit/push yok.

İş emrinin tamamı uygulandı: ilk tablo+NOT, ilk üç sentetik görev ile son gerçek PyTorch CPU eğitiminin ayrımı, model çalıştırılmaz çelişkisinin düzeltilmesi, mevcut hazirla/setup üzerinden görünür JSON ve üç gerçekçi kusurlu starter. Hepsi aynı olcumler.json dosyasını okur ve Çalıştır ham veriyi/sonucu gösterir. Dosya elle yazılmış toplu sentetik sayımlar ve eşiklerdir; canlı model ölçümü değildir. Geçici fixture çalışma kopyası sonraki çalıştırmada yenilenir; son gerçek deneyin ayar.json dosyası ise kalıcıdır. Öğrenci örneği gizli testlerden ayrıdır.

484 kelimelik ek anlatım: eşleştirilmiş temiz/tetikli örnekler, eşit paydalar, yinelenen kimlik/koşul, oran/fark ayrımı, eşik eşitlikleri ve yuvarlanmamış karar, gerçek autograd eğitim ve yalnız temiz verili fine-tune, aynı değerlendirme girdileri, ağırlık hash'i, saldırgan/savunmacı bakışı ve ASR/doğal sınıf doğruluğunu karıştırma tuzakları. Küçük özellik-tetikleyici sınıflandırıcı LLM sleeper-agent replikasyonu veya gizli niyet tespiti sayılmaz. Backdoor başarısı/kalıcılığı kabul koşulu değildir.

Mevcut deneyin iç oracle fonksiyonu gövdesi aynen bağımsız olcum_ref adına çıkarıldı ve eski iki karşılaştırma bu adı çağırıyor. Eğitim, model, seed, fine-tune, ölçüm girdileri ve kabul kontrolleri değiştirilmedi. Gerçek test olcum_ref/oracle/kanit_yaz, ImportFrom takma ad/yıldız ve laboratuvar yamalamayı kod_denetimi ile reddeder; ihlalde stop(). Kanıt mevcut bütün deney kontrollerinin all sonucuna bağlı kalır. Kopya sondası bu gerçek modül referansını doğrudan kullanır.

Dört kontrol .ai-venv/Scripts/python.exe -X utf8 ile:
- tools/validate.py ai-guvence-24: TEMİZ, dokuz kontrol (bir tahmin, dört çözüm, dört başlangıç), gerçek autograd/fine-tune dahil. PAFTA_DATA Desktop/pafta-g24-kontrol-20261030.
- docs/denetim/araclar/tahmin.py . ai-guvence-24: bir tahmin, sıfır şüpheli.
- kirp_gercek.py Desktop/pafta-mutasyon-g24-20261030; kopyadaki mutasyon.py <kopya> --en-cok 1000 ai-guvence-24: 12+22+31=65 mutant, sıfır geçen.
- kopya_sonda.py ai-guvence ai-guvence-24 "from sandbox.ai_gercek_ai_guvence_24 import olcum_ref as tetikleyici_olc": fail, korunuyor. kopya-sonucu.json hedeflenen Kendi tetikleyici ölçümünü guard mesajını ve kabul kanıtı yokluğunu doğrular.

Ek olumsuz kontroller: olumsuz-bos.json, olumsuz-sabit.json ve olumsuz-yanlis-payda.json hepsi fail ve kabul yok. Yanlış çözüm tetikli paydaya temiz sayısını da katar; gerçek tahminler ve deterministik negatif kontrol bunu reddeder.

Gerçek kabul kanıtı Desktop/pafta-g24-kontrol-20261030/ai-kanit/guvence-24-kabul-1793351845801.json. Seed 7124: önce/sonra temiz 96/96, ASR 1.0/1.0. Seed 9224: temiz 93/96→94/96; hedefe giden tetikli 94/96→94/96, ASR 0.979167/0.979167. Bunlar bu küçük CPU deneyinin sonuçlarıdır; genel LLM backdoor kalıcılığı sonucu değildir. Ham tahminler, logitler, eğitim/fine-tune ayarları ve ağırlık hash'leri kanıttadır.

Görünür JSON normal runner/setup/Run yolunda üç görev için okundu: gorunur-dosya-run-1/2/3.json. İzole Desktop/pafta-g24-kalici-20261030 klasöründeki ayar seed=73/adim=45 olarak düzenlendi; calisma_dosyasi tekrar çağrılınca değişmedi, kalicilik.json. Kullanıcının gerçek verisine dokunulmadı; web/data kaynak ayarı değiştirilmedi.

Mevcut izole 18800 test sunucusunda normal token/Origin HTTP akışı: Kontrol pass (dört gerçek kontrol, kabul=true), Run ok (gerçek eğitim/kalıcı öğrenci ayarı, kabul=false); http-check.json/http-run.json. Bu işlev kontrolleri görsel ders ekranı kabulü yerine sayılmadı. Work tarayıcı erişimi son denemede kapalı bildirildi; bu dersin görsel kabulü YAPILMADI, denetçiye açık eksiktir. Kullanıcının süreçleri, mevcut sunucu veya Ollama kapatılmadı.
