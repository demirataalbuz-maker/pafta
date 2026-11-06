# Yeni ders pu20 (plan-klasik-7, Pentest raporu): yazar kontrolleri tamam, denetime hazır

- Yazar: claude-yazar.
  - Atama: ortak pano 04.11.2026 18:13 kararı.
  - Kullanıcının 04.11 tarihli "Evet, A + başla" kararıyla Purple yapısı **seçenek A** oldu: mevcut modüller ve `pu01`–`pu19` değişmedi.
- Puan verilmedi; bağımsız denetim claude-opus'tadır.
- Görsel sınama yapılmadı; kabul CLI üzerinden `tools/validate.py` ile yapıldı.
- Kurulum ve indirme yok. Yalnız Python standart kütüphanesi ve pu19'un yerel labı kullanıldı.

## Eklenen / değişen dosyalar

- `tracks/purple/lessons/pu20-pentest-raporu.md` (sha256 b1c506b8f35de793…)
- `sandbox/purple_rapor_lab.py` (dde6b72d061fbb1a…):
  - pu19'un `YerelSQLiLab` sınıfını yalnız **import eder**; `purple_sqli_lab.py` değişmedi.
  - İçerik: CVSS 3.1, kanıt ve rapor referansları, `kod_koruma`, `calistir`.
- `tracks/purple/fixtures/pu20_rapor/README.md` ve `bulgular.json` (61205285eb5ae6cd…); sentetik.
- `outputs/yeni-pu20/` altında son kabul kanıtı ve ürettiği Markdown rapor:
  - `pu20-1793809052453079100.json`
  - `pu20-rapor-1793809052453079100.md`
- `tracks/purple/track.json`: yalnız sona yeni modül eklendi: "Tatbikat Yönetimi ve Raporlama" (rank `baspehlivan`, lessons `["pu20"]`). Diff yalnız ekleme içeriyor.
- `engine/` ve `web/` değişmedi. Commit/push yok.

## Kaynak doğrulaması

- **CVSS v3.1 spesifikasyonu (FIRST):** formül, katsayı tablosu, tam sayıya dayalı Roundup ve seviye ölçeği resmî belgeden okundu.
- **Referans uygulamanın sınaması:**
  - Bilinen değerlerle karşılaştırıldı: 9.8, 6.1, 7.8, 9.9, 10.0, 0.0.
  - Bütün 2592 temel vektör tarandı; en küçük sıfır olmayan puan 1.6, en büyük 10.0. Seviye sınırlarına denk gelen vektörler (3.9, 4.0, 6.9, 7.0, 8.9, 9.0) testlerde kullanıldı.
- **NIST SP 800-115:** genel çerçeve olarak anıldı; içinden sayısal bir iddia alınmadı.

## İçerik

### Görevler

1. **`cvss31`:** vektör sırasını ve değerlerini doğrular. Kapsama bağlı PR katsayısını ve Roundup'ı uygular, seviyeyi döndürür.
2. **`kanit_dogrula`:** `sha256(istek + "\n\n" + yanit)` hesaplar ve sonucu dört listeye ayırır: `dogru`, `uyusmayan`, `eksik`, `kullanilmayan`.
3. **`rapor_olustur`:** yalnız doğrulanmış bulguları puana göre azalan sırayla alır. Diğerlerini `kanit-yok`, `kanit-eksik` ya da `kanit-uyusmuyor` nedeniyle ayrı bölüme koyar. Ayrıca seviye sayılarını ve en yüksek bulguyu verir.
4. **Gerçek deney:** dört gerçek HTTP isteği (E1–E4) ve dört bulguluk taslak.
   - F3, rapora eklenmemiş E9'a dayanıyor.
   - F4, yanıtı sonradan "429" diye düzeltilmiş E1'e dayanıyor.

### KUSURLU başlangıç kodları

Üç kusurlu başlangıç kodu var; kusurlar kodda yorumla söylenmez.

- **K1:** PR kapsama göre ayarlanmıyor; `round(x,1)` kullanılıyor; 9 ve üstü "Yüksek" sayılıyor; vektör doğrulanmıyor.
- **K2:** yalnız yanıt özetleniyor; büyük/küçük harf farkı yok sayılıyor; eksik ve kullanılmayan kanıtlar raporlanmıyor.
- **K3:** uyuşmayan kanıtlı bulgu rapora alınıyor, sıra artan, seviye ölçeği yanlış.

### Anlatım öğeleri

- Bölümler: tablo, NOT, bulgu anatomisi, CVSS'nin iki tuzağı, kanıt bütünlüğü.
- Purple yollarına uygun karşılıklar: "raporu kim yanıltır", Blue karşılığı ve savunmanın neden kırıldığı.
- Tahmin bloğu: Roundup ile `round` farkı ve sıra.
- Hata vitrini: aynı labın dört iddiası.
- Sınır cümlesi.

## Gerçek final (son kabul koşusu)

- **Lab:** yerel `127.0.0.1` HTTP + geçici SQLite. Dört isteğin durumları 200, 200, 401, 500. `cleanup: true`.
- **Kanıt durumu:** `dogru` E2, E3, E4; `uyusmayan` E1; `eksik` E9; `kullanilmayan` boş.
- **Rapor:**
  - Ana bölümde F1 (8.2 Yüksek, `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`) ve F2 (5.3 Orta).
  - Doğrulanmamış bölümünde F3 (`kanit-eksik`) ve F4 (`kanit-uyusmuyor`).
- **Ek doğrulama:** gerçek koşuda ayrıca 5 ek vektör referansla karşılaştırıldı.

## Kendi kontrollerim (`.ai-venv/Scripts/python.exe -X utf8`)

- **`tools/validate.py pu20`:** TEMİZ, 9 kontrol (1 tahmin, 4 solution, 4 starter).
- **`tahmin.py`:** 1 tahmin, 0 şüpheli.
- **`kirp_gercek.py` + `mutasyon.py --en-cok 1000`:** 21 + 14 + 19 + 54 = 108 mutant, 0 geçen.
  - Son görev, adı "Gerçek deney" olmadan önce mutasyona dahildi.
  - İlk turda 1 mutant (iki görevde) geçti: Görev 1'deki "Düşük ≥ 0.1" sınırı. CVSS 0 ile 1.6 arasında puan üretemediği için bu mutant eşdeğerdi. Sınır `> 0` yazıldı; 0.1 sınırını Görev 3 sınıyor.
- **Kopya sondası 7/7 reddedildi:**
  - Denenenler: modül takma adı, `from` import, importlib, `__import__`, inspect + exec, `*` import, doğru çözüm + eval.
  - `kod_koruma` izinli importları `json`/`math`/`hashlib`/`re` ile sınırlar; `from` import'ta yalnız `pathlib.Path` ve `purple_rapor_lab.calistir` serbesttir. Ayrıca dinamik kodu ve `_` ile başlayan öznitelikleri reddeder.

## Denetçiye not

- Purple dersleri `ai_ders_takip` tracker'ında değil. Durum, pano ve bu raporla izleniyor; `DENETIM.md`'deki Aşama 2 tablosu güncellenmedi.
- Ders CVSS 3.1 kullanıyor, çünkü formülü açık ve tek sayfada doğrulanabilir. CVSS 4.0 anlatımda ve Sınır cümlesinde "kapsam dışı" diye geçiyor.
