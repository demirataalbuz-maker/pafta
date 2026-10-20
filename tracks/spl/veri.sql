-- SPL yolunun ek verisi: KQL yolunun günlük tabloları (tracks/kql/veri.sql) yüklendikten sonra çalışır.
-- Splunk'ta her olayın bir _time alanı (epoch saniyesi) vardır; aynı anı bu tablolara da ekler.
ALTER TABLE istekler ADD COLUMN _time INTEGER;
UPDATE istekler SET _time = CAST(strftime('%s', zaman) AS INTEGER);
ALTER TABLE gunluk ADD COLUMN _time INTEGER;
UPDATE gunluk SET _time = CAST(strftime('%s', zaman) AS INTEGER);
ALTER TABLE dagitimlar ADD COLUMN _time INTEGER;
UPDATE dagitimlar SET _time = CAST(strftime('%s', zaman) AS INTEGER);
