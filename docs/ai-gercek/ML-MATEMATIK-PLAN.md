# Uygulamalı ML Matematiği modülü

Kaynak: kullanıcının 07.11.2026 kararı (panoda daraltılmış not). Kapsam yalnız ML matematiğini anlatan ve ölçen dersler; saldırı↔savunma çift çalışma haritası kapsam dışıdır.

## Yerleşim

`tracks/ai-guvence/track.json` sonunda yeni modül (M07, `baspehlivan`). Mevcut modüllerin sırası değişmedi. FGSM/PGD/GCG/MI mekanikleri `ai-guvence-07/08/09/17` ve `ai-saldiri-48` derslerindedir; bu modül onları tekrar etmez, arkasındaki matematiği ölçer.

| Ders | Konu | Gerçek deney | Cihaz |
|---|---|---|---|
| ai-guvence-35 | Dual norm ve Taylor | `load_digits` GELU MLP: autograd/merkezi fark, birinci ve ikinci derece tahminin koptuğu ε | CPU float64 (merkezi fark gereği) |
| ai-guvence-36 | Projeksiyon ve gradient masking | Aynı ağırlıkların logit ölçekli kopyası: CE-PGD ile margin-PGD | GPU float32 |
| ai-guvence-37 | GCG-lite | SmolLM2-135M, zararsız ` muz` hedefi: one-hot tahmin ile gerçek loss farkının Spearman/top-k ilişkisi | GPU |
| ai-guvence-38 | Embedding geometrisi | `all-minilm:22m`, Gaussian taban: etkin boyut, kontrast, hubness | Ollama + torch |
| ai-guvence-39 | Üyelik çıkarımı istatistiği | Hedef + 16 shadow MLP: loss eşiği ve likelihood ratio, Clopper-Pearson | GPU |
| ai-guvence-40 | Kalibrasyon, ROC, EER | `deepset/prompt-injections` + donuk distilbert özellikleri: ECE, temperature scaling, EER, sabit eşikli alarm | GPU |

## Sınırlar

- Yeni kurulum veya indirme yok; yalnız kurulu model, önbellek ve scikit-learn verisi kullanılır.
- 8 GB tek GPU; büyük eğitim yok. Her gerçek adım komut satırında GPU'da 6–15 sn, ders ekranında Çalıştır veya Kontrol 8–29 sn; CPU'ya düşünce en ağır ders (37) 52 sn sürdü. Ölçülen tepe ayrılan GPU belleği: 36: 68 MiB, 37: 1532 MiB, 39: 66 MiB, 40: 554 MiB.
- Hiçbir ders saldırı başarısını kabul şartı yapmaz; kabul, öğrencinin hesabının bağımsız referansla ve matematiksel değişmezliklerle uyuşmasıdır.
- 37'deki hedef zararsız sabit bir kelimedir; güvenlik hizalaması veya jailbreak ölçülmez.

Ders başına kontrol sonuçları: `docs/ai-gercek/CLAUDE-YENI-ai-guvence-{35..40}.md`.
