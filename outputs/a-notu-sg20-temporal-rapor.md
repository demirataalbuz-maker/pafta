# 46 · SG20 zamansal korelasyon gerçek Splunk'ta

27 Ekim 2026 · Claude.

Bağımsız denetimin eksiği: **zamansal korelasyon (`temporal` / `temporal_ordered`) hiç yok.** ASAMA2 sıra ve yinelenen olay testleri de istiyor.

## Eklenen

- **Ders bölümü:** `temporal` korelasyonun Splunk backend'indeki gerçek çevirisi (`multisearch` + `bin` + `dc(event_type)`), ölçülerek yazıldı. Sonuçları: sıra yok, pencere sabit kutu, tekrar sayılmaz. `temporal_ordered` bu backend sürümünde (2.1.0) desteklenmiyor; çeviri hata verir.
- **Görev 3:** başarısız (4625) ardından başarılı (4624) giriş, `group-by: TargetUserName`, 5 dk. Tanıklar: ayse (eşleşir); can (ters sırada, yine eşleşir); deniz (kutu sınırının iki yanında); berk/ece (tek tür); ek veride farklı hesap adı, üç tekrar başarılı giriş ve listede olmayan 4672. Sıralı türün çeviri hatası test içinde ölçülür.
- **Harness:** `|` ile başlayan korelasyon sorgusunda her `[ search` alt araması laboratuvar dizinine sınırlanır (ilk denemede alt aramalar dizini görmedi ve sonuç boş geldi; bulundu, düzeltildi).

## Kabul

- `tools/test_sigma_temporal.py`: **8 davranış bozan mutant reddedildi, 0 geçen** (pencere 10/2 dk, grup yok ya da yanlış grup, tek kural, yanlış olay kimliği, sayım korelasyonu).
- `tools/validate.py --yol sigma`: 22 ders, 130 kontrol temiz; `sg20` değişiklikten sonra ayrıca temiz.
- Kanıt: [a-notu-sg20-temporal-kabul.json](a-notu-sg20-temporal-kabul.json).

## Öz değerlendirme

**92/100 (A)**: test 23, kapsam 22, derinlik 23, gerçeklik 15, yol 9. Bağımsız denetim değildir.
