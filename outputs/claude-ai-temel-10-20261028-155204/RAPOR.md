# ai-temel-10 · gerçek deney adımı (uygulayıcı raporu, bağımsız denetim değil)

Adım 8 (index 7): "Gerçek deney · Elle LoRA ile gerçek modelde ince ayar", `motor: ai-gercek`, `gereksinim: torch`, timeout 300.
Derse özel kod: `sandbox/ai_gercek_ai_temel_10.py` (yeni). PEFT kullanılmaz, yeni kurulum yok. Öğrencinin `LoraDogrusal` sınıfı
gerçek q_proj/v_proj kopyalarında sözleşmeyle sınanır, sonra modelin deepcopy'sinde 30 katman × q/v'ye takılıp 40 adım Adam
(lr 2e-3, tohum 2026) ile CPU'da eğitilir; önbellekteki ortak model değişmez (özet karşılaştırması). Ortak dosya değişmedi.

Kabul (`python -X utf8 kabul.py`, gerçek koşucu): referans PASS + `kaynak: gercek, kabul: true`; başlangıç, boş, sabit ve 4 anlamlı
hata (ölçek alfa, B rastgele, temel dondurulmuyor, yerinde birleştirme) reddedildi; test içinde 6 mutant daha. Referans 3 ek koşuda
PASS (~20 sn). `validate.py --yol ai-temel` TEMİZ. Ders ekranı: başlangıç "kabul yok", çözüm "✓ geçti / kabul edildi" (Codex'in
paralel validate yükü altında ~2,5 dk), Çalıştır gerçek çıktı.

Gerçek sonuç: 460.800 / 134.515.008 parametre (%0,34) eğitildi (= rank·(giriş+çıkış) toplamı). Hedef cümle kaybı 4,85 → 0,0006;
"The secret code of the Pafta lab is" devamı ' that the first two letters of' → ' 7342.'. İlgisiz metin kaybı 2,67 → 6,72:
tek cümleye 40 adım aşırı öğrenme genel davranışı bozdu (bulgu, kabul şartı değil). Birleşik ağırlıklı model ile adaptörlü
model farkı 1,4e-4 (float32 logit).
