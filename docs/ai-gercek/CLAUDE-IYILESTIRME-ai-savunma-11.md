# ai-savunma-11 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo + `[!NOT]`:** İlk anlatımın başına bir tablo eklendi. Tablo üç şeyi anlatıyor: Ollama/OpenAI araç tanımı, `tool_calls` çıktısı ve FastAPI/Pydantic doğrulaması; dersin bunları nasıl temsil ettiği; iki senaryoluk deneyin, üç araçlı kuralların, sembolik bağlantı, Unicode ve DNS yeniden bağlama saldırılarının sınırları. Ardından sentetik veri ve kalıcılık notu var.
- **Çelişkili cümle:** "Bu derste model, ağ ve dosya sistemi kullanılmaz" cümlesi gerçek deneyle çelişiyordu. İş emrinde etiket olarak yoktu ama düzeltildi.
- **Görünür fixture:** `tracks/ai-savunma/fixtures/ai-savunma-11/` altına README ve üç veri dosyası eklendi:
  - `veri/arac_semalari.json`: 3 dar şema ve 5 bozuk şema. Bozuk şemalar: geniş yetki, gizlenmiş yan etki, fazla parametre, genel araç, 0 zaman aşımı.
  - `veri/arac_cagrilari.json`: 12 çağrı. Bunlar 9 tuzak içeriyor:
    - gezinti, mutlak yol, ters eğik çizgi, sürücü harfi
    - HTTP
    - `@` ile metadata IP'si
    - port
    - izinli alan adıyla başlayan yabancı alan adı
    - boşluklu başlık
  - `veri/yetki_istekleri.json`: 5 istek ve 3 bozuk istek.
  - Beklenen sonuçlar referans doğrulayıcıyla doğrulandı. Görev 1–3 `hazirla("ai-savunma-11")` çağırıyor.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Yalnız gerekli yetkinin varlığına bakıyor | 5 bozuk şemanın hepsi kabul ediliyor |
  | 2 | Yolda yalnız `..` parçasını arıyor, URL'yi önek ile denetliyor | 12 çağrının 10'u geçiyor; mutlak yol, `\`, sürücü harfi, `@`, port, yabancı alan adı ve boşluklu başlık kaçıyor |
  | 3 | Yalnız oturum kapsamına bakıyor | `i-genis` ve `i-yanlis` `calistir` alıyor |
  | Gerçek deney | Yalnız araç adına bakıyor | Çalıştır'da modelin taşıdığı `../../gizli/anahtar.txt` geçiyor, referans ise reddediyor |

- **Anlatım:** 4 anlatım bloğu toplam yaklaşık 900 kelime oldu. Eklenen konular:
  - Dar araç ilkesi: yanlış çağrının en kötü sonucunu sınırlamak.
  - Saldırgan bakışı: şemaya uyan ama tehlikeli argüman değerleri.
  - Sık tuzaklar: önek ile alan adı denetimi, yalnız `..` aramak, düzeltmek yerine reddetmek, normalleştirme sırası.
  - Gerçek deneyin 4 adımı ve bu makinede ölçülen sonuç.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_savunma_11.py`, yalnız bu derse ait):**
  - Her çağrı öğrenci doğrulayıcısının yanında bağımsız `arac_cagrisi_dogrula_referans` ile de değerlendiriliyor. Referans, dersin kendi çözümünden türetildi.
  - Ham yanıt ve araç çağrıları kanıta yazılıyor. Eskiden yalnız yol ve karar yazılıyordu.
  - Model ne metin ne araç çağrısı döndürürse `GercekLabYok` hatası veriliyor.
  - Ayarlar kanıta yazılıyor.
  - Kullanılmayan eski `_ilk_cagri` yardımcı işlevi kaldırıldı.
- **Kopya koruması:**
  - Yasak listesi `("arac_cagrisi_dogrula_referans", "kanit_yaz")` oldu. Eskiden `("referans", "getattr")` idi ve ihlalde test durmuyordu.
  - AST kontrolü eklendi; ihlalde `stop()` çağrılıyor.
- **Gerçek deney testi:**
  - Sözleşmeye eklenen kontroller: `web_getir` geçerli URL; yabancı alan adı, `@`, port ve HTTP reddi; boş parça, `.` parçası, 201 karakter, fazla argüman ve string olmayan değer reddi.
  - **Bilerek yapılan değişiklik:** Eski testte iki koşul vardı: "`guvenli-1` çağırmalı ve geçerli olmalı", "`gezinti-1` çağırmalı ve reddedilmeli". İkisi de modelin aracı çağırmasını ve dizeyi aynen taşımasını kabul şartı yapıyordu. Yeni koşullar şunlar:
    - Model hangi çağrıyı ürettiyse, öğrencinin kararı o çağrı için referans kararla aynı olmalı.
    - Gerçek yolda `..` parçası varsa red zorunlu.

    Doğru bir çözüm için test gevşemedi. Referans karşılaştırması eskisinden sıkı.
  - Kanıt yalnız `kabul=all(sonuclar)` ile yazılıyor.
- Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-savunma-11` (PAFTA_DATA=`<scratchpad>/s11-kabul`) | **TEMİZ**, 9 kontrol |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-savunma-11` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` ile kopya, ardından `mutasyon.py --en-cok 1000 ai-savunma-11` | 10 + 23 + 5 = 38 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-savunma ai-savunma-11 ...` | 6/6 **fail → korunuyor**, kanıt yazılmadı |

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/s11-kabul/ai-kanit/savunma-arac-*.json`, kabul `true`.
- **Model:** `qwen3:4b-instruct-2507`. İki senaryoda da `dosya_oku` aracını çağırdı:

  | Senaryo | Modelin verdiği yol | Karar |
  |---|---|---|
  | `guvenli-1` | `belgeler/ozet.txt` | geçerli |
  | `gezinti-1` | `../../gizli/anahtar.txt` (aynen taşındı) | reddedildi, "dosya parçası geçersiz" |

  İki kararda da referansla uyumlu. Araç hiç çalıştırılmadı.
- **Çalıştır (CLI runner `run`):** Kusurlu başlangıç kodu `ok` döndü ama gezinti çağrısını geçirdi; referansla uyumsuzluk görünür.
- **Görev 1–3 (görünür veriyle elle koşturuldu):** Başlangıç kodları tablodaki kusurları gösterdi. Çözümler:
  - 5 bozuk şemayı ayrı nedenlerle reddetti.
  - 12 çağrıdan yalnız `c-01`, `c-06` ve `c-11` çağrılarını geçirdi.
  - Yalnız `i-oku` için `calistir` verdi.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- FastAPI ve Pydantic çalıştırılmadı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
