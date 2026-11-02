# ai-savunma-15 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo ve `[!NOT]`:** İlk anlatıma eklendi.
  - **Gerçekte ne olur:** Vault/STS/Workload Identity, broker, Gitleaks/TruffleHog.
  - **Ders ne kullanır:** Görev 1–3 sentetik veriyle çalışır. Son adım yerel modelin metinlerini sandbox'ın sentetik sırrıyla maskeler.
  - **Ders ne söyleyemez:** Bölünmüş, kodlanmış ya da büyük harfe çevrilmiş sır yakalanmaz.
- **Anlatım derinleştirme:** Anlatım blokları **~350 → 859 kelime**. Eklenen konular: saldırganın denedikleri, savunmanın kırıldığı yerler, her göreve sık tuzaklar ve çıktı okuma.
- **Tutarlılık düzeltmeleri:**
  - Anlatım ömrü "1–300 **saniye**" diyordu; görev ve test ise 1–300 **ms** kullanıyor. Anlatım ms olarak düzeltildi ve bunun sentetik bir ölçek olduğu yazıldı.
  - İlk anlatımdaki "bütün değerler yapay fixture" cümlesi son adımı da kapsayacak şekilde netleştirildi.
- **Görünür fixture** (`tracks/ai-savunma/fixtures/ai-savunma-15/`). Beklenen değerler çözümle hesaplandı.
  - `veri/log_kayitlari.json`: 6 kayıt ve 4 bozuk girdi. Kayıtlar: önek çakışması, aynı satırda iki sır, bölünmüş sır ve büyük harfli sır (son ikisi bilinen sınır, `bulgu: 0`).
  - `veri/kapsamlar.json`: 9 kapsam. Örnekler arasında 300 saniye birim tuzağı, `model_gorebilir: 0`, joker ve `sil` var.
  - `veri/broker_istekleri.json`: 6 istek, son geçerlilik anında ve 1 ms geç kullanım, 4 bozuk girdi.
- **Kusurlu başlangıç kodları:**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Verilen sırayla maskeliyor, `[GIZLI]CD34` kuyruğu kalıyor; bulgu sır türü olarak sayılıyor; doğrulama yok | 2 kayıt, sıra ve 4 bozuk girdi yanlış |
  | 2 | Ömür saniye sanılıyor; `model_gorebilir` doğruluk değeriyle okunuyor; liste denetimi yok | 9 kapsamın 5'i yanlış |
  | 3 | Yalnız araç karşılaştırılıyor; kanal ve tekrar denetimi yok; son an dışarıda; izinde ham anahtar dönüyor | 6 isteğin 6'sı yanlış |
  | Gerçek deney | Görev 1'in kusurlu işlevi | `all(sonuclar)` kapısı canlı deneyi başlatmıyor (ikinci kanıt `kabul: false`) |

- **Kopya koruması:** AST kontrolü ve `stop()` eklendi. Yasak listesine `kanit_yaz` ve sandbox'taki `SECRET` sabiti eklendi.
- **Değiştirilmeyenler:** Sandbox, var olan testler, `engine/` ve `web/`.

## Kontroller

| Kontrol | Sonuç |
|---|---|
| validate | **TEMİZ**, 9 kontrol, ilk koşuda |
| tahmin | **0 şüpheli** |
| mutasyon | **29 mutant, 0 geçen** |
| kopya sondası | 8/8 **fail → korunuyor**: `kanit_yaz` altı yoldan bağlandı, ayrıca `import inspect` ve `eval` denendi |

Görünür veri kontrolü: Kusurlu kodlar tablodaki yerlerde düştü; çözümler bütün beklenen değerleri verdi.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sv15-kabul/ai-kanit/savunma-secret-*.json` (kabul `true`).
- **Ölçüm:** Model log senaryosunda sırrı 1 kez yazdı. Maskeleme 1 eşleşmeyi `[GIZLI]` yaptı; maskeli metinde ham sır kalmadı. Zararsız senaryoda bulgu 0.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.**
- **Kurulum, commit/push ve puan yazımı yapılmadı.**
