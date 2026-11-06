# ai-saldiri-09 — gerçek çıktı sink'i
Uygulayıcı kabulü; bağımsız denetim değildir. 29 Ekim 2026.

Değişen: tracks/ai-saldiri/lessons/ai-saldiri-09-guvensiz-llm-ciktisi.md (eski adımlar + anlat/gerçek görev index8), sandbox/ai_gercek_ai_saldiri_09.py, web/data/ai-saldiri-09-ciktilar.txt. Paket/ortak motor/uygulama kodu değiştirilmedi; commit/push yok.

Görünür elle yazılmış sentetik JSON örnekleri + ayrı kalıcı öğrenci dosyası + iki gerçek Qwen yanıtı. Çalıştır her örneği gerçek HTMLParser'da ham ve kaçışlı işler; etiket/metin etkisini ölçer. Model belirli metni aynen döndürmek zorunda değildir. HTMLParser JavaScript çalıştırmaz; bu bir tarayıcı XSS yürütme kanıtı değildir. Markdown dar sözleşmesidir, tam renderer değildir; izinli URL SSRF açısından güvenli demek değildir.

Öğrenci dosyası ilk açılışta oluşturulur, sonraki çalıştırmada üzerine yazılmaz. Her denemenin ham TXT ve CSP taşıyan güvenli HTML belgeleri yeni klasörde korunur. Hatalı kaçış çözümü varsa belgeye güvenli referans yazılır; öğrenci hatası yine FAIL olur, hata etkin HTML olarak yayılmaz. Kullanıcı dosyası/kurulumu silinmez.

Kabul: hedef validate 1 ders/10 kontrol TEMİZ. kabul.py / summary.json 10/10: referans PASS; starter/boş/sabit + tırnaksız kaçış, userinfo kabulü, tehlikeli hedefi koruma, çift kaçış mutantları FAIL; Çalıştır OK + kabul=false; eksik Ollama FAIL, gerçek kabul yok. Test içinde önceki 9 mutant + yeni rastgele HTML/URL örnekleri sınanır.

Ders ekranında starter reddedildi; referans 35/35 gerçek PASS. Kanıt outputs/codex-kirmizi-seri-20261029/ui-data/ai-kanit/saldiri-09-cikti-1793267794655.json. CLI Çalıştır: 6 sentetik örnek + 2 canlı yanıt; ham markup görülen4, korumalı markup0. Bu yalnız bu örneklerdir, bütün XSS biçimlerinin engellendiği iddiası değildir.

Ek tarayıcı dosya görünümü doğrulanamadı: güvenli HTML'nin file:// adresini açma isteğini tarayıcı aracı güvenlik politikası engelledi (yalnız http/https izinli). Başka yüzey/protokolle aynı dosyayı açarak engel aşılmadı. Bu işlem PASS sayılmadı. Öğrenci normal kendi tarayıcısında dosyayı açabilir; bu oturumda onun adına açıldığı iddia edilmez.

Tam yol regresyonu ayrı logda kaydedilecek. Bağımsız denetim bekliyor.

UI Çalıştır kanıtı: outputs/codex-kirmizi-seri-20261029/ui-data/ai-kanit/saldiri-09-cikti-1793267881910.json; ham/sentetik ve canlı model çıktıları ayrı etiketli, korumalı markup0, bütün kontroller true, kabul=false. İki farklı süreç/çalışma dizininde kalıcılık persistence.json ile doğrulandı.

Tam yol regresyonu: 41 ders / 338 çalıştırma kontrolü geçti; 40 ve 41 derslerinde [cikti / degerlendirme] biçimi nedeniyle toplam4 kazanım metadata hatası var. Çalıştırma testleri TEMİZ, bütün validate sonucu metadata nedeniyle başarısızdır. Sahiplerine ortak panoda bildirildi, dosyalarına müdahale edilmedi.
