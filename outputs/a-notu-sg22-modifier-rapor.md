# 48 · SG22 re, fieldref ve UTF-16 bayt sırası gerçek hedefte

27 Ekim 2026 · Claude.

Bağımsız denetimin eksikleri: **`re` ve `fieldref` görevde yok** (orta), **`utf16le`/`utf16be` ayrı görevde yok** (düşük).

## Eklenen

- **Ders bölümü:** bu sürümde ölçülen dönüşümler. `re` → `| regex`, `fieldref` → harfe duyarlı `| where 'A'='B'`, `wide` ve `utf16be` farklı kalıplar üretir. `utf16le` pySigma 1.5.1'de bilinmeyen değiştiricidir.
- **Görev 3:** `re` ile tire biçimli ve en az 16 karakterlik base64 yükü, `fieldref` ile kullanıcısı üst süreçten farklı PowerShell. Tanıklar: SYSTEM'in başlattığı kullanıcı süreci; harf farkı yüzünden farklı sayılan `PAFTA\mert`/`pafta\MERT`; kısa yük, çift boşluk, `+/` içeren yük, boşluksuz bayrak, aynı kullanıcı.
- **Görev 4:** aynı metin UTF-16LE ve UTF-16BE, başta ve ortada; UTF-8 ve başka metin yakalanmamalı. `utf16le` çevirisinin hata verdiği test içinde ölçülür.

## Kabul

- `tools/test_sigma_modifiers.py`: **13 davranış bozan mutant reddedildi, 0 geçen.** İlk koşuda dar base64 sınıfı (`+/=` yok) geçiyordu; `+/` içeren bir yük tanığı eklendi, şimdi reddediliyor.
- `tools/validate.py sg19 sg20 sg21 sg22`: Git Bash ve PowerShell temiz (30 kontrol).
- Kanıt: [a-notu-sg22-modifier-kabul.json](a-notu-sg22-modifier-kabul.json).

## Öz değerlendirme

**93/100 (A)**: test 24, kapsam 23, derinlik 22, gerçeklik 15, yol 9. Bağımsız denetim değildir.
