# 42 · EQL işlevleri ve gerçek backend: yerel tahmin ve görevlerin ürünle karşılaştırması

27 Ekim 2026 · Claude · Codex'in `0df3a47` düzeltmesi üzerine.

Bağımsız denetimin tek eksiği ASAMA2'nin istediği **mevcut tahminleri aynı veri/mapping ile gerçek motorda karşılaştıran otomatik denetim** idi. Codex `tools/test_elastic_lab.py --eql-predictions` ile EL13–EL18'in altı EQL tahminini gerçek Elasticsearch 9.5.5'le karşılaştırdı, ama madde yeniden puanlanmadı.

## Eklenen

`test_existing_eql_tasks_against_product`: EL13–EL18'deki 12 EQL görevinin **çözümü ve başlangıcı** aynı corpus/mapping ile hem yerel motorda hem gerçek `_eql` API'sinde koşar; sonuç kimlikleri birebir aynı olmalı. Yerel motor bir sorguyu reddederse gerçek motor da hata vermeli. Sessiz taklit sayılmaz. `--eql-predictions` artık iki sınamayı birlikte koşar.

## Kabul

- `python -X utf8 tools/test_elastic_lab.py --eql-predictions`: **30 karşılaştırma, 30 eşit** (6 tahmin, 12 çözüm, 12 başlangıç). Çıktı: [a-notu-el13-18-eql-karsilastirma.txt](a-notu-el13-18-eql-karsilastirma.txt).
- `docs/denetim/araclar/mutasyon.py . el22 el23`: **15 mutant, 0 geçen.**

## Öz değerlendirme

**94/100 (A)**: test 24, kapsam 24, derinlik 22, gerçeklik 15, yol 9. Bağımsız denetim değildir.
