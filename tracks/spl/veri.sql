-- SPL yolunun ek verisi: KQL yolunun günlük tabloları (tracks/kql/veri.sql) yüklendikten sonra çalışır.
-- Splunk'ta her olayın bir _time alanı (epoch saniyesi) vardır; aynı anı bu tablolara da ekler.
ALTER TABLE istekler ADD COLUMN _time INTEGER;
UPDATE istekler SET _time = CAST(strftime('%s', zaman) AS INTEGER);
ALTER TABLE gunluk ADD COLUMN _time INTEGER;
UPDATE gunluk SET _time = CAST(strftime('%s', zaman) AS INTEGER);
ALTER TABLE dagitimlar ADD COLUMN _time INTEGER;
UPDATE dagitimlar SET _time = CAST(strftime('%s', zaman) AS INTEGER);

-- Bilgi nesneleri: gerçek Splunk'ta .conf dosyalarında ya da Ayarlar menüsünde tanımlanır
-- (macros.conf, eventtypes.conf, tags.conf, props.conf). Tezgah aynı tanımları bu tablolardan okur.
-- makrolar: `ad` ya da `ad(a, b)`; argumanlar virgülle ayrılmış adlar, tanımda $ad$ olarak geçer
CREATE TABLE makrolar (ad TEXT, argumanlar TEXT, tanim TEXT);
INSERT INTO makrolar VALUES
 ('web_istekleri', '', 'sourcetype=istekler'),
 ('sunucu_hatalari', '', 'sourcetype=istekler durum>=500'),
 ('hata_kodlari', '', 'durum=500 OR durum=503'),
 ('yavas', 'esik', 'sure_ms>$esik$'),
 ('yuzde', 'pay, payda', 'round(100 * $pay$ / $payda$, 1)'),
 ('sunucu_ozeti', '', 'stats count AS istek, avg(sure_ms) AS ort_sure by sunucu');
-- olay_turleri: eventtype=ad, kayıtlı bir arama (borusuz)
CREATE TABLE olay_turleri (ad TEXT, arama TEXT);
INSERT INTO olay_turleri VALUES
 ('sunucu_hatasi', 'sourcetype=istekler durum>=500'),
 ('istemci_hatasi', 'sourcetype=istekler durum>=400 durum<500'),
 ('yavas_istek', 'sourcetype=istekler sure_ms>1000'),
 ('yazma_istegi', 'sourcetype=istekler (yontem=POST OR yontem=PUT OR yontem=DELETE)'),
 ('uygulama_hatasi', 'sourcetype=gunluk seviye=ERROR');
-- etiketler: alan=deger çiftine (eventtype ve sourcetype da birer alandır) verilen etiket; tag=etiket
CREATE TABLE etiketler (alan TEXT, deger TEXT, etiket TEXT);
INSERT INTO etiketler VALUES
 ('sourcetype', 'istekler', 'web'),
 ('eventtype', 'sunucu_hatasi', 'hata'),
 ('eventtype', 'istemci_hatasi', 'hata'),
 ('eventtype', 'uygulama_hatasi', 'hata'),
 ('eventtype', 'yavas_istek', 'performans'),
 ('yontem', 'POST', 'yazma'),
 ('yontem', 'PUT', 'yazma'),
 ('yontem', 'DELETE', 'yazma');
-- props.conf'un arama zamanı alanları: FIELDALIAS (alan_takma_adlari) ve EVAL (hesaplanan_alanlar).
-- Varsayılan olarak boştur; dersler kendi hazırlık (setup) bloklarında doldurur.
CREATE TABLE alan_takma_adlari (sourcetype TEXT, alan TEXT, takma_ad TEXT);
CREATE TABLE hesaplanan_alanlar (sourcetype TEXT, alan TEXT, ifade TEXT);
