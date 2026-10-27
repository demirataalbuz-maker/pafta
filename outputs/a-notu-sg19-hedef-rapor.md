# 45 · SG19 aynı kural Splunk, Defender (Kusto) ve Elastic (EQL) hedeflerinde

27 Ekim 2026 · Claude. [a-notu-sg19-cli-rapor.md](a-notu-sg19-cli-rapor.md) teslimine ek.

Açık kalan yüksek öncelikli eksik: **yalnız Splunk; Elastic ve Kusto backend'i yok.** Kullanıcı `pysigma-backend-elasticsearch==2.1.1` ve `pysigma-backend-kusto==1.0.1` paketlerini `.deps`'e kendisi kurdu (`--no-deps`, pySigma 1.5.1 korundu).

## Eklenen

- **Ders bölümü:** hedef/pipeline tablosu, bu sürümde ölçüldü. `kusto -p microsoft_xdr` → `DeviceProcessEvents`; `-p sentinel_asim` → `imProcessCreate`; pipeline'sız Kusto tablosuz çıktı üretir; `eql -p ecs_windows` `.caseless` alt alanına dayanır; `esql` + `ecs_windows` sigma-cli tarafından reddedilir. Ürünler arası harf duyarlılığı farkı.
- **Görev 4:** öğrenci iki `sigma convert` satırı yazar. `motor: sigma-hedef` ([sandbox/sigma_hedef_lab.py](../sandbox/sigma_hedef_lab.py)) her çıktıyı gerçek motorda koşar: Kusto Emulator'da `DeviceProcessEvents`, Elasticsearch 9.5.5 `_eql` API'sinde ECS belgeleri. İki ürün de aynı iki cihazı bulmalı.
- `elastic_lab.properties`: normalizer'lı keyword alt alanları (`fields`), yalnız `type/normalizer/ignore_above`.
- `requirements-detection.txt`: sigma-cli ve backend/pipeline sürümleri eklendi (önce dosyada yoktu).

## Kabul

- `tools/test_sigma_hedefler.py`: **8 davranış bozan komut reddedildi, 0 geçen** (pipeline'sız Kusto/EQL, ASIM tablosu, Sysmon alanları, tek hedef, desteklenmeyen hedefler).
- `tools/validate.py sg19`: Git Bash ve PowerShell temiz. `tools/test_elastic_lab.py --eql-predictions` değişiklikten sonra temiz.
- Kanıt: [a-notu-sg19-hedef-kabul.json](a-notu-sg19-hedef-kabul.json).

## Açık kalan

Defender ve Sentinel servisleri yok; tablolar ders verisidir. ASIM ayrıştırıcısı (`imProcessCreate`) laboratuvarda tanımlı değil.

## Öz değerlendirme

**94/100 (A)**: test 24, kapsam 24, derinlik 22, gerçeklik 15, yol 9. Bağımsız denetim değildir.
