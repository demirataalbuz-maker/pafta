# Yeni ders pu24 (plan-klasik-1, Keşif: ffuf, nuclei, tespit): yazar kontrolleri tamam, denetime hazır

- **Yazar:** claude-yazar.
- **Atama:** ortak pano 04.11.2026 18:13.
- **Kararlar:**
  - Purple yapısı seçenek A.
  - Araç indirmeleri kullanıcı onaylı ("Hepsini onayla", 04.11).
- **Puan** verilmedi; bağımsız denetim claude-opus'tadır.
- **Görsel sınama** yapılmadı; kabul CLI üzerinden `tools/validate.py` ile yapıldı.

## Eklenen / değişen dosyalar

- `tracks/purple/lessons/pu24-kesif-ffuf-nuclei-tespit.md` (sha256 1128d85fff60985c…)
- `sandbox/purple_kesif_lab.py` (2419e50d81558d7d…):
  - Kendi `127.0.0.1` "Pafta Market" sunucusu: yumuşak 404 döner, X-Forwarded-For'u kaydeder.
  - `.deps` altındaki ffuf 2.3.0 ve nuclei 3.11.1'i yalnız bu sunucuya koşturur.
    - nuclei `-duc` ile ve yalnız öğrenci şablonlarıyla koşar; genel şablon deposu yoktur.
  - Kayıt vekili, referanslar, `kod_koruma` ve `calistir`.
- `tracks/purple/fixtures/pu24_kesif/`: `ornekler.json` (71fb8076…), `kelimeler.txt` (25 kelime) ve `README.md`; sentetik.
- `outputs/yeni-pu24/pu24-1793828138681021900.json`: son kabul kanıtı.
- `tracks/purple/track.json`: mevcut "Keşif ve İlk Erişim" modülüne pu22'den sonra yalnız `pu24` eklendi; panoda `uyari` yazıldı.
- `engine/` ve `web/` değişmedi. Commit/push yok.

## İçerik

### Görevler

1. **`ffuf_ayikla`:** 404'ü ve taban imzasını (`status`, `words`, `lines`) eler. Uzunluk bilerek imzaya katılmaz, çünkü yumuşak 404 sayfası istenen yolu kendine yazar.
2. **`sablon_kur`:** Sözlük olarak bir nuclei şablonu üretir. `matchers-condition: and` kullanır; durum 200, bütün kelimeler ve isteğe bağlı negatif eşleştirici içerir. Kimlik, yol ve önem doğrulanır.
3. **`tarama_tespit`:** Güvenilir vekilden gelen XFF'nin en sağdaki öğesini istemci sayar. "Bulunamadı" istekleri için iki ucu dahil kayan pencere uygular; farklı yol sayısını ve User-Agent'ları raporlar.
4. **Gerçek deney:** Akış şöyledir:
   - meşru kullanıcı gezintisi;
   - kalibrasyon isteği;
   - ffuf koşusu;
   - nuclei koşusu: öğrencinin 3 şablonu ve karşılaştırma için negatif eşleştiricisiz bir "saf" şablon;
   - erişim kaydında tespit.

### KUSURLU başlangıç kodları

- **K1:** Yalnız 404'ü eliyor.
- **K2:** Eşleştiriciler `or` ile birleşiyor, durum kodu ve negatif eşleştirici yok.
- **K3:** XFF'ye körü körüne güveniyor, toplam sayıya bakıyor, pencere yok.

## Gerçek final (son kabul koşusu)

- **ffuf:** `-mc all` ile 25 yanıt aldı. Ayıklama sonrası 5 gerçek yol kaldı: `/.git/HEAD`, `/admin` (302), `/api/surum`, `/urunler`, `/yedek`.
- **nuclei:** Öğrenci şablonları `/api/surum` ve `/.git/HEAD`'de eşleşti; `/yonetim`'de eşleşmedi. "Saf" şablon `/yonetim`'de **yanlış pozitif** verdi.
- **Alarm:** Yalnız `10.66.0.9` için çıktı: en çok 21–22 "bulunamadı", 21 farklı yol, 5 farklı User-Agent. Liste ffuf'un adını, kalibrasyon isteğinin adını ve nuclei'nin rastgele seçtiği tarayıcı adlarını içeriyor.
- **Vekile güvenilmezse:** Alarm `127.0.0.1` için çaldı.
- **Diğer:** Dış istek 0, `cleanup: true`, `kabul: true`.

## Kendi kontrollerim (`.ai-venv/Scripts/python.exe -X utf8`)

- **`tools/validate.py pu24`:** TEMİZ, 9 kontrol.
  - İlk koşuda bir gizli test beklentim yanlıştı: tabanla eşleşmeyen 200 yanıtının da tutulması gerekiyordu. Test düzeltildi; çözüm değişmedi.
- **`tahmin.py`:** 1 tahmin, 0 şüpheli.
- **Mekanik mutasyon:** 31 mutant, 0 geçen.
  - İlk turda 2 mutant geçti. İkisi de görünür örnek koddaki gösterim sabitleriydi (`indent=1`, eşik `3`); sabitler fixture'a taşındı.
  - Referanstaki iki eşdeğer `or→and` kaynağı sadeleştirildi.
- **Elle anlamsal mutant:** 25 mutant, 0 geçen.
  - İlk turda 3 mutant geçti:
    - XFF'nin sol ucu: testte sol ucun sahte olduğu kayıtlar eklendi.
    - Boş ya da boşluk XFF: test eklendi.
    - `t[0]` → `min(...)`: eşdeğer, listeden çıkarıldı.
- **Kopya sondası:** 7/7 reddedildi.

## Denetçiye not

- nmap bu derste yok; pu18 ağ katmanını zaten kapsıyor. Plan maddesi klasik-1 burada uygulama katmanında tamamlanıyor.
- Süreler makine yüküne göre değişti: ffuf 0,2–1,6 sn, nuclei 0,3–2,9 sn. Ders yalnız aralık veriyor.
- `-ot` ve `-or` ile nuclei yanıtları kanıta girmez; kanıtta yalnız şablon kimliği ve adres var.
