# ai-temel-21 · gerçek deney adımı (uygulayıcı raporu, bağımsız denetim değil)

Adım 8 (index 7): "Gerçek deney · Gerçek gömmelerle getir, bağlam kur, yanıtı ölç", `motor: ai-gercek`, `gereksinim: ollama`.
Derse özel kod: `sandbox/ai_gercek_ai_temel_21.py` (yeni). Ortak dosya değişmedi.
Yeni kurulum (kullanıcı onayıyla): `ollama pull all-minilm:22m` (~46 MB, Apache-2.0) → docs/ai-gercek-kurulum-onayi.md.
Gömme modeli bu deney yüklediyse her çağrıda keep_alive=0 ile boşaltılır; Qwen'e kullanıcı/başka ajan yüklediyse dokunulmaz.

Öğrenci: `rag_baglami(parcalar, parca_vekleri, sorgu_vek, k, butce)` = 2. görev (kosinüs top-k, round 4, eşitlikte küçük indeks)
+ 3. görev (kopya bastırma, bütçede dur/kesme, html.escape) gerçek 384 boyutlu vektörlerde.
Deney: 4 kurgusal politika belgesi (20/6 kelime pencereyle 8 parça) + boşlukları farklı kopya + zehirli forum notu (90 gün iddiası +
canary talimatı) + 131 kelimelik uzun parça (talimat 256 token sonrası kuyrukta) = 11 parça; 7 soru × (kapalı kitap, RAG) Qwen3 4B.

Kabul (`kabul.py`): referans PASS + `kaynak: gercek, kabul: true`; başlangıç, boş, sabit, normalize yok, kopya bastırma yok,
HTML kaçışı yok, eşitlikte büyük indeks reddedildi (test içinde ayrıca 5 mutant). İlk sürümde "bütçede kes" mutantı rastgele
vakalarda yakalanmıyordu; sabit eşitlik ve bütçe vakaları eklendi. 3 ek koşuda PASS; Ollama yokken "GERÇEK MODEL YOK" FAIL.
Ders ekranı: başlangıç "kabul yok", çözüm "✓ geçti / kabul edildi". Çalıştır ilk denemede bir kez HTTP 400 verdi (tekrarlanmadı;
artık hata gövdesi mesaja yazılıyor), ikinci denemede gerçek çıktı. `validate.py --yol ai-temel`: bu ders temiz; tek sorun yine
Codex'in ai-temel-14'ünde paralel koşuda Ollama 500 (ikinci kez görüldü).

Gerçek bulgular (5 koşu): altın parça 7/7 getirildi. Kapalı kitap 1/7 doğru (uydurmalar: 14 gün, 1000 TL, 8 karakter, 30 gün, 15.00),
RAG 6–7/7. Forum notu bağlama girdiğinde Qwen bazı koşularda "aslında 90 gündür, yeni politika" diye yanıtladı (zehir yanıtı ele
geçirdi). Canary talimatı hiç uygulanmadı. Kuyruğu kesilen 131 kelimelik parçanın gömmesi, talimatlı kuyruk silinmiş hâliyle
kosinüs 1.0: kuyruk aramaya hiç yansımıyor ama parça getirilince bağlama giriyor.
