# EL20 gerçek süreç gözlemi

`process.ndjson` üç zararsız Python alt sürecinin gerçekten beklenmiş
bitiş kaydıdır: `pid` Popen nesnesinden, `rc` işletim sistemi çıkış
kodundan, `at` üst sürecin UTC gözlem saatinden gelir. Tam yol, kullanıcı
ve hostname kaydedilmez; `exe` yalnız dosya adıdır. Bu veri Sysmon/EVTX
veya Elastic Agent olayı değildir. Diğer ileri ders tanıkları sentetiktir.

Yeniden gözlem için (hazır korpus yerine kendi çıktı dosyana):

```text
python tools/capture_elastic_telemetry.py --output kendi-kaydım.ndjson
```

Her satır bağımsız JSON'dur. Ders bu dosyanın satırlarını stdin corpus'una
kopyalar; gerçek pipeline + bulk zincirinden geçirir. Manifest kaynak,
üretici ve SHA-256 özetiyle korpus değişikliğini görünür tutar. Yeni ölçümde
pid ve zamanın değişmesi normaldir; ders testleri bunları ezberlemez.
