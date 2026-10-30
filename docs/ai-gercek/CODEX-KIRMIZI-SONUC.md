# Codex atanmış kırmızı dersler — sonuç

29 Ekim2026. Kullanıcının atadığı21ders gerçek deney ve uygulayıcı kabulüyle tamamlandı. Tracker durumu denetime-hazır;bağımsızdenetim yapıldığı iddia edilmez. Bütün AI müfredatı bitmiş değildir.

Kapsam:08,09,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,34. Kullanıcının başka ajana çıkardığı12,31,32,33,30 değiştirilmedi. Savunma/başkaajan işleri alınmadı.

## Kabul

| Ders | CLI kabul senaryosu | Rapor |
|---|---:|---|
| ai-saldiri-08 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-08-20261029/RAPOR.md |
| ai-saldiri-09 | 10/10 beklenen sonuç | ../../outputs/codex-ai-saldiri-09-20261029/RAPOR.md |
| ai-saldiri-10 | 10/10 beklenen sonuç | ../../outputs/codex-ai-saldiri-10-20261029/RAPOR.md |
| ai-saldiri-11 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-11-20261029/RAPOR.md |
| ai-saldiri-13 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-13-20261029/RAPOR.md |
| ai-saldiri-14 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-14-20261029/RAPOR.md |
| ai-saldiri-15 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-15-20261029/RAPOR.md |
| ai-saldiri-16 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-16-20261029/RAPOR.md |
| ai-saldiri-17 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-17-20261029/RAPOR.md |
| ai-saldiri-18 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-18-20261029/RAPOR.md |
| ai-saldiri-19 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-19-20261029/RAPOR.md |
| ai-saldiri-20 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-20-20261029/RAPOR.md |
| ai-saldiri-21 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-21-20261029/RAPOR.md |
| ai-saldiri-22 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-22-20261029/RAPOR.md |
| ai-saldiri-23 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-23-20261029/RAPOR.md |
| ai-saldiri-24 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-24-20261029/RAPOR.md |
| ai-saldiri-25 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-25-20261029/RAPOR.md |
| ai-saldiri-26 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-26-20261029/RAPOR.md |
| ai-saldiri-28 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-28-20261029/RAPOR.md |
| ai-saldiri-29 | 10/10 beklenen sonuç | ../../outputs/codex-ai-saldiri-29-20261029/RAPOR.md |
| ai-saldiri-34 | 9/9 beklenen sonuç | ../../outputs/codex-ai-saldiri-34-20261029/RAPOR.md |

Toplam192/192 kabul senaryosu beklenen sonuçta:referanslar geçer,boş/sabit/anlamlıyanlış çözümler ve eksikbağımlılık koşulları reddedilir. Bu sayı192başarılı model saldırısı anlamına gelmez.

Ders ekranı Kontrol/Çalıştır ile herders ayrı doğrulandı;gerçek kanıtlar outputs/codex-kirmizi-seri-20261029/ui-data/ai-kanit altında. CLI referans kanıtı her raporun reference.json dosyasında belirtilir. Sonuçların kökeni ayrıdır:sentetik girdi,doğrudankontrol,gerçek model/protokol/disk etkisi. Öğrenci dosyaları ayrı kalıcıkopyadır;farklı süreç/cwdkalıcılık sınamaları fixturealtyapıkontrolü diye etiketlidir.

Tam AI-saldırı regresyonu:46ders429kontrol TEMİZ. Gerçekkomutçıktısı outputs/codex-kirmizi-seri-20261029/validate-full-son.log. Toplu CLI sonuçları aynı klasörde toplu-kabul-ozeti.json.

## Değişenler ve yeniden çalıştırma

Her dersin sonuna anlat/gerçekgörev eklendi;eski adımlar korunur. Dersözelmodüller sandbox/ai_gercek_ai_saldiri_NN.py,görünürveriler web/data/ai-saldiri-NN*.txt.13PDF,20argv ve29TLS için ek worker dosyaları vardır. Herdersin RAPOR.md dosyası özel kapsam/komut/sonuç ve sınırları açıklar. Yeniden kabul:python -X utf8 outputs/codex-ai-saldiri-NN-20261029/kabul.py. Regresyon:python -X utf8 tools/validate.py --yol ai-saldiri.

Bu devam çalışmasında yeni paket/model kurulmadı;mevcut Ollama,Qwen,embedding/vision,PDF ve cryptography ortamları kullanıldı. Commit/push yok. AnaPafta/ortakgiriş birleştirmesi yapılmadı. Yalnız kendi başlatılan kaynaklar kapatılır;öğrenci verileri/kurulumlar silinmez.

## Bilinen sınırlar

-19ve25başta olmak üzere bazı koşularda aralıklı OllamaHTTP500 vardı;FAILkanıtları korundu. Sonraki başarılıkoşu köknedençözüldü iddiası değildir.
-Ortak Markdownrenderer dosya linklerini tıklanabilir yapmıyor;hamdosyaURLsi veRun içindeki kalıcıyol/içerik erişimi var. Yerleşikdosyaeditörü yok.
-34örneğinde rolmarkerkaçışı canary açıklanmasını önlemedi;bu güvenlikgarantisi diye sunulmaz. GerçekcontexttokenIDleri sunucu tarafından verilmedi.
-24nativeaktarım açıkça izinlipozitifrelaydir;jailbreakbaşarısı değildir.29kontrollütamzincir sentetikaraçadayı+gerçekTLS/disk etkisidir,modelbaşarısı diye sayılmaz. Diğer özel sınırlar dersraporlarında.
-İkinciWindowscihaz kabulü ve bağımsızdenetim yapılmadı.
