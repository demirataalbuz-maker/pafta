# Yeni ders pu21 (plan-purple-9, Tatbikat yönetimi): yazar kontrolleri tamam, denetime hazır

- Yazar: claude-yazar. Atama: ortak pano 04.11.2026 18:13. Purple yapısı seçenek A (kullanıcı, 04.11).
- Puan verilmedi; bağımsız denetim claude-opus'tadır.
- Görsel sınama yapılmadı; kabul CLI üzerinden `tools/validate.py` ile yapıldı.
- Kurulum ve indirme yok. Yalnız standart kütüphane ve pu19'un yerel labı kullanıldı.

## Eklenen / değişen dosyalar

- `tracks/purple/lessons/pu21-tatbikat-yonetimi.md` (sha256 52776cb604b6a6aa…)
- `sandbox/purple_tatbikat_lab.py` (369c7d5758438798…):
  - RoE, eşleştirme ve özet için referans işlevler; `kod_koruma`.
  - Kapsam dışı yem dinleyicisi (`_Yem`) ve `calistir`.
  - pu19 labını yalnız import eder.
- `tracks/purple/fixtures/pu21_tatbikat/README.md` ve `plan.json` (caa25fd611395c1c…); sentetik.
- `outputs/yeni-pu21/pu21-1793809755503386500.json`: son kabul kanıtı.
- `tracks/purple/track.json`: pu20 ile açılan "Tatbikat Yönetimi ve Raporlama" modülüne yalnız `pu21` eklendi.
- `engine/`, `web/` ve `purple_sqli_lab.py` değişmedi. Commit/push yok.

## İçerik

### Görevler

1. **`kapsam_kontrol` (RoE kapısı):**
   - Hedefin adı ve portu birebir karşılaştırılır; `*` port jokeri yalnız RoE'de geçerlidir.
   - Ana tekniği yasak olan alt teknik de yasaktır.
   - Saat dilimli `[baslangic, bitis)` penceresi uygulanır.
   - Karar sırası: kapsam → yasak teknik → zaman.
2. **`eslestir`:**
   - Eylemler zaman sırasıyla gezilir.
   - Alarm aynı teknik ve hedefe ait olmalı ve `0 ≤ fark ≤ pencere` sağlanmalı.
   - Her alarm tek kez kullanılır; eşitlikte küçük `id` kazanır. Eşleşmeyen alarmlar ayrıca listelenir.
3. **`tatbikat_ozeti`:**
   - Teknik bazında `denenen`, `onlendi`, `tespit` ve `kacirildi` (ne önlenen ne tespit edilen) sayılır.
   - Reddedilen eylemler nedenleriyle listelenir.
   - Tespit oranının paydası yalnız izinli kayıtlardır.
   - `kapsam-disi-hedef` reddi varsa `durdur` döner.

### KUSURLU başlangıç kodları

Üç kusurlu başlangıç kodu var; kusurlar kodda yorumla söylenmez.

- **K1:** hedefi metin içinde arıyor (`127.0.0.10` kapsam içi çıkıyor); alt tekniği atlıyor; zamanı metin olarak ve bitiş dahil karşılaştırıyor.
- **K2:** hedefe bakmıyor; mutlak zaman farkı kullandığı için önceki alarmı da eşleştiriyor; alarmı tekrar kullanıyor.
- **K3:** reddedilenleri denenmiş sayıyor; `kacirildi = tespit yok`; oranı tüm kayıtlardan alıyor; her retle durduruyor.

### Anlatım öğeleri

- Tablo ve NOT.
- RoE'nin bir kapı olarak ele alınması ve kapının üç tuzağı.
- Eşleştirme (deconfliction).
- "Saldırgan ne dener, savunma neden kırılır" bölümü: T1078 kör noktası ve tırnak kuralının yanlış alarmı.
- Tahmin bloğu: metin ile zaman karşılaştırması, IP alt dizesi.
- Hata vitrini ve Sınır cümlesi.

### Kaynak doğrulaması

- ATT&CK kimlikleri (T1190, T1078, T1110.001, T1499, T1485) kullanılan anlamlarıyla yazıldı.
- NIST SP 800-115 genel çerçeve olarak anıldı; sayısal bir iddia alınmadı.
- VECTR yalnız "sahada kullanılan açık kaynak takip aracı örneği" olarak anıldı; kurulmadı.

## Gerçek final (son kabul koşusu)

- **Ortam:** yerel lab + kapsam dışı yem dinleyicisi, ikisi de `127.0.0.1` üzerinde. Dokuz eylemlik plan.
- **RoE kararları:** A5 yasak teknik; A6 ve A7 kapsam dışı (A7 = `127.0.0.10`); A8 zaman dışı. Diğer beş eylem izinli.
- **Trafik:** yem dinleyicisine **0** bağlantı gitti. Labda 7 gerçek istek oldu.
- **Alarmlar:** 4 alarm üretildi.
  - Eşleşmeler: A2→AL1, A3→AL2, A4→AL3.
  - A1 ve A9 (T1078) kaçırıldı.
  - AL4 (adında kesme işareti olan meşru hesap) hiçbir eylemle eşleşmedi; yanlış alarm.
- **Özet:** tespit oranı 3/5 = 0.6, `durdur: true`. Kabul `true`, `cleanup: true`.

## Kendi kontrollerim (`.ai-venv/Scripts/python.exe -X utf8`)

- **`tools/validate.py pu21`:** TEMİZ, 9 kontrol (1 tahmin, 4 solution, 4 starter).
- **`tahmin.py`:** 1 tahmin, 0 şüpheli.
- **`kirp_gercek.py` + `mutasyon.py --en-cok 1000`:** 18 + 18 + 15 = 51 mutant, 0 geçen. İlk turda 5 mutant geçti:
  - Port uzunluğu sınırı test edilmiyordu → 6 haneli port testi eklendi.
  - Sıfır gecikmeli alarm test edilmiyordu → aynı anda gelen alarm testi eklendi.
  - Üç eşdeğer mutant kaynağıyla kaldırıldı:
    - tek `:` garanti olduğu için `rsplit(":", 1)` yerine `split(":")`;
    - örnekteki pencere sabiti fixture'a taşındı;
    - yazdırmadaki `indent` kaldırıldı.
- **Kopya sondası 7/7 reddedildi:**
  - Altısı `kod_koruma` ile testte düştü. Bu koruma importları `json`/`re`/`pathlib.Path`/`datetime` ve yalnız `calistir` ile sınırlar; dinamik kodu ve `_` ile başlayan öznitelikleri reddeder.
  - inspect + exec hata vererek düştü.

## Denetçiye not

- Purple dersleri `ai_ders_takip`'te değil; durum pano ve bu raporla izleniyor.
- Son adım "Gerçek deney" başlıklı olduğu için mutasyonda kırpılıyor (AI dersleriyle aynı). Ayrıca `validate` ile iki kez gerçek koşuldu.
