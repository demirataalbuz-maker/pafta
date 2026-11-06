# Yeni ders pu22 (plan-klasik-2, Web sömürüsü: XSS, SSTI, XXE): yazar kontrolleri tamam, denetime hazır

- **Yazar:** claude-yazar.
- **Atama:** ortak pano 04.11.2026 18:13.
- **Kararlar:** Purple yapısı seçenek A (kullanıcı, 04.11). Juice Shop yerine kurulumsuz kendi yerel uygulamamız kullanıldı (plan, Dalga A).
- **Puan** verilmedi; bağımsız denetim claude-opus'tadır.
- **Görsel sınama** yapılmadı; kabul CLI üzerinden `tools/validate.py` ile yapıldı.
- **Kurulum ve indirme** yok; yalnız standart kütüphane kullanıldı (`http.server`, `string`, `xml.sax`, `xml.parsers.expat`).

## Eklenen / değişen dosyalar

- `tracks/purple/lessons/pu22-yerel-web-xss-ssti-xxe.md` (sha256 c01e70b394004575…)
- `sandbox/purple_web_lab.py` (e090b21f52a5e295…):
  - Kendi `127.0.0.1` sunucusu; üç açık/korumalı uç çifti, korumalı uçlar öğrencinin işlevlerini kullanır.
  - Referanslar, `kod_koruma`, `calistir`.
- `tracks/purple/fixtures/pu22_web/README.md` ve `ornekler.json` (b66bb3ed59ed51d2…); sentetik.
- `outputs/yeni-pu22/pu22-1793810381144406800.json`: son kabul kanıtı.
- `tracks/purple/track.json`: mevcut "Keşif ve İlk Erişim" modülüne (plan M2) pu19'dan sonra yalnız `pu22` eklendi. Eski dersler taşınmadı ve değişmedi; panoda `uyari` yazıldı.
- `engine/`, `web/` ve diğer lab modülleri değişmedi. Commit/push yok.

## Kaynak doğrulaması (yerelde ölçüldü)

- **Python 3.13.14, expat 2.8.1** ile ölçülen davranış:
  - `xml.sax` dış genel varlıkları varsayılan olarak açmıyor.
  - Özellik açılınca yerel dosyayı okuyor.
  - `ElementTree` tanımsız varlıkta hata veriyor.

  Python belgelerindeki "XML vulnerabilities" bölümüyle tutarlı.
- **`str.format`:** öznitelik ve indeks erişimi "Format String Syntax" belgesine göre çalışıyor. Ders bunu kod çalıştıran bir SSTI değil, "biçim dizisi enjeksiyonu" diye adlandırıyor; kod çalıştırma iddiası yok.
- **OWASP XSS ve XXE Prevention Cheat Sheet:** genel düzeltme ilkeleri için anıldı.

## İçerik

### Görevler

1. **`guvenli_html`:** beş karakteri kaçışlar; `&` önce.
2. **`sablon_dogrula`:** `string.Formatter().parse` ile çözer. Yalnız izinli, düz alan adlarına izin verir; dönüşüm ve biçim belirtecini reddeder; `{{` ile `}}` düz metin sayılır.
3. **`dtd_var_mi`:** expat'ın `StartDoctypeDeclHandler` olayıyla DOCTYPE'ı (iç ya da dış) bulur. UTF-16'yı ayrıştırıcı çözer; yorum ya da CDATA içindeki yazı bildirim sayılmaz.
4. **Gerçek deney:** 13 gerçek istek (her açık sınıfı için meşru ve saldırı, açık ve korumalı uç), artı UTF-16 DTD.

### KUSURLU başlangıç kodları

Üç kusurlu başlangıç kodu var; kusurlar kodda yorumla söylenmez.

- **K1:** `&` en sonda kaçışlanıyor (çift kaçış); tırnaklar kaçışlanmıyor; tür denetimi yok.
- **K2:** alanlar düzenli ifadeyle bulunuyor; `{{ad}}` alan sanılıyor, `{u.ayar[...]}` yalnız `u` olarak görülüyor.
- **K3:** baytlarda `<!ENTITY` aranıyor; dış DTD, UTF-16 ve yorum yanlış değerlendiriliyor.

### Anlatım öğeleri

- Tablo ve NOT.
- Kök neden: veri ile kodun karışması.
- "Saldırgan ne dener" ve "savunma neden kırılır" bölümleri.
- Blue karşılığı: denetim kaydı ve log kuralının yanlış alarmı.
- Tahmin bloğu: kaçış sırası ve `format` ile öznitelik erişimi.
- Hata vitrini ve Sınır cümlesi.

## Gerçek final (son kabul koşusu)

- **XSS:**
  - Açık uç işaret etiketini ham döndürdü.
  - Korumalı uç kaçışladı.
  - Meşru "Ayşe & Ali <3" araması doğru gösterildi.
- **Şablon:**
  - Açık uç gizli ayarı sızdırdı.
  - Korumalı uç 400 verdi.
  - "Merhaba {ad}!" iki uçta da "Merhaba Deniz!" oldu.
- **XXE:**
  - Açık uç geçici gizli dosyayı okudu.
  - Korumalı uç UTF-8 ve UTF-16 DTD'lerine 400 verdi.
  - Meşru sipariş iki uçta da okundu.
- **Sızıntı:** denetim kaydında gizli değer yalnız `/vulnerable/selam` ve `/vulnerable/xml` yanıtlarında sızdı. Hiçbir `/secure/` uç sızdırmadı.
- **Sonuç:** kabul `true`, `cleanup: true`.

## Kendi kontrollerim (`.ai-venv/Scripts/python.exe -X utf8`)

- **`tools/validate.py pu22`:** TEMİZ, 9 kontrol (1 tahmin, 4 solution, 4 starter).
  - İlk iki denemede çözüm geçmedi; ikisi de düzeltildi:
    - (a) `kod_koruma`, expat işleyici atamasını reddediyordu. İzin yalnız yerel bir değişkenin `…Handler` özniteliğine verildi.
    - (b) SAX'ın ilk açılışı `urllib`/`ssl` yüklediği için bir istek 3 sn'yi aştı. Sunucu açılırken ayrıştırıcı bir kez ısıtılıyor; istemci zaman aşımı 15 sn yapıldı.
- **`tahmin.py`:** 1 tahmin, 0 şüpheli.
- **Mekanik mutasyon** (`kirp_gercek` + `mutasyon --en-cok 1000`): 4 mutant, 0 geçen.
  - Görev 1 ve 3'te araç hiç mutant bulamadı, çünkü kod karşılaştırma ya da sayı içermiyor (replace zinciri, ayrıştırıcı çağrısı).
  - Bu boşluk için **elle anlamsal mutant** sınaması yapıldı (`pu22_elle_mutant.py`): çözüm kaynağı değiştirilip dersin kendi sinama işlevleriyle denendi. 18 mutant, 0 geçen. Denenenler:
    - her replace adımını silmek;
    - sırayı değiştirmek;
    - `&#39;` kullanmak;
    - tür denetimini kaldırmak;
    - `bicim`/`donusum`/izin şartını kaldırmak;
    - sırasız dönüş;
    - DOCTYPE işleyicisini silmek;
    - `Parse(..., False)`;
    - bozuk XML'de False dönmek;
    - `bytes()` zorlaması.
  - İlk turda "EntityDeclHandler'ı sil" mutantı geçti. Varlık bildirimi ancak DOCTYPE içinde olabildiği için eşdeğerdi; o işleyici çözümden, referanstan ve görev metninden kaldırıldı.
  - Ayrıca her görevin testinde 3 anlamlı yanlış çözüm reddediliyor.
- **Kopya sondası 7/7 reddedildi.**

## Denetçiye not

- Ders Juice Shop kullanmıyor. Bilinçli ve kurulumsuz bir seçim; plan dosyasında yazıyor.
- Purple dersleri `ai_ders_takip`'te değil; durum pano ve bu raporla izleniyor.
