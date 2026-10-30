# AI Temel08 sunucu kapsamı

30 Ekim2026 kullanıcı en güçlü öğretim seçeneğini istedi; uygulama tercihi mevcut CPU KV deneyini korumak ve kurulu Ollama ile ikinci gerçek deney eklemek oldu. Yeni indirme/kurulum yok. Eski vLLM/llama.cpp sunucuları karşılaştırma planı bu dersin kabul iddiası değildir.

- Görev1–3: sentetik K/V, bütçe seçimi, kiracı görünürlüğü; görünür veri/cache.json.
- Gerçek görev1: kurulu SmolLM2 CPU modeli; gerçek past_key_values uzunluğu, devam tokenları, tam hesap ile logit eşdeğerliği.
- Gerçek görev2: kurulu Ollama modeli; deneye ait dinamik loopback HTTP uygulamasında iki çakışan istek ve gerçek model çıktıları. Geçici Bearer kimliğinden tenant belirlenir. Öğrencinin kiraci_cache işlevi gerçek HTTP okuma yolunda çalışır. Korumasız negatif kontrol, korumalı kendi kayıt görünümü, sahte kimlik403, anonim401 ve kendi sunucu kapanışı ölçülür.

HTTP isteği çakışması backend'in aynı anda token ürettiği, sürekli batching yaptığı, GPU belleğinin kiracılar arasında yalıtıldığı veya vLLM/llama.cpp ile performans karşılaştırıldığı anlamına gelmez. Uygulama çıktı indeksi K/V tensoru değildir. Süre veya rastgele yanıt metni geçme şartı değildir.

Yalnız deneyin kendi HTTP sunucusu kapanır; kullanıcının Ollama sunucusu kapanmaz. Ortak SohbetOturumu sahiplik kuralı uygulanır. Puanı Codex yazmaz; Opus denetler. Denetimde kapsam eksik bulunursa gerekçesiyle iade edilir; yeni araç gerektiğinde kaynak/sürüm/boyutla ayrıca onay alınır.
