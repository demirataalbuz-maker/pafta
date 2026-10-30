# 49 · YR19 gerçek MinGW çıktısında PE mimarisi ve rolü

27 Ekim 2026 · Claude.

Bağımsız denetimin eksikleri: **gerçek derleyici çıktısı (MinGW 32/64) yok, örnekler Python'da sentezleniyor** (orta) ve **`pe.is_32bit`/`is_64bit`/`machine` görevde yok; bozuk başlık tanığı zayıf** (düşük).

## Eklenen

- `ctypes_lab`'a `win32-dll` hedefi (i686-w64-mingw32-gcc -shared).
- **Ders bölümü:** `pe.machine` (COFF) ile `is_32bit()`/`is_64bit()` (Optional Header Magic) ayrı alanlardır; uyuşmazlık kurcalanma işaretidir. `is_dll()` ve bozuk `e_lfanew`'da modülün sessiz kalması.
- **Görev:** aynı C kaynağından gerçek MinGW ile derlenen 32/64 bit DLL ve EXE. `Win64_DLL_Export` ile `Win32_Program` kuralları yazılır. Tanıklar: başka export adı, `pafta_topla`'yı export eden 64 bit program, e_lfanew dışarıda/sıfır, Machine↔Magic uyuşmazlığı (dört yön), PE olmayan metin.

## Kabul

- `tools/test_yara_pe_mingw.py`: **7 davranış bozan mutant reddedildi, 0 geçen.** İki eşdeğer ayrı raporlandı: `is_64bit` kaldırılsa da Magic PE32 yapılan PE32+'ta export bulunmuyor; `is_pe` kaldırılsa da modül alanları PE dışında tanımsız.
- `docs/denetim/araclar/mutasyon.py . yr19 yr20`: 28 mutant, 0 geçen.
- `tools/validate.py --yol yara`: PowerShell 24 ders/146 kontrol temiz; `yr19 yr20` Git Bash temiz.
- Kanıt: [a-notu-yr19-mingw-kabul.json](a-notu-yr19-mingw-kabul.json).

## Öz değerlendirme

**92/100 (A)**: test 24, kapsam 23, derinlik 21, gerçeklik 15, yol 9. Bağımsız denetim değildir.
