# ai-saldiri-10 — katı JSON'dan gerçek SQLite kuyruğuna
Uygulayıcı kabul raporu; bağımsız denetim değildir. 29 Ekim 2026.

Değişen dosyalar: tracks/ai-saldiri/lessons/ai-saldiri-10-yapilandirilmis-cikti.md (mevcut adımlar korunur, anlat + gerçek görev index8); sandbox/ai_gercek_ai_saldiri_10.py; web/data/ai-saldiri-10-json.txt. Kurulum/ortak motor/uygulama kodu/commit/push yok.

Veri: elle yazılmış sentetik ham JSON örnekleri + ayrı kalıcı öğrenci kopyası; iki canlı yerel Qwen3 4B yanıtı, gerçek SQLite isler/inceleme tabloları. Geçerli iç komut allowlist üzerinden kuyruğa yazılır; düşük güvence boş içerikle incelemeye gider; geçersiz JSON sıfır DB değişimi yapmalıdır. Bağlantı kapanıp yeni bağlantıyla kalıcı kuyruk okunur; sürüm, DB SHA256, gerçek satırlar ve model/cihaz/bellek kanıtta. Kuyruk adaptörü dersidir; model eylemi eval/exec/shell ile çalıştırılmaz, gerçek çeviri/özet üretildiği iddiası yoktur. Sentetik dosya_sil alanı hiçbir dosyayı silmez.

Model bozuk JSON'u düzeltirse, ya da kod çiti eklerse gerçek ham çıktı bağımsız sözleşmeyle değerlendirilir. Modelin bozuk JSON üretmesi veya saldırının başarılı olması geçme şartı değildir. Öğrencinin yanlış parser'ı geçersizi geçirirse sandbox kuyruğunda bu etki gerçekten gözlenir ve kabul FAIL olur. Görünür örnek ile gizli yeni metin/kimlik testleri ayrıdır.

Kabul: hedef validate 1 ders/10 kontrol TEMİZ. kabul.py/summary.json 10/10: referans PASS; starter/boş/sabit ve yinelenen anahtar/ek metin/bool güvence/düşük eşik mutantları FAIL. Çalıştır OK kabul=false; kapalı port + olmayan Ollama ile eksik bağımlılık FAIL, kabul kanıtı yok. Test içinde önceki8 mutant ve yeni rastgele JSON sözleşmeleri de sınanır. Kalıcı öğrenci dosyası farklı süreç ve çalışma dizinlerinde korunur (persistence.json; fixture kontrolü).

CLI referans gerçek sonuç: red6, iş3, inceleme1, canlı yanıt2; bütün disk/pipeline/kaynak/cihaz kontrolleri true. Bu küçük setin sayımlarıdır, genel güvenlik puanı değildir. Tam saldırı regresyonu önceki09 koşusunda338 çalıştırma geçti;40/41 kazanım metadata hatası4 ayrı bildirilmişti. Yeni10 ile ilişkili08/09/10 grup regresyonu ayrıca kaydedilir.

UI kabul ve son grup regresyonu tamamlandığında eklenecek. Masaüstü ikinci cihaz kabulü yok; bağımsız denetim bekliyor.

Son UI Kontrol38/38: outputs/codex-kirmizi-seri-20261029/ui-data/ai-kanit/saldiri-10-json-1793268336007.json. UI Çalıştır: saldiri-10-json-1793268405430.json; gerçek kuyruk yolu, red kayıtlar DB değişim0, bütün kontroller true/kabulfalse. 08/09/10 grup regresyonu 3 ders/30 kontrol TEMİZ (grup-regresyon.log). Bağımsız denetim bekliyor.
