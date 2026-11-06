# ai-saldiri-08 — disk hafızası ve yerel model kabulü
Uygulayıcı raporu; bağımsız denetim değildir. 29 Ekim 2026.

Değişiklikler: tracks/ai-saldiri/lessons/ai-saldiri-08-hafiza-zehirleme.md (eski adımlar korunarak anlat + gerçek görev, index8); sandbox/ai_gercek_ai_saldiri_08.py; web/data/ai-saldiri-08-hafiza.txt. Ortak motor/web kodu ve paketler değişmedi.

Veri kökeni: elle yazılmış sentetik JSONL, her koşuda yeni canary/zehir işareti; gerçek SQLite dosyası ve canlı Qwen3 4B çağrıları. Çalıştır öğrenci veri alanında kalıcı JSONL kopyası ve her deneye özel SQLite oluşturur. Şablonun üzerine yazılmaz, mevcut öğrenci verisi silinmez. Web dosyası görünür; düzenleme dış editör veya Python ile yapılır, uygulama içi dosya editörü yoktur. İki ayrı süreç/çalışma dizininde kalıcılık persistence.json ile doğrulandı (fixture kontrolü, canlı model kabulü sayılmaz).

Deney: öğrenci anahtar/yaz/oku işlevleriyle gerçek DB anlık görüntüsü oluşur; bağlantı kapanır, yeni SQLite bağlantısıyla yeniden okunur. Başka kullanıcı/oturum, olmayan kapsam, geri dönen kaydın kopyası ve veri rolü denetlenir. Dört canlı senaryo: temiz, korumalı, kusurlu global okuma, kusurlu rol terfisi. Modelin saldırıya uyması geçme şartı değildir. Kusurlu akış yalnız izole laboratuvar karşılaştırmasıdır. Üretim kimlik doğrulaması veya evrensel enjeksiyon savunması iddiası yoktur.

Kabul: python -X utf8 tools/validate.py --yol ai-saldiri ai-saldiri-08 → 1 ders/10 kontrol TEMİZ. kabul.py/summary.json: 9/9 beklenen sonuç. Referans PASS; starter/boş/sabit + kapsam birleştirme, veri rolünü sisteme çevirme, oturumu yok sayma mutantları FAIL. Test içinde önceki 9 mutant ve rastgele yeni kimlik/not sözleşmeleri de sınanır. Çalıştır OK ve kabul=false; eksik Ollama FAIL/kanıt yok. UI başlangıç 10/14 ile reddedildi; referans 33/33 gerçek PASS, kanıt outputs/codex-kirmizi-seri-20261029/ui-data/ai-kanit/saldiri-08-hafiza-1793267406324.json.

Gerçek bulgu (CLI referans): global kusurlu akışta canary bağlama ve yanıta girdi; korumalı akışta yabancı canary ne bağlama ne yanıta girdi. Zehir işareti korumalı yanıtta da görüldü; işaretin görünmesi tek başına modelin talimata uyduğu ile alıntı yaptığı durumları ayırmaz. Bu yüzden başarı oranı diye sunulmadı. Veri rolünü korumak modelin anlamsal olarak talimata uymamasını garanti etmez. Sürüm/model/digest/cihaz/bellek, gerçek mesajlar/yanıtlar/hatalar, SQLite sürümü ve DB SHA-256 kanıtta.

Tam saldırı yolu regresyonu ayrıca kaydedilecek. Commit/push, kurulum yok. Sonraki ders 09; kullanıcı tarafından çıkarılan 12/31/32/33/30 alınmayacak.

Son regresyon: 40 ders/325 koşulun tamamı geçti; yalnız başka ajanın aktif ai-saldiri-40 dersinde iki BİLİNMEYEN KAZANIM metadata hatası var ([cikti, degerlendirme]). Regresyon bütünü TEMİZ diye sunulmaz, konu panoda sahibine bildirildi. UI Çalıştır kanıtı: outputs/codex-kirmizi-seri-20261029/ui-data/ai-kanit/saldiri-08-hafiza-1793267498074.json; SQLite dosyası ve dört gerçek yanıt görüldü, bütün kontroller true, kabul=false.
