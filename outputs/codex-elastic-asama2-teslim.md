# Elastic 41–44 · Codex teslimi

Kullanıcının dört maddenin tamamını verme ve resmi imajları indirme onayıyla
Elastic yolu **19 → 27 ders**, **6 rütbe**, **55 görev / 27 tahmin** oldu.
EL01–EL19'un temel motoru korunur; EL20–EL27 gerçek Elasticsearch/Kibana
**9.5.5 Basic** kullanır. Native bölümde yerel motora sessiz fallback yoktur.

| Madde | Teslim | Commit |
|---|---|---|
| 41 · Gerçek telemetri, ECS, ingest | EL20–EL21; gerçek zararsız alt süreçlerden NDJSON, gerçek pipeline/simulate/bulk, strict mapping, sayı ve tarih sınırları | `bd44e96` |
| 42 · Gerçek EQL backend | EL22–EL23; endsWith~/between~, sequence/by/maxspan/until, baştaki eksik olay; eski altı EQL tahmininin gerçek ürün karşılaştırması | `e3dab5e` |
| 43 · Security kuralı | EL24–EL25; gerçek query/EQL/threshold create/preview, gerçek exception listesi; ayrıca gerçek Task Manager ve operational alarm kabulü, öğrencinin kendi kodunu canlı çalıştırma aracı | `c923b11` |
| 44 · ES\|QL | EL26–EL27; gerçek _query API, WHERE/EVAL/STATS/SORT/KEEP, null/eksik ölçüm ve çok değerli gruplar | `ebfe74c` |

Ortak altyapı/arayüz: `3d929a1`, `196c504`; kurulum hata çıktısını kimlik
bilgilerinden arındırma: `8ad335e`; pano: `c56962c`; başlama: `ec1bf8a`.
Diğer ajanın önceden staged Python dosyaları ilk altyapı commit'ine karışınca
dosya içeriklerine dokunmadan ayrıldı ve onun staging'i geri bırakıldı;
yukarıdaki geçerli altyapı commit'i yalnız Elastic dosyalarını içerir.

## Gerçeğe sadakat ve sınırlar

- Elasticsearch/Kibana resmi registry imajları sürüm ve SHA-256 digest ile
  sabit; çalışan sürüm ve Basic lisans API'den doğrulandı.
  [Ortam kanıtı](codex-elastic-environment.json).
- Elasticsearch 127.0.0.1:19200, Kibana 127.0.0.1:15601. Auth/API keys açık,
  trial yok; parola ve anahtarlar Git dışındaki `.deps/elastic-lab` içinde.
  Her konteyner 2 GiB sınırda; otomatik açılış yok. Bu localhost HTTP labı
  TLS üretim dağıtımı değildir; EL19'un TLS yönergesiyle karıştırılmaz.
- EL20 dosyası gerçek üst süreç gözlemidir: gerçek pid, bitiş zamanı ve exit
  code. Sysmon/EVTX/Agent olayı iddiası yok. `captures/manifest.json` kaynak,
  üretici ve SHA-256'yı kaydeder. Diğer yeni ders verileri sentetik sınır tanıklarıdır.
- Ingest hem `_simulate` hem `_bulk` üzerinden geçer. Simülasyon başarılı
  olsa da strict mapping indekslemeyi reddedebilir; hata görünür kalır.
  Metadata ile indeks yönlendirme, dinamik alan adı, script ve başka pipeline
  çağrısı açıkça reddedilir. Drop/noop ayrı davranış olarak ölçülür.
- EQL sorgusu ve zaman filtresi gerçek `_eql/search` API'sine gider.
  Anahtarlar, sıra, eşit maxspan ucu ve missing event ürün tarafından çözülür.
  Eski altı tahminin eşleşmesi bütün yerel alt kümenin eşdeğerlik ispatı değildir.
- ES|QL yalnız `FROM pafta` adını geçici indekse bağlar; kısa ömürlü okuma
  anahtarı yalnız o indekse yetkilidir. Başka indeks okuma reddi gerçek API'de sınandı.
  Python agregasyon/eşleşme modeli yoktur; sütunlar ve değerler üründen gelir.
- Security görevinde devre dışı gerçek kural kaydı + gerçek preview kullanılır.
  9.5.5'in geçici preview belgeleri operational alarm diye sunulmaz; yalnız
  o preview kimliğiyle okunup temizlenir. Exception list/öğeleri gerçek API nesneleridir.
- Gerçek zamanlayıcı kabulü ayrıca query, EQL sequence ve threshold türlerini
  etkinleştirip gerçek operational alarm indeksini okudu. İkinci pencere de
  beklendi; query ve EQL kaynak olayları tekrar alarm olmadı.
  [Kanıt](codex-elastic-scheduled.json).
- `tools/elastic_rule_live.py` öğrencinin kendi EL24 JSON dosyasını gerçek
  zamanlayıcıyla çalıştırır. Tarihler açıkça yeniden bazlanır, canlı deney
  penceresi now-10m olur; sabit now-2m preview sınır testiyle aynı olduğu
  iddia edilmez. Task 1 örneği gerçek a/b/d operational alarmlarını verdi.
- Normal tamamlanma/hatada yalnız işin geçici nesneleri temizlenir. Zorla
  süreç sonlandırmada finally garanti değildir; kalan nesneler/yerel volume
  için sınır ve kontrol yönergesi yol README'sindedir.

## Doğrulama

- Elastic özel Windows taraması: **27 ders / 170 kontrol, temiz**.
- **16 yeni çözümün tamamı geçti**. Son mutasyon turu **106 deneme**:
  **105 fail, 1 kanıtlı eşdeğer, 0 zayıf test / 0 altyapı hatası**.
  Eşdeğer, BY olmayan STATS'ın zaten döndürdüğü aynı iki sütunu aynı sırayla
  tutan kimlik KEEP projeksiyonunun kaldırılmasıdır; bozuk sorgu sayılmadı.
  [Ayrıntılı mutasyon kaydı](codex-elastic-native-mutations.json).
- Gerçek runtime kabulü **10 test temiz**: sürüm/lisans, altı eski tahmin,
  gerçek zaman filtresi, hata temizliği, scoped key, UTF-8, mapping/simulate
  ayrımı, metadata/işlemci reddi, drop/noop, bilinmeyen context reddi.
  [Günlük](codex-elastic-native-runtime.log).
- Uzun ilk unit/müfredat/API turunda 79 testin birinde zaman aşımı görüldü;
  başarılı sayılmadı. İlgili müfredat/API grubu ve ek native API akışı
  **7 testte temiz yeniden ölçüldü**. Native API denemesinde yanlış test
  adresi de düzeltilip tekrar çalıştırıldı. İlerleme ve tekrar verisi geçici
  PAFTA_DATA içinde tutuldu; kullanıcının ilerleme kaydı değiştirilmedi.
  [İlk tur](codex-elastic-suite-initial.log), [yeniden ölçüm](codex-elastic-suite-recheck.log).
- Node arayüz regresyonları (Elastic/packet/CMD): **21 test temiz**. Yeni
  üç dilin girdisi/editörü, tahmin öncesi gizleme, JSON+tablo görünürlüğü ve
  HTML kaçışı sınandı. Görsel tarayıcı denetimi iddiası yoktur.
- Kaynaklar UTF-8/LF; `git diff --check` temiz.

Git Bash özel taraması ilk yoğun paralel turda EL20:3 içinde API zaman
aşımı verdi; başarılı sayılmadı. Son tekrar **27 ders / 170 kontrol temiz**.
[İlk özel tarama](codex-elastic-track-gitbash.log),
[temiz tekrar](codex-elastic-track-gitbash-recheck.log).

### Tam uygulama · Windows ve Git Bash

İki tarama da tamamlandı. Her biri başlangıçtaki **471 ders / 3931 kontrol**
anlık görüntüsünü çalıştırdı. **İki ortamda da Elastic bulgusu yoktur.**
Uygulama geneli temiz değildir; aşağıdaki bulgular diğer yollardadır.

| Ortam | Geçen kontrol | Bulgu | Günlük |
|---|---:|---:|---|
| Windows | 3925 | 6 | [Windows tam tarama](codex-elastic-full-windows.log) |
| Git Bash | 3921 | 10 | [Git Bash tam tarama](codex-elastic-full-gitbash.log) |

- İki ortamda: `powershell/ps22:6` ACL raporunda satırlar eksik;
  `ps25:3` imza alanları boş; `ps25:4` güven kararı beklenenden farklı.
- Windows'ta ayrıca: `powershell/ps23:5`, `ps24:4`, `ps24:5` zaman aşımı.
- Git Bash'te ayrıca: `powershell/ps19:0` bir örnek, `ps19:5` bir görev,
  `ps20:0` iki örnek, `ps20:1` iki örnek zaman aşımı; `spl/sp22:4` bastırma
  görevinde beklenen yalnız web06 yerine web01/web02/web06 raporu geldi.

Taramalar eşzamanlıydı ve oturum tarih değişimini aşan uzun bir bekleme içerdi.
Bu, zaman aşımlarının veya Splunk bulgusunun nedeninin teşhis edildiği anlamına
gelmez. Diğer yollara düzeltme yapılmadı; günlüklerdeki bulgular gizlenmedi.
Aynı checkout'ta başka ajanlar çalıştığından tarama başlangıcından sonra
eklenen derslerin bu anlık görüntüye dahil olduğu iddia edilmez.

Son temizlikte, zaman aşımı denemelerinden kalmış ve en az 10 dakika yaşındaki
beş kendi geçici indeksim ile bir eski prototip preview belgesi silindi.
Kalan `pafta-elastic-*` indeks sayısı sıfır; pipeline ve geçici Pafta kuralı
da yoktu. Kullanıcının başka indekslerine dokunulmadı.
[Temizlik kanıtı](codex-elastic-cleanup.json).

Pano **denetime-hazir** olarak kaydedildi. 44'ün Excel adı `Elastic: ES`
diye kesik olduğu için aynı maddeye bir durum eşlemesi eklendi; denetçinin
Excel dosyası değiştirilmedi.

## Kurulum ve tekrar ölçüm

`python tools/elastic_lab_setup.py --start` indirme yapmadan servisi başlatır;
`--stop` durdurur. İlk kurulumdaki `--pull` imaj indiren açık eylemdir.
Elastic Agent veya ek Python paketi kurulmadı. Bu görevde yalnız kullanıcının
onayladığı iki resmi ürün imajı indirildi. Ayrıntı: `tracks/elastic/README.md`.

```text
python tools/validate.py --yol elastic
python tools/test_elastic_lab.py
python tools/test_elastic_lab.py --scheduled
python tools/audit_elastic_native.py
python -m unittest tools.test_elastic_curriculum tools.test_elastic_integration
node --test tools/test_elastic_ui.mjs tools/test_packet_ui.mjs tools/test_cmd_ui.mjs
```

DENETIM.md, ASAMA2.md ve denetçinin Excel dosyası değiştirilmedi. Push yok.
41–44 bağımsız denetime sunulur; denetçinin “bitti” kararı yerine geçmez.
