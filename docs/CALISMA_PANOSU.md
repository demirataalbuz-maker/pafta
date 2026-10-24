# Çalışma panosu

İki ajan aynı işi yapmasın, kimse "bu ne zaman oldu" demesin.

**Canlı liste:** `docs/DURUM.html` (tarayıcıda aç; 20 saniyede bir kendini yeniler) ve `docs/DURUM.md`. İkisi de her commit'ten sonra `.git/hooks/post-commit` → `tools/durum_listesi.py` ile kendiliğinden üretilir; git'e girmez, elle düzenlenmez. Elle yenilemek için: `python -X utf8 tools/durum_listesi.py`.

## Kurallar

- Bir maddeye **başlamadan önce** `docs/durum.json`'a o maddenin satırını `"durum": "calisiliyor"` ve `"kim"` ile ekle ve commit et. Anahtar, `Pafta_Takip.xlsx`'teki "Ne yapılacak" metninin birebir aynısıdır.
- Commit etmeden bırakacağın dosyalar varsa `"durum": "taslak"` ve `"dosyalar": [...]` yaz; panel onları sahibinin adıyla gösterir.
- İş bitince `"denetime-hazir"` ve `"commit"` yaz. "Bitti" kararı denetçinindir (`DENETIM.md` → Excel); Excel'de "Bitti" olan madde panelde kendiliğinden bitti görünür.
- Ortak bir dosyaya (`engine/`, `sandbox/`, `server.py`, `web/`, `tools/validate.py`) dokunacaksan `"not"` alanına hangi dosya ve neden, onu da yaz. Başkasının commit edilmemiş değişikliği olan dosyada yalnız kendi parçanı sahneye al.
- `Pafta_Takip.xlsx`, `DENETIM.md` ve `ASAMA2.md` denetçinindir.

> **Codex'e not:** 45 (regex lehçeleri) maddesinin PCRE2 ayağı (`sandbox/pcre2_engine.py`, `motor: pcre2`) ve 23 (SQL lehçeleri) maddesinin PostgreSQL ayağı (`sandbox/pg_lab.py`, `motor: postgres`) hazır. Yeniden yazma; kullan ya da genişlet.
