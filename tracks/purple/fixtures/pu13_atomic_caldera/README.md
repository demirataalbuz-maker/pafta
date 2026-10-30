# PU13 Atomic / Caldera sözleşme fixture'ı

Bu klasördeki bütün kayıtlar ders için elle üretilmiş sentetik örneklerdir. Atomic Red Team veya Caldera kurulumu, çalıştırılması, ajan bağlantısı, komut yürütme, ağ erişimi ya da gerçek telemetri toplama iddiası yoktur.

- `atomic_test.yaml`: Atomic'in `atomic_tests`, `dependencies`, `input_arguments`, `executor` ve `cleanup_command` alanlarını gösterir.
- `caldera_ability.yaml`: Caldera'nın `platforms → executor → command/cleanup` ve ATT&CK eşlemesini gösterir. `requirements` bir **listedir**; `requirements[0]` tek anahtarlı `{plugins.stockpile.app.requirements.basic: [...]}` mapping'idir. Modülün liste değeri doğrudan `source`, `edge` ve `target` alanlı ilişki öğelerini taşır; arada `relationship_match` katmanı yoktur. Modül anahtarı veya liste kapsayıcısı atlanmaz. `#{output_file}` bir değişken yer tutucusudur.
- `source_contract.json`: YAML'lardan elle çıkarılan küçük doğrulama dizinidir; gerçek araç çıktısı değildir.
- `plan.json`: Çalıştırılacak komutlar yerine incelenecek adım ve beklenen gözlem sözleşmesini taşır.
- `telemetry.jsonl`: Gerçek olay günlüğü değildir; her satır sentetik bir olaydır.
- `rules.json`: Gerçek SIEM kuralları değil, sentetik eşleştirme ölçütleridir.

Komut metinleri yalnız veri olarak okunur. `sandbox/emulation_lab.py` ağ ve alt süreç kullanmaz; dosyaları dersin geçici çalışma klasörüne kopyalar.
