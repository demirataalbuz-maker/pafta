# Temel17 gerçek sunucu kabul sınırı

Üretim tipi API ilkelerini öğretir; üretim ölçeği veya vLLM/llama.cpp kabulü değildir. İlk üç görev görünür sentetik istek/SSE/FIFO örneklerini işler. Kelime sayımı gerçek tokenizer değildir; batching benzetimi prefill/KV blokları/gerçek token bütçesini ölçmez.

Gerçek final kurulu Ollama /api/generate stream=true ile dört ardışık ve iki istemci iş parçacığından eşzamanlı HTTP isteği atar. İstek başlangıç/bitiş aralıkları, ham NDJSON ve geliş zamanları korunur. Altı hatasız yanıt, bağımsız rapor karşılaştırması, çakışan iki istemci çağrısı, ölçülen ilk parça gecikmesi ve num_predict kesmesi kabul edilir. İstemci çakışması backend decode batching kanıtı değildir; sunucu iç sıraya koyabilir.

TTFT alanı ilk doneFalse NDJSON parçası zamanıdır; boş içerik de parça sayılır. Cihazda ilk token çekirdeği zamanı değildir. sure_ms son yanıt parçasıdır, son done nesnesinin uçtan uca süresi değildir. İstek aralıkları ayrı kaydedilir. Socket zaman aşımı vardır; gerçek kullanıcı iptalinin sunucu GPU işini durdurması, çift deadline politikası ve üretim servis güvencesi bu deneyde kabul edilmez.

Yeni indirme/kurulum ve mevcut servis ayarı değişikliği yoktur. Yalnız kendi kaynaklarını kapatan SohbetOturumu kullanılır. İleri backend batching telemetrisi ve üretim kapasite çalışması ayrı açık kapsamdır; tamamlandı denmez.
