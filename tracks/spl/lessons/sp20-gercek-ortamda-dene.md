---
id: sp20
title: Gerçek Ortamda Dene · Splunk
summary: Aramaları ücretsiz gerçek bir Splunk'a taşımak (Splunk Enterprise denemesi ve Free lisansı, Splunk Cloud denemesi, BOTS veri kümeleri); tezgahın verisini CSV ve arama tablosu olarak yüklemek, makeresults ile küçük veri kurmak; tezgahla Splunk arasındaki farklar (olay sırası, zaman seçici, alan adlarında büyük-küçük harf, saat dilimi) ve iki sonucu karşılaştırmak.
---

::: anlat Ücretsiz gerçek Splunk
Pafta'nın SPL tezgahı bir Splunk değildir: aramalar SQLite'a çevrilip yerel bir veritabanında çalışır. Bu derste aynı aramaları **gerçek ürüne** taşıyacaksın:

| Seçenek | Ne |
|---|---|
| **Splunk Enterprise** denemesi | splunk.com'dan Windows ya da Linux için indirilir, kendi bilgisayarında çalışır. Deneme süresi bitince **Splunk Free** lisansına geçirilebilir: günlük veri sınırı düşüktür, tek kullanıcılıdır, uyarılar ve kullanıcı yönetimi yoktur. Süre ve sınırlar için Splunk'ın güncel lisans sayfasına bak. |
| **Splunk Cloud Platform** denemesi | kurulum gerektirmeyen, tarayıcıda çalışan kısa süreli deneme |
| **BOTS** (Boss of the SOC) | Splunk'ın güvenlik alıştırması veri kümeleri (`github.com/splunk/botsv1`, `botsv2`, `botsv3`); bir Splunk'a uygulama olarak yüklenir ve gerçekçi, büyük bir veride arama pratiği sağlar |

Yerel kurulumdan sonra tarayıcıda `http://127.0.0.1:8000` adresinden **Search & Reporting** uygulamasını aç.

> [!GÜVENLİK]
> İndirdiğin paketin yayımlanmış sağlama toplamını (SHA-512 ya da MD5) denetle. Kurulumda güçlü bir yönetici parolası seç. Laboratuvarı yerel makinede tut: web arayüzünü (8000) ve yönetim bağlantı noktasını (8089) ağa açma. Splunk'a yalnızca örnek ya da anonimleştirilmiş veri yükle.
:::

::: anlat Tezgahın verisini taşımak
Tezgahtaki `sourcetype=istekler` gibi kaynaklar senin Splunk'ında yoktur. Üç yol var:

**1. CSV olarak yüklemek.** Tezgahta `sourcetype=istekler | table zaman istemci yontem yol durum sure_ms sunucu` çalıştırıp sonucu bir CSV dosyasına kaydet. Splunk'ta **Settings → Add Data → Upload** ile dosyayı seç:

- kaynak türü olarak `csv`'yi seç, sonra bu kaynak türünü `istekler` adıyla kaydet
- zaman damgası için `zaman` sütununu ve `%Y-%m-%d %H:%M` biçimini göster
- veriyi ayrı bir dizine (index) koy: ör. `pafta`

Sonra aynı arama `index=pafta sourcetype=istekler ...` diye başlar.

**2. Arama tablosu (lookup) olarak yüklemek.** Zamanı önemsiz küçük tablolar için **Settings → Lookups → Lookup table files** ile `biletler.csv`'yi ekle ve `| inputlookup biletler.csv` ile oku (SP11'deki arama tabloları).

**3. makeresults ile sorgunun içinde kurmak.** Birkaç satırlık bir deneme için yükleme bile gerekmez. Aynı arama tezgahta da Splunk'ta da çalışır:

```spl
| makeresults count=4
| streamstats count as n
| eval sunucu=case(n=1,"web01",n=2,"web01",n=3,"db01",n=4,"db01"), durum=case(n=1,500,n=2,499,n=3,503,n=4,200)
| where durum>=500
| stats count as hata by sunucu
```

`makeresults count=4` dört boş olay üretir, `streamstats count` onlara 1'den 4'e sıra numarası verir, `case` her numaraya bir değer atar.
:::

::: anlat Farklara dikkat
Aynı arama iki yerde farklı sonuç veriyorsa sebep çoğu zaman şunlardan biridir:

| Konu | Tezgah | Gerçek Splunk | Ne yap |
|---|---|---|---|
| olay sırası | eskiden yeniye | **en yeniden eskiye** | `head`, `dedup`, `first` öncesi sırayı `sort` ile kur (SP04) |
| zaman aralığı | tablonun tamamı | **zaman seçicisi** her aramayı sınırlar; geçmiş tarihli veri dar bir aralıkta görünmez | seçicide `All time` ya da aramada `earliest=` ve `latest=` |
| alan adları | tablo sütunları | alan adları büyük-küçük harfe **duyarlıdır** (`Sunucu` ile `sunucu` ayrı alanlar); arama değerleri duyarsızdır | yüklerken sütun adlarını aynı yaz |
| saat dilimi | `_time` UTC'den | yükleme ayarına ve kullanıcının saat dilimine bağlı; `strptime` ve `strftime` kullanıcının saat dilimiyle yorumlar | yüklerken saat dilimini belirt; saatleri karşılaştırırken buna bak |
| bilgi nesneleri | veri tablolarından | **Settings**'te tanımlanır | SP17'deki makro, olay türü ve etiketleri orada kur |
| sayı gösterimi | `69.0` | `69` | biçimi değil değeri karşılaştır |

Karşılaştırırken satırları **küme** olarak karşılaştır; sırayı ancak aramada `sort` varsa karşılaştır. Bir fark bulursan aramayı, veriyi, zaman aralığını ve Splunk sürümünü yan yana kaydet. Tezgah bir Splunk taklididir; ayrıştığı yer bir öğrenme fırsatıdır, Pafta'ya da bir bulgu olarak bildirilebilir.
:::

::: tahmin
Ne yazar?

```spl
| makeresults count=5
| streamstats count as n
| eval sure=case(n=1,120,n=2,300,n=3,300,n=4,80,n=5,2410), sunucu=case(n<=2,"web01",n=3,"db01",true(),"web02")
| where sure>=120
| stats count as adet, sum(sure) as toplam by sunucu
```

???

`db01|1|300`, `web01|2|420` ve `web02|1|2410`. Birinci ve ikinci olay `web01`, üçüncüsü `db01`, geri kalanlar (`true()` kolu) `web02` olur. `where sure>=120` yalnızca 80'lik dördüncü olayı atar; 120 dahildir. `stats ... by sunucu` sonucu sunucu adına göre sıralar. Aynı arama gerçek Splunk'ta da bu üç satırı verir.
:::

::: gorev En son istek
Her sunucunun **en son** isteğini getir: `sunucu`, `_time`, `yol`; sunucuya göre sıralı. Gerçek Splunk olayları en yeniden eskiye, tezgah eskiden yeniye getirir; sonuç ikisinde de aynı olmalı.

```starter
sourcetype=istekler
| dedup sunucu
| table sunucu _time yol
```

```test
import re
eq(sutunlar, ["sunucu", "_time", "yol"], "alanlar: sunucu, _time, yol")
eq([(r[0], r[2]) for r in sonuc], [("web01", "/api/bilet"), ("web02", "/api/bilet"), ("web03", "/api/durum")], "her sunucunun en son isteği")
yeni = ("INSERT INTO istekler (zaman, istemci, yontem, yol, durum, sure_ms, sunucu, _time) VALUES "
        "('2026-10-19 11:59','10.9.9.9','GET','/en-yeni',200,1,'web02', CAST(strftime('%s','2026-10-19 11:59') AS INTEGER));")
eq([(r[0], r[2]) for r in dene(yeni)], [("web01", "/api/bilet"), ("web02", "/en-yeni"), ("web03", "/api/durum")], "daha yeni bir istek gelince o seçilir")
ok(re.search(r"\bsort\s+-\s*_time\b[^|]*\|\s*dedup\b", src), "dedup'tan önce sırayı sort -_time ile kur")
```

```solution
sourcetype=istekler
| sort -_time
| dedup sunucu
| sort sunucu
| table sunucu _time yol
```

```hint
`dedup` ilk gelen olayı tutar. Önce `sort -_time` ile en yeniyi başa al, sonra `dedup sunucu`, en sonda `sort sunucu`.
```
:::

::: gorev Zamanı açık yaz
**19 Ekim 2026 08:00 (dahil) ile 09:00 (hariç)** arasındaki istekleri sunucu başına say: `sunucu`, `count`. Aralığı `where` ile `_time` üzerinden ve `strptime` kullanarak yaz; gerçek Splunk'ta zaman seçicisi `All time` olsa da aynı sonucu vermeli.

```starter
sourcetype=istekler
| stats count by sunucu
```

```test
eq(sutunlar, ["sunucu", "count"], "alanlar: sunucu, count")
eq(sonuc, [("web01", 3), ("web02", 3), ("web03", 1)], "08:00-09:00 arası")
def satir(an, sunucu):
    return (f"('{an}','10.9.9.9','GET','/x',200,1,'{sunucu}', CAST(strftime('%s','{an}') AS INTEGER))")
ekle = ("INSERT INTO istekler (zaman, istemci, yontem, yol, durum, sure_ms, sunucu, _time) VALUES "
        + ", ".join([satir("2026-10-19 08:00", "web09"), satir("2026-10-19 09:00", "web08"), satir("2026-10-19 07:59", "web07")]) + ";")
eq(dene(ekle), [("web01", 3), ("web02", 3), ("web03", 1), ("web09", 1)], "08:00 dahil; 07:59 ve 09:00 hariç")
ok(kullanir("strptime"), "zamanı strptime ile yaz")
```

```solution
sourcetype=istekler
| where _time>=strptime("2026-10-19 08:00", "%Y-%m-%d %H:%M") AND _time<strptime("2026-10-19 09:00", "%Y-%m-%d %H:%M")
| stats count by sunucu
```

```hint
`strptime("2026-10-19 08:00", "%Y-%m-%d %H:%M")` metni epoch saniyesine çevirir. Aralığı yarı açık kur: alt uçta `>=`, üst uçta `<`.
```
:::

::: gorev makeresults ile taşınabilir veri
Aşağıdaki beş olayı `makeresults`, `streamstats` ve `eval` ile kur (alanlar `sunucu` ve `durum`). Sonra her sunucu için bütün olayları (`toplam`) ve durumu **500 ya da üstü** olanları (`hata`) say: `sunucu`, `toplam`, `hata`. Tezgahın kaynaklarını kullanma: arama gerçek Splunk'ta yükleme yapmadan çalışmalı.

| sıra | sunucu | durum |
|---|---|---|
| 1 | web01 | 500 |
| 2 | web01 | 499 |
| 3 | db01 | 503 |
| 4 | db01 | 200 |
| 5 | cache01 | 500 |

```starter
sourcetype=istekler
| where durum>=500
| stats count as hata by sunucu
```

```test
eq(sutunlar, ["sunucu", "toplam", "hata"], "alanlar: sunucu, toplam, hata")
eq(sonuc, [("cache01", 1, 1), ("db01", 2, 1), ("web01", 2, 1)], "beş olay doğru kurulmuş; 500 dahil, 499 hariç")
ok(kullanir("makeresults"), "makeresults kullan")
ok(not kullanir("sourcetype") and not kullanir("inputlookup"), "tezgahın kaynaklarını kullanma")
```

```solution
| makeresults count=5
| streamstats count as n
| eval sunucu=case(n<=2,"web01",n<=4,"db01",true(),"cache01"), durum=case(n=1,500,n=2,499,n=3,503,n=4,200,n=5,500)
| stats count as toplam, count(eval(durum>=500)) as hata by sunucu
```

```hint
`| makeresults count=5 | streamstats count as n` her olaya 1'den 5'e bir numara verir; `eval ... case(n=1, ..., n=2, ...)` ile değerleri ata. İki sayımı tek `stats`'ta yap: `count as toplam, count(eval(durum>=500)) as hata` (SP15).
```
:::
