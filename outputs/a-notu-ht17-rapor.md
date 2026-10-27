# 24 · Burp Proxy → History → Repeater

27 Ekim 2026 · Codex

HT17'ye gerçek Burp dışa aktarımını okuyan yazma görevi eklendi. Kali WSL'de kurulu Burp Suite Community 2026.8 geçici projesinde, Pafta yerel HTTP laboratuvarına gerçek Proxy üzerinden 200/403/200/401 yanıtları alındı. İlk History isteği GUI'de Repeater'a taşınıp Send ile yeniden gönderildi; gerçek 200 yanıtı Save item ile kaydedildi. History dört kaydı Save items ile kaydedildi. Base64 açık; fixture XML satır sonları LF, ham HTTP baytları korunur. Bu, tarayıcı yakalaması diye sunulmaz: History istemcisi Python http.client'dir.

Yeni görev Base64 baytlarını, XML sırasını/tekrarları ve metadata–ham ilk satır uyumunu ölçer. Dosya boyutunun 65536/65537 sınırı, status 100/599 ve dış komşular, eksik/tekrarlı alan, bozuk Base64, ikili gövde, kayıp CRLF, destek dışı HTTP sürümü, entity/dış kaynak bildirimi ve boş arşiv sınanır. Destek dışı kayıt açık ValueError verir. Gerçek Burp'ün dahili ELEMENT/ATTLIST DTD'si kabul edilir. Eski hedef değiştirme görevine tek başına yanlış tür ve ASCII !/~ sınırları da eklendi; eski çözümler değiştirilmedi.

Doğrulama:

- HT17: 1 ders, 7 kontrol TEMİZ.
- HTTP tam yol Windows: 24 ders, 177 kontrol TEMİZ.
- HTTP tam yol Git Bash: 24 ders, 177 kontrol TEMİZ.
- tools/test_http_burp_export.py: referans geçti, **18 davranış bozan mutant reddedildi, 0 geçen**. Fixture hash'leri doğrulandı.
- Standart betik tüm HT17 görevlerinde 44 mutant üretti: 40 reddedildi, 4 geçti. Bunlar gizlenmedi: ilk görevde ayraç yokluğu zaten zorunlu CRLF sonlandırmasıyla reddedilir; yeni görevde 1 baytlık geçerli items XML'i bulunmadığından boyut alt sınırı 1→2 / <=→< sonucu değiştirmez (iki varyant); request.split maxsplit 1→2 ilk [0] elemanını değiştirmez. Bu dört varyant görev sözleşmesinde eşdeğerdir, test açığı diye yapay assertion eklenmedi.

Sınırlar: arşivi okumak her öğrencinin GUI'yi kullandığını veya XML'i gerçekten Burp'ün yazdığını tek başına kanıtlamaz. Tam HTTP framing ve HTTP/2 desteklenmez, açıkça yazıldı. Gerçek ürün çıktısı fixture provenance.json ile kayda alınır. Yeni indirme yapılmadı.

Öz değerlendirme: test 24/25, kapsam 24/25, derinlik 21/25, gerçeklik 15/15, yol 10/10 = **94/A**. Önceki bağımsız 76 puan korunmalı; bağımsız yeniden denetim yapılmadı. Ortak puanlar.json dosyasında başka ajanın 92 ve 105–108 değişiklikleri bulunduğu için bu teslimde ortak dosya düzenlenmedi. Önerilen panel satırı a-notu-ht17-panel-onerisi.json içinde; panelde güncellendi diye sunulmaz.

Resmî kaynaklar kontrol edildi:
- https://portswigger.net/burp/documentation/desktop/tools/message-editor (Save item XML istek/yanıt ve metadata)
- https://portswigger.net/burp/documentation/desktop/tools/context-menu (Save items)
- https://portswigger.net/burp/documentation/desktop/tools/repeater

GUI işlemleri bilgisayar kullanımı becerisiyle yürütüldü: C:/Users/albuz/.codex/plugins/cache/openai-bundled/computer-use/26.1021.31345/skills/computer-use/SKILL.md
