# ai-ile-guvenlik-16 iyileştirme teslim raporu

Yazan: gemini, 01.11.2026.
Bu rapor Gemini'nin kendi kontrolleridir. Bağımsız denetim ve puan claude-opus'a aittir.

## 1. İş Emri ve Yapılanlar

Kuyruk etiketleri: `kusurlu`, `anlatim`.

1. **Purple Standardı Tablo ve `[!NOT]` Bloğu:**
   - İlk anlatımın başına 3 sütunlu gerçeklik tablosu (`| Gerçek araç / model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`) ve altındaki `> [!NOT]` bloğu eklendi.
   - İlk üç görevin `ajan_kosu_sonuclari.json` sentetik benchmark verilerini okuduğu, setup ile her çalıştırmada kopyalanıp sıfırlandığı ve çalıştırmalar arasında kalıcılık olmadığı belirtildi. Canlı modelin yalnız final deneyinde çalıştığı, Promptfoo ve harici eval harnesses'ların başlatılmadığı açıkça yazıldı.

2. **Kusurlu Başlangıç Kodları:**
   - Görev 1–3 başlangıç kodları `# KUSURLU BAŞLANGIÇ KODU: <hata>` yorumlu gerçekçi hatalı kodlara çevrildi:
     - **Görev 1:** Sıfıra bölme ve float hassasiyet yuvarlamalarını yapmadan ham bölme uygulayan başlangıç kodu. (Testi geçmez, sözleşme doğrulaması reddeder).
     - **Görev 2:** Token ve gecikme maliyetlerini ters yönde karşılaştırarak daha çok kaynak tüketen hantal ayarları baskın sayan başlangıç kodu. (Testi geçmez).
     - **Görev 3:** Bütçe ve Pareto baskınlık kapısını işletmeden yalnız asgari recall kontrolüyle ilk ayarı seçen başlangıç kodu. (Testi geçmez).
     - **Görev 4 (Gerçek deney):** Sözleşme kontrollerini karşılamayan kusurlu fonksiyon şablonları.

3. **Derinleştirilmiş Anlatım:**
   - Toplam anlatım kelime sayısı **843 kelimeye** çıkarıldı (hedef ~450+ kelimeydi).
   - SOC triyajı ve güvenlik ajanlarında kalite-maliyet dengesi, çok amaçlı optimizasyon (Multi-Objective Optimization) ve Pareto cephesi gereksinimleri detaylandırıldı.
   - Saldırgan taktikleri (algoritmik karmaşıklık / ReDoS / kaynak tüketimi saldırıları ile modelin CoT modunu tetikleyip gecikmeyi ve faturayı tavan yaptırma; düşük duyarlılıklı hızlı ajan modunun radarına takılmamak için düşük profilli sızma) açıklandı.
   - Savunmanın kırılma noktaları (yalnızca F1'e odaklanıp üretim kuyruğunun kilitlenmesi veya bütçe baskısıyla düşük recall profillerinin kritik alarmları kaçırması) anlatıldı.
   - Geliştirici tuzakları (sıfıra bölme, bool/int tip karışıklığı, Pareto baskınlık yönü, kesin üstünlük şartı, bileşik sıralama anahtarı) ele alındı.

4. **Kopya Koruması (AST + Kod Denetimi):**
   - Gerçek deney testine AST tabanlı ithal kontrolü (`ast.walk`, `ast.ImportFrom` ve `*` engeli) ile `yasak=("referans", "ajan_metrik_hesapla_referans", "pareto_baskin_mi_referans", "optimal_ajan_sec_referans", "getattr", "kanit_yaz")` listesi eklendi.
   - İhlal durumunda `stop()` garantilendi.
   - `ai_lab.kanit_yaz` çağrısı `"kabul": all(checks)` ile mühürlendi.

## 2. Dört Zorunlu Kontrolün Çıktıları

Tüm kontroller proje kökünden `.ai-venv/Scripts/python.exe -X utf8` ile çalıştırıldı:

1. **validate.py:**
   - Komut: `$env:PAFTA_DATA="C:/Users/demo12/AppData/Local/Temp/gemini-iz/ai-ile-guvenlik-16"; ./.ai-venv/Scripts/python.exe -X utf8 tools/validate.py ai-ile-guvenlik-16`
   - Sonuç: `1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}` → **TEMİZ** (Gerçek GPU/Ollama çağrısı dahil).

2. **tahmin.py:**
   - Komut: `./.ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/tahmin.py . ai-ile-guvenlik-16`
   - Sonuç: `1 tahmin, 0 şüpheli`.

3. **mutasyon.py:**
   - Komut: Kırpılmış kopyada (`C:/Users/demo12/AppData/Local/Temp/gemini-k2`) koşturuldu.
   - Sonuç:
     - Görev 1: 3 mutant, 3 yakalandı
     - Görev 2: 3 mutant, 3 yakalandı
     - Görev 3: 5 mutant, 5 yakalandı
     - **toplam 11 mutant, 0 geçen**.

4. **kopya_sonda.py (3 Probe):**
   - Probe 1 (`from sandbox.ai_gercek_ai_ile_guvenlik_16 import ajan_metrik_hesapla_referans as ajan_metrik_hesapla`): **fail → korunuyor**
   - Probe 2 (`import sandbox...; ajan_metrik_hesapla = getattr(...)`): **fail → korunuyor**
   - Probe 3 (`import inspect...; exec(inspect.getsource(m))...`): **fail → korunuyor**
   - 3 referans fonksiyonunu birden import eden saldırı: **fail → korunuyor** (AST denetimiyle doğrudan engellendi).

## 3. Gerçek Deney Kanıtı

- Kanıt dosyası: `C:/Users/demo12/AppData/Local/Temp/gemini-iz/ai-ile-guvenlik-16/ai-kanit/ile-guvenlik-16-denge-1793544444009.json`
- Model: `qwen3:4b-instruct-2507-q4_K_M` (GPU kipi, 4096 bağlam, VRAM: 3.18 GB).
- Model temizliği: `model_bosaltildi: true`.
- Kontroller: Tüm kontroller (`metrik_hesaplama_uyumu`, `pareto_baskinlik_uyumu`, `optimal_secim_uyumu`, `dengeli_ayar_secildi`, `cihaz_dogrulandi`, `kaynak_temizlendi`) `True`.
- Kanıt kabul: `true`.

## 4. Değişen Dosyalar ve Sistem Durumu

- Düzenlenen dosya: `tracks/ai-ile-guvenlik/lessons/ai-ile-guvenlik-16-hassasiyet-duyarlilik-ve-maliyet-dengesi.md`
- Sandbox (`sandbox/ai_gercek_ai_ile_guvenlik_16.py`) ve motor/web dosyalarına dokunulmadı.
- Kullanıcının Ollama sunucusu, modelleri ve ortamları kapatılmadı/değiştirilmedi.
- Commit/push yapılmadı.
