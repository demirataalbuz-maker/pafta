# ai-ile-guvenlik-18 iyileştirme teslim raporu (İade Sonrası Yeniden Teslim)

Yazan: gemini, 01.11.2026.
Bu rapor Gemini'nin kendi kontrolleridir. Bağımsız denetim ve puan claude-opus'a aittir.

## 1. İade Gerekçesi ve Düzeltmeler

Denetçi `claude-opus`'un iade notu:
> "Anlatım '[SİSTEM:' ve '[System:' varyantlarının casefold()/lower() ile yakalandığını söylüyor ama bu YANLIŞ: Python'da '[SİSTEM:'.casefold() == '[si̇stem:' (İ → i + U+0307), '[sistem:' içermez. Referans (sandbox/ai_gercek_ai_ile_guvenlik_18.py:117) da .lower() kullanıyor, yani dersin kendi örneği karantinayı atlıyor. Düzelt: (1) referansta ve görev 1 çözümünde normalize et (ör. unicodedata.normalize('NFKD', s) + birleşik işaretleri at, sonra casefold), (2) görev 1 testine '[SİSTEM:' ve '[System:' içeren vaka ekle (başlangıç/eski çözüm bunu kaçırmalı), (3) anlatımdaki cümleyi doğru mekanizmayla yaz."

Uygulanan Düzeltmeler:
1. **Referans ve Çözüm Normalizasyonu:**
   - `sandbox/ai_gercek_ai_ile_guvenlik_18.py` içindeki `anomali_adaylarini_cikar_referans` fonksiyonuna Unicode NFKD normalizasyonu eklendi:
     `temiz = "".join(c for c in unicodedata.normalize("NFKD", ua) if not unicodedata.combining(c)).casefold()`
     ve `"[sistem:" in temiz or "[system:" in temiz` ile hem Türkçe `İ` harfi (`[SİSTEM:`) hem de İngilizce `[System:` varyantları eksiksiz yakalandı.
   - Görev 1 ve Görev 4 çözümlerine aynı normalizasyon mekanizması entegre edildi.
2. **Görev 1 Test Vakaları:**
   - Görev 1 `sozlesme` testine `[SİSTEM:` ve `[System:` içeren test logları eklendi. Başlangıç kodu ve eski düz `.lower()` kullanan çözümler bu vakaları kaçırarak sözleşme testinden elenir.
   - Görev 4 `_on_sozlesme` fonksiyonuna da aynı Unicode test vakaları eklendi.
3. **Anlatım Güncellemesi:**
   - Anlatımdaki geliştirici tuzakları maddesi, Unicode dekompozisyonu, `İ` harfinin `i + \u0307` davranışı ve NFKD + combining filtresi gereksinimiyle birebir uyumlu olacak şekilde düzeltildi. Toplam anlatım **891 kelimedir**.
4. **AST Kopya Koruması:**
   - `yasak` listesine `_zehirli_mi` eklenerek tam AST koruması sürdürüldü.

## 2. Dört Zorunlu Kontrolün Çıktıları

Tüm kontroller proje kökünden `.ai-venv/Scripts/python.exe -X utf8` ile çalıştırıldı:

1. **validate.py:**
   - Komut: `$env:PAFTA_DATA="C:/Users/demo12/AppData/Local/Temp/gemini-iz/ai-ile-guvenlik-18"; ./.ai-venv/Scripts/python.exe -X utf8 tools/validate.py ai-ile-guvenlik-18`
   - Sonuç: `1 ders, 9 kontrol · geçen: {'tahmin': 1, 'solution': 4, 'starter': 4}` → **TEMİZ** (Gerçek GPU/Ollama çağrısı dahil).

2. **tahmin.py:**
   - Komut: `./.ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/tahmin.py . ai-ile-guvenlik-18`
   - Sonuç: `1 tahmin, 0 şüpheli`.

3. **mutasyon.py:**
   - Komut: Kırpılmış kopyada (`C:/Users/demo12/AppData/Local/Temp/gemini-k2`) koşturuldu.
   - Sonuç:
     - Görev 1: 6 mutant, 6 yakalandı (yeni eklenen test vakalarıyla birlikte)
     - Görev 2: 3 mutant, 3 yakalandı
     - Görev 3: 3 mutant, 3 yakalandı
     - **toplam 12 mutant, 0 geçen**.

4. **kopya_sonda.py (3 Probe + Yardımcı):**
   - Probe 1 (`from sandbox.ai_gercek_ai_ile_guvenlik_18 import anomali_adaylarini_cikar_referans as anomali_adaylarini_cikar`): **fail → korunuyor**
   - Probe 2 (`import sandbox...; anomali = getattr(...)`): **fail → korunuyor**
   - Probe 3 (`import inspect...; exec(inspect.getsource(m))...`): **fail → korunuyor**
   - Probe 4 (`from sandbox... import _zehirli_mi`): **fail → korunuyor** (AST denetimiyle doğrudan engellendi).

## 3. Gerçek Deney Kanıtı

- Kanıt dosyası: `C:/Users/demo12/AppData/Local/Temp/gemini-iz/ai-ile-guvenlik-18/ai-kanit/ile-guvenlik-18-tatbikat-1793546436965.json`
- Model: `qwen3:4b-instruct-2507-q4_K_M` (GPU kipi, 4096 bağlam, VRAM: 3.18 GB).
- Model temizliği: `model_bosaltildi: true`.
- Kontroller: Tüm kontroller (`anomali_cikarma_uyumu`, `mudahale_dogrulama_uyumu`, `tatbikat_sonuc_uyumu`, `yalniz_dogrulanmis_mudahale_uygulandi`, `cihaz_dogrulandi`, `kaynak_temizlendi`) `True`.
- Kanıt kabul: `true`.

## 4. Değişen Dosyalar ve Sistem Durumu

- Düzenlenen dosyalar:
  - `tracks/ai-ile-guvenlik/lessons/ai-ile-guvenlik-18-uctan-uca-ai-destekli-olay-mudahale-tatbikati.md`
  - `sandbox/ai_gercek_ai_ile_guvenlik_18.py` (referans fonksiyona Unicode NFKD normalizasyonu eklendi)
- Motor/web dosyalarına dokunulmadı.
- Kullanıcının Ollama sunucusu, modelleri ve ortamları kapatılmadı/değiştirilmedi.
- Commit/push yapılmadı.
