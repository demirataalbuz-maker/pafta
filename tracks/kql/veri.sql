-- KQL yolunun ek verisi: SQL yolunun ornek.sql veritabanının üstüne yüklenir.
-- istekler: bir iç uygulamanın web istek günlüğü (ayrinti sütunu JSON, dinamik alan olarak okunur)
-- dagitimlar: sunuculara yapılan sürüm dağıtımları
CREATE TABLE istekler (zaman TEXT, istemci TEXT, yontem TEXT, yol TEXT, durum INTEGER, sure_ms INTEGER, sunucu TEXT, kullanici TEXT, ayrinti TEXT);
INSERT INTO istekler VALUES
 ('2026-10-19 08:02','10.0.1.15','GET','/api/bilet',200,120,'web01','ayse','{"bolge":"ist","istemci":"tarayici","etiketler":["mobil"]}'),
 ('2026-10-19 08:05','10.0.1.22','GET','/api/bilet/42',200,95,'web02','can','{"bolge":"ank","istemci":"tarayici","etiketler":[]}'),
 ('2026-10-19 08:07','203.0.113.7','GET','/',200,40,'web01',NULL,'{"bolge":"dis","istemci":"tarayici","etiketler":["ilk-ziyaret"]}'),
 ('2026-10-19 08:12','10.0.2.8','POST','/api/bilet',201,310,'web02','mert','{"bolge":"izm","istemci":"uygulama","surum":"2.4.1","etiketler":["mobil","beta"]}'),
 ('2026-10-19 08:15','10.0.1.15','GET','/api/rapor',200,850,'web01','ayse','{"bolge":"ist","istemci":"tarayici","etiketler":[]}'),
 ('2026-10-19 08:31','198.51.100.23','GET','/api/durum',200,15,'web03',NULL,'{"bolge":"dis","istemci":"izleyici","etiketler":["otomatik"]}'),
 ('2026-10-19 08:46','10.0.1.22','PUT','/api/bilet/42',200,180,'web02','can','{"bolge":"ank","istemci":"tarayici","etiketler":[]}'),
 ('2026-10-19 09:01','10.0.3.4','GET','/api/rapor',500,2300,'web01','zeynep','{"bolge":"ist","istemci":"tarayici","etiketler":[]}'),
 ('2026-10-19 09:02','10.0.3.4','GET','/api/rapor',500,2410,'web01','zeynep','{"bolge":"ist","istemci":"tarayici","etiketler":["yeniden-deneme"]}'),
 ('2026-10-19 09:04','10.0.1.15','GET','/api/bilet',200,140,'web02','ayse','{"bolge":"ist","istemci":"tarayici","etiketler":["mobil"]}'),
 ('2026-10-19 09:10','203.0.113.7','GET','/giris',200,60,'web03',NULL,'{"bolge":"dis","istemci":"tarayici","etiketler":[]}'),
 ('2026-10-19 09:12','10.0.2.8','GET','/api/rapor',503,30,'web01','mert','{"bolge":"izm","istemci":"uygulama","surum":"2.4.1","etiketler":["mobil"]}'),
 ('2026-10-19 09:15','10.0.1.22','GET','/api/bilet',200,110,'web02','can','{"bolge":"ank","istemci":"tarayici","etiketler":[]}'),
 ('2026-10-19 09:20','10.0.3.4','GET','/api/rapor',200,1900,'web01','zeynep','{"bolge":"ist","istemci":"tarayici","etiketler":["yeniden-deneme"]}'),
 ('2026-10-19 09:41','198.51.100.23','GET','/api/durum',200,12,'web03',NULL,'{"bolge":"dis","istemci":"izleyici","etiketler":["otomatik"]}'),
 ('2026-10-19 10:03','10.0.1.15','DELETE','/api/bilet/17',404,25,'web02','ayse','{"bolge":"ist","istemci":"tarayici","etiketler":[]}'),
 ('2026-10-19 10:05','10.0.2.8','GET','/api/bilet',200,130,'web01','mert','{"bolge":"izm","istemci":"uygulama","surum":"2.5.0","etiketler":["mobil"]}'),
 ('2026-10-19 10:06','10.0.2.8','GET','/api/rapor',200,700,'web01','mert','{"bolge":"izm","istemci":"uygulama","surum":"2.5.0","etiketler":["mobil"]}'),
 ('2026-10-19 10:30','172.16.5.9','GET','/api/durum',200,18,'web03',NULL,'{"bolge":"ist","istemci":"izleyici","etiketler":["otomatik"]}'),
 ('2026-10-19 10:42','10.0.1.22','GET','/api/rapor',500,2600,'web02','can','{"bolge":"ank","istemci":"tarayici","etiketler":[]}'),
 ('2026-10-19 10:44','10.0.1.22','GET','/api/rapor',200,1200,'web02','can','{"bolge":"ank","istemci":"tarayici","etiketler":["yeniden-deneme"]}'),
 ('2026-10-19 10:50','203.0.113.40','GET','/',200,35,'web03',NULL,'{"bolge":"dis","istemci":"tarayici","etiketler":["ilk-ziyaret"]}'),
 ('2026-10-19 11:05','10.0.1.15','GET','/api/bilet',200,90,'web01','ayse','{"bolge":"ist","istemci":"tarayici","etiketler":["mobil"]}'),
 ('2026-10-19 11:20','192.168.10.5','POST','/api/bilet',201,280,'web02','selin','{"bolge":"ist","istemci":"tarayici","etiketler":[]}'),
 ('2026-10-19 11:31','198.51.100.23','GET','/api/durum',200,14,'web03',NULL,'{"bolge":"dis","istemci":"izleyici","etiketler":["otomatik"]}'),
 ('2026-10-19 11:47','10.0.3.4','GET','/api/bilet',200,100,'web01','zeynep','{"bolge":"ist","istemci":"tarayici","etiketler":[]}');
CREATE TABLE dagitimlar (zaman TEXT, sunucu TEXT, surum TEXT);
INSERT INTO dagitimlar VALUES
 ('2026-10-19 08:55','web01','2.5.0'), ('2026-10-19 10:40','web02','2.5.0'), ('2026-10-19 11:40','web01','2.5.1');
-- gunluk: uygulama ve sistem günlüğü; mesajlar serbest metin (parse ve extract için)
CREATE TABLE gunluk (zaman TEXT, sunucu TEXT, seviye TEXT, mesaj TEXT);
INSERT INTO gunluk VALUES
 ('2026-10-19 08:00','web01','INFO','hizmet başladı surum=2.4.1'),
 ('2026-10-19 08:15','web01','WARN','yavaş sorgu tablo=biletler sure=850ms'),
 ('2026-10-19 08:40','db01','WARN','disk uyarısı bolum=/var doluluk=81%'),
 ('2026-10-19 08:55','web01','INFO','hizmet başladı surum=2.5.0'),
 ('2026-10-19 09:01','web01','ERROR','yavaş sorgu tablo=raporlar sure=2300ms'),
 ('2026-10-19 09:02','web01','ERROR','bağlantı havuzu dolu aktif=50 bekleyen=12'),
 ('2026-10-19 09:12','web01','ERROR','bağlantı havuzu dolu aktif=50 bekleyen=31'),
 ('2026-10-19 09:20','web01','WARN','yavaş sorgu tablo=raporlar sure=1900ms'),
 ('2026-10-19 09:30','db01','WARN','disk uyarısı bolum=/var doluluk=88%'),
 ('2026-10-19 10:05','db01','WARN','disk uyarısı bolum=/data doluluk=93%'),
 ('2026-10-19 10:40','web02','INFO','hizmet başladı surum=2.5.0'),
 ('2026-10-19 10:42','web02','ERROR','yavaş sorgu tablo=raporlar sure=2600ms'),
 ('2026-10-19 10:43','web02','ERROR','bağlantı havuzu dolu aktif=40 bekleyen=5'),
 ('2026-10-19 11:00','yedek01','INFO','yedekleme bitti boyut=12.5GB sure=40dk'),
 ('2026-10-19 11:40','web01','INFO','hizmet başladı surum=2.5.1'),
 ('2026-10-19 11:50','db01','WARN','disk uyarısı bolum=/var doluluk=79%');
