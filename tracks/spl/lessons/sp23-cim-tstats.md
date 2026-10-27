---
id: sp23
title: Veriyi CIM'e Eşlemek ve tstats · Gerçek Web Veri Modeli
summary: Splunk Common Information Model'in (CIM) resmi eklentisiyle bir web erişim günlüğünü Web veri modeline bağlamak; zincir: props.conf'ta arama zamanı alan takma adları (FIELDALIAS), eventtypes.conf'ta olay türü, tags.conf'ta web etiketi ve modelin `cim_Web_indexes` makrosu; eşlenmemiş alanın boş değil "unknown" görünmesi; tstats ile veri modelinden özet, rename Web.* AS *, summariesonly ve hızlandırılmamış modelde boş sonuç. Görevler Docker'daki gerçek Splunk Enterprise'da, resmi CIM 8.5.0 eklentisiyle çalışır.
kazanim: PU 10.1, PU 10.3, APU 9.1, APU 19.2
---

::: anlat Ortak bir dil
SP17'de CIM'i kavram olarak gördün: farklı ürünlerin farklı adlarla yazdığı aynı bilgiyi ortak alan adlarında buluşturmak. Bir sunucu `istemci=10.0.1.15`, öteki `c-ip=10.0.1.15`, üçüncüsü `clientip=10.0.1.15` yazar; CIM'in **Web** veri modeli hepsini `src` olarak görmek ister. Böylece bir pano ya da kural bütün kaynaklarda aynı aramayla çalışır.

Bu pafta laboratuvarında Splunk'ın **resmi CIM eklentisi** (Splunk_SA_CIM 8.5.0) kurulu. Bir olayın Web modeline girmesi için üç halka gerekir:

1. **Alan adları.** `props.conf`'ta arama zamanı takma adları: `FIELDALIAS-<ad> = istemci AS src ...`. Takma ad veriyi değiştirmez; arama sırasında aynı değere ikinci bir ad verir.
2. **Olay türü.** `eventtypes.conf`'ta bu olayları tarif eden bir arama: `search = sourcetype=pafta_erisim`.
3. **Etiket.** `tags.conf`'ta o olay türüne `web` etiketi. Web modelinin kısıtı tam olarak budur:

```text
(`cim_Web_indexes`) tag=web
```

Makro, modelin hangi dizinlerde arayacağını söyler; laboratuvar onu `pafta_ders` dizinine bağladı. Gerçek bir kurulumda bu ayar CIM eklentisinin kurulum sayfasından yapılır; boş bırakılırsa model, kullanıcının varsayılan dizinlerinde arar.

Web modelinin sık kullanılan alanları: `src` (istemci), `dest` (sunucu), `http_method`, `uri_path`, `status`, `user`, `url`, `bytes`.

> [!NOT] Bu paftanın laboratuvarı
> Bazı görevlerde kod tek bir metindir ve içinde başlıklarla ayrılmış üç dosya bulunur: `# props.conf`, `# eventtypes.conf`, `# tags.conf`. Laboratuvar bunları gerçek Splunk'a uygular, görevin günlüğünü alır ve sonucu görevin `tstats` aramasıyla gösterir. Görevin zaman ayarları (SP21) hazırlıkta kurulu; senin `props.conf` kıtan onların üstüne eklenir.
:::

::: gorev 1 · Erişim günlüğünü Web modeline bağla
`pafta_erisim` kaynağının satırları şöyle:

```text
2026-10-19 09:01:12 istemci=10.0.1.15 yontem=GET yol=/api/bilet durum=200 sunucu=web01 kullanici=ayse
```

Üç dosyayı yaz:

- `[pafta_erisim]` kıtasında tek bir `FIELDALIAS-cim` satırıyla şu eşlemeler: `istemci` → `src`, `yontem` → `http_method`, `yol` → `uri_path`, `durum` → `status`, `sunucu` → `dest`, `kullanici` → `user`.
- `pafta_web_erisim` adlı, `sourcetype=pafta_erisim` olaylarını tarif eden bir olay türü.
- Bu olay türüne `web` etiketi.

Görev sonucu şu aramayla gösterir:

```spl norun
| tstats count from datamodel=Web by Web.dest Web.http_method Web.status | rename Web.* AS * | sort dest http_method status
```

```starter
# props.conf
[pafta_erisim]
FIELDALIAS-cim = istemci AS src yontem AS http_method yol AS uri_path sunucu AS dest kullanici AS user
```

```test
eq(sutunlar, ["dest", "http_method", "status", "count"], "tstats'ın by alanları ve sayı")
eq(sonuc, [("web01", "GET", 200, 1), ("web01", "GET", 500, 2), ("web01", "GET", 503, 1),
           ("web02", "DELETE", 404, 1), ("web02", "GET", 200, 1), ("web02", "POST", 201, 1),
           ("web03", "GET", 200, 1)],
   "sekiz isteğin hepsi Web modelinde, durum kodlarıyla")
EK = ("2026-10-19 09:07:00 istemci=10.0.9.9 yontem=GET yol=/a durum=502 sunucu=web03 kullanici=x\n", "pafta_erisim")
BASKA = ("2026-10-19 09:08:00 istemci=10.0.9.9 yontem=GET yol=/a durum=500 sunucu=web09\n", "pafta_uygulama")
yeni = dene("veri(%r, %r)\nveri(%r, %r)" % (EK + BASKA))
eq([r for r in yeni if r[0] in ("web03", "web09")], [("web03", "GET", 200, 1), ("web03", "GET", 502, 1)],
   "yeni gelen erişim satırı modele kendiliğinden girer; etiketlenmemiş başka bir kaynak (web09) girmez")
```

```solution
# props.conf
[pafta_erisim]
FIELDALIAS-cim = istemci AS src yontem AS http_method yol AS uri_path durum AS status sunucu AS dest kullanici AS user

# eventtypes.conf
[pafta_web_erisim]
search = sourcetype=pafta_erisim

# tags.conf
[eventtype=pafta_web_erisim]
web = enabled
```

```hint
Başlangıçtaki takma ad satırı modeli doldurmaya yetmez: model yalnız `tag=web` taşıyan olayları görür. `# eventtypes.conf` bölümüne `[pafta_web_erisim]` ve `search = sourcetype=pafta_erisim`, `# tags.conf` bölümüne `[eventtype=pafta_web_erisim]` ve `web = enabled` yaz.
```

```hint
Takma ad satırında `durum AS status` eksik: model eşlenmemiş alanı boş değil `unknown` olarak doldurur.
```

```meta
motor: splunk
girdi: bilgi
```

```setup
props("pafta_erisim", {"SHOULD_LINEMERGE": "false", "TIME_PREFIX": "^", "TIME_FORMAT": "%Y-%m-%d %H:%M:%S",
                       "MAX_TIMESTAMP_LOOKAHEAD": "19"})
props("pafta_uygulama", {"SHOULD_LINEMERGE": "false", "TIME_PREFIX": "^", "TIME_FORMAT": "%Y-%m-%d %H:%M:%S",
                         "MAX_TIMESTAMP_LOOKAHEAD": "19", "FIELDALIAS-cim": "durum AS status sunucu AS dest"})
veri("""2026-10-19 09:01:12 istemci=10.0.1.15 yontem=GET yol=/api/bilet durum=200 sunucu=web01 kullanici=ayse
2026-10-19 09:01:40 istemci=10.0.1.22 yontem=POST yol=/api/bilet durum=201 sunucu=web02 kullanici=can
2026-10-19 09:02:05 istemci=10.0.3.4 yontem=GET yol=/api/rapor durum=500 sunucu=web01 kullanici=zeynep
2026-10-19 09:02:30 istemci=10.0.3.4 yontem=GET yol=/api/rapor durum=500 sunucu=web01 kullanici=zeynep
2026-10-19 09:03:10 istemci=10.0.2.8 yontem=GET yol=/api/rapor durum=503 sunucu=web01 kullanici=mert
2026-10-19 09:04:00 istemci=198.51.100.23 yontem=GET yol=/api/durum durum=200 sunucu=web03
2026-10-19 09:05:15 istemci=10.0.1.15 yontem=DELETE yol=/api/bilet/17 durum=404 sunucu=web02 kullanici=ayse
2026-10-19 09:06:00 istemci=10.0.2.8 yontem=GET yol=/api/bilet durum=200 sunucu=web02 kullanici=mert
""", "pafta_erisim", "erisim.log")
goster("| tstats count from datamodel=Web by Web.dest Web.http_method Web.status | rename Web.* AS * | sort dest http_method status")
```
:::

::: tahmin
Bu adımın hazırlığında eşleme yarım kalmış: takma ad satırında `durum AS status` yok, olay türü ve etiket kurulu. Ne yazar?

```spl
| tstats count from datamodel=Web by Web.status | rename Web.* AS *
```

???

**Tek satır: `unknown|8`.**

```
unknown|8
```

Sekiz olayın hepsi modele girdi (etiket doğru), ama modelin `status` alanı boş kalmadı: Web modeli eşlenmemiş alanları `if(isnull(status) OR status="" OR status="-", "unknown", status)` hesabıyla doldurur. Bu bir hata vermez; pano "her şey unknown" gösterir, durum koduna bakan bir kural ise hiç tetiklenmez. Bir kaynağı CIM'e bağladıktan sonra modelin her önemli alanında `unknown` sayısına bakmak, eşlemeyi denetlemenin en hızlı yoludur.

```meta
motor: splunk
```

```setup
props("pafta_erisim", {"SHOULD_LINEMERGE": "false", "TIME_PREFIX": "^", "TIME_FORMAT": "%Y-%m-%d %H:%M:%S",
                       "MAX_TIMESTAMP_LOOKAHEAD": "19",
                       "FIELDALIAS-cim": "istemci AS src yontem AS http_method yol AS uri_path sunucu AS dest kullanici AS user"})
olay_turu("pafta_web_erisim", "sourcetype=pafta_erisim")
etiket("eventtype=pafta_web_erisim", {"web": "enabled"})
veri("""2026-10-19 09:01:12 istemci=10.0.1.15 yontem=GET yol=/api/bilet durum=200 sunucu=web01 kullanici=ayse
2026-10-19 09:01:40 istemci=10.0.1.22 yontem=POST yol=/api/bilet durum=201 sunucu=web02 kullanici=can
2026-10-19 09:02:05 istemci=10.0.3.4 yontem=GET yol=/api/rapor durum=500 sunucu=web01 kullanici=zeynep
2026-10-19 09:02:30 istemci=10.0.3.4 yontem=GET yol=/api/rapor durum=500 sunucu=web01 kullanici=zeynep
2026-10-19 09:03:10 istemci=10.0.2.8 yontem=GET yol=/api/rapor durum=503 sunucu=web01 kullanici=mert
2026-10-19 09:04:00 istemci=198.51.100.23 yontem=GET yol=/api/durum durum=200 sunucu=web03
2026-10-19 09:05:15 istemci=10.0.1.15 yontem=DELETE yol=/api/bilet/17 durum=404 sunucu=web02 kullanici=ayse
2026-10-19 09:06:00 istemci=10.0.2.8 yontem=GET yol=/api/bilet durum=200 sunucu=web02 kullanici=mert
""", "pafta_erisim", "erisim.log")
```
:::

::: anlat tstats ve özetler
`tstats` olayları tek tek açmaz; dizinin yanındaki **tsidx** dosyalarından ya da bir veri modelinin **hızlandırılmış özetinden** sayar. Bu yüzden çok hızlıdır, ama yalnız bu yapıların bildiği alanlarla çalışır:

```spl norun
| tstats count from datamodel=Web where Web.status>=500 by Web.dest
| rename Web.* AS *
```

- `from datamodel=Web`: modelin kökü; alanlar `Web.` önekiyle gelir. `rename Web.* AS *` öneki atar.
- `where`: tstats'ın kendi süzgeci; modelin alanlarıyla yazılır.
- `by`: gruplama alanları; sonuç sütunları önce `by` alanları, sonra sayılar.

Bir veri modeli **hızlandırılmışsa** Splunk onun özetini arka planda, belirli aralıklarla kurar. `summariesonly=true` yalnız bu özeti okur: hızlıdır ama özetin henüz kapsamadığı (yeni gelmiş ya da hiç özetlenmemiş) olayları görmez. `summariesonly=false` (varsayılan) özette olmayan kısmı ham olaylardan tamamlar.
:::

::: tahmin
Gorev 1'in eşlemesi tam kurulu. Bu laboratuvarda Web modeli **hızlandırılmamış**. Ne yazar?

```spl
| tstats summariesonly=true count from datamodel=Web by Web.dest
```

???

**Hiçbir satır.**

Model hızlandırılmadığı için ortada okunacak bir özet yok; `summariesonly=true` ham olaylara bakmayı reddeder ve boş döner. Aynı arama `summariesonly=true` olmadan sekiz olayı sayar. Gerçek bir SOC'ta bu iki sonucun farkı bir **kapsam tanığıdır**: hızlandırılmış bir modelde ikisi arasındaki fark, özetin geride kaldığı ya da bir dizinin özete hiç girmediği anlamına gelir. "Sonuç yok" ile "veri yok" aynı şey değildir.

```meta
motor: splunk
```

```setup
props("pafta_erisim", {"SHOULD_LINEMERGE": "false", "TIME_PREFIX": "^", "TIME_FORMAT": "%Y-%m-%d %H:%M:%S",
                       "MAX_TIMESTAMP_LOOKAHEAD": "19",
                       "FIELDALIAS-cim": "istemci AS src yontem AS http_method yol AS uri_path durum AS status sunucu AS dest kullanici AS user"})
olay_turu("pafta_web_erisim", "sourcetype=pafta_erisim")
etiket("eventtype=pafta_web_erisim", {"web": "enabled"})
veri("""2026-10-19 09:01:12 istemci=10.0.1.15 yontem=GET yol=/api/bilet durum=200 sunucu=web01 kullanici=ayse
2026-10-19 09:02:05 istemci=10.0.3.4 yontem=GET yol=/api/rapor durum=500 sunucu=web01 kullanici=zeynep
""", "pafta_erisim", "erisim.log")
```
:::

::: gorev 2 · Modelden sunucu başına hata oranı
Eşleme tam kurulu. **Yalnız Web veri modelini** kullanarak (`tstats`) her sunucu için: `toplam` (istek sayısı), `hata` (durumu 500 ya da üstü istek sayısı) ve `oran` (hata yüzdesi, bir ondalık). Sütunlar: `dest`, `toplam`, `hata`, `oran`; sunucuya göre artan.

```starter
index=pafta_ders sourcetype=pafta_erisim
| stats count AS toplam by sunucu
```

```test
eq(kullanir("tstats"), True, "olayları açma; Web veri modelinden tstats ile say")
eq(sutunlar, ["dest", "toplam", "hata", "oran"], "sütunlar")
eq(sonuc, [("web01", 4, 3, 75.0), ("web02", 3, 0, 0.0), ("web03", 1, 0, 0.0)],
   "web01'de 500, 500 ve 503; 404 hata sayılmaz")
yeni = dene("veri(%r, %r)" % ("2026-10-19 09:07:00 istemci=10.0.9.9 yontem=GET yol=/a durum=499 sunucu=web03 kullanici=x\n"
                              "2026-10-19 09:07:30 istemci=10.0.9.9 yontem=GET yol=/a durum=500 sunucu=web03 kullanici=x\n",
                              "pafta_erisim"))
eq(yeni[-1], ("web03", 3, 1, 33.3), "499 hata değil, 500 hata; oran bir ondalığa yuvarlanır")
```

```solution
| tstats count from datamodel=Web by Web.dest Web.status
| rename Web.* AS *
| eval hata=if(status>=500, count, 0)
| stats sum(count) AS toplam sum(hata) AS hata by dest
| eval oran=round(hata/toplam*100, 1)
| sort dest
```

```hint
Önce `| tstats count from datamodel=Web by Web.dest Web.status | rename Web.* AS *` ile sunucu ve durum başına sayıları al; sonra `eval` ve `stats sum(...)` ile sunucu başına topla.
```

```hint
`eval hata=if(status>=500, count, 0)`: her satır bir (sunucu, durum) çiftidir ve `count` o çiftin istek sayısıdır. Oran: `round(hata/toplam*100, 1)`.
```

```meta
motor: splunk
```

```setup
props("pafta_erisim", {"SHOULD_LINEMERGE": "false", "TIME_PREFIX": "^", "TIME_FORMAT": "%Y-%m-%d %H:%M:%S",
                       "MAX_TIMESTAMP_LOOKAHEAD": "19",
                       "FIELDALIAS-cim": "istemci AS src yontem AS http_method yol AS uri_path durum AS status sunucu AS dest kullanici AS user"})
olay_turu("pafta_web_erisim", "sourcetype=pafta_erisim")
etiket("eventtype=pafta_web_erisim", {"web": "enabled"})
veri("""2026-10-19 09:01:12 istemci=10.0.1.15 yontem=GET yol=/api/bilet durum=200 sunucu=web01 kullanici=ayse
2026-10-19 09:01:40 istemci=10.0.1.22 yontem=POST yol=/api/bilet durum=201 sunucu=web02 kullanici=can
2026-10-19 09:02:05 istemci=10.0.3.4 yontem=GET yol=/api/rapor durum=500 sunucu=web01 kullanici=zeynep
2026-10-19 09:02:30 istemci=10.0.3.4 yontem=GET yol=/api/rapor durum=500 sunucu=web01 kullanici=zeynep
2026-10-19 09:03:10 istemci=10.0.2.8 yontem=GET yol=/api/rapor durum=503 sunucu=web01 kullanici=mert
2026-10-19 09:04:00 istemci=198.51.100.23 yontem=GET yol=/api/durum durum=200 sunucu=web03
2026-10-19 09:05:15 istemci=10.0.1.15 yontem=DELETE yol=/api/bilet/17 durum=404 sunucu=web02 kullanici=ayse
2026-10-19 09:06:00 istemci=10.0.2.8 yontem=GET yol=/api/bilet durum=200 sunucu=web02 kullanici=mert
""", "pafta_erisim", "erisim.log")
```
:::


::: anlat Authentication ve Endpoint: aynı alan, farklı model kapısı
Bu ek görevler gerçek Splunk Enterprise ve kurulu resmî **Splunk_SA_CIM 8.5.0** veri modellerini kullanır; model sorgusu Python'da taklit edilmez. Authentication kök kısıtı bu paket sürümünde `tag=authentication NOT (action=success user=*$)` içerir: başarılı makine hesabı kayıtları dışarıda kalırken başarısız makine hesabı kayıtları kalabilir. `Endpoint.Processes` ise `tag=process tag=report` ister; etiketlerden yalnız biri yeterli değildir. Alan eşleme, olay türü seçimi ve etiket kapısı ayrı ayrı doğrulanır.

`Authentication.user/action/src/dest/app` kimlik doğrulama alanlarını, `Processes.dest/user/process_name/parent_process_name/process_id` süreç alanlarını taşır. Alanı FIELDALIAS ile adlandırmak tek başına olayı modele katmaz; modelin etiketini ve alan değerlerini birlikte kontrol et. Bu görevde `ok/fail` kaynak değerleri `success/failure` olarak EVAL-action ile normalize edilir. Geçerli kaynak değerini sabit failure'a çevirmek raporu yanlış üretir.

Kurulum tekrarlanabilirliği: `python tools/splunk_cim_kur.py` mevcut yerel CIM arşivinin kabul edilen SHA256'sını ve kurulu/etkin 8.5.0 sürümünü denetler. Eksikse `--install` mevcut arşivi yalnız Pafta Splunk konteynerine kurar; internetten indirme yapmaz. Yeni bilgisayarda resmî paketi kullanıcı onayıyla edinmek gerekir; Splunkbase hesabı/koşulları betikle atlanmaz. SHA256 depodaki kabul edilen yerel paketi sabitler, üreticinin ayrıca yayımladığı imza diye sunulmaz. Kurulu aynı sürümde komut değişiklik yapmaz. Paket kurulumunu ders/test içinde tekrarlamıyoruz.

Kaynaklar: [Authentication modelini besleyen kaynakları doğrulama](https://docs.splunk.com/Documentation/InfoSec/latest/Admin/ValidateDataSources), [CIM alan/model eşlemesi](https://help.splunk.com/en/splunk-cloud-platform/common-information-model/6.0/data-models/cim-fields-per-associated-data-model), [resmî CIM paketi](https://splunkbase.splunk.com/app/1621). Sürümdeki gerçek model JSON'u da bu dersin testinde kullanılır; başka CIM sürümüne genellemeden kontrol et.
:::

::: gorev Authentication modeline değerleri ve kapıyı eşle
Üç bölüm yaz: props.conf `pafta_cim_auth` için kaynak→CIM alias'ları `hesap AS user`, `kaynak AS src`, `hedef AS dest`, `uygulama AS app`. `EVAL-action = case(sonuc="ok","success",sonuc="fail","failure",true(),"unknown")`. eventtypes.conf içinde `pafta_cim_auth_event`, yalnız `sourcetype=pafta_cim_auth tur=auth`; tags.conf içinde bu eventtype'a authentication=enabled. Rapor gerçek `tstats` ile Authentication.user/action/src başına sayar. `tur=heartbeat` ve etiketlenmemiş başka sourcetype modele girmesin. Ham kayıtlardaki hesap harflerini değiştirme.

```meta
motor: splunk
girdi: bilgi
```

```setup
props('pafta_cim_auth',{'SHOULD_LINEMERGE':'false','TIME_PREFIX':'^','TIME_FORMAT':'%Y-%m-%d %H:%M:%S','MAX_TIMESTAMP_LOOKAHEAD':'19'})
props('pafta_cim_noise',{'SHOULD_LINEMERGE':'false','TIME_PREFIX':'^','TIME_FORMAT':'%Y-%m-%d %H:%M:%S','MAX_TIMESTAMP_LOOKAHEAD':'19','FIELDALIAS-cim':'hesap AS user kaynak AS src hedef AS dest uygulama AS app','EVAL-action':'"failure"'})
veri('''2026-10-19 09:01:00 tur=auth hesap=ayse kaynak=198.51.100.1 hedef=dc01 sonuc=fail uygulama=ssh
2026-10-19 09:01:01 tur=auth hesap=ayse kaynak=198.51.100.1 hedef=dc01 sonuc=fail uygulama=ssh
2026-10-19 09:01:02 tur=auth hesap=ayse kaynak=198.51.100.1 hedef=dc01 sonuc=ok uygulama=ssh
2026-10-19 09:01:03 tur=auth hesap=berk kaynak=203.0.113.2 hedef=dc02 sonuc=fail uygulama=vpn
2026-10-19 09:01:04 tur=auth hesap=svc$ kaynak=10.0.0.9 hedef=dc01 sonuc=ok uygulama=win
2026-10-19 09:01:05 tur=auth hesap=svc$ kaynak=10.0.0.9 hedef=dc01 sonuc=fail uygulama=win
2026-10-19 09:01:06 tur=heartbeat hesap=izleme kaynak=10.0.0.8 hedef=dc01 sonuc=fail uygulama=ping
''','pafta_cim_auth')
goster('| tstats count from datamodel=Authentication by Authentication.user Authentication.action Authentication.src | rename Authentication.* AS * | sort user action src')
```

```starter
# props.conf
[pafta_cim_auth]
FIELDALIAS-cim = hesap AS user kaynak AS src
# eventtypes.conf
[pafta_cim_auth_event]
search = sourcetype=pafta_cim_auth
# tags.conf
[eventtype=pafta_cim_auth_event]
web = enabled
```

```test
eq(sutunlar,['user','action','src','count'],'gerçek Authentication sütunları')
eq(sonuc,[('ayse','failure','198.51.100.1',2),('ayse','success','198.51.100.1',1),('berk','failure','203.0.113.2',1),('svc$','failure','10.0.0.9',1)],'başarı/başarısız ayrı; makine başarı ve heartbeat model dışı')
extra=('2026-10-19 09:02:00 tur=auth hesap=Zeynep kaynak=203.0.113.5 hedef=dc03 sonuc=timeout uygulama=vpn\n','pafta_cim_auth')
noise=('2026-10-19 09:02:01 tur=auth hesap=Noise kaynak=203.0.113.5 hedef=dc03 sonuc=fail uygulama=vpn\n','pafta_cim_noise')
y=dene('veri(%r,%r)\nveri(%r,%r)'%(extra+noise))
eq([r for r in y if r[0] in ('Zeynep','Noise')],[('Zeynep','unknown','203.0.113.5',1)],'bilinmeyen eylem korunur, etiketsiz kaynağa kapı açılmaz')
```

```solution
# props.conf
[pafta_cim_auth]
FIELDALIAS-cim = hesap AS user kaynak AS src hedef AS dest uygulama AS app
EVAL-action = case(sonuc="ok","success",sonuc="fail","failure",true(),"unknown")
# eventtypes.conf
[pafta_cim_auth_event]
search = sourcetype=pafta_cim_auth tur=auth
# tags.conf
[eventtype=pafta_cim_auth_event]
authentication = enabled
```

```hint
Etiket modelin kapısıdır; action kaynaktaki iki ayrı durumu korumalı. Authentication modelinin başarılı makine hesabı istisnası bu sürümün kendi kısıtıdır.
```
:::

::: gorev Endpoint.Processes: iki etiket ve süreç kökeni
props.conf `pafta_cim_endpoint` için alias'lar `cihaz AS dest`, `hesap AS user`, `cocuk AS process_name`, `ebeveyn AS parent_process_name`, `pid AS process_id`. Eventtype `pafta_cim_process_event` yalnız bu sourcetype ve `tur=process` kayıtlarını alsın; process ve report etiketleri ikisi de enabled olsun. Rapor Processes.dest/process_name/parent_process_name/user başına gerçek tstats sayımıdır. Başka olay türü modele girmesin; ebeveyn ile çocuğu ters eşleme.

```meta
motor: splunk
girdi: bilgi
```

```setup
props('pafta_cim_endpoint',{'SHOULD_LINEMERGE':'false','TIME_PREFIX':'^','TIME_FORMAT':'%Y-%m-%d %H:%M:%S','MAX_TIMESTAMP_LOOKAHEAD':'19'})
veri('''2026-10-19 10:00:00 tur=process cihaz=pc01 hesap=ayse cocuk=powershell.exe ebeveyn=winword.exe pid=100
2026-10-19 10:00:01 tur=process cihaz=pc01 hesap=ayse cocuk=powershell.exe ebeveyn=winword.exe pid=101
2026-10-19 10:00:02 tur=process cihaz=pc02 hesap=berk cocuk=cmd.exe ebeveyn=explorer.exe pid=102
2026-10-19 10:00:03 tur=service cihaz=pc03 hesap=svc cocuk=svchost.exe ebeveyn=services.exe pid=103
''','pafta_cim_endpoint')
goster('| tstats count from datamodel=Endpoint.Processes by Processes.dest Processes.process_name Processes.parent_process_name Processes.user | rename Processes.* AS * | sort dest process_name parent_process_name user')
```

```starter
# props.conf
[pafta_cim_endpoint]
FIELDALIAS-cim = cihaz AS dest hesap AS user cocuk AS parent_process_name ebeveyn AS process_name
# eventtypes.conf
[pafta_cim_process_event]
search = sourcetype=pafta_cim_endpoint
# tags.conf
[eventtype=pafta_cim_process_event]
process = enabled
```

```test
eq(sutunlar,['dest','process_name','parent_process_name','user','count'],'gerçek Processes model sütunları')
eq(sonuc,[('pc01','powershell.exe','winword.exe','ayse',2),('pc02','cmd.exe','explorer.exe','berk',1)],'çocuk/ebeveyn kaynağı, tekrar sayımı; service türü dışarıda')
eq(dene("veri('2026-10-19 10:01:00 tur=process cihaz=pc04 hesap=Can cocuk=notepad.exe ebeveyn=cmd.exe pid=104\\n','pafta_cim_endpoint')")[-1],('pc04','notepad.exe','cmd.exe','Can',1),'yeni cihaz ve farklı süreç çifti')
eq(dene("goster('| tstats count from datamodel=Endpoint.Processes by Processes.dest Processes.process_id | rename Processes.* AS * | sort dest process_id')"),[('pc01',100,1),('pc01',101,1),('pc02',102,1)],'pid AS process_id: aynı çocuk/ebeveyn çiftinin iki ayrı süreci ayrı kimlik taşır')
```

```solution
# props.conf
[pafta_cim_endpoint]
FIELDALIAS-cim = cihaz AS dest hesap AS user cocuk AS process_name ebeveyn AS parent_process_name pid AS process_id
# eventtypes.conf
[pafta_cim_process_event]
search = sourcetype=pafta_cim_endpoint tur=process
# tags.conf
[eventtype=pafta_cim_process_event]
process = enabled
report = enabled
```

```hint
Endpoint.Processes modelinin kaynak araması hem process hem report etiketi ister. “Endpoint” adı tek bir genel etiket anlamına gelmez.
```
:::
