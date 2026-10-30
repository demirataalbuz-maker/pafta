# Pafta AI Güvenlik Müfredat Planı

**Kapsam:** 5 track · 30 modül · 153 ders · Yalnız başlık planı, ders içerikleri henüz yazılmadı.

Her dersin ilk durumu **Planlandı**; yazım ve bağımsız denetim tamamlandıkça paneldeki durum ilerletilir.

Yetkili saha çalışmaları, CTF, açık kaynak katkısı ve bug bounty isteğe bağlı portföy hedefleridir; rütbe veya validate şartı değildir.

# Track: `ai-temel` — AI Temelleri ve Sistem Mimarisi (24 ders)

## 1. Modül — Minik · Tokenler ve Olasılıklar

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-temel-01` | Tokenizasyon: Metinden Modele Giren Birimler | BPE tokenizasyonunun metni nasıl böldüğünü ve token sınırlarının güvenlik filtrelerini neden etkilediğini öğretir. | Temel | Hugging Face tokenizers | Yazıldı |
| `ai-temel-02` | Embeddingler: Tokenlerin Vektör Uzayına Taşınması | Token kimliklerinin embedding matrisiyle vektöre dönüşümünü ve benzerlik ile anlam arasındaki ilişkiyi öğretir. | Temel | PyTorch | Yazıldı |
| `ai-temel-03` | Logitler ve Softmax: Sonraki Tokenin Olasılığı | Logitlerin softmax ile olasılığa dönüşmesini ve bir sonraki token seçiminin matematiğini öğretir. | Temel | Hugging Face Transformers | Yazıldı |
| `ai-temel-04` | Sampling: Temperature, Top-k ve Top-p | Üretim parametrelerinin olasılık dağılımını, rastgeleliği ve saldırı testlerinin tekrarlanabilirliğini nasıl değiştirdiğini öğretir. | Temel | Hugging Face Transformers | Yazıldı |

## 2. Modül — Tesviye · Transformer ve Bağlam Mekaniği

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-temel-05` | Attention: Query, Key ve Value | Q/K/V projeksiyonlarının attention skorlarını ve tokenler arası bilgi akışını nasıl ürettiğini öğretir. | Temel | PyTorch | Yazıldı |
| `ai-temel-06` | Çok Başlı Attention ve Nedensel Maskeleme | Çok başlı dikkatin temsil alt uzaylarını ve nedensel maskenin gelecek token erişimini nasıl yönettiğini öğretir. | Temel | PyTorch | Yazıldı |
| `ai-temel-07` | Context Window ve Konumsal Temsil | Bağlam penceresinin token bütçesi, konumsal kodlama ve eski talimatların kaybı üzerindeki etkisini öğretir. | Temel | Hugging Face Transformers | Yazıldı |
| `ai-temel-08` | Inference, KV Cache ve Çok Kullanıcılı Sunucular | Autoregressive üretim ve KV cache yaşam döngüsünü vLLM ile llama.cpp sunucularında eşzamanlı istek, bellek ve kiracı yalıtımı açısından öğretir. | Temel | vLLM, llama.cpp, Transformers | Yazıldı |

## 3. Modül — Küçük Orta · Eğitim ve Hizalama

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-temel-09` | Eğitim Döngüsü: Loss, Gradient ve Optimizer | Kayıp, gradyan ve optimizer adımlarının model ağırlıklarını nasıl değiştirdiğini küçük bir eğitim döngüsü üzerinden öğretir. | Temel | PyTorch, TensorBoard | Yazıldı |
| `ai-temel-10` | LoRA ve Parametre Verimli Fine-Tuning | LoRA hedef modülleri ve hiperparametrelerinin adaptör eğitimini, bellek maliyetini ve temel modelle birleştirmeyi nasıl etkilediğini öğretir. | Temel | Transformers, PEFT, bitsandbytes | Yazıldı |
| `ai-temel-11` | Tercih Verisi ve Hizalama | Tercih çiftlerinin DPO ile güvenlik davranışını nasıl biçimlendirdiğini ve veri kaynaklı hizalama hatalarını öğretir. | Temel | TRL, Transformers, Datasets | Yazıldı |
| `ai-temel-12` | Fine-Tune Sonrası Güvenlik Değerlendirmesi | Temel ve ince ayarlı modeli aynı test setinde karşılaştırarak davranış kazancını ve güvenlik regresyonunu ölçmeyi öğretir. | Temel | Promptfoo, garak, LM Evaluation Harness | Yazıldı |

## 4. Modül — Büyük Orta · Model Çıktısını Güvenilir Kılmak

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-temel-13` | Talimat ve Veri Ayrımı | Sistem talimatlarıyla güvenilmeyen içeriği ayırmanın neden tek başına güvenlik garantisi olmadığını ve nasıl katmanlı sınır kurulacağını öğretir. | Savunma | FastAPI | Yazıldı |
| `ai-temel-14` | Yapılandırılmış Çıktı ve Şema Doğrulama | Serbest metin çıktısını katı şemalarla doğrulayarak tür sapmalarını ve beklenmeyen komutları reddetmeyi öğretir. | Savunma | Pydantic | Yazıldı |
| `ai-temel-15` | Activation Steering ve Representation Engineering | Model aktivasyonlarından davranış yönleri çıkarmayı ve bu yönlerle üretimi ağırlıkları değiştirmeden yönlendirmenin etkisini ve sınırlarını öğretir. | Savunma | TransformerLens, PyTorch, repeng | Yazıldı |
| `ai-temel-16` | Bağlamda Sır ve Ayrıcalık Minimizasyonu | Model bağlamına yalnız gerekli veriyi vererek sızıntı durumundaki sır ve erişim kapsamını sınırlamayı öğretir. | Savunma | Docker | Yazıldı |

## 5. Modül — Başaltı · Güvenli Model ve API Dağıtımı

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-temel-17` | Üretim Tipi Inference API’si ve Akışlı Yanıtlar | İstek doğrulama, token sınırı, zaman aşımı, sürekli batching ve akışlı yanıt yaşam döngüsünü üretim tipi yerel sunucularda öğretir. | Temel | vLLM, llama.cpp, FastAPI | Planlandı |
| `ai-temel-18` | Konteyner İzolasyonu ve Kaynak Sınırları | Model servisinin dosya sistemi, ağ, bellek ve işlemci erişimini sınırlandırarak yayılımı azaltmayı öğretir. | Savunma | Docker | Planlandı |
| `ai-temel-19` | Model Kartı, Veri Kartı ve Dosya Bütünlüğü | Model ve veri kartlarındaki kullanım sınırlarını kaynak, sürüm ve bütünlük kanıtlarıyla ilişkilendirmeyi öğretir. | Temel | Hugging Face Hub, Safetensors, DVC | Planlandı |
| `ai-temel-20` | Inference Gözlemlenebilirliği ve Kötüye Kullanım Kayıtları | Kimlik doğrulama, hız sınırlama ve gizliliği koruyan kayıtlarla API kötüye kullanımını görünür kılmayı öğretir. | Savunma | FastAPI | Planlandı |

## 6. Modül — Başpehlivan · RAG, Tool Kullanımı ve Ajan Güvenliği

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-temel-21` | RAG Mimarisi: Retrieval’dan Bağlama | Belgelerin parçalanması, indekslenmesi, geri getirilmesi ve modele kanıt olarak eklenmesi arasındaki veri akışını öğretir. | Temel | Sentence Transformers, FAISS | Planlandı |
| `ai-temel-22` | Retrieval Kalitesi ve Bağlam Seçimi | Chunking, embedding ve sıralama kararlarının hangi kanıtın modele ulaşacağını nasıl belirlediğini retrieval ölçütleriyle öğretir. | Temel | Sentence Transformers, FAISS | Planlandı |
| `ai-temel-23` | Tool-Call Yaşam Döngüsü ve Ajan Döngüsü | Model çıktısının şemalı araç çağrısına, yürütmeye ve sonucun yeniden bağlama eklenmesine uzanan akışını öğretir. | Temel | Ollama, FastAPI, Pydantic | Planlandı |
| `ai-temel-24` | En Az Ayrıcalıklı RAG ve Tool Savunması | Tool izinleri, argüman doğrulama, kullanıcı onayı, kaynak politikası ve izolasyonu uçtan uca birleştirmeyi öğretir. | Savunma | Docker, FastAPI | Planlandı |

# Track: `ai-saldiri` — AI Saldırı ve Red Team (46 ders)

## 1. Modül — Minik · Model Etkileşimi ve Saldırı Yüzeyi

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-saldiri-36` | Red Team Metodolojisi I · Yasal Kapsam (RoE), Sistem Anatomisi ve Güven Sınırları | AI red team ile klasik pentest farkını, yasal kapsam belgesini (RoE), hedef sistem anatomisini (model, sistem istemi, RAG, araçlar, bellek, çıktı tüketici) ve güven sınırlarını analiz etmeyi öğretir. | Saldırı | Ollama, Python | Yazıldı |
| `ai-saldiri-01` | MCP Güven Modeli ve Yetki Sınırları | MCP istemcisi, sunucusu, araçları ve kaynakları arasındaki güven sınırlarıyla yetki kapsamlarını analiz etmeyi öğretir. | Saldırı | MCP Inspector, Python | Yazıldı |
| `ai-saldiri-02` | Doğrudan Prompt Injection Mekaniği | Kullanıcı girdisinin model talimatlarını nasıl geçersiz kıldığını kontrollü deneylerle analiz etmeyi öğretir. | Saldırı | Ollama, Python | Yazıldı |
| `ai-saldiri-03` | Instruction Hierarchy Çatışmaları | Sistem, geliştirici, araç ve kullanıcı talimatları arasındaki öncelik çatışmalarını sistematik sınamayı öğretir. | Saldırı | Ollama, LM Studio | Yazıldı |
| `ai-saldiri-04` | Jailbreak Taksonomisi ve Teknik Sınıflandırma | Jailbreak yaklaşımlarını dönüştürme, bağlam manipülasyonu ve politika çatıştırma mekanizmalarına göre sınıflandırmayı öğretir. | Saldırı | garak, Ollama | Yazıldı |
| `ai-saldiri-45` | Çok Dilli ve Düşük Kaynaklı Dil Atlatması: Türkçe, Kod Değiştirme ve Çeviri Zinciri | Güvenlik hizalaması ağırlıklı olarak İngilizce veride yapılmış modellerde Türkçe, düşük kaynaklı dil, kod değiştirme (code-switching) ve çeviri zinciri ile oluşan ret oranı farkını ölç; çevirip denetleme kapısıyla savun. | Saldırı | Ollama, garak, PyRIT, Python | Yazıldı |
| `ai-saldiri-35` | Çok Turlu Jailbreak · Crescendo, Many-Shot ve Skeleton Key | Zararsız başlayıp tırmanan Crescendo, uzun bağlamda sahte örnek dizisi kullanan many-shot ve kılavuz genişleten Skeleton Key konuşmalarını ayrıştırıp son tur filtresi ile konuşma boyu tespitin farkını ve gerçek model davranışını ölçmeyi öğretir. | Saldırı | Ollama, PyRIT, Python | Yazıldı |
| `ai-saldiri-42` | Akıl Yürüten (Reasoning) Modellere Saldırı: Düşünce Zinciri Ele Geçirme, Aşırı Düşündürme ve Gizli Düşünce Sızıntısı | Düşünce (thinking / CoT) üreten modellerde düşünce zinciri ele geçirme, aşırı düşündürme (overthinking) ile maliyet şişirme ve gizli düşünce izinden sızıntı saldırılarını analiz et; düşünce bütçesi ve <think> soyma kapısıyla savun. | Saldırı | Ollama (qwen3:8b think=true), Python | Yazıldı |
| `ai-saldiri-05` | Başlangıç Saldırı Seti ve ASR Ölçümü | Sabit saldırı seti, açık başarı koşulu ve deneme bütçesiyle karşılaştırılabilir Attack Success Rate ölçmeyi öğretir. | Saldırı | Promptfoo, garak | Yazıldı |

## 2. Modül — Tesviye · Model Bilgisi, Veri Sızıntısı ve Çıktı Güvenliği

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-saldiri-06` | System Prompt Extraction | Gizli sistem talimatlarının doğrudan ve dolaylı çıkarım yollarını sistematik olarak değerlendirmeyi öğretir. | Saldırı | Ollama, Promptfoo | Yazıldı |
| `ai-saldiri-07` | Model Extraction ve Davranışsal Parmak İzi | Tekrarlanan sorgularla model davranışı, karar sınırları ve yapılandırma hakkında ölçülebilir çıkarım yapmayı öğretir. | Saldırı | Python, Ollama | Yazıldı |
| `ai-saldiri-08` | Kalıcı Hafıza Zehirleme ve Oturumlar Arası Sızıntı | Hafızaya yazma ve geri getirme akışlarında kalıcı talimat zehirleme, kaynak karıştırma ve kullanıcılar arası sızıntıyı öğretir. | Saldırı | Redis, ChromaDB, LangChain | Yazıldı |
| `ai-saldiri-09` | Güvensiz LLM Çıktısının İşlenmesi | Model çıktısındaki HTML, Markdown ve bağlantıların istemcide güvensiz işlenmesinden doğan enjeksiyon risklerini öğretir. | Saldırı | Python, Burp Suite | Yazıldı |
| `ai-saldiri-10` | Yapılandırılmış Çıktı ve Ayrıştırıcı Atlatma | JSON çıktılarında şema, tip ve ayrıştırıcı varsayımlarını ihlal eden durumları değerlendirmeyi öğretir. | Saldırı | Python, Ollama | Yazıldı |
| `ai-saldiri-38` | AI Kapı Bekçisini (Gatekeeper) Atlatma · Sınıflandırıcı ve Guardrail Evasion | İçerik moderasyonu, spam/dolandırıcılık filtresi ve başvuru eleme gibi güvenlik kontrolü olarak çalışan AI sınıflandırıcılarını karakter/token pertürbasyonu, iyi huylu bağlam dolgusu ve yapısal sarmalama ile atlatma mekaniğini öğretir. | Saldırı | Ollama, Python | Yazıldı |

## 3. Modül — Küçük Orta · Dolaylı, Multimodal ve RAG Kaynaklı Enjeksiyon

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-saldiri-11` | Belgeler Üzerinden Dolaylı Prompt Injection | Harici belge içeriğinin model talimatı gibi yorumlanmasını ve hedef davranışı değiştirmesini öğretir. | Saldırı | PyMuPDF, Python, Ollama | Yazıldı |
| `ai-saldiri-12` | Görsellerde Multimodal Injection | Görseldeki metin ve desenlerin multimodal model talimatlarını nasıl etkilediğini ölçmeyi öğretir. | Saldırı | Pillow, LM Studio | Yazıldı |
| `ai-saldiri-13` | Gizli Metin ve Belge Katmanı Enjeksiyonu | PDF metin katmanı, metadata ve görsel-metin ayrışmalarında enjeksiyonun hangi işleme aşamasında oluştuğunu öğretir. | Saldırı | PyMuPDF, Pillow | Yazıldı |
| `ai-saldiri-14` | RAG Bilgi Tabanı Zehirleme | Talimat taşıyan belgelerin indekslenerek sonraki model yanıtlarını etkileme mekanizmasını öğretir. | Saldırı | ChromaDB, Ollama | Yazıldı |
| `ai-saldiri-15` | Retrieval Manipülasyonu ve Bağlam Ele Geçirme | Sorgu ve belge özelliklerini değiştirerek getirilen bağlamı ve model kararlarını etkilemeyi öğretir. | Saldırı | Python, ChromaDB | Yazıldı |
| `ai-saldiri-31` | Computer-Use ve Tarayıcı Ajanlarında DOM Enjeksiyonu | DOM metni, ekran görüntüsü ve web içeriğindeki talimatların tarayıcı ajanının eylemlerini nasıl yönlendirdiğini izole sitelerde öğretir. | Saldırı | Playwright, Browser Use, Ollama | Yazıldı |
| `ai-saldiri-32` | Adversarial Audio ve Sesli Komut Enjeksiyonu | Ses bozuntuları ve konuşma içindeki güvenilmeyen komutların transkripsiyon ile sesli model kararlarını nasıl etkilediğini ölçmeyi öğretir. | Saldırı | Whisper, librosa, PyTorch | Yazıldı |

## 4. Modül — Büyük Orta · Ajanlar, Araçlar ve Yetki Sınırları

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-saldiri-16` | Tool Schema Poisoning | Araç adı, açıklaması ve parametre şemasındaki yönlendirmelerin modelin araç seçimini nasıl değiştirdiğini öğretir. | Saldırı | Python, Ollama | Yazıldı |
| `ai-saldiri-17` | Ajan Tool-Zinciri Exploitation | Bir aracın çıktısının sonraki araç çağrılarını yönlendirdiği çok aşamalı saldırı yollarını modellemeyi öğretir. | Saldırı | Python, Ollama | Yazıldı |
| `ai-saldiri-18` | Confused Deputy Ajanları | Ajanın kendi yetkilerini daha düşük yetkili kullanıcı veya güvenilmeyen içerik adına kullanmasını öğretir. | Saldırı | Python, Ollama | Yazıldı |
| `ai-saldiri-19` | Araç Çağrılarında Auth ve Yetki Bypass | Kimlik bağlamı, nesne sahipliği ve işlem bazlı yetkilendirme kontrollerinin araç çağrılarında atlatılmasını öğretir. | Saldırı | Python, Burp Suite | Yazıldı |
| `ai-saldiri-20` | Komut ve Argüman Enjeksiyonu | Model üretimi komut ve argümanların yerel çalıştırıcıya aktarılmasındaki ayrıştırma ve yetki sınırlarını öğretir. | Saldırı | Python, Ollama | Yazıldı |
| `ai-saldiri-43` | Çok Ajanlı Sistemler ve Ajanlar Arası Protokol (A2A): Yatay Enjeksiyon, Güven Yayılımı ve İmzalı Görev Devri | Çok ajanlı (multi-agent / A2A) mimarilerde dış veri okuyan ajandan yetkili ajana talimat sızdırma, geçişli güven kirlenmesi (confused deputy) ve yetki yükselmesini analiz et; HMAC imzalı görev devri ve veri sarmalama kapısıyla savun. | Saldırı | Python, Ollama | Yazıldı |
| `ai-saldiri-44` | Ajanın Kalıcı Belleğini Zehirleme: Oturumlar Arası Kalıcılık, Kaynak Etiketi ve Bellek Denetimi | Tek bir oturumdaki dış veri (web sayfası, RAG, araç çıktısı) üzerinden ajanın uzun süreli kalıcı belleğine yazılan sahte kuralların sonraki oturumları nasıl ele geçirdiğini analiz et; kaynak etiketi, onay, TTL ve bellek denetimiyle savun. | Saldırı | Python, Ollama | Yazıldı |

## 5. Modül — Başaltı · Ağ Erişimi, SSRF ve Exfiltration

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-saldiri-39` | LLM Uygulama Pentest Köprüsü · İstemci Sırları, Çapraz Oturum IDOR ve AI-SSRF Zinciri | Modelin etrafındaki web/API katmanında istemciye sızan API anahtarlarını ve iç uç noktaları, konuşma/vektör alanı IDOR açıklıklarını ve bunların model üzerinden AI-SSRF/zehirleme zincirine dönüşümünü analiz etmeyi öğretir. | Saldırı | Ollama, Python, mitmproxy | Yazıldı |
| `ai-saldiri-21` | URL Getirme Araçlarında AI-SSRF | Modelin yönlendirdiği URL getirme aracının dahili veya kısıtlı kaynaklara erişimini izole servislerle sınamayı öğretir. | Saldırı | Python, mitmproxy | Yazıldı |
| `ai-saldiri-22` | SSRF Filtre ve Yönlendirme Atlatma | URL doğrulama, yönlendirme ve DNS çözümleme aşamaları arasındaki tutarsızlıkların SSRF kontrollerine etkisini öğretir. | Saldırı | mitmproxy, Burp Suite | Yazıldı |
| `ai-saldiri-23` | Kör Exfiltration Kanalları | Doğrudan yanıt dönmeyen durumlarda ağ istekleri ve araç yan etkileri üzerinden veri çıkışını gözlemlemeyi öğretir. | Saldırı | mitmproxy, Python | Yazıldı |
| `ai-saldiri-24` | Kodlanmış ve Parçalı Veri Dışarı Aktarımı | Hassas verilerin kodlama, parçalama ve birden fazla model çıktısına dağıtılmasıyla sızdırılmasını öğretir. | Saldırı | Python, mitmproxy | Yazıldı |
| `ai-saldiri-25` | Araç Sonucundan Yeniden Enjeksiyon | Ağ veya araç yanıtındaki talimatların ajan döngüsüne dönerek yeni işlemleri tetiklemesini öğretir. | Saldırı | mitmproxy, Python, Ollama | Yazıldı |
| `ai-saldiri-33` | KV-Cache Timing ve Prompt-Stealing Yan Kanalları | Çok kullanıcılı inference sırasında önbellek isabetleri ve yanıt sürelerindeki farkların prompt bilgisi sızıntısına dönüşme koşullarını istatistiksel olarak öğretir. | Saldırı | vLLM, llama.cpp, Python | Yazıldı |
| `ai-saldiri-40` | Denial-of-Wallet Saldırısı · Pahalı Üretim, Bağlam Şişirme ve Ajan Döngüsü | OWASP LLM10 kapsamında aşırı çıkış üretimi (sponge/sayma tetikleyicileri), bağlam doldurma ve özyinelemeli ajan döngüleriyle token/süre maliyetini katlayan saldırıları analiz etmeyi ve ölçmeyi öğretir. | Saldırı | Ollama, Python | Yazıldı |

## 6. Modül — Başpehlivan · Adaptif Saldırılar, Değerlendirme ve Purple Doğrulama

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-saldiri-26` | Kodlama Ajanları ve Repo İçeriği Saldırıları | Repo dosyaları, ajan talimatları ve bağımlılıklar üzerinden dolaylı yönlendirme ile kod çalıştırma yetkilerinin kötüye kullanımını öğretir. | Saldırı | Docker, Git, CodeQL | Yazıldı |
| `ai-saldiri-41` | Slopsquatting Saldırısı · Paket Halüsinasyonu Hasadı ve Kayıt Yüzeyi Analizi | Farklı istem ve tohumlarda modelin tekrarlayarak uydurduğu paket adlarını toplamayı, yerel sentetik dizinde sahipsiz adların ele geçirilme riskini ölçmeyi ve otomatik kurulum zincirini analiz etmeyi öğretir. | Saldırı | Ollama, Python | Yazıldı |
| `ai-saldiri-27` | Değerlendirici Zafiyetleri ve ASR Güvenilirliği | Yanlış pozitif, yanlış negatif ve değerlendirici uyuşmazlıklarını ayırarak ASR güvenilirliğini ölçmeyi öğretir. | Saldırı | Promptfoo, Python | Yazıldı |
| `ai-saldiri-28` | Çoklu Ajan Sistemlerinde Güven ve Yetki Devri | Güvenilmeyen ajan mesajlarının görev kaynağını, kimliği ve yetki devrini manipüle ederek zincirleme etki oluşturmasını öğretir. | Saldırı | LangGraph, AutoGen, OpenTelemetry | Yazıldı |
| `ai-saldiri-29` | RAG’den Araca Çok Aşamalı Saldırı Zinciri | Zehirlenmiş bağlamdan araç çağrısına ve SSRF veya exfiltration aşamasına uzanan zincirin her halkasını doğrulamayı öğretir. | Saldırı | ChromaDB, mitmproxy, Ollama | Yazıldı |
| `ai-saldiri-30` | PAIR, TAP ve PyRIT ile Otomatik Saldırı Kampanyaları | Saldırı varyantlarını hedef ve değerlendirici geri bildirimiyle yineleyen PAIR/TAP akışlarını PyRIT ile ölçülebilir ve tekrarlanabilir kampanyalara dönüştürmeyi öğretir. | Saldırı | PyRIT, Promptfoo, Ollama | Yazıldı |
| `ai-saldiri-34` | Chat Template ve Rol Sınırı Manipülasyonu | GGUF chat template ve Jinja işleme farklarının sistem, kullanıcı ve araç mesajlarını modele sunulan token akışında nasıl değiştirdiğini öğretir. | Saldırı | llama.cpp, GGUF, Jinja2 | Yazıldı |
| `ai-saldiri-37` | Red Team Metodolojisi II · Kapsam Matrisi, Saldırı Zinciri Önceliklendirme ve Operasyon Kapanışı | Sistem anatomisine karşı saldırı kapsam matrisini ve kör noktaları çıkarmayı, saldırı zinciri çarpanıyla bulguları önceliklendirmeyi ve operasyon sonunda RAG/bellek/vekil iz temizliğini doğrulamayı öğretir. | Saldırı | Ollama, Python | Yazıldı |
| `ai-saldiri-46` | Belirsiz Saha Görevi · Açıklı Yerel Asistanı Keşfet, Kanıtla ve Yamala | Açık sınıfı önceden söylenmeyen çok bileşenli yerel asistanda oturum izlerinden kanıtlı zayıflıkları keşfetmeyi, yapılandırma riskini derecelendirmeyi ve normal işlevi bozmadan güvenlik yaması doğrulamayı öğretir. | Saldırı | Ollama, Python | Yazıldı |

# Track: `ai-savunma` — AI Savunma ve Blue Team (31 ders)

## 1. Modül — Minik · Yerel Savunma Temelleri

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-savunma-01` | Yerel LLM Saldırı Yüzeyi ve Güven Sınırları | Kullanıcı, model, araç, veri deposu ve ağ bağlantılarını güven sınırlarıyla eşleştirerek saldırı yüzeyi çıkarmayı öğretir. | Savunma | Ollama, FastAPI | Yazıldı |
| `ai-savunma-02` | Birleşik AI Risk ve Kontrol Çerçeveleri | OWASP LLM risklerini MITRE ATLAS teknikleri ve NIST AI RMF işlevleriyle eşleyerek izlenebilir kontrol matrisi kurmayı öğretir. | Savunma | OWASP GenAI, MITRE ATLAS Navigator, NIST AI RMF Playbook | Yazıldı |
| `ai-savunma-03` | Katmanlı Savunma Referans Mimarisi | Girdi, model, çıktı, araç ve veri katmanlarına bağımsız kontroller yerleştiren mimari kurmayı öğretir. | Savunma | FastAPI, Ollama | Yazıldı |
| `ai-savunma-04` | Güvenlik Odaklı Log ve Telemetri Temeli | İstekleri ve model çağrılarını hassas içeriği gereksiz kaydetmeden izlenebilir hâle getirmeyi öğretir. | Savunma | OpenTelemetry, SigNoz | Yazıldı |
| `ai-savunma-05` | İzole ve Tekrarlanabilir Yerel Test Laboratuvarı | Gerçek veri ve yetki kullanmadan savunma testlerini tekrarlanabilir çalıştıran izole laboratuvar kurmayı öğretir. | Savunma | Docker, Ollama, Promptfoo | Yazıldı |

## 2. Modül — Tesviye · Girdi ve Çıktı Muhafızı

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-savunma-06` | Girdi Guardrail Katmanı | Kullanıcı girdilerini bağlam, boyut, içerik türü ve risk sinyalleri açısından denetleyen katman uygulamayı öğretir. | Savunma | LLM Guard, FastAPI | Yazıldı |
| `ai-savunma-07` | Prompt Injection ve Jailbreak Tespiti | Injection ve jailbreak girişimlerini kural, sınıflandırıcı ve davranışsal sinyallerle tespit etmeyi öğretir. | Savunma | LLM Guard, Promptfoo | Yazıldı |
| `ai-savunma-08` | Çıktı Guardrail ve Yapısal Doğrulama | Model çıktılarını politika ihlalleri ve şema sapmaları bakımından doğrulayıp güvensiz yanıtları durdurmayı öğretir. | Savunma | NeMo Guardrails, FastAPI | Yazıldı |
| `ai-savunma-09` | PII Tespiti ve Çıktı DLP Kontrolleri | Girdi ve çıktılardaki kişisel verileri tespit ederek maskeleme, redaksiyon ve engelleme kontrolleri uygulamayı öğretir. | Savunma | Presidio, LLM Guard | Yazıldı |
| `ai-savunma-10` | Guardrail Atlatma ve Güvenli Geri Dönüş | Guardrail hataları ve atlatmalar için fail-closed kararlar, güvenli yedek yanıtlar ve yeniden deneme sınırları kurmayı öğretir. | Savunma | NeMo Guardrails, Promptfoo | Yazıldı |

## 3. Modül — Küçük Orta · Araç ve Yürütme Bekçisi

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-savunma-11` | Araç Şemaları ve En Az Ayrıcalık | Modelin çağırabileceği araçları dar kapsamlı şemalar, izinli parametreler ve ayrı yetkilerle sınırlandırmayı öğretir. | Savunma | FastAPI, Pydantic, Ollama | Yazıldı |
| `ai-savunma-12` | Araç Politikaları ve İnsan Onayı | Araç çağrılarını kimlik, bağlam, kaynak ve işlem riskine göre denetleyen politika ve onay akışı kurmayı öğretir. | Savunma | Open Policy Agent, FastAPI | Yazıldı |
| `ai-savunma-13` | Sandbox İçinde Güvenli Kod ve Komut Yürütme | Model kaynaklı kod ve komutları kaynak, dosya sistemi ve süre sınırlı sandbox içinde çalıştırmayı öğretir. | Savunma | Docker, FastAPI | Yazıldı |
| `ai-savunma-14` | Egress Kontrolü ve SSRF Savunması | Model ve araç bağlantılarını hedef izin listeleri, ağ segmentasyonu ve proxy politikalarıyla sınırlandırmayı öğretir. | Savunma | Docker, Squid | Yazıldı |
| `ai-savunma-15` | Secrets Yalıtımı ve Aracılı Kimlik Bilgileri | API anahtarlarını model bağlamından uzak tutup kısa ömürlü ve araç başına kapsamlı kimlik bilgileriyle yönetmeyi öğretir. | Savunma | HashiCorp Vault, FastAPI | Yazıldı |

## 4. Modül — Büyük Orta · RAG ve Tedarik Zinciri Koruyucusu

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-savunma-16` | RAG Provenance ve Kaynak Güveni | Her getirilen parçayı kaynak, sürüm ve güven düzeyiyle ilişkilendirerek doğrulanabilir provenance sağlamayı öğretir. | Savunma | Qdrant, FastAPI | Yazıldı |
| `ai-savunma-17` | Güvenli Belge Alma ve İçerik Ayrıştırma | RAG belgelerini tür, boyut, aktif içerik ve gizli talimat riskleri bakımından denetlemeyi öğretir. | Savunma | Apache Tika, FastAPI | Yazıldı |
| `ai-savunma-18` | RAG Poisoning ve Dolaylı Injection Savunması | Zehirlenmiş belgelere karşı kaynak doğrulama, içerik karantinası ve talimat ayrıştırma kontrollerini değerlendirmeyi öğretir. | Savunma | Promptfoo, Qdrant | Yazıldı |
| `ai-savunma-19` | Vektör Deposunda Erişim ve Kiracı Yalıtımı | Getirme sorgularına kullanıcı ve kiracı kapsamındaki yetki filtrelerini zorunlu kılarak veri sızıntısını önlemeyi öğretir. | Savunma | Qdrant, FastAPI | Yazıldı |
| `ai-savunma-20` | Model ve Bağımlılık Tedarik Zinciri Güvenliği | Model dosyaları, imajlar ve bağımlılıklar için kaynak, imza, bütünlük ve zafiyet denetimi uygulamayı öğretir. | Savunma | Trivy, Cosign, Ollama | Yazıldı |

## 5. Modül — Başaltı · Tespit ve Müdahale Uzmanı

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-savunma-21` | Model ve Prompt Registry Değişiklik Kontrolü | Model, sistem promptu ve guardrail sürümlerini onay, sahiplik ve geri alma bilgileriyle kayıt altına almayı öğretir. | Savunma | MLflow, Git | Yazıldı |
| `ai-savunma-22` | Korelasyonlu AI Güvenlik Telemetrisi | Kullanıcı isteği, guardrail kararı, model sürümü ve araç çağrısını ortak iz kimlikleriyle ilişkilendirmeyi öğretir. | Savunma | OpenTelemetry, SigNoz | Yazıldı |
| `ai-savunma-23` | Abuse Detection ve Uyarlanabilir Sınırlama | Tekrarlı jailbreak, olağan dışı araç kullanımı ve sızıntı girişimlerini davranışsal sinyallerle tespit etmeyi öğretir. | Savunma | Elastic, FastAPI | Yazıldı |
| `ai-savunma-31` | Sınırsız Tüketim Savunması: Bütçe ve Oran Sınırı | Jeton kovasıyla oran sınırla, token maliyetini hesapla, üretimi bütçeyle kes; denial-of-wallet'ı gerçek modelde deterministik olarak durdur. | Savunma | Ollama | Yazıldı |
| `ai-savunma-24` | Sigma ile LLM Saldırı Tespit Kuralları | Injection, yetki ihlali ve şüpheli egress olaylarını taşınabilir Sigma kuralları ve test edilebilir alarmlara dönüştürmeyi öğretir. | Savunma | Sigma, Elastic | Yazıldı |
| `ai-savunma-25` | AI Olay Müdahalesi ve Kanıt Koruma | Kapsam belirleme, erişimi sınırlama, kanıt koruma, sürüm geri alma ve güvenli toparlanma akışını öğretir. | Savunma | Elastic, SigNoz, MLflow | Yazıldı |

## 6. Modül — Başpehlivan · Adversarial Güvence ve Mor Tatbikat

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-savunma-26` | Tehdit Odaklı Eval ve ASR Ölçümü | Saldırı senaryolarını başarı koşullarıyla tanımlayıp ASR, yanlış pozitif ve savunma geçiş oranlarını ölçmeyi öğretir. | Savunma | Promptfoo, Ollama | Yazıldı |
| `ai-savunma-27` | garak ile Yerel Model Güvenlik Taraması | Yerel modelde garak taramaları çalıştırıp probe, detector ve bulguları risk bağlamıyla yorumlamayı öğretir. | Savunma | garak, Ollama | Yazıldı |
| `ai-savunma-28` | Uygulamaya Özel garak Detector Geliştirme | Uygulamanın başarısızlık koşulunu makine tarafından doğrulanabilir detector ile tanımlayıp yanlış tespitleri sınamayı öğretir. | Savunma | garak, FastAPI | Yazıldı |
| `ai-savunma-29` | Adversarial Regression ve Yayın Kapıları | Bilinen saldırıları sürüm bazlı regresyon paketlerine dönüştürerek model ve guardrail değişikliklerinde güvenlik eşiği kurmayı öğretir. | Savunma | Promptfoo, garak, Git | Yazıldı |
| `ai-savunma-30` | Uçtan Uca Yerel Purple Tatbikatı | Saldırı simülasyonu, guardrail, telemetri, olay müdahalesi ve regresyon doğrulamasını tek ölçülebilir tatbikatta birleştirmeyi öğretir. | Savunma | Ollama, garak, Promptfoo, SigNoz, Elastic | Yazıldı |

# Track: `ai-guvence` — AI Güvence, Araştırma ve Kanıt (34 ders)

## 1. Modül — Minik · ML Güvenliğine Giriş

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-guvence-01` | ML Güvenliği Deney Defteri | Veri, model, tehdit varsayımı ve ölçütleri tanımlayarak tekrarlanabilir bir ML güvenliği deney planı hazırlamayı öğretir. | Güvence | Python, JupyterLab, scikit-learn | Yazıldı |
| `ai-guvence-02` | Taban Model ve Ölçüm Referansı | Eğitim-test ayrımı, sınıf dengesi ve belirsizlik ölçümleriyle doğrulanabilir taban performans referansı oluşturmayı öğretir. | Güvence | scikit-learn, pandas, Matplotlib | Yazıldı |
| `ai-guvence-03` | Tehdit Modelinden Deney Sorusuna | Evasion, poisoning, gizlilik ve tedarik zinciri risklerini gözlemlenebilir hipotez ve ölçülebilir deney sorularına dönüştürmeyi öğretir. | Araştırma | JupyterLab, scikit-learn, Mermaid | Yazıldı |
| `ai-guvence-04` | Yanlış Pozitiflerin Güvenlik Maliyeti | Farklı eşiklerde hata matrisi ve maliyet değişimini ölçerek yalnız doğruluğa dayanan güvenlik iddialarını sınamayı öğretir. | Güvence | scikit-learn, NumPy, Matplotlib | Yazıldı |
| `ai-guvence-05` | Tekrarlanabilirlik ve Kanıt Paketi | Sabit tohum, veri sürümü, ortam kaydı ve deney çıktılarıyla bağımsız yeniden üretilebilir kanıt paketi oluşturmayı öğretir. | Güvence | MLflow, DVC, Git, JupyterLab | Yazıldı |

## 2. Modül — Tesviye · Sağlamlık ve Evasion

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-guvence-06` | TransformerLens ile Refusal Mekanizması | Refusal davranışının katman ve aktivasyonlardaki izlerini inceleyerek mekanistik yorumlanabilirlik bulgularını davranışsal testlerle ilişkilendirmeyi öğretir. | Araştırma | TransformerLens, PyTorch, Hugging Face | Yazıldı |
| `ai-guvence-07` | Beyaz Kutu FGSM Ölçümü | FGSM bozuntularını farklı epsilon değerlerinde üreterek doğruluk kaybı ve bozuntu büyüklüğü ilişkisini ölçmeyi öğretir. | Araştırma | PyTorch, ART, Matplotlib | Yazıldı |
| `ai-guvence-08` | PGD ile Saldırı Gücü Eğrileri | Adım sayısı ve bozuntu bütçesini değiştirerek sağlamlığı tek sonuç yerine eğriler üzerinden değerlendirmeyi öğretir. | Araştırma | ART, PyTorch, pandas | Yazıldı |
| `ai-guvence-09` | GCG ve AutoDAN: Ayrık Token Optimizasyonu | Gradyan ve genetik arama tabanlı yaklaşımların ayrık token uzayında saldırı soneklerini nasıl optimize ettiğini sorgu bütçesi ve transfer başarısıyla ölçmeyi öğretir. | Araştırma | PyTorch, llm-attacks, AutoDAN | Yazıldı |
| `ai-guvence-10` | Refusal Direction Removal ve Abliteration Ölçümü | Ortogonal projeksiyonla refusal yönünü kaldırmanın model davranışına, genel yeteneğe ve güvenlik regresyonuna etkisini kontrollü karşılaştırmayla ölçmeyi öğretir. | Araştırma | TransformerLens, PyTorch, LM Evaluation Harness | Yazıldı |

## 3. Modül — Küçük Orta · Veri Bütünlüğü ve Poisoning

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-guvence-11` | Veri Kökeni ve Şüpheli Kayıt Profili | Veri kaynağı, dönüşüm geçmişi ve dağılım sapmalarını inceleyerek izlenebilir şüpheli kayıt profili üretmeyi öğretir. | Güvence | pandas, DVC, Evidently | Yazıldı |
| `ai-guvence-12` | Etiket Gürültüsü ile Zehirlemenin Ayrımı | Rastgele etiket gürültüsüyle hedefli etiket değişikliğinin performans etkilerini ayrı deneylerde ölçmeyi öğretir. | Araştırma | scikit-learn, Cleanlab, NumPy | Yazıldı |
| `ai-guvence-13` | Zehirleme Oranı ve Etki Eğrisi | Kontrollü zehirli örnek oranlarını değiştirerek performans bozulmasının eşik ve doyum noktalarını ölçmeyi öğretir. | Araştırma | scikit-learn, PyTorch, Matplotlib | Yazıldı |
| `ai-guvence-14` | Backdoor Tetikleyici Deneyi | Yerel deneyde tetikleyici biçimi ve yerleşimini değiştirerek hedef sınıf başarısı ile temiz örnek davranışını ölçmeyi öğretir. | Araştırma | PyTorch, ART, Torchvision | Yazıldı |
| `ai-guvence-15` | Veri Ayıklama Yöntemlerinin Kanıt Değeri | Anomali ve etki temelli ayıklama yöntemlerinin tespit, yanlış alarm ve veri kaybı oranlarını karşılaştırmayı öğretir. | Güvence | Cleanlab, scikit-learn, PyTorch | Yazıldı |

## 4. Modül — Büyük Orta · Gizlilik

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-guvence-16` | Gizlilik Tehdit Modeli ve Bilgi Sızdıran Kanıtlar | Eğitim verisi, model çıktısı ve saldırgan bilgisi arasındaki ilişki için ölçülebilir gizlilik kanıtları tanımlamayı öğretir. | Araştırma | PyTorch, scikit-learn, JupyterLab | Yazıldı |
| `ai-guvence-17` | Üyelik Çıkarımı Saldırısı Ölçümü | Üye ve üye olmayan kayıtlar üzerinde üyelik çıkarımı kurarak AUC, avantaj ve yanlış pozitif oranlarını ölçmeyi öğretir. | Araştırma | ART, scikit-learn, PyTorch | Yazıldı |
| `ai-guvence-31` | Embedding Inversion: Gömmeden Kaynak Metin | Gömmenin kaynak metni ne kadar sızdırdığını ölç; parafraz geri-çıkarma (recovery@k) ve nitelik çıkarımını gerçek gömmelerde gör. | Araştırma | Ollama (all-minilm) | Yazıldı |
| `ai-guvence-18` | Aşırı Öğrenme ile Gizlilik Riski İlişkisi | Model kapasitesi ve eğitim süresini değiştirerek genelleme açığı ile üyelik çıkarımı başarısını karşılaştırmayı öğretir. | Araştırma | PyTorch, ART, MLflow | Yazıldı |
| `ai-guvence-19` | Diferansiyel Gizlilik Bütçesi Deneyi | DP-SGD epsilon, gürültü çarpanı ve kırpma eşiğini değiştirerek gizlilik bütçesi ile model faydası ödünleşimini ölçmeyi öğretir. | Güvence | Opacus, PyTorch, pandas | Yazıldı |
| `ai-guvence-20` | Gizlilik İddialarının Saldırıyla Doğrulanması | Diferansiyel gizlilikli ve standart modelleri aynı üyelik çıkarımı deneyinde karşılaştırarak gizlilik iddialarını sınamayı öğretir. | Güvence | Opacus, ART, MLflow | Yazıldı |

## 5. Modül — Başaltı · Tedarik Zinciri Güvencesi

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-guvence-21` | Model ve Veri SBOM Envanteri | Model, veri, bağımlılık ve temel imaj bileşenlerini ilişkilendirerek denetlenebilir tedarik zinciri envanteri oluşturmayı öğretir. | Güvence | Syft, CycloneDX, DVC | Yazıldı |
| `ai-guvence-32` | Slopsquatting Savunması: Paket Halüsinasyonu | Modelin önerdiği paketleri çıkar, typosquat'ı Levenshtein ile yakala, allow-list ile doğrula; halüsine paketin körü körüne kurulmasını gerçek modelde engelle. | Güvence | Ollama | Yazıldı |
| `ai-guvence-22` | Pickle, Safetensors, GGUF ve Chat Template Riskleri | Model dosyası biçimlerinin yürütme ve ayrıştırma farklarını, GGUF içindeki chat template’in rol sınırlarını ve prompt manipülasyonu riskini yalıtılmış örneklerle karşılaştırmayı öğretir. | Araştırma | Safetensors, PyTorch, llama.cpp, Jinja2 | Yazıldı |
| `ai-guvence-23` | Quantization Kaynaklı Güvenlik Regresyonu | GGUF quantization seviyeleri arasında aynı güvenlik ve yetenek testlerini çalıştırarak ağırlık sıkıştırmasının hizalama davranışına etkisini ölçmeyi öğretir. | Güvence | llama.cpp, GGUF, Promptfoo, garak | Yazıldı |
| `ai-guvence-24` | Sleeper Agent ve Model Ağırlığı Backdoor Ölçümü | Tetikleyiciye bağlı davranışların temiz ve tetikli girdilerdeki farkını ölçerek model ağırlıklarına gömülü backdoor iddialarını kanıtla sınamayı öğretir. | Araştırma | PyTorch, Transformers, Promptfoo | Yazıldı |
| `ai-guvence-25` | Yerel Model Tedarik Zinciri Değerlendirmesi | Yerel modelin indirme, bağımlılık, dosya biçimi ve çalıştırma katmanlarını ölçümlerle desteklenen raporda değerlendirmeyi öğretir. | Güvence | Ollama, Safetensors, modelscan, Syft | Yazıldı |

## 6. Modül — Başpehlivan · Araştırma ve Saha

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-guvence-26` | Makale Replikasyonu ve Sapma Analizi | Bir AI güvenliği makalesinin temel deneyini yeniden üreterek sonuç farklarını veri, hiperparametre ve uygulama ayrıntılarıyla açıklamayı öğretir. | Araştırma | PyTorch, ART, MLflow, JupyterLab | Yazıldı |
| `ai-guvence-33` | Red Team Metodolojisi ve Tekrarlanabilir Değerlendirme | Kapsam ve kuralı doğrula, bulguyu şiddetle puanla ve birleştir, iddiayı tek koşuyla değil gerçek modelde N koşunun tekrarlanabilirliğiyle kanıtla. | Araştırma | Ollama | Yazıldı |
| `ai-guvence-34` | LLM Uygulama Pentest Köprüsü: SSRF ve Yetki | Modelin etrafındaki uygulamayı saldırı yüzeyi gör; URL'leri SSRF + allow-list kapısından geçir, IDOR'u engelle ve gerçek modelin iç-adres denemesini durdur. | Araştırma | Ollama | Yazıldı |
| `ai-guvence-27` | Açık Eval Tasarımı ve Kalibrasyonu | Görev seti, değerlendirici, başarısızlık sınıfları ve insan doğrulaması örneklemiyle ölçüm kalibrasyonunu sınamayı öğretir. | Araştırma | LM Evaluation Harness, Promptfoo, Ollama | Yazıldı |
| `ai-guvence-28` | Opt-in Küçük–Güçlü Model Karşılaştırması | Açık tercihle küçük ve güçlü modelleri aynı görevlerde karşılaştırarak kalite, maliyet, gecikme ve güvenlik farklarını ölçmeyi öğretir. | Araştırma | Ollama, Promptfoo, opt-in güçlü model API’si | Yazıldı |
| `ai-guvence-29` | Sorumlu Bildirim Raporu | Yetkili veya sentetik bulguyu etki, yeniden üretim adımları, kapsam, kanıt ve belirsizliklerle sorumlu bildirim standardında raporlamayı öğretir. | Güvence | Markdown, Git, CVSS Calculator | Yazıldı |
| `ai-guvence-30` | Yayınlanabilir Purple Çalışma | Saldırı ve savunma deneylerini ortak ölçütlerle birleştirip yöntem, karşılaştırma ve yeniden üretim paketiyle yayınlanabilir çalışma hazırlamayı öğretir. | Araştırma | ART, Promptfoo, PyTorch, MLflow | Yazıldı |

# Track: `ai-ile-guvenlik` — AI ile Güvenlik: Zafiyet Avı, Triyaj ve Otonom Savunma (18 ders)

## 1. Modül — Minik · Yerel LLM'i Güvenlik Aracı Olarak Kullanmak

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-ile-guvenlik-01` | Yapılandırılmış Güvenlik Çıktısı ve Şema Zorlama | Güvenlik analizinde serbest metin yerine katı JSON şeması üretmeyi, eksik/fazla alanları ve tip kaymalarını yakalamayı ve yeniden deneme bütçesini öğretir. | Savunma | Ollama, Python | Yazıldı |
| `ai-ile-guvenlik-02` | Güvenlik Analizinde Halüsinasyon ve Kanıt Eşleştirme | Modelin raporladığı satır numarası, dosya yolu, CVE veya paket adını kaynak dosyayla çapraz doğrulamayı ve halüsinasyon oranını hesaplamayı öğretir. | Güvence | Ollama, Python ast/difflib | Yazıldı |
| `ai-ile-guvenlik-03` | Embedding ile Güvenlik Korpusu ve Benzer Zafiyet Arama | Zafiyet kayıtlarını, olay özetlerini ve yama notlarını yerel embedding modeliyle indekslemeyi ve kosinüs benzerliğiyle benzer vakaları bulmayı öğretir. | Temel | Ollama all-minilm:22m, SQLite | Yazıldı |

## 2. Modül — Tesviye · Kod Okuma ve Zafiyet Avında LLM

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-ile-guvenlik-04` | AST Ön-Elemesi ve LLM ile Kaynak–Evye (Source-to-Sink) Triyajı | Python ast ile tehlikeli çağrı adaylarını çıkarmayı ve sabit dizge ile kullanıcı girdisini ayırt etmek için LLM triyajı ve yanlış pozitif ölçümü yapmayı öğretir. | Savunma | Python ast, Ollama | Yazıldı |
| `ai-ile-guvenlik-05` | Kimlik Bilgisi ve Sır Sızıntısı Avında Bağlamsal Triyaj | Regex/entropi tarayıcılarının ürettiği sahte alarmları gerçek sır sızıntısından ayırmayı ve modele gerçek sırrı göndermeden maskeli bağlamla sınıflandırmayı öğretir. | Savunma | Python re, Ollama | Yazıldı |
| `ai-ile-guvenlik-06` | Yama Önerisi Üretimi ve Regresyon Doğrulaması | Açıklı kod parçası için yerel modelden yama üretmeyi ve yamanın hem açığı kapattığını hem normal işlevi bozmadığını otomatik sınamayı öğretir. | Savunma | Ollama, Python unittest | Yazıldı |

## 3. Modül — Küçük Orta · Keşif ve Fuzzing Otomasyonu

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-ile-guvenlik-07` | Kapsam Kilitli HTTP Keşfi ve Parametre Haritalama | Yerel web tezgahından dönen uç noktaları ve form parametrelerini ayrıştırmayı ve kapsam dışı hedefleri reddeden deterministik keşif kapısını öğretir. | Saldırı | http_tezgah, Ollama | Yazıldı |
| `ai-ile-guvenlik-08` | Dilbilgisi Destekli (Grammar-Guided) Fuzzing Yükü Üretimi | Modelin rastgele bozuk metin yerine hedef ayrıştırıcının sınır durumlarını zorlayan kurallı mutasyon yükleri üretmesini ve yanıt anomalisi tespitini öğretir. | Saldırı | Ollama, Python | Yazıldı |
| `ai-ile-guvenlik-09` | Başsız Tarayıcı (Playwright) ile DOM Güvenlik Denetimi | Yerel HTML uygulamasında Playwright ile form, gizli girdi ve CSP yüzeyini toplamayı ve dış ağ kapalıyken model destekli güvenlik doğrulamasını öğretir. | Saldırı | Playwright, Chromium, Ollama | Yazıldı |

## 4. Modül — Büyük Orta · Log, Telemetri ve Alarm Triyajı

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-ile-guvenlik-10` | Çoklu Log Akışı Özeti ve Kanıt Satırı Doğrulaması | Web, kimlik doğrulama ve DNS loglarını kümelemeyi, yerel modelle olay özeti üretmeyi ve özetteki her varlığı ham log satırlarıyla doğrulamayı öğretir. | Savunma | Ollama, JSONL | Yazıldı |
| `ai-ile-guvenlik-11` | LLM Destekli Sigma Kuralı Taslağı ve Yanlış Alarm Sınaması | Saldırı örneğinden yerel modelle Sigma kuralı taslağı üretmeyi, şemasını doğrulamayı ve temiz/saldırı log korpusunda TPR ile FPR oranını ölçmeyi öğretir. | Savunma | Ollama, Sigma | Yazıldı |
| `ai-ile-guvenlik-12` | Log Enjeksiyonuna Dayanıklı SOC Triyaj Hattı | Saldırganın User-Agent veya kullanıcı adına gömdüğü dolaylı prompt injection yüklerinin SOC özetleyici modelini yanıltmasını engellemeyi öğretir. | Savunma | Ollama, Python | Yazıldı |

## 5. Modül — Başaltı · Kendi Güvenlik Ajanını Yazmak

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-ile-guvenlik-13` | Salt-Okunur Keşif Ajanı ve Deterministik Kapsam Kilidi | Araç çağıran yerel güvenlik ajanında hedef IP/alan/dosya kapsam kilidi, adım bütçesi ve döngü kırıcı tasarımını öğretir. | Savunma | Ollama, Python | Yazıldı |
| `ai-ile-guvenlik-14` | Yıkıcı Eylemlerde İnsan Onayı (HITL) ve İmzalı Görev Kapısı | Güvenlik ajanının karantina, IP engelleme veya dosya silme gibi yüksek etkili araçları yalnızca doğrulanmış insan onayı ve parametre özeti eşleştiğinde çalıştırmasını öğretir. | Savunma | Ollama, hashlib/hmac | Yazıldı |
| `ai-ile-guvenlik-15` | Çok Ajanlı Mavi/Mor Takım İş Akışı (Toplayıcı → Analist → Doğrulayıcı) | Kanıt toplayan ajan, hipotez kuran analist ajan ve bulguyu bağımsız araçla doğrulayan hakem ajanın görev ayrımını ve zehirlenme izolasyonunu öğretir. | Savunma | Ollama, Python | Yazıldı |

## 6. Modül — Başpehlivan · Güvenlik Ajanını Değerlendirmek ve Güvence

| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |
|---|---|---|---|---|---|
| `ai-ile-guvenlik-16` | Güvenlik Ajanlarında Hassasiyet, Duyarlılık ve Maliyet Dengesi | Farklı istem/model/eşik ayarlarında güvenlik ajanının precision, recall, F1, gecikme ve token maliyetini birlikte ölçüp Pareto optimal yapılandırmayı seçmeyi öğretir. | Güvence | Ollama, Promptfoo | Yazıldı |
| `ai-ile-guvenlik-17` | Güvenlik Ajanına Karşı Kırmızı Takım (Anti-Triage & Evasion) | Saldırganın güvenlik ajanını kör etmek, yanlış hedefe yönlendirmek veya sonsuz araç döngüsüne sokmak için kullandığı karşı-saldırıları sınamayı ve sağlamlaştırmayı öğretir. | Saldırı | Ollama, Python | Yazıldı |
| `ai-ile-guvenlik-18` | Uçtan Uca Yerel AI Destekli Olay Müdahale ve Doğrulama Tatbikatı | Log anomalisi tespiti, kök neden hipotezi, kapsam kilitli inceleme, insan onaylı müdahale ve regresyon kuralı üretimini tek bir tekrarlanabilir kanıt paketinde birleştirmeyi öğretir. | Savunma | Ollama, SQLite, Sandbox | Yazıldı |
