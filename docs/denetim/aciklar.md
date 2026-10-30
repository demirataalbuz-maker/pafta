# Pafta · Açıklar ve Eksikler (Codex iş listesi)

Son güncelleme: 2026-10-26 · Denetçi: Claude (Yazar 2) · Atanan: Codex (test kusurları + kod).
Kimi şu an yeni dersleri (pu13–pu17) ekliyor; bu listedeki açıklar **Codex'e**.

**Nasıl çalışılır:** Çoğu "yanlış-çözümü yakalayan test ekle" tipinde. Ders **çözümünü ve anlatımını değiştirme** — yalnız test bloğunu güçlendir. Her düzeltmeden sonra doğrula:
`python docs/denetim/araclar/mutasyon.py . <ders_id>` → hedef satırda **"0 geçen"**; `python tools/validate.py --yol <yol>` **TEMİZ** kalmalı.

Önem: 🔴 yüksek · 🟠 orta · 🟡 düşük

---

## A) Temiz test-sıkılaştırma (Codex — yanlış-çözüm/sınır testi ekle)

| # | Madde | Yol | Önem | Açık | Yapılacak |
|---|---|---|---|---|---|
| 1 | md1 | python | 🔴 | P75:11 sürümleri **metin** olarak karşılaştıran çözümü kabul ediyor (testte 0.10.0 gibi sürüm yok) | Sürüm sıralamasını zorlayan vaka ekle (ör. 0.9.0 < 0.10.0) |
| 2 | md1 | python | 🔴 | P75:5 `--no-index` olmadan da geçiyor (çevrimdışılık koşucudan geliyor) | Öğrenci kodunun `--no-index` içermesini zorlayan test |
| 3 | md11 | bash | 🔴 | BS35:5 özet uyuşmazlığı **hiç** sınanmıyor; yanlış/boş özette "tamam" diyen çözüm geçiyor | Yanlış ve boş özet vakası ekle (BUTUNLUK BOZUK beklensin) |
| 4 | md83 | javascript | 🟠 | js13:3 s18 hata-**mesajı açığa çıkarma** dalı yalnız 413 ile test; 6 mutant yaşıyor | expose=false 4xx, tam 400/500 sınırı, &&/|| ayıran girdiler |
| 5 | md13 | powershell | 🟠 | 2xx dalı sınanmıyor | 2xx yanıt vakası ekle |
| 6 | md22 | cmd | 🟠 | CM23 hata yolu (whoami başarısız) hiç sınanmıyor | Başarısız whoami vakası |
| 7 | md29 | http | 🟠 | max_redirects ve 300/399 sınırları sınanmıyor | Sınır + fazla yönlendirme vakaları |
| 8 | md38 | spl | 🟠 | SP21:2 ve SP21:4'te saat değeri +1 testten geçiyor | Saat/zaman değerini pinleyen vaka |
| 9 | md45 | sigma | 🟠 | SG19:2 eşik değeri +1 geçiyor | Eşik sınırını pinleyen vaka |
| 10 | md7 | python | 🟡 | P79'da 2**64 sınır değeri sınanmıyor | 2**64 sınır vakası |
| 11 | md15 | powershell | 🟡 | Kanonik sıranın son iki grubu + stderr temizliği tam sınanmıyor | Eksik grupları + stderr vakası |
| 12 | md16 | powershell | 🟡 | Boş yayıncı satırı sınanmıyor | Boş yayıncı vakası |
| 13 | md62 | ad | 🟡 | AD21:2'de `-band 2` → `-band 3` mutantı geçiyor (bit değeri ayırt ettirmiyor) | Bit değerini ayıran şablon/girdi |
| 14 | md69 | csharp | 🟡 | cs13 girdi-doğrulama guard dalları az test (or→and / 400→401 yaşıyor) | Geçersiz-girdi yolları (islem="", yanlış tip) |
| 15 | md72 | csharp | 🟡 | cs16:4 `ord>0xFFFF` sınırı test edilmemiş | U+FFFF (tek ?) ve U+10000 (iki ?) vakaları |

## A2) Purple / Bitirme / IDS test boşlukları (26.10 oturumunda bulundu)
Not: md93/md95/md101 **Kimi'nin dersleri** — Codex testlerini sıkılaştırabilir ya da Kimi kendi yeni işini bitirince bakar.

| # | Madde | Yol | Önem | Açık | Yapılacak |
|---|---|---|---|---|---|
| 21 | md93 | purple (pu02) | 🟠 | `kanit_yolu` yol-doğrulama guard'ları (@37/40/41) + bütünlük (@59 `size≠ VEYA hash≠`) `or→and` yaşıyor — güvenlik-kritik | Her guard'ı ayrı pinle + "boyut doğru ama hash yanlış" (ve tersi) vakası |
| 22 | md101 | purple (pu12) | 🟠 | pu12:4/5 `and→or`/`or→and` (@9/27/40) + sınır `<→<=` yaşıyor | Mantık ve eşik kararlarını ayıran girdiler |
| 23 | md95 | purple (pu10) | 🟠 | pu10:3/4 sınır `<=→<` + mantık `==→!=` (@49) yaşıyor | Eşik komşusu + eşitlik kararı vakaları |
| 24 | md96 | ids | 🟠 | id01/02/03/05 eşik/pencere sayıları (`1→2`, `60→61`, `5→6`) yaşıyor (10 geçen) | Eşik sınır testleri (altında/üstünde tetiklenme) |
| 25 | md104 | bitirme (bt05/06) | 🟡 | bt05:2 `<=→<`, bt06:3 `or→and`(@4) + `25→26`(@5) yaşıyor | Kabul kapısı eşik/mantığını pinle |
| 26 | md98 | purple (pu06) | 🟡 | pu06:3 geçiş kapısı eşiği (`<=→<`, `25→26`) yaşıyor | Eşik sınırını pinle |

## B) Test değil — ayrı ele alınır (Codex)

| # | Madde | Yol | Önem | Açık | Yapılacak |
|---|---|---|---|---|---|
| 16 | md63 | ad | 🟠 | **Kod hatası:** `sandbox/ad_ldap_client.py:24` wslpath'e yolu tırnaksız geçiriyor; boşluksuz yola kurulursa AD22/AD23 kırılır (Codex'in dosyası) | Yolu tırnakla sar; boşluksuz yolda sına |
| 17 | md42 | elastic | 🟠 | EL13–EL18 yerel EQL tahminlerini **gerçek Elasticsearch** ile karşılaştıran otomatik denetim yok | Opt-in gerçek-ES karşılaştırma betiği |
| 18 | md45 | sigma | 🟠 | SigmaSplunkRunner'ın kendi altyapı testi yok | Koşucu için altyapı testi |
| 19 | md40 | spl | 🟡 | Bir tahmin ~8 çalıştırmada bir farklı çıkıyor (determinizm) | Belirsizlik kaynağını sabitle |
| 20 | md41 | elastic | 🟡 | EL20/EL21 yük altında zaman aşımı kararsızlığı | Timeout/stabilite |

## C) Bayat durum — ✅ Claude (Yazar 2) düzeltti
- **md51, md52** artık **Tam** olarak puanlandı — yr23 (externals/include/namespace) ve yr24 (toplu tarama) var; tahmin uyuşuyor, mutasyon temiz. (puanlar.json güncellendi.)

---

### Notlar
- **Denetim artık tam:** 1-104'ün **103'ü puanlı** (yalnız md92/pu13 "Bekliyor" — Kimi yazıyor). Bu oturumun bulguları (65-104 + 51/52) `puanlar.json`'a işlendi; canlı panel `DENETIM_SAYFASI.html` hepsini gösteriyor.
- "Kısmen" olan diğer maddeler (CDSA/CPTS/CDEP/CAPE etiketli) **kusur değil**, yol-kapsam notu — bunlar Kimi'nin eklediği 4 yeni ders (phishing, Windows adli, Linux privesc, hash biçimleri) ile kapanıyor.
- A2'deki md93/md95/md101 **Kimi'nin dersleri**; test boşlukları. Kimi yeni dersleri bitirince kendi işine de bakabilir, ya da Codex devralır.
