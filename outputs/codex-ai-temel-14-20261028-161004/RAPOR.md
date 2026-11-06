# ai-temel-14 · Gerçek JSON Schema üretimi · Codex kendi kabul raporu

Ders ortak takip aracından Codex adına alındı. Mevcut adımlar korunarak sonuna gerçek anlatım ve görev eklendi. Yeni yardımcı yalnız bu derse özel sandbox/ai_gercek_ai_temel_14.py. Ortak engine/web/ai_gercek_lab dosyaları değişmedi. Yeni kurulum/indirme, commit ve push yapılmadı.

## Gerçek model ve kaynak sahipliği

Ollama 0.40.11, kurulu qwen3:4b-instruct-2507-q4_K_M (digest 0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0). /api/chat format alanına gerçek JSON Schema verildi. İki rastgele sentetik not üretildi; ham istek ve yanıtlar arşivlendi. Semantik alan eşleşmesi bulgu olarak kaydedildi; sabit metin yanıtı test beklentisi yapılmadı.

Deney ayrı localhost Ollama sunucusu açtı; her istekte num_gpu=0, num_ctx=1024, num_predict=96. Gerçek /api/ps ölçümü: toplam 2,729,978,100 bayt, VRAM 0. Sahipli süreç ağacı kapandı. Kullanıcının sunucusu deney öncesi ve sonrası 0.40.11 yanıtını vermeye devam etti; başka model boşaltılmadı. Süre sınırı mevcut koşucu tavanı olan 300 saniyeye uyarlandı; ortak koşucu değiştirilmedi.

## Kabul

- Referans çözüm PASS; kaynak=gercek, kabul=true kanıtı.
- Starter, boş kod, sabit nesne, yinelenen anahtarı gizleme, sayısal onayı kabul etme ve ek alana izin verme: tümü FAIL olarak reddedildi.
- İç testte yedi mutant reddedildi. Katı bool, yinelenen anahtar, 4096 karakter sınırı, Türkçe/emoji, NaN/Infinity, Markdown ve trailing içerik reddi sınandı.
- Çalıştır modu OK; gerçek model çağrıları yapıldı.
- Ayrı test ilerlemesiyle gerçek Pafta ekranında Kontrol Et: 16/16 kontrol geçti, GERÇEK ÇAĞRI / kabul edildi. Ekran: ai-temel-14-ekran.png.
- AI Temel regresyonu: 18 mevcut ders / 154 kontrol; 18 tahmin, 68 çözüm, 68 starter geçti. Altı yazılmamış ders açık kaldı. Bu, eşzamanlı geliştirilen yolun bu koşu anındaki durumudur.
- Ham koşucu JSON, gerçek kanıt arşivi ve validate-ai-temel.log bu klasörde.

## Sınırlar

Şema ve tür kabulü, içeriğin doğruluğu veya araç yürütme yetkisi değildir. Modelin onay=true çıktısı kullanıcı onayı olarak kullanılmadı. Hiçbir dosya/araç eylemi yürütülmedi. Üretim güvenliği veya tüm promptlarda semantik doğruluk iddia edilmez. Kendi kabulüdür, bağımsız denetim değildir; ders denetime-hazir, bitti kararı bağımsız denetçiye aittir.

Protokolün resmî kaynağı: https://docs.ollama.com/capabilities/structured-outputs