# Pafta · Denetim

Son denetim: 2026-10-21, `ac5e308`. 12 yol, 271 ders. Bütün ders kimlikleri **yeni numaralardır** (`dcd8375` ile harita sırasına göre yeniden numaralandı); eski raporlardaki kimlikler için [tools/numara_eslemesi.json](tools/numara_eslemesi.json). Bu dosyanın eski, ayrıntılı sürümleri git geçmişinde: `git log -p DENETIM.md`.

Bir madde yazarın raporuyla değil, denetçinin kendi betikleri yeniden koşturulunca kapanmış sayılır.

## Ölçümler

| Kontrol | Yöntem | Sonuç |
|---|---|---|
| Görevler çalışıyor mu | `tools/validate.py` | 271 ders, **2518 kontrol temiz** |
| Tahmin açıklamaları | Her tahmin kodu çalıştırıldı; çıktının her satırı açıklamada geçiyor mu | 328 tahminin hepsi uyuşuyor (Sigma/YARA dahil) |
| "Beklenen çıktı" blokları | Örnek çözüm çalıştırılıp blokla karşılaştırıldı | 78 bloğun hepsi doğru (4 bilinen yanlış alarm: `...` ile kısaltılmış ya da fonksiyonun dönüş değeri) |
| Testler yanlış cevabı yakalıyor mu | **Mutasyon testi:** her örnek çözüm küçük hatalarla bozuldu (sınır kaydırma, artan↔azalan, AND↔OR, LIMIT+1, değiştirici silme...) | **696 görevde 0 zayıf test.** 5 işaretin hepsi sonucu değiştirmeyen zararsız mutasyon: p20:6, p48:5, p59:5, p59:6, p68:5 |
| Ders sırası ve rütbeler | Kimlikler harita sırasıyla uyuşuyor mu, 6 rütbe dolu mu | **12 yolun hepsi sıralı ve 6 rütbeli** |
| Dersler arası atıflar | "SP13'te", "(P05)" gibi her atıf var olan bir derse, doğru konuya gidiyor mu | **234 atıf, 0 kırık**; yeniden numaralandırma atıfları doğru çevirmiş (eski metinle karşılaştırıldı). Bir eski, yanlış adresli atıf var (A3). |
| Uygulama | Önizlemede SP17 ve çift ters tırnaklı kod | doğru görünüyor |

Sigma ve YARA ders metinleri tek tek okunmadı, yalnızca betiklerle denetlendi.

## Açık bulgular

| # | Yer | Bulgu | Düzeltme | Sahibi |
|---|---|---|---|---|
| A3 | python/p17:1 | "(hash rastgeleleştirme, P52)" atfı yanlış adrese gidiyor: P52 (Özet Fonksiyonları ve HMAC) bu konuyu anlatmıyor. Atıf yeniden numaralandırmadan önce de böyleydi (eski P49). Hash'lenebilirliği anlatan ders P19. | atfı P19 yap ya da kaldır | Yazar 1 |
| A4 | regex/rx19:0 | "RX15'daki gibi": Türkçe ek yanlış, "RX15'teki" olmalı (on beş) | ek düzeltmesi | Yazar 1 |
| A5 | sandbox/spl.py, SP17 | Ders doğru söylüyor: Splunk'ta hesaplanan alanlar aynı anda değerlendirilir, biri ötekini kullanamaz. Motor ise sırayla uyguluyor: `iki = cpu*2` ve `dort = iki*2` tanımlanınca Pafta `dort = 288` veriyor, Splunk'ta `dort` boş kalır. | başka bir hesaplanan alana dayanan tanımı boş bırak ya da açık hatayla reddet | Yazar 1 |
| A6-ek | powershell/ps20 | Arka plan işleri yalnızca bir kez adıyla geçiyor (`Start-Job -ScriptBlock { ... }`); `Wait-Job`, `Receive-Job`, `Remove-Job` hiç yok. AZ-040'ın iş yaşam döngüsü anlatılmıyor. (İkinci denetçinin bulgusu, doğrulandı.) | `Start-Job` → `Wait-Job` → `Receive-Job` → `Remove-Job` örneği ve bir görev | Yazar 1 |
| A9 | PowerShell · Active Directory | Kullanıcının ilk dil listesinde "AD" vardı, hiç yazılmadı (`Get-ADUser`, `Get-ADGroupMember`, DN/OU yapısı, LDAP filtreleri yok). Tezgahta etki alanı olmadığı için ancak dışa aktarılmış veriyle ya da okuma düzeyinde kurulabilir. Not: aynı rapordaki "Başpehlivan boş", "Security günlüğü yok", "Sysmon yok" bilgileri eskiydi; üçü de `f6241cf` ile PS19–PS21'de var. | AZ-040'ın AD yönetimi çerçevesinde bir köprü ders | düşük öncelik; **kullanıcı kararı** |
| A7 | proje dersleri | Tahmin adımı yok: p70–p73, bs26, bs27, ps10, ps18, kq11, sp08, sq17. Sigma ve YARA'nın projelerinde var. | her projeye bir ara sonuç tahmini | ertelendi |

## Kapanan bulgular

| Bulgu | Commit | Denetçinin kanıtı |
|---|---|---|
| sp04: `dedup`/`head` gerçek Splunk'ta ters sonuç veriyordu | `8702ea3` | TUZAK kutusu; görev `sort acilis \| dedup sunucu_id` ile sıradan bağımsız |
| 20 görevde sınır değeri test edilmiyordu | `8702ea3`, `f6241cf` | 696 görevlik mutasyonda geçen bozuk hâl yok |
| p71:4 «Motor»: `lt` test edilmiyordu (A1) | `f6241cf` | `<` → `<=` artık yakalanıyor |
| ph11:3 «Kaydet»: listede olmayan öncelik test edilmiyordu (A2; ilk denetimde denetçinin atladığı madde) | `f6241cf` | `and` → `or` artık yakalanıyor |
| YARA'da 7 görevin örnek kümesinde eşik örneği yoktu | `00bec2a` (Codex) | 7 görevde 0 geçen bozuk hâl |
| Ders numaraları harita sırasıyla uyuşmuyordu | `dcd8375` | 12 yol sıralı; 234 atıf, 0 kırık |
| PowerShell'de Başpehlivan rütbesi yoktu (A6) | `f6241cf` | PS19 keşif ve sağlayıcılar, PS20 CIM, modüller ve `Invoke-Command`, PS21 Security ve Sysmon olay kimlikleri; AZ-040'tan eksik saydığım konuların hepsi (yalnızca `Receive-Job` yok) |
| KQL ile Kibana KQL karışıklığı (A8) | `f6241cf` | yol adı "KQL (Kusto)"; KQ01'de iki dilin farkını anlatan TUZAK kutusu |
| Python PCPP1 eksikleri | `8be71c9` | kod standartları, pickle/shelve, XML/INI, yerleşik türler (yeni numaralar: P50, P53, P30, P43) |
| SPL bilgi nesneleri | `1f5c8e8` | **SP17**: makrolar, olay türleri, etiketler, takma adlar ve hesaplanan alanlar tezgahta çalışıyor; Splunk'ın arama zamanı sırasına uygun (bkz. A5) |
| Tezgahta sınıflar pickle'lanamıyordu | `4b8d158` | tezgahta kullanıcı sınıfı pickle'lanıyor |
| Sigma/YARA tezgah ve anlatım eklemeleri | `2fed4c2` (Codex) | doğrulama ve tahmin kontrolleri temiz |
| Küçük notlar (serbest metin terimi, Kusto tarih gösterimi, `startsWith`/`match`, `isnull`) | `ae18f5e` | |
| PowerShell yolunun açıklaması olmayan konuları vaat ediyordu | `99885a4` | |

## Ajanlar arası kurallar

Pafta'da üç yapay zekâ çalışıyor: Yazar 1 (Claude, Sigma/YARA dışındaki yollar), Yazar 2 (ChatGPT/Codex, Sigma, YARA ve TryHackMe kapsam belgesi) ve Denetçi (Claude, bu dosya). Birbirlerine mesaj gönderemezler; kullanıcı aktarır.

- Ortak dosyalar (`sandbox/py_harness.py`, `engine/*.py`, `web/*.js`, `README.md`, `tracks/sql/ornek.sql`, `tools/validate.py`) aynı anda tek yazar tarafından düzenlenir. Düzenlemeden önce `git status`'a bak, bitince hemen commit et.
- `git add -A` ya da `git commit -a` yok: yalnızca kendi dosyalarını ekle.
- Yazarlar bu dosyada bir maddeyi kapatabilir; denetçi bir sonraki denetimde ölçerek onaylar.
