# Pafta · Denetim Bulguları (2026-10-20 gece)

Denetlenen sürüm: `99885a4`, 10 yol, 227 ders. Bu dosya bir bulgu listesidir: her madde hangi dersin hangi adımında ne olduğunu ve nasıl düzeltileceğini söyler. `:N` adım numarasıdır (0'dan başlar, `tools/validate.py` çıktısındakiyle aynı).

## Ne denetlendi, ne çıktı

| Kontrol | Yöntem | Sonuç |
|---|---|---|
| Görevler çalışıyor mu | `tools/validate.py` | 2206 kontrol temiz |
| Tahmin açıklamaları doğru mu | Her tahmin kodu çalıştırıldı; çıktının her satırı açıklamada geçiyor mu | 284 tahminin hepsi uyuşuyor |
| "Beklenen çıktı" blokları doğru mu | Örnek çözüm çalıştırılıp blokla karşılaştırıldı | 78 bloğun hepsi doğru |
| Testler yanlış cevabı yakalıyor mu | **Mutasyon testi:** örnek çözüm küçük hatalarla bozuldu (`>`→`>=`, artan↔azalan, AND→OR, LIMIT+1, LEFT JOIN→JOIN...); bozuk çözüm farklı sonuç verip testi geçiyor mu | SQL, KQL, SPL, Bash, PowerShell, JS: **0 zayıf test**. Python, PHP, C: 20 görevde sınır değeri test edilmiyor (bkz. 1.2; ikisi P70–P73 ek denetiminden) |
| Önce anlat, sonra yazdır | Görev çözümündeki her komut ve fonksiyon, haritada daha önce bir anlatımda geçmiş mi | PowerShell, KQL, SQL temiz; birkaç küçük istisna (bkz. 3.3, 3.4) |
| Yapı | Rütbeler, sahipsiz dosyalar, adım dağılımı, ipuçları | Sahipsiz ya da eksik dosya yok; her görevin ipucu ve çözümü var |
| Gerçek sisteme sadakat | Splunk ve Kusto taklidinin gerçek davranıştan ayrıldığı yerler | Bir yüksek (1.1), iki düşük bulgu (3.1, 3.2) |

## Durum tablosu (son denetim: 22:55, `00bec2a`)

Her düzeltme yazarın raporuna değil, denetçinin kendi betikleriyle yeniden koşturulmasına göre kapandı sayıldı.

| Bulgu | Durum | Kanıt |
|---|---|---|
| 1.1 sp04 sıralama tuzağı | **kapandı** (`8702ea3`) | ikinci TUZAK kutusu; görev `sort acilis \| dedup sunucu_id` ile sıradan bağımsız |
| 1.2 sınır değeri test edilmeyen 20 görev | **20/20 kapandı** (`8702ea3` + ek testler) | yeniden mutasyon: c08:3, p70:5, p73:5 ve diğerleri artık bozuk hâli reddediyor |
| 1.2a p71:4 «Motor»: `lt` | **kapandı** | `lt` sınır testi (`10` ve `9`) eklendi |
| 1.2b ph11:2 «Kaydet»: öncelik denetimi | **kapandı** | geçersiz öncelik (`"acil"`) testi eklendi |
| 1.3 YARA eşik örnekleri (7 görev) | **kapandı** (`00bec2a`) | 7 görevde 0 geçen bozuk hâl; commit yalnızca YARA dosyalarına dokunuyor |
| 2.1 ders numaraları harita sırasıyla uyuşmuyor | **kapandı** (`dcd8375`) | 10 yol, 94 ders harita sırasına göre yeniden numaralandı |
| 2.2 PowerShell Başpehlivan modülü | **kapandı** | 6. rütbe (`ps19`, `ps20`, `ps21`): keşif ve sağlayıcılar, CIM/modüller/Invoke-Command, Security & Sysmon olay kimlikleri |
| 2.3 Python PCPP1 | **kapandı** (`8be71c9`) | |
| 2.4 SPL bilgi nesneleri | **kapandı** (`1f5c8e8`) | `sp19` bilgi nesneleri ve CIM; tezgahta makro, olay türü, etiket, takma ad, hesaplanan alan |
| 2.5 tezgahta pickle | **kapandı** (`4b8d158`) | tezgahta kullanıcı sınıfı pickle'lanıyor; python/php/c doğrulaması temiz |
| Sigma/YARA tezgah & pedagoji eksikleri | **kapandı** (`2fed4c2`) | 38 YARA görevine `stdin` örnekleri, 18 YARA dersine `[!DERİN]`/`[!TUZAK]`/`[!GÜVENLİK]` kutuları ve `#!` notları, Sigma starter girintisi, `anlat` adımı örnek girdisi ve 10 dil playground kaydı |

## 1 · Yüksek öncelik

### 1.1 SPL sp04, gerçek Splunk'ta ters sonuç veren bir şey öğretiyor

[sp04-sort-top.md](tracks/spl/lessons/sp04-sort-top.md) satır 20–22 `head N`'i "ilk N olay", `dedup`'u "her değer için yalnızca ilk olayı tutar" diye anlatıyor. "Her sunucunun ilk bileti" görevi (sp04:4) de `dedup sunucu_id` ile **en eski** bileti bekliyor.

Gerçek Splunk olayları **en yeniden eskiye** getirir. Aynı arama orada her sunucunun **en yeni** biletini verir; `head 3` de en yeni üç olayı. Bu fark [sp16-hizli-dogru.md](tracks/spl/lessons/sp16-hizli-dogru.md) satır 37'de doğru anlatılıyor, ama 12 ders sonra. O zamana kadar öğrenci yanlış bir model kurmuş oluyor.

**Düzeltme:** sp04'ün anlatımına bir `[!TUZAK]` kutusu ekle: gerçek Splunk en yeniden eskiye getirir, tezgah eskiden yeniye okur. Görevi sıradan bağımsız yap: "her sunucunun en eski bileti" iste ve çözümde `sort acilis` ile sırayı açıkça kur (`sort acilis | dedup sunucu_id`).

### 1.2 Sınır değerleri test edilmiyor (20 görev)

Aşağıdaki görevlerde örnek çözümdeki karşılaştırma bir adım kaydırıldığında (`>` yerine `>=` gibi) test yine geçiyor. Yani tam sınırdaki bir hatayı (off-by-one) yapan öğrenci de ONAYLANDI mührü alıyor. En çarpıcısı, **sınır denetimini öğreten derslerin testleri tam sınırı denemiyor.**

| Görev | Geçen bozuk hâl | Eklenecek test |
|---|---|---|
| c/c08:3 «Sınır denetimli okuyucular» | `ofset + 2 > len(b)` → `>=` | tamponun **son** iki baytı okunabilmeli: `ofset = len(b) - 2` |
| c/c08:5 «Onaltılık döküm satırı» | `0x20 <= x` → `0x20 < x` | boşluk (0x20) nokta değil boşluk olarak basılmalı |
| c/c13:4 «Kayıtları çıkar» | `> boyut` → `>=` ve `boyut < BASLIK.size` → `<=` | kayıt tablosu dosyanın tam sonunda biten dosya kabul edilmeli; yalnızca başlıktan oluşan dosya da |
| php/ph04:3 «Durum uç noktası» | `cpu >= 80` → `> 80` | `cpu = 80` "yoğun" olmalı |
| php/ph05:4 «Kopyalayan ve paylaşan closure» | `cpu > esik` → `>=` | `cpu = esik` eşiği aşmış sayılmamalı |
| php/ph08:5 «Ya hep ya hiç» | `kalan < 0` → `<= 0` | bakiyenin **tamamını** aktarmak başarılı olmalı |
| php/ph11:3, ph11:4 «Kaydet», «Uçtan uca» | `len(baslik) > 80` → `>= 80` | tam 80 karakterlik başlık kabul, 81 ret |
| python/p31:6 «Kaba kuvvet dedektörü» | `< pencere` → `<=` | denemeler tam pencere süresi kadar aralıklıysa |
| python/p34:6 «Aykırı değer dedektörü» | `> k * sapma` → `>=` | tam `k * sapma` uzaklıktaki değer (düşük önem) |
| python/p35:4 «Banka hesabı» | `miktar > bakiye` → `>=` ve `miktar <= 0` → `< 0` | bakiyenin tamamını çekmek başarılı; 0 yatırmak hata |
| python/p38:5 «Sürüm karşılaştırma» | `__lt__`'de `<` → `<=` | aynı sürüm için `v < v` **False** olmalı |
| python/p39:5 «Termostat» | `> hedef + 0.5`, `< hedef - 0.5`, `5 <= deger <= 30` | tam ±0.5 sapma; tam 5 ve 30 derece kabul |
| python/p39:6 «Hesaplanan boyut» | `bayt < 1024` → `<=` | tam 1024 bayt, KB olarak gösterilmeli |
| python/p40:5 «Önem derecesi» | `puan >= 9` → `> 9` ve `0 <= puan` → `0 < puan` | puan 9 ve puan 0 |
| python/p51:6 «Uzunluk önekli mesajlar» | `while len(tampon) < n` → `<=` | tam `n` bayt geldiğinde fazladan okumaya çalışmamalı |
| python/p67:1, p67:2, p67:4 «Kural motoru» | `gt`/`lt` → `>=`/`<=` | eşit değerde `gt` ve `lt` **False** olmalı (gt ile gte farkı dersin konusu) |
| python/p68:2 «İmzalı kayıt» | `sort_keys=True` silinse de geçiyor | anahtarları farklı sırayla eklenmiş iki eş sözlük **aynı** imzayı vermeli |
| python/p69:1 «Jetonlayıcı» | `i + 1 < len(metin)` → `i < len(metin)` | sonunda tek bir `.` olan girdi (`"3."`) |
| python/p70:5 «Kendi mini linter'ın» *(ek denetim)* | `len(satir) > 79` → `>= 79` | tam 79 karakterlik satır E501 **vermemeli**, 80 karakterlik vermeli (PEP 8'in sınırı tam olarak bu) |
| python/p73:5 «Doğrulanmış port» *(ek denetim)* | `0 <= n` → `0 < n` | `Port(0)` ve `Port(65535)` geçerli, `Port(65536)` `ValueError` |

Zararsız çıkanlar (sonucu değiştirmiyor, işlem gerekmez): p20:6, p46:5, p55:5, p55:6, p64:5.

### 1.3 YARA örnek kümelerinde eşik örneği yok (7 görev) *(Sigma/YARA denetimi)*

yr12:4, yr15:3, yr16:3, yr17:3, yr17:4, yr18:3, yr18:4. Koşuldaki `<=` / `>=` bir adım kaydırıldığında (`<`, `>`) bütün örnek dosyalarda sonuç **birebir aynı** kalıyor. Sebep: hiçbir örnek tam eşikte değil (tam N bayt, tam N eşleşme, tam eşik değerinde entropi). Test, sınırın hangi tarafta olduğunu ayırt edemiyor. En dikkat çekeni yr18: konusu regresyon testi olan projenin kendi kümesinde sınır örneği yok.

**Düzeltme:** her görevin örnek kümesine eşiğin tam üstünde ve tam altında birer örnek ekle; bozuk hâlin artık geçmediğini doğrula.

## 2 · Orta öncelik

### 2.1 Ders numaraları haritadaki sırayla uyuşmuyor

Haritada SP08'den sonra SP07, SP13'ten sonra SP11, PS10'dan sonra PS14 geliyor. Aynı durum KQL, SQL, Regex, JS ve PHP'de de var. Öğrenci ders kodlarını sıra numarası sanır.

| Yol | Haritadaki sıra |
|---|---|
| SPL | sp01–sp06, **sp08, sp07**, sp09, sp10, **sp12, sp13, sp11**, sp14… |
| KQL | kq01–kq07, **kq09, kq10, kq11, kq08**, kq12… |
| SQL | sq01–sq05, **sq11**, sq06, sq07, **sq12, sq13**, sq08, **sq14**, sq09, sq15–sq17, **sq10** |
| Regex | rx01–rx06, **rx12**, rx07–rx09, **rx13, rx11**, rx14, rx15, **rx10**, rx16… |
| JavaScript | js01–js03, **js10, js06, js07, js04, js08, js05**, js09, js11, js12 |
| PHP | ph01–ph03, **ph06, ph05**, ph07, **ph04**, ph08… |
| PowerShell | ps01–ps10, **ps14–ps18, ps11–ps13** |
| Python *(ek denetim)* | p01–p29, **p72**, p30–p41, **p73**, p42–p47, **p70**, p48, p49, **p71**, p50… |

**Şimdi düzeltmek bedava:** ilerleme ders kimliğiyle saklanıyor ve `progress.json` henüz yok. Öğrenci başladıktan sonra yeniden numaralamak ilerlemesini siler. Kimlikleri ve dosya adlarını harita sırasına göre yeniden numaralandır (derslerin içindeki "SP11'de gördün" gibi atıfları da güncelle).

### 2.2 PowerShell'de Başpehlivan rütbesi boş

PowerShell 5 rütbede kaldı: en üst rütbe olan Başpehlivan'ın modülü yok. AZ-040'tan eksik konular bu modülün doğal içeriği: `Get-Help` ve `Get-Command` ile keşif, sağlayıcılar (`Env:`, `Variable:`, kayıt defteri), `Get-CimInstance`, işler (`Start-Job`, `Receive-Job`), modüller (`.psm1`, `Import-Module`), uzaktan yönetimi okumak (`Invoke-Command`). Bunların hepsi nötr yönetim konuları.

### 2.3 Python'un PCPP1 eksikleri · KAPANDI

`8be71c9` ile P70–P73 eklendi (kod standartları, pickle ve shelve, XML ve INI, yerleşik türleri genişletmek). Ek denetim: 40 kontrol temiz, 4 tahminin hepsi doğru. İçerik Python 3.11 ile tutarlı (pickle varsayılan protokol 4, en yüksek 5; `defusedxml` uyarısı Python belgeleriyle aynı). Kalan iki sınır testi 1.2'ye eklendi. tkinter bilerek dışarıda.

### 2.5 Tezgahta sınıflar pickle'lanamıyor: düzenekte birkaç satırlık düzeltme *(ek denetim)*

P71 bu yüzden sınıf pickle'lama örneğini çalıştırılmayan örnek yaptı, görevde de `copy.deepcopy` ile dolaylı sınadı. Sebep motor değil düzenek: [py_harness.py](sandbox/py_harness.py) `exec_user` kullanıcı kodunu düz bir sözlükte çalıştırıyor, `sys.modules["__main__"]` ise düzeneğin kendisi. pickle sınıfı `__main__.Hesap` adıyla aradığında bulamıyor.

**Düzeltme:** ad alanını gerçek bir modül yap ve çalışırken `sys.modules["__main__"]` yerine koy:

```python
mod = types.ModuleType("__main__")
mod.__dict__.update({"__builtins__": builtins, "__file__": "kod.py"})
ns = mod.__dict__
eski = sys.modules["__main__"]
sys.modules["__main__"] = mod
try:
    exec(compile(code, FNAME, "exec"), ns)
finally:
    sys.modules["__main__"] = eski
```

Ayrı bir betikle denendi: bugünkü yolda `PicklingError: attribute lookup Hesap on __main__ failed`, düzeltmeyle aynı kod çalışıyor. Sonra P71'in `norun` örneği çalıştırılır yapılabilir ve görev pickle'ı doğrudan sınayabilir. **Dikkat:** `sandbox/py_harness.py` şu an Sigma/YARA üzerinde çalışan oturumda değişiklik halinde; bu düzeltme o iş commit edildikten sonra yapılmalı. Ardından bütün Python yolu yeniden doğrulanmalı (Röntgen ve testler de `exec_user` kullanıyor).

### 2.4 SPL'de bilgi nesneleri yok

Splunk Power User sınavının **%60'ı** arayüzde kurulan bilgi nesneleri: alan takma adları, hesaplanan alanlar, etiketler, olay türleri, makrolar, iş akışı eylemleri, veri modelleri ve CIM. Tezgahta çalışmazlar, ama bir kavram dersi kurulabilir. Görevlerde "bu olay türünün / makronun açılmış hâlini yaz", "alanları CIM adlarına `rename` ile eşle" gibi aramalar yazdırılabilir.

## 3 · Düşük öncelik

1. **SPL serbest metin:** Pafta alt metin eşler, Splunk ise bütün terim eşler: `dolu` araması Splunk'ta "doluluğu"nu bulmaz. [sp01-arama.md](tracks/spl/lessons/sp01-arama.md) satır 29'daki tablo "herhangi bir alanda geçiyorsa" diyor. Hiçbir görev bu farka dayanmıyor; anlatıma bir not yeter.
2. **KQL tarih gösterimi:** Pafta `2026-10-19 08:00`, gerçek Kusto `2026-10-19T08:00:00Z` gösterir. KQL derslerinde buna hiç değinilmiyor; kq07'ye bir not.
3. **JS okuma:** `startsWith` (js09:4) ve `match` (js12:2) hiçbir anlatımda geçmeden görev çözümünde kullanılıyor; görev metni de söylemiyor.
4. **SPL:** `isnull` ve `isnotnull` (sp07:1, sp10:5, sp18:4) anlatımda geçmeden görevde; görev metninde adı söyleniyor. sp02'nin fonksiyon tablosuna eklenebilir.
5. **Proje derslerinde tahmin yok:** p66–p69, bs26–bs27, ps10, ps13, kq08, sp07, sq10. Bilinçli bir tercihse sorun değil; değilse her projeye "bu ara sonuç ne çıkar?" tahmini eklenebilir.
6. **SPL sayı gösterimi:** tam sayı çıkan ortalamaları Pafta `69.0`, Splunk `69` gösterir. Bugün hiçbir tahmini etkilemiyor, yeni derslerde dikkat.
7. **Kapsamda kalan küçük boşluklar:** Bash'te başlangıç dosyaları (`.bashrc`, `.bash_profile`), `alias`, `sha256sum`, `nice`; SQL'de `CREATE VIEW` ve veri sözlüğü (`sqlite_master`, `PRAGMA table_info`); KQL'de `render` (kavram olarak).

## Sigma ve YARA denetimi (`ed6e89d`)

| Kontrol | Sonuç |
|---|---|
| Bütün yollar (gerileme dahil; düzenek değişti) | 267 ders, **2466 kontrol temiz** |
| Tahmin açıklamaları | Sigma ve YARA'nın 36 tahmininin hepsi gerçek çıktıyla uyuşuyor |
| Mutasyon testi (koşulda and/or, 1 of/all of, değiştirici silme, sınır kaydırma) | **Sigma: 36 görevde 0 zayıf test.** YARA: 38 görevin 7'sinde eşik ayırt edilmiyor (1.3) |
| Yapı | İkisinde de 6 rütbe dolu, ders numaraları sıralı, **her derste tahmin var** (projeler dahil). Bu konuda en düzenli iki yol. |
| Motorlar | Sigma resmi pySigma ayrıştırıcısıyla, YARA gerçek libyara ile çalışıyor; KQL/SPL taklitlerinden daha güvenilir. Bağımlılık yoksa ikisi de kurulum komutunu gösteren anlaşılır bir hata veriyor. |
| Bağımlılıklar | `.deps/` (17 MB) git'e girmiyor; README kurulumu anlatıyor. Temiz bir kopyada iki yol kurulum yapılana kadar çalışmaz. Bilinçli ve belgelenmiş bir seçim. |
| Uygulama | 12 yol sekmesi açılıyor, hata kartı yok |

Not: içerik betiklerle denetlendi; Sigma/YARA ders metinleri bu oturumda tek tek okunmadı (bu konuşmada konu daha önce otomatik güvenlik denetimine takılmıştı).

## Hedef kapsam belgesine yorum

Yazan tarafın TryHackMe yollarına göre çıkardığı kapsam belgesine (Codex çıktısı `pafta-hedef-kapsami.md`) büyük ölçüde katılıyorum. Elastic/Kibana KQL ve EQL, Wireshark görüntü filtreleri, Java ve C# okuma, CMD gerçek boşluklar. İki ekleme:

1. **Ad karışıklığı:** Pafta'daki "KQL" Microsoft'un Kusto dilidir. TryHackMe SOC Level 1'deki Kibana "KQL"si bambaşka bir dildir. Elastic yolu eklenmeden önce bile yol adını "KQL (Kusto)" yapmak, sekmede de bunu göstermek yanlış öğrenmeyi önler.
2. **Windows güvenlik olay kimlikleri:** SOC yollarında Security günlüğü (oturum açma, süreç oluşturma gibi olaylar) ve Sysmon olay kimlikleri temeldir. PowerShell yolu bilerek yalnızca System/Application günlüklerini kullanıyor. SOC hedefi için bu, okuma düzeyinde bir köprü dersiyle kapatılabilir.

## Diğer oturuma verilecek kısa talimat

> Pafta kökündeki DENETIM.md'yi oku; en üstteki durum tablosu açık maddeleri gösteriyor. Sigma ve YARA denetimden iyi geçti. Yeni yol eklemeden önce sırayla: (1) 1.1 sp04 sıralama tuzağı. (2) 1.2'deki 20 görev ve 1.3'teki 7 YARA görevi: sınırdaki testi ya da örneği ekle, bozuk hâlin artık geçmediğini doğrula. (3) 2.1 yeniden numaralandırma; progress.json henüz yok, şimdi yapmak ilerleme kaybettirmez. (4) 2.5 tezgahta pickle düzeltmesi ve ardından bütün Python yolunu doğrula. (5) 2.2 PowerShell Başpehlivan ve 2.4 SPL bilgi nesneleri. Sonra kapsam belgesindeki yeni yollara geç; "KQL (Kusto)" adlandırmasını Elastic yolundan önce yap.
