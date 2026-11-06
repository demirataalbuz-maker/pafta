# Yeni ders ai-savunma-37 (plan-savunma-6, Watermark/C2PA): yazar kontrolleri tamam, denetime hazır

- Yazar: claude-yazar.
- Atama: ortak pano 04.11.2026 18:13 kararı. Codex devreden çıktı; bütün yazılacak işler claude-yazar'a geçti.
- Puan verilmedi; bağımsız denetim claude-opus'tadır.
- Görsel sınama yapılmadı; kabul CLI üzerinden `tools/validate.py` ile yapıldı.

## Kurulum (kullanıcı onayıyla, 04.11.2026)

- Önce panoya `soru` yazıldı. Kullanıcı "İkisini de onayla" dedi; ardından panoya `karar` yazıldı.
- İndirilen dosya: `c2patool` v0.28.4, Windows zip (https://github.com/contentauth/c2patool/releases/tag/v0.28.4).
  - Boyut 10.998.290 bayt; sha256 `00e5bcfe…72f1`. İkisi de codex'in hazırladığı onay listesiyle birebir aynı.
  - Zip, yol taşması denetimiyle `.deps/c2patool-0.28.4/acik/` altına açıldı.
- `c2patool.exe` sha256 `9a447201…8e98`; sandbox bunu her koşuda doğruluyor.
- PATH, Windows kurulumu, `.ai-venv` ve `%APPDATA%\c2pa\c2pa.toml` değişmedi; sonuncusu yoktu ve yine yok.

## Eklenen / değişen dosyalar

- `tracks/ai-savunma/lessons/ai-savunma-37-c2pa-filigran.md` (sha256 52b8cd87bc288dfa…)
- `sandbox/ai_gercek_ai_savunma_37.py` (ced0ea4420bd9a61…)
- `tracks/ai-savunma/fixtures/ai-savunma-37/README.md` ve `veri/c2pa.json` (2b0bb18a6f5b9683…)
  - `okumalar` yazar koşusundan alınmış ham c2patool çıktılarıdır.
  - Diğer alanlar elle yazıldı.
- `outputs/yeni-ai-savunma-37/` altında iki kanıt dosyası:
  - `yazar-sondasi.json`: hata vitrininin kaynağı.
  - `savunma37-kabul-1793806538301.json`: son kabul kanıtı.
- `tracks/ai-savunma/track.json`: "RAG ve Tedarik Zinciri Koruyucusu" modülünde 36'dan sonra yalnız `ai-savunma-37` eklendi.
- `engine/`, `web/` ve `sandbox/ai_gercek_lab.py` değişmedi. Commit/push yok.

## Kaynak doğrulaması

C2PA Teknik Spesifikasyonu 2.1'den okunanlar:
- Hard binding: varlığın ya da bir bölümünün kriptografik hash'i.
- Soft binding: filigran ve parmak izi; manifest silindiğinde yeniden eşleştirmek için kullanılır.
- C2PA Trust List: X.509 güven çapaları.
- Spesifikasyon, köken verisinin iyi ya da kötü olduğuna dair değer yargısı vermemesi gerektiğini söyler.

Durum kodlarının hepsi (`signingCredential.untrusted`, `assertion.dataHash.mismatch`, `Trusted/Valid/Invalid`, "No claim found") gerçek c2patool çıktısından alındı; varsayım yok.

## İçerik

### Görevler

1. `c2pa_durumu`: c2patool ham çıktısını `manifest-yok`, `gecersiz`, `gecerli-guvenilmeyen` ya da `guvenilen` olarak sınıflandırır; ayrıca sıralı hata kodlarını ve **aktif** manifestin imzacısını döndürür.
2. `filigran_gom` ve `filigran_oku`: tekrarlı LSB filigranı gömer ve çoğunluk oyuyla okur; kapasiteyi denetler.
3. `kanit_raporu`: her dönüşümü C2PA sınıfı, güven ve filigranın kalıp kalmadığıyla raporlar. Üç liste üretir: `yalniz_filigran`, `hicbiri`, `imzali_guvenilmeyen`.

### KUSURLU başlangıç kodları

Üç kusurlu başlangıç kodu var; kusurlar kodda yorumla söylenmez.

- **K1:**
  - `rc≠0` her zaman `gecersiz` sayılıyor.
  - `failure` listesi boş değilse `gecersiz` deniyor; böylece `Valid` ama güvenilmeyen bir imza yanlış sınıflanıyor.
  - İmzacı ilk manifestten okunuyor; hatalar sırasız.
- **K2:** gömme `|` ile yapılıyor, bu yüzden 0 biti yazılamıyor. Okuma yalnız ilk değere bakıyor; çoğunluk oyu yok.
- **K3:** bozuk manifest `imzali` sayılıyor, güven varsayılan okumadan alınıyor, eşik katı uygulanıyor (`<`), sıralama yok.

### Anlatım öğeleri

- Kaynak tablosu ve NOT.
- Üç ayrı soru: bütünlük, imzacı güveni, içerik gerçekliği.
- "Saldırgan ne dener" ve "savunma neden kırılır" bölümleri.
- Tahmin bloğu: `|` ile `&254|` farkı ve çoğunluk.
- Eşleme: `esleme: ai-savunma-36, ai-savunma-20, ai-saldiri-53`.
- Hata vitrini, yazar koşusundan üç örnekle:
  1. Pikseller aynı kaldığı hâlde manifest `Invalid`.
  2. Yeniden kaydedince manifest gitti, filigran kaldı.
  3. Saldırganın imzası `Valid` çıktı.
- Kanıt okutma ve Sınır cümlesi.

## Gerçek final (son kabul koşusu)

- Ortam: c2patool 0.28.4, 12 gerçek okuma, yaklaşık 26 sn (validate toplamı). Ağ yok, zaman damgası yok; geçici klasör silindi.

| Dönüşüm | Varsayılan | Test kök | Filigran BER |
|---|---|---|---|
| imzali | gecerli-guvenilmeyen (`signingCredential.untrusted`) | **guvenilen** | 0.0 |
| meta_eklendi (yalnız tEXt parçası) | gecersiz (`assertion.dataHash.mismatch`) | gecersiz | 0.0 |
| png_yeniden | manifest-yok | manifest-yok | 0.0 |
| jpeg_q85 | manifest-yok | manifest-yok | 0.469 |
| olcek_yarim | manifest-yok | manifest-yok | 0.438 |
| saldirgan_imzali ("Haber Ajansi (sahte)") | gecerli-guvenilmeyen | gecerli-guvenilmeyen | 0.0 |

- Rapor listeleri:
  - `yalniz_filigran`: [png_yeniden]
  - `hicbiri`: [jpeg_q85, olcek_yarim]
  - `imzali_guvenilmeyen`: [saldirgan_imzali]
- Ölçekleme BER'i yazar koşusunda 0.344, kabul koşusunda 0.438. Bitler her koşuda rastgele; ders sabit değer iddia etmiyor.
- **Kabul şartları:**
  - Dört işlevin gerçek çıktılarda referansla birebir aynı olması.
  - Test kökün imzalı dosyayı gerçekten `Trusted` yapması.
  - Saldırgan imzacısının bu koşuda üretilen sertifika olması.
  - 6 farklı dosya ve imzalı dosyada BER 0.

  Filigranın JPEG ya da ölçeklemede yaşaması kabul şartı değil.

## Kendi kontrollerim (`.ai-venv/Scripts/python.exe -X utf8`)

- `tools/validate.py ai-savunma-37` (PAFTA_DATA scratchpad):
  - Sonuç: TEMİZ, 9 kontrol (1 tahmin, 4 solution, 4 starter).
  - `gereksinim: torch`: `.ai-venv`'deki Pillow ve cryptography kullanılıyor.
- `tahmin.py`: 1 tahmin, 0 şüpheli.
- `kirp_gercek.py` + `mutasyon.py --en-cok 1000`: 5 + 32 + 24 = 61 mutant, 0 geçen.
  - İlk turda 2 mutant geçti: okumada 0/255 sınırı ve çoğunluk katsayısı.
  - `[0]`, `[255]`, 5'te 2 ve 7'de 3 testleri eklendi.
- Kopya sondası 7/7 reddedildi:
  - modül takma adı, `from sandbox import`, importlib, `__import__` + vars, `*` import ve doğru çözüm + eval testte düştü (`kod_denetimi(..., izin=())`).
  - inspect + exec ise hata vererek düştü.

## Bilinen sınırlar / denetçiye not

- **TEST kökü üretim güveni değildir.** `guvenilen` sonucu yalnız c2patool'un örnek TEST kökü bilerek güvenilir sayıldığında çıkıyor. Ders bunu açıkça söylüyor.
- **Saldırgan sertifikası.** Sertifika her koşuda `cryptography` ile üretiliyor ve atılıyor. Adı "Haber Ajansi (sahte)", kurum adı "Sahte Org". Gerçek bir kurumu taklit etmiyor.
- **Filigranın kapsamı.** Filigran eğitim amaçlı basit bir LSB filigranı; ticari ya da üretken model filigranlarının dayanıklılığını temsil etmiyor (Sınır cümlesinde yazıyor).
- **Platform.** Final yalnız Windows'ta çalışıyor ve onaylı `.deps` kurulumu gerekiyor. Kurulum yoksa `GercekLabYok` ile duruyor; otomatik indirme yok.
