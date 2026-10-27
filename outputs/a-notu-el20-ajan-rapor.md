# 41 · EL20 gerçek Elastic Agent standalone alımı

27 Ekim 2026 · Claude.

Bağımsız denetimin eksiği: **Elastic Agent yok; ajan tabanlı alım öğretilmiyor.** Kullanıcı ücretsiz indirmeyi onayladı. `docker.elastic.co/elastic-agent/elastic-agent:9.5.5` imajı indirildi ve digest ile sabitlendi (`sha256:4610f3c4…cfb15c`). Koşucu imajı kendiliğinden indirmez.

## Eklenen

- **Ders bölümü (EL20):** standalone politika katmanları (`outputs`, `filestream`, `parsers`, `processors`), ortam değişkeniyle kimlik bilgisi, `logs-<dataset>-<namespace>` veri akışı adı, hazır `logs` şablonunun ECS eşlemesi (`source.ip` → ip), ajanın eklediği alanlar (`agent.type`, `input.type`, `log.file.path`, `log.offset`), bozuk satırın okuma anı zamanı taşıması.
- **Görev:** öğrenci `elastic-agent.yml` yazar. Klasörde güncel `erisim.ndjson`, döndürülmüş `erisim.ndjson.1` ve düz metin `diger.log` var. Doğru politika yalnız güncel dosyayı okur, JSON'u köke ve olay zamanına ayrıştırır, bozuk satırı işaretler, `/saglik` isteklerini ajanda düşürür.
- **Koşucu:** [sandbox/elastic_agent_lab.py](../sandbox/elastic_agent_lab.py), `motor: elastic-agent`. Gerçek ajan konteyneri yalnız `pafta-elastic` ağında. Klasör bağlanmaz, dosyalar `docker cp` ile kopyalanır. 5 dakikalık ve yalnız `logs-pafta.*-*` yazabilen bir API anahtarı kullanılır. Çalıştırmaya özel namespace eki eklenir; konteyner, veri akışı ve anahtar `finally` içinde silinir. Politikada yalnız `filestream`, `ndjson`/`multiline` ve zararsız işlemciler kabul edilir.

## Kabul

- `tools/test_elastic_agent.py`: gerçek ajan + Elasticsearch 9.5.5 ile **13 davranış bozan mutant reddedildi, 0 geçen**: geniş/döndürülmüş glob, `overwrite_keys` ya da `add_error_key` yok, düşürme yok ya da yanlış alanda, `target: json`, yanlış dataset/namespace, izleme açık, parola ya da anahtar dosyada, eski `log` girdisi. Sonda konteyner, veri akışı ve etkin anahtar kalmadığı doğrulandı.
- `tools/validate.py el20`: Git Bash ve PowerShell temiz.
- Kanıt: [a-notu-el20-ajan-kabul.json](a-notu-el20-ajan-kabul.json).

## Açık kalan

Fleet, entegrasyon paketleri ve Kibana varlıkları kapsam dışı. Sysmon/Windows olay kanalı okunmaz; girdi uygulama JSON günlüğüdür.

## Öz değerlendirme

**93/100 (A)**: test 23, kapsam 24, derinlik 22, gerçeklik 15, yol 9. Bağımsız denetim değildir.
