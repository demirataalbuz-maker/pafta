# 45 · SG19 sigma-cli ile gerçek çeviri ve CIM veri modeli

27 Ekim 2026 · Claude.

Bağımsız denetimin iki yüksek öncelikli eksiği vardı: **sigma-cli hiç kullanılmıyor** ve **yalnız Splunk; Elastic ve Kusto backend'i yok.** Bu teslim birincisini kapatır. İkincisi açık: pySigma Elastic/Kusto backend kurulumu otomatik izin denetiminden geçmedi ve atlatılmadı.

## Eklenen

- **Ders bölümü:** `sigma convert` seçenekleri ve bu sürümde ölçülen davranışlar. Pipeline'sız çeviri çıkış kodu 2 verir. `-s` tanımlanmamış yer tutucuyu atlar, ama `|cased` kuralını atlayamaz ve çeviri çıkış kodu 1 ile durur. `splunk_cim` + `data_model` çıktısı `tstats` ile `Endpoint.Processes`'ten okur.
- **Görev 2:** kural klasörünü kurumun pipeline dosyasıyla çevir; yer tutuculu kural atlanır, iki sorgu da gerçek Splunk'ta doğru olayları bulur.
- **Görev 3:** aynı kuralı CIM veri modeline çevir. Etiketsiz kaynak, aynı alan adlarına sahip olsa bile modele girmez (SP23'teki gerçek CIM 8.5.0).
- **Koşucu:** `motor: splunk`, `girdi: komut` ([sandbox/py_harness.py](../sandbox/py_harness.py) `_sgs_komut`). Gerçek sigma-cli (`.deps`) geçici klasörde, hazırlığın `dosya(...)` dosyalarıyla çalışır. Hedef yalnız `splunk`, biçim `default`/`data_model`; dosya yazan seçenekler reddedilir.

## Kabul

- `tools/test_sigma_cli.py`: **12 davranış bozan komut reddedildi, 0 geçen**.
- `tools/validate.py sg19`: Git Bash ve PowerShell temiz.
- Kanıt: [a-notu-sg19-cli-kabul.json](a-notu-sg19-cli-kabul.json).

## Öz değerlendirme

**88/100 (B)**: test 23, kapsam 19, derinlik 22, gerçeklik 15, yol 9. Elastic ve Kusto backend'i olmadan A sayılmaz.
