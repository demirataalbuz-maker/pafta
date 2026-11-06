# ai-temel-19 · gerçek deney adımı (uygulayıcı raporu, bağımsız denetim değil)

Adım 8 (index 7): "Gerçek deney · Önbellekteki model dosyalarını Hub kaydıyla doğrula", `motor: ai-gercek`, `gereksinim: torch`.
Derse özel kod: `sandbox/ai_gercek_ai_temel_19.py` (yeni). Ortak dosya değişmedi, kurulum/indirme yok.

Manifest kaynağı: 2026-10-28'de `HfApi().get_paths_info("HuggingFaceTB/SmolLM2-135M", ..., revision=93efa2f0…)` ile okunan
git blob kimlikleri, boyutlar ve model.safetensors LFS sha256 oid'i (yalnız meta veri isteği; ders sırasında ağ kullanılmaz).

Öğrenci: `ozetler(yol)` (akışlı sha256 + git blob sha1) ve `safetensors_baslik(yol)` (yalnız başlık; dtype/shape/offset/kapsama
denetimi, parametre sayımı). Test: geçici sentetik dosyalarda sözleşme (3 geçerli, 13 geçersiz başlık + yol hataları), sonra gerçek
önbellekte 8 dosya Hub manifestiyle, başlık parametresi transformers modeliyle; geçici kopyalarda 3 kurcalama.

Kabul (`kabul.py`): referans PASS + `kaynak: gercek, kabul: true`; başlangıç, boş, sabit, git blob \0'sız, big-endian, kapsama
denetimsiz, bayt sayan çözümler reddedildi. 2 ek koşuda PASS. Boş HF önbelleğiyle (`model_yok.py`) "GERÇEK MODEL DOSYALARI YOK"
FAIL, kanıt yok. Geçici kopyalar siliniyor. Ders ekranı: başlangıç "kabul yok", çözüm "✓ geçti / kabul edildi", Çalıştır raporu.
`validate.py --yol ai-temel`: bu ders temiz; tek sorun Codex'in ai-temel-14'ünde paralel koşu sırasında Ollama 500
(apply-template dial tcp). O ders tek başına 2/2 PASS; geçici yük hatası.

Gerçek sonuç: 8/8 dosya Hub kaydıyla aynı; yerel model.safetensors sha256 = Hub LFS oid 80521b40…; elle kurulan 134 baytlık LFS
işaretçisinin git blob kimliği Hub'daki ed736e4e… ile aynı. Başlık 30.528 bayt, 272 BF16 tensör, 134.515.008 parametre (= model).
Kurcalama: tek veri baytı değişikliği başlık denetiminden geçti, yalnız sha256 yakaladı; kesik dosya ve bozuk başlık boyu reddedildi.
