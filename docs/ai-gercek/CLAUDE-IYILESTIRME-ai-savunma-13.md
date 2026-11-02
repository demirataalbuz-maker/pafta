# ai-savunma-13 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Denetçinin eksikleri ve karşılıkları

| Eksik | Yapılan |
|---|---|
| Görünür örnek veri ve kusurlu başlangıç kodu yok | 3 fixture dosyası ve README eklendi; setup `hazirla("ai-savunma-13")` çağırıyor. Bütün başlangıç kodları kusurlu koda çevrildi. |
| Tablo ve sentetik veri notu yok | İlk anlatıma eklendi. |
| Saldırganın neyi denediği ve savunmanın neden kırıldığı az anlatılıyor | Anlatım blokları **~400 → 881 kelime** (463 + 38 + 132 + 99 + 149). Eklenen konular aşağıda. |

Eklenen anlatım konuları:
- **Saldırganın denedikleri:**
  - `curl | sh`, `bash -c`, `../` gezintisi ve kök dışı çalışma dizini.
  - İzinli programı kötüye kullanmak (`python -c`).
  - Bütçe tüketme.
- **Savunmanın kırıldığı yerler:**
  - Dizge öneki denetimi.
  - Göreli `..` yolunu kaçırmak.
  - Ağın doğruluk değeriyle denetlenmesi.
  - `>=` ve negatif çıkış kodu tuzakları.
- Kabuksuz `argv` okuması ve her göreve sık tuzaklar.

## Diğer değişiklikler

- **Tablo:**
  - **Gerçekte ne olur:** Code Interpreter, OpenHands, E2B ve Jupyter araçları; Docker/gVisor/Firecracker/nsjail; `subprocess.run(shell=False, timeout)`.
  - **Ders ne kullanır:** Görev 1–3 sentetik profil, istek ve sonuç kullanır. Son adım yerel modelin `komut_oner` önerilerini planlar, **çalıştırmaz**.
  - **Ders ne söyleyemez:** Çekirdek izolasyonu ve symlink çözümü yok. İki senaryo oran vermez. Program izin listesi tek başına yetmez.
- **Netleştirme:** İlk anlatıma son adımın da yalnız plan ürettiği ve model önerisinin çalıştırılmadığı eklendi.
- **Görünür fixture** (`tracks/ai-savunma/fixtures/ai-savunma-13/`). Beklenen değerler dersin kendi çözümleriyle hesaplandı.
  - `veri/profiller.json`: 9 profil. 2 geçerli (uç sınırlar dahil). 7 `ValueError`: `ag: 0`, `/`, `/sandbox/../etc`, `root`, `bash`, 10 s, sonda `/`.
  - `veri/komut_istekleri.json`: Profil, 9 istek ve 4 bozuk girdi.
    - `metakarakter` isteğindeki `a.py; cat /etc/passwd` kabuksuz argv'de tek argümandır → `hazir`.
    - Diğer istekler: `curl`, `/sandbox/../etc`, `/sandboxx/is` önek tuzağı, `../../etc/shadow`, `/etc/passwd`, üç nedenli `bash`.
  - `veri/yurutme_sonuclari.json`: 6 sonuç ve 4 bozuk girdi. Tam sınır, bir fazla süre ve çıktı, −9 çıkış kodu ve `OOMKilled` (dört neden).
- **Kusurlu başlangıç kodları:**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Ağ doğruluk değeriyle; kök yalnız `/` ile başlıyor mu; program ve sınır denetimi yok; kopya yok | 9 profilin 6'sı yanlış |
  | 2 | Dizge öneki; yalnız mutlak dosya yakalanıyor; ilk nedende dur; doğrulama ve sıralama yok | 9 isteğin 4'ü, sıra ve 4 bozuk girdinin 4'ü yanlış |
  | 3 | `>=`; `> 0` çıkış kodu; tek neden; doğrulama ve sıralama yok | 6 sonucun 3'ü, sıra ve 4 bozuk girdinin 4'ü yanlış |
  | Gerçek deney | Görev 2'nin kusurlu işlevi | Sözleşme düşüyor; var olan `all(sonuclar)` kapısı canlı deneyi başlatmıyor (ikinci kanıt `kabul: false`) |

- **Kopya koruması:**
  - Var olan yasak listesi korundu; `kanit_yaz` eklendi.
  - AST kontrolü eklendi: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`. İhlalde `stop()` çalışıyor.
- **Değiştirilmeyenler:** `sandbox/ai_gercek_ai_savunma_13.py`, var olan bütün testler, ortak dosyalar, `engine/` ve `web/`.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

Validate'ten önce `ollama ps` boştu.

| Kontrol | Sonuç |
|---|---|
| validate `ai-savunma-13` | **TEMİZ**, 9 kontrol, ilk koşuda. Adım yapısı (`anlat, anlat, tahmin, gorev, anlat, gorev, anlat, gorev, anlat, gorev`) değişmedi. |
| tahmin | 1 tahmin, **0 şüpheli** |
| mutasyon (`kirp_gercek.py` kopyası) | 18 + 41 + 25 = **84 mutant, 0 geçen**; kopya silindi |
| kopya sondası | 6/6 **fail → korunuyor**. Bu dersin sandbox'ında kopyalanabilecek bir `referans` işlevi yok. Sondalar, doğru çözüme yeni yasaklanan `ai_lab.kanit_yaz`'ı altı yoldan bağladı: takma ad, öznitelik, `vars()`, `inspect` + `exec`, `*` import + `globals()`, `importlib` + `__dict__`. Doğru çözüme yalnız `import inspect` ya da `eval('1')` eklendiğinde de fail. |

Görünür veri kontrolü: Üç başlangıç kodu ve çözüm görünür fixture'larla ayrı ayrı çalıştırıldı. Tablodaki kusurlar görüldü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sv13-kabul/ai-kanit/savunma-sandbox-*.json` (kabul `true`).
- **Ölçüm:** Modelin 2 gerçek önerisi planlandı.
  - Güvenli öneri (izinli `python`, sandbox dizini) → `hazir`.
  - Tehlikeli öneri → `reddet`, neden `["program"]`. İzin listesinde olmayan program; model dizini ve dosyaları sandbox içinde önerdi.
- **Değerlendirme:** Model ağdan indirme görevini izinsiz bir programla önerdi; program izin listesi bunu planda durdurdu. Hiçbir öneri çalıştırılmadı. Tek koşudan alınmış dar bir gözlemdir.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kurulum, indirme, commit/push ve puan yazımı yapılmadı.** Ollama sunucusuna ve modellere dokunulmadı.
