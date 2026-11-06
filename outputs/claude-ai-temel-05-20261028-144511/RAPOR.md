# ai-temel-05 · gerçek deney adımı (uygulayıcı raporu, bağımsız denetim değil)

Adım 8 (index 7): "Gerçek deney · Gerçek bir kafada nedensel dikkat", `motor: ai-gercek`, `gereksinim: torch`.
Derse özel kod: `sandbox/ai_gercek_ai_temel_05.py` (yeni). Q/K/V, SmolLM2'nin q/k/v_proj ağırlıkları ve RoPE'u ile
kancalardan çıkarılır; doğrulama modelin o kafadaki gerçek çıktısıyla (o_proj girdisi) yapılır. Ortak dosya değişmedi.

Kabul (`python -X utf8 kabul.py`, gerçek koşucu): referans PASS + `kaynak: gercek, kabul: true` kanıtı; başlangıç, boş,
sabit cevap ve 4 anlamlı hata (ölçek yok, maske yok, softmax sütunda, maske softmax sonrası) reddedildi. Test içinde
ayrıca 7 mutant reddediliyor. Referans 3 ek koşuda PASS (rastgele cümle/katman/kafa). Modelle en büyük fark 4.7e-07–1.4e-06.
`validate.py --yol ai-temel` TEMİZ. Ders ekranı: başlangıç reddedildi, çözüm "✓ geçti", kanıt "kabul edildi";
Çalıştır gerçek dikkat haritası + "kabul yok (yalnız deneme)" kanıtı.

Gerçek bulgu: 4. tokendan itibaren ilk tokena giden ortalama dikkat (attention sink), katman 0/3/15/29:
0.20 / 0.41 / 0.71 / 0.63 ("The cat sat on the mat because it was tired").
