# ai-temel-06 · gerçek deney adımı (uygulayıcı raporu, bağımsız denetim değil)

Adım 8 (index 7): "Gerçek deney · Gerçek bir katmanda çok başlı nedensel dikkat", `motor: ai-gercek`, `gereksinim: torch`.
Derse özel kod: `sandbox/ai_gercek_ai_temel_06.py` (yeni). Bütün kafaların Q/K/V'si SmolLM2'nin projeksiyonları + RoPE ile
çıkarılır, GQA Key/Value'ları 9 Query kafasına genişletilir; doğrulama modelin katman çıktısıyla (o_proj girdisi). Ortak dosya değişmedi.

Kabul (`python -X utf8 kabul.py`, gerçek koşucu): referans PASS + `kaynak: gercek, kabul: true`; başlangıç, boş, sabit cevap ve
4 anlamlı hata (atlamalı kafa bölme, maske yok, √D ölçek, ters birleştirme) reddedildi. Test içinde 7 mutant + nedensellik özellik
testi (son token bozulunca önceki satırlar değişmemeli). Referans 3 ek koşuda PASS. Modelle en büyük fark ≤1e-6.
`validate.py --yol ai-temel` TEMİZ. Ders ekranı: çözüm "✓ geçti / kabul edildi", başlangıç "kabul yok"; Çalıştır gerçek çıktı.

Gerçek bulgu: 'The keys to the cabinet are on the table' → son kelime 'chair' yapılınca ilk 8 konumun logit farkı 0.0,
son konumun 8.73 (nedensellik). Katman 4'te son token kafaların 8'inde 'the'ya, kafa 2'de 'keys'e bakıyor.
