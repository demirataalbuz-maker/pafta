# Yeni AI yazar — ÖNCE BUNU OKU

**Hazırlayan:** claude-opus (denetçi) · **Tarih:** 2026-11-04

Pafta'ya ders yazmak için katıldın. Bu dosya sana her şeyi anlatır. Önce bunu, sonra `YENI-AJAN-REHBERI.md`'yi oku. Ayrıntılı çalışma protokolü orada; burada **rol, kurallar, denetim barı, teslim akışı ve kalan işler** var.

---

## 0. Roller (çok önemli)
- **Denetçi = claude-opus (ben).** Ders YAZMAM. Gelen her dersi bağımsız denetler, kabul/iade kararını ve puanı yalnız ben veririm. "bitti" yalnız benden çıkar.
- **Yazar = sen.** Dersleri sen yazarsın, kendi kontrolünü yaparsın, sonra bana teslim edersin.
- **codex artık devrede değil.** gemini yeni ders almıyor. Yazılacak her iş sende.
- Bir şeyi bana sormadan önce: iş senin, yaz ve teslim et. Ben denetlerim.

## 1. Tek cümlede hedef
Pafta, **tamamen ücretsiz ve yerel** çalışan bir siber güvenlik + AI güvenliği eğitimi. Her ders gerçek araç/model çalıştırır, uydurma yoktur.

## 2. Çekirdek kurallar (ihlal = iade)
1. **Ücretsiz ve yerel.** Ücretli SaaS / gerçek bulut hesabı YOK. Ücretsiz-ama-kısıtlı olanı (Splunk Free, değerlendirme ISO, model lisansı) açıkça işaretle.
2. **Terimler çevrilmez.** Yalnız anlatım Türkçe. `prompt injection`, `membership inference`, `circuit breaker` terim olarak kalır. "Şaşkın Vekil", "Toplam Varyasyon Uzaklığı" gibi çeviri UYDURMA.
3. **Doğrulanmamış teknik iddia YAZMA.** Yanlış atıf, ters çevrilmiş metrik, uydurma sayı, sandbox'ın sabit seçimini genel gerçek gibi sunmak = iade. Her sayı/atıf ya kanıt dosyasından ya da adıyla bilinen kaynaktan (arXiv/commit numarasıyla) gelmeli. Makaleden aldığın sayının yanına "bu sayı makaleye aittir" yaz.
4. **Kurulum/indirme → önce onay.** Yeni model/araç/paket/imaj indireceksen ÖNCE panoya `uyari` + kaynak/sürüm/boyut/lisans yaz, **kullanıcı onayını** bekle. Onaysız indirme yapma. İndirince sabit revizyon + sha256 kullan, kanıta yaz.
5. **Dürüst kapsam.** Konuyu gerçekte gösteremiyorsan uydurma; ölçebildiğini ölç ve farkı yaz. Her ders "bu ders neyi **gösteremez**" sınır cümlesiyle biter.

## 3. Ders formatı
- Bloklar: `::: anlat`, `::: tahmin`, `::: gorev`. Son görev `::: gorev Gerçek deney` + `motor: ai-gercek`.
- `motor: ai-gercek` dersi GERÇEK araç/model ister; fixture'dan ayrı, yanlış çözümü reddeden test + kanıt dosyası üretir.
- Başlık alanında `esleme:` (saldırı↔savunma köprüsü ve/veya ilgili dersler).
- En az **3 KUSURLU başlangıç kodu** (starter). Kusuru doğrudan söyleme; tahminle buldur, çözümde açıkla.
- İlk anlatımda **gerçek araç tablosu** ("Gerçek araç ne der | Bu ders ne kullanır | Ne söyleyemez") ve bir `[!NOT]` bloğu (kalıcılık/görüntüleyici notu).
- Fixture: açılabilir sentetik veri + `hazirla()`; her çalıştırmada geçici kopyaya gelir, kalıcılık yoktur, gizli test ayrıdır.

## 4. Yeni anlatım teknikleri (bu dalgada zorunlu)
1. **Tahmin → çalıştır → fark:** tahminden sonra gerçek çıktı, öğrenci farkı kendi yazar.
2. **Saldırı↔savunma köprüsü:** `esleme:` ile açığı kapatmasına bağla.
3. **Hata vitrini:** gerçekte görülen yanıltıcı çıktıyı göster, "neden güven vermez?" sor.
4. **Kusurlu kodu öğrenci teşhis etsin.**
5. **Kanıt dosyasını yorumlat:** seed/sürüm/ikinci koşu kararı.
6. **Sınır cümlesi:** her ders neyi gösteremediğini söyler.

## 5. DENETİM BARI — ilk seferde geçmek için
Teslim etmeden önce kendin koş (`.ai-venv/Scripts/python.exe -X utf8`). Benim denetimim tam bunları arar:
- `tools/validate.py <id>` → **TEMİZ 9** (1 tahmin, 4 solution, 4 starter).
- `docs/denetim/araclar/tahmin.py . <id>` → **0 şüpheli**.
- `docs/denetim/araclar/mutasyon.py . --en-cok 1000 <id>` → **0 geçen** (hiçbir mutant testi atlatmamalı). Geçen varsa testi güçlendir, çözümü/testi ZAYIFLATMA.
- **Kopya sondası 4/4+ reddedilir:** derste `ai_lab.kod_denetimi(src, (yasak_adlar...), izin=())` çağır. `exec` konu değilse `izin=()`. Guard import-referans, inspect/getsource, exec/eval, `__code__`, getattr bypass'ini bloklar.
- İçerik okuması: tablo + `[!NOT]`, fixture + `hazirla()`, ≥3 KUSURLU starter, esleme, sınır cümlesi, atıfların doğruluğu.
- Gerçeklik: kanıt dosyasında model adı+sürüm+seed; ikinci koşuda aynı karar; gerçek biçimli fixture.

## 6. Teslim akışı
1. `tools/ai_pano.py acik` ve `tools/ai_ders_takip.py liste` → kimse aynı işte mi?
2. `tools/ai_ders_takip.py al <id> --kim <adın>` (sahiplen). Kurulum gerekiyorsa önce `uyari` + onay.
3. Yaz, kendi kontrollerini koş (bölüm 5).
4. `tools/ai_ders_takip.py durum <id> denetime-hazir --kim <adın> --not "..."`.
5. Teslim raporu yaz: `docs/ai-gercek/<ADIN>-YENI-<id>.md` — ne yaptın, atıf kaynakları, kendi kontrol çıktıları, kanıt dosyası yolu, bilinen sınırlar/kapsam notu.
6. Bana (claude-opus) bırak. Ben denetlerim; küçük düzeltmeyi "claude-opus düzeltti" notuyla ben yaparım, büyük sorun iade.
- **Dokunma:** `engine/`, `web/`, `sandbox/ai_gercek_lab.py` (ortak), puan dosyaları, başkasının aldığı ders. Ortak `track.json`'a yalnız kendi tek satırını ekle.
- Kullanıcının Ollama/WSL/Docker/yüklü modelini KAPATMA; yalnız kendi başlattığın süreci kapat.

## 7. Ortam
- Dersler: `.ai-venv` (torch/transformers). Red-team araçları: `.ai-araclar` (garak/PyRIT/lm-eval). Karıştırma.
- Yeni indirmeler ayrı `.deps/` altına (gitignore'da), `.ai-venv` kirletme.

## 8. KALAN İŞLER — hepsi sana atalı (21 ders)
Öncelik sırası kabaca: AI → klasik keşif/web → Purple modüller.

**AI (2):**
- `plan-saldiri-9` deepfake / ses klonlama tespiti (yerel TTS — KURULUM ONAYI)
- `plan-savunma-6` watermark / C2PA gömme + doğrulama (yerel, hafif)

**Klasik (9):**
- `plan-klasik-1` keşif (nmap/ffuf/nuclei, yalnız 127.0.0.1)
- `plan-klasik-2` web sömürüsü (SQLi/XSS/SSTI/XXE, Juice Shop/DVWA)
- `plan-klasik-3` pwn (overflow/ROP/format string)
- `plan-klasik-4` tersine mühendislik (Ghidra/capa/FLOSS)
- `plan-klasik-5` Windows/AD saldırı
- `plan-klasik-6` DevSecOps (Semgrep/Trivy/gitleaks)
- `plan-klasik-7` pentest raporu
- `plan-klasik-8` cloud/container (sonra)
- `plan-klasik-9` mobil/kripto/gerçek imajla DFIR (sonra)

**Purple modül kırmızı yarıları (10):** `plan-purple-1`…`plan-purple-10` — M1 CTID öykünme, M2 keşif/web/phishing, M3 kalıcılık, M4 privesc, M5 Kerberoast/LSASS, M6 Sliver C2+Zeek, M7 Atomic Red Team, M8 atlatma, M9 rapor/VECTR, M10 APT29 uçtan uca. Ayrıntı: `EKLEME-PLANI-KAYNAK.md` / `claude-devir/PAFTA-EKLEME-PLANI.md`.

> Not: `plan-savunma-8` (unlearning) ve `plan-ai-purple-kopru` (SOC köprü) codex tarafından yazıldı, şu an denetçi denetiminde — onları YAZMA.

## 9. En iyi örnekler (referans al)
- `ai-saldiri-48` (membership inference): arXiv numaralı atıf, metrik yönü doğru, hata vitrini gerçek AUC ile.
- `ai-saldiri-53` (VLM): gerçek model donuk, "yanlış başarı" kabul=false ile dürüstçe gösterilmiş, kapsam dar ve açık.
- `ai-savunma-34` (injection mimari): CaMeL/dual-LLM/spotlighting doğru atıf, "sayılar makaleye ait".

Bunların ders dosyalarını ve teslim raporlarını (`docs/ai-gercek/*-YENI-*.md`) açıp kalıbı gör. Bol şans — temiz ve dürüst yaz, denetimden ilk seferde geçersin.
