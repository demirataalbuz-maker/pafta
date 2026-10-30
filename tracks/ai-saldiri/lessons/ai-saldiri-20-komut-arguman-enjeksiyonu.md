---
id: ai-saldiri-20
title: Komut ve Argüman Enjeksiyonu
summary: Model çıktısını shell metnine çevirmeden izinli program ve ayrık argüman listesiyle doğrula, seçenek sınırını uygula, politika ile çalıştırıcı arasındaki sapmaları raporla.
timeout: 45
---

::: anlat Komut ile argüman aynı veri türü değildir
Modelin ürettiği bir metni doğrudan shell'e vermek, metindeki boşlukları ve metakarakterleri komut diline dönüştürür. `program` ile `args` ayrı taşınırsa çalıştırıcı shell açmadan bir argüman vektörü alabilir. Böylece `;`, `$()` veya boşluk içeren bir değer yeni komut değil, tek argüman olarak kalır.

Ayrık argüman listesi tek başına yeterli değildir. Program adı izin listesinde olmalı, alt komutun seçenek ayrıştırması bilinmeli ve kullanıcı verisinin seçenek gibi okunması `--` sınırıyla önlenmelidir. `--` shell güvenliği sağlamaz; yalnız destekleyen programın seçenek ayrıştırma sınırıdır.

Bu derste gerçek komut, shell, Ollama veya ağ kullanılmaz. Bütün çalıştırıcı kayıtları deterministik fixture'dır; amaç güvenli sözleşmeyi ve bypass kanıtlarını ölçmektir.
:::

::: tahmin
Aynı kullanıcı verisi bir argüman listesinde ve görüntü amaçlı birleştirilmiş metinde kullanılıyor. Üç çıktı satırını yaz:

```python
program = "git"
girdi = "main; echo test"
argv = [program, "checkout", "--", girdi]
print(argv)
print(" ".join(argv))
print(program in {"git", "python"})
```

???

```cikti
['git', 'checkout', '--', 'main; echo test']
git checkout -- main; echo test
True
```

Birleştirilmiş metin shell'e verilirse noktalı virgil komut ayracı olur. `argv` listesinde ise dördüncü öge tek bir veri argümanıdır; bu ders hiçbirini gerçekte çalıştırmaz.
:::

::: gorev 1 · Programı ve ayrık argüman vektörünü doğrula
`komut_dogrula(cagri, izinli_programlar)` işlevini yaz. Çağrı tam olarak `program`, `args` alanlarını taşısın. Program boş olmayan string, `args` stringlerden oluşan liste olmalıdır. Boş argüman geçerlidir fakat hiçbir argümanda NUL (`"\x00"`) bulunamaz. İzin listesi boş olmayan, benzersiz ve boş olmayan program adlarından oluşan liste olmalı; izinli adlarda `/`, `\` veya NUL kabul edilmez. Şema veya tür ihlalinde `ValueError` yükselt.

Program izin listesinde yoksa `{"izinli":False,"neden":"program-izinsiz","argv":[]}` dön. İzinliyse `{"izinli":True,"neden":"dogrulandi","argv":[PROGRAM]+ARGS_KOPYASI}` dön. Argümanlardaki boşluk veya shell metakarakterlerini tek başına ret nedeni sayma; onlar ayrık vektörde veridir. Dönen liste girdiden bağımsız olmalıdır. Bu işlev komut çalıştırmaz.

```starter
def komut_dogrula(cagri, izinli_programlar):
    return {}
```

```test
CAGRI = {"program": "git", "args": ["checkout", "--", "main; echo test"]}
IZINLI = ["git", "python"]
def sozlesme(fn):
    try:
        beklenen = {"izinli": True, "neden": "dogrulandi", "argv": ["git", "checkout", "--", "main; echo test"]}
        if fn(CAGRI, IZINLI) != beklenen:
            return False
        if fn({"program": "git", "args": ["", "a b", "$(test)"]}, IZINLI)["argv"] != ["git", "", "a b", "$(test)"]:
            return False
        for program in ["sh", "git; echo test", "/bin/git"]:
            if fn({"program": program, "args": []}, IZINLI) != {"izinli": False, "neden": "program-izinsiz", "argv": []}:
                return False
        kopya = {"program": "git", "args": ["status"]}
        sonuc = fn(kopya, IZINLI)
        sonuc["argv"].append("degisiklik")
        if kopya["args"] != ["status"]:
            return False
        for cagri, izinli in [
            (None, IZINLI), (dict(CAGRI, ek=1), IZINLI),
            (dict(CAGRI, program=""), IZINLI), (dict(CAGRI, program=3), IZINLI),
            (dict(CAGRI, args="status"), IZINLI), (dict(CAGRI, args=["x", None]), IZINLI),
            (dict(CAGRI, args=["a\x00b"]), IZINLI), (CAGRI, "git"),
            (CAGRI, []), (CAGRI, ["git", "git"]), (CAGRI, [""]),
            (CAGRI, ["bin/git"]), (CAGRI, ["bin\\git"]), (CAGRI, [3]),
        ]:
            try:
                fn(cagri, izinli)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(komut_dogrula), "program izni, ayrık argv, veri argümanları ve şema korunmalı")
def m_program(cagri, izinli_programlar):
    return komut_dogrula(cagri, list(izinli_programlar) + [cagri["program"]])
def m_birlestir(cagri, izinli_programlar):
    sonuc = komut_dogrula(cagri, izinli_programlar)
    if sonuc["izinli"]:
        sonuc["argv"] = [" ".join(sonuc["argv"])]
    return sonuc
def m_meta(cagri, izinli_programlar):
    sonuc = komut_dogrula(cagri, izinli_programlar)
    if sonuc["izinli"]:
        sonuc["argv"] = [x for x in sonuc["argv"] if ";" not in x]
    return sonuc
for ad, mutant in [("her programı izinli yapan", m_program), ("argv'yi tek metne birleştiren", m_birlestir), ("veri argümanını silen", m_meta)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def komut_dogrula(cagri, izinli_programlar):
    if not isinstance(izinli_programlar, list) or not izinli_programlar:
        raise ValueError("izin listesi geçersiz")
    if not all(isinstance(x, str) and bool(x) and not any(k in x for k in ("/", "\\", "\x00")) for x in izinli_programlar):
        raise ValueError("izinli program geçersiz")
    if len(izinli_programlar) != len(set(izinli_programlar)):
        raise ValueError("izin listesi benzersiz olmalı")
    if not isinstance(cagri, dict) or set(cagri) != {"program", "args"}:
        raise ValueError("çağrı şeması geçersiz")
    if not isinstance(cagri["program"], str) or not cagri["program"] or not isinstance(cagri["args"], list):
        raise ValueError("çağrı alanları geçersiz")
    if not all(isinstance(x, str) and "\x00" not in x for x in cagri["args"]):
        raise ValueError("argüman geçersiz")
    if cagri["program"] not in izinli_programlar:
        return {"izinli": False, "neden": "program-izinsiz", "argv": []}
    return {"izinli": True, "neden": "dogrulandi", "argv": [cagri["program"]] + list(cagri["args"])}
```

```hint
Önce izin listesini ve çağrı şemasını doğrula. Program adını birebir karşılaştır; başarılı sonuçta programı listedeki argümanların önüne ekle, string birleştirme yapma.
```
:::

::: anlat Tire ile başlayan veri seçenek olabilir
Shell'i kaldırmak seçenek enjeksiyonunu kaldırmaz. Örneğin dosya adı veya yazdırılacak metin `--help` olduğunda alt komut bunu veri yerine seçenek olarak yorumlayabilir. Bu fixture sözleşmesinde `yazdir` bir, `kopyala` iki konumsal değer alır ve her ikisinde de `--` sonrası yalnız veri kabul edilir.

Güvenli plan, kullanıcıdan alınan değerleri yeniden shell metnine çevirmez. Eylem ve `--` uygulama tarafından eklenir; değerler aynen ve ayrı öğeler olarak korunur. Gerçek bir araca bağlanırken o aracın `--` desteği ayrıca doğrulanmalıdır.
:::

::: gorev 2 · Seçenek sınırıyla güvenli alt komut planı üret
`arguman_plani(eylem, degerler)` işlevini yaz. Eylem yalnız `yazdir` veya `kopyala` olabilir. Değerler string listesi olmalı ve hiçbirinde NUL bulunamaz. `yazdir` tam bir, `kopyala` tam iki değer ister. Boş string geçerli bir değerdir. Geçersiz eylem, tür, değer veya sayıda `ValueError` yükselt.

Dönüş tam olarak:

```text
{"argv":[EYLEM,"--"]+DEGERLER_KOPYASI,
 "ayristirici":"argv","shell":False}
```

Değer `-v`, `--help`, boşluk veya shell metakarakteri içerse bile tek argüman olarak korunur. `shell` her zaman `False`, `ayristirici` her zaman `argv` olmalıdır. Girdi listesini değiştirme ve komut çalıştırma.

```starter
def arguman_plani(eylem, degerler):
    return {}
```

```test
def sozlesme(fn):
    try:
        if fn("yazdir", ["--help"]) != {"argv": ["yazdir", "--", "--help"], "ayristirici": "argv", "shell": False}:
            return False
        if fn("kopyala", ["a b", "-v;echo test"]) != {"argv": ["kopyala", "--", "a b", "-v;echo test"], "ayristirici": "argv", "shell": False}:
            return False
        if fn("yazdir", [""])["argv"] != ["yazdir", "--", ""]:
            return False
        degerler = ["metin"]
        sonuc = fn("yazdir", degerler)
        sonuc["argv"].append("ek")
        if degerler != ["metin"]:
            return False
        for eylem, degerler in [
            ("sil", ["x"]), ("yazdir", []), ("yazdir", ["a", "b"]),
            ("kopyala", ["a"]), ("kopyala", ["a", "b", "c"]),
            ("yazdir", "metin"), ("yazdir", [None]), ("yazdir", ["a\x00b"]),
            (None, ["x"]),
        ]:
            try:
                fn(eylem, degerler)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(arguman_plani), "eylem, değer sayısı, seçenek sınırı ve kapalı shell korunmalı")
def m_sinir(eylem, degerler):
    sonuc = arguman_plani(eylem, degerler)
    sonuc["argv"].remove("--")
    return sonuc
def m_shell(eylem, degerler):
    sonuc = arguman_plani(eylem, degerler)
    sonuc["shell"] = True
    return sonuc
def m_metin(eylem, degerler):
    sonuc = arguman_plani(eylem, degerler)
    return {"argv": " ".join(sonuc["argv"]), "ayristirici": "shell", "shell": True}
for ad, mutant in [("seçenek sınırını kaldıran", m_sinir), ("shell'i açan", m_shell), ("argümanları metne çeviren", m_metin)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def arguman_plani(eylem, degerler):
    if eylem not in ("yazdir", "kopyala"):
        raise ValueError("eylem geçersiz")
    if not isinstance(degerler, list) or not all(isinstance(x, str) and "\x00" not in x for x in degerler):
        raise ValueError("değerler geçersiz")
    beklenen = 1 if eylem == "yazdir" else 2
    if len(degerler) != beklenen:
        raise ValueError("değer sayısı geçersiz")
    return {"argv": [eylem, "--"] + list(degerler), "ayristirici": "argv", "shell": False}
```

```hint
Eyleme göre beklenen değer sayısını denetle. Dönen listeyi uygulamanın sabitleri olan eylem ve `--` ile başlat; kullanıcı değerlerini liste kopyası olarak arkasına ekle.
```
:::

::: anlat Doğru politika yanlış çalıştırıcıyı temizlemez
Program doğrulaması ile gerçek dispatcher arasında sapma olabilir. Reddedilen isteğin çalışması yetki bypass'ı, `shell=True` kullanılması komut enjeksiyonu yüzeyi, beklenen vektörden farklı vektör ise argüman sapmasıdır. İzinli bir işin hiç çalışmaması da güvenlik açığı değil fakat işlev hatasıdır.

Regresyon raporu bu olayları birbirine karıştırmaz. Bir vaka birden fazla listeye girebilir. `temiz` olmak için çalışma durumu izinle aynı olmalı, varsa gerçekleşen aday shell kullanmamalı ve beklenen argüman vektörüyle birebir aynı olmalıdır.
:::

::: gorev 3 · Yetki, shell ve argüman sapmalarını ayrı raporla
`calistirma_regresyonu(kayitlar)` işlevini yaz. Girdi liste olmalıdır. Her kayıt tam olarak `vaka_id`, `izinli`, `beklenen_argv`, `gerceklesen` alanlarını taşısın. Vaka kimliği boş olmayan ve benzersiz string, `izinli` bool, `beklenen_argv` NUL içermeyen stringlerden oluşan liste olmalıdır. `gerceklesen`, çağrı yoksa `None`; varsa tam olarak `argv`, `shell`, `calistirildi` alanlarını taşıyan dict olmalıdır. Burada `argv` aynı kuralları taşıyan liste, diğer iki alan bool olmalıdır. Geçersiz veride `ValueError` yükselt.

Dönüş:

```text
{"vaka":N,"yetkisiz_calisma":[...],"kabuk_kullanimi":[...],
 "argv_sapmasi":[...],"beklenen_calismadi":[...],"temiz":[...]}
```

- `yetkisiz_calisma`: `izinli=False` iken gerçekleşen çağrı `calistirildi=True`.
- `kabuk_kullanimi`: gerçekleşen adayda `shell=True`; çalışıp çalışmamasından bağımsız.
- `argv_sapmasi`: gerçekleşen adayın vektörü beklenen vektörden farklı.
- `beklenen_calismadi`: izinli vakada çağrı yok veya `calistirildi=False`.
- `temiz`: fiili çalışma `izinli` ile aynı; aday varsa shell kapalı ve vektör beklenenle aynı.

Listeler alfabetik vaka kimliği sıralıdır. Boş girdi için boş rapor dön; sıralama ve girdi değişimi sonucu etkilememelidir.

```starter
def calistirma_regresyonu(kayitlar):
    return {}
```

```test
import copy
KAYITLAR = [
    {"vaka_id": "v1", "izinli": True, "beklenen_argv": ["git", "status"], "gerceklesen": {"argv": ["git", "status"], "shell": False, "calistirildi": True}},
    {"vaka_id": "v2", "izinli": False, "beklenen_argv": [], "gerceklesen": {"argv": ["git", "clean", "-f"], "shell": False, "calistirildi": True}},
    {"vaka_id": "v3", "izinli": True, "beklenen_argv": ["git", "checkout", "--", "x; y"], "gerceklesen": {"argv": ["git", "checkout", "--", "x; y"], "shell": True, "calistirildi": True}},
    {"vaka_id": "v4", "izinli": True, "beklenen_argv": ["git", "checkout", "--", "--help"], "gerceklesen": {"argv": ["git", "checkout", "--help"], "shell": False, "calistirildi": True}},
    {"vaka_id": "v5", "izinli": True, "beklenen_argv": ["git", "status"], "gerceklesen": None},
    {"vaka_id": "v6", "izinli": False, "beklenen_argv": [], "gerceklesen": None},
    {"vaka_id": "v7", "izinli": False, "beklenen_argv": [], "gerceklesen": {"argv": [], "shell": False, "calistirildi": False}},
    {"vaka_id": "v8", "izinli": True, "beklenen_argv": ["git", "status"], "gerceklesen": {"argv": ["git", "status"], "shell": False, "calistirildi": False}},
]
BEKLENEN = {"vaka": 8, "yetkisiz_calisma": ["v2"], "kabuk_kullanimi": ["v3"], "argv_sapmasi": ["v2", "v4"], "beklenen_calismadi": ["v5", "v8"], "temiz": ["v1", "v6", "v7"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR) != BEKLENEN or KAYITLAR != once or fn(list(reversed(KAYITLAR))) != BEKLENEN:
            return False
        if fn([]) != {"vaka": 0, "yetkisiz_calisma": [], "kabuk_kullanimi": [], "argv_sapmasi": [], "beklenen_calismadi": [], "temiz": []}:
            return False
        for kayitlar in [
            None, {}, KAYITLAR + [KAYITLAR[0]], [None], [dict(KAYITLAR[0], ek=1)],
            [dict(KAYITLAR[0], vaka_id="")], [dict(KAYITLAR[0], izinli=1)],
            [dict(KAYITLAR[0], beklenen_argv="git status")],
            [dict(KAYITLAR[0], beklenen_argv=["a\x00b"])],
            [dict(KAYITLAR[0], gerceklesen={})],
            [dict(KAYITLAR[0], gerceklesen={"argv": [], "shell": 0, "calistirildi": True})],
            [dict(KAYITLAR[0], gerceklesen={"argv": [], "shell": False, "calistirildi": 1})],
            [dict(KAYITLAR[0], gerceklesen={"argv": "git", "shell": False, "calistirildi": True})],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(calistirma_regresyonu), "yetkisiz çalışma, shell, argv sapması ve temizlik ayrımı korunmalı")
def m_shell(kayitlar):
    sonuc = calistirma_regresyonu(kayitlar)
    sonuc["kabuk_kullanimi"] = []
    return sonuc
def m_argv(kayitlar):
    sonuc = calistirma_regresyonu(kayitlar)
    sonuc["argv_sapmasi"] = []
    return sonuc
def m_temiz(kayitlar):
    sonuc = calistirma_regresyonu(kayitlar)
    sonuc["temiz"] = sorted(x["vaka_id"] for x in kayitlar if bool(x["gerceklesen"] and x["gerceklesen"]["calistirildi"]) == x["izinli"])
    return sonuc
for ad, mutant in [("shell kullanımını gizleyen", m_shell), ("argv sapmasını gizleyen", m_argv), ("temizliği yalnız çalışmaya indirgeyen", m_temiz)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def calistirma_regresyonu(kayitlar):
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    def argv_gecerli(argv):
        return isinstance(argv, list) and all(isinstance(x, str) and "\x00" not in x for x in argv)
    sonuc = {"vaka": 0, "yetkisiz_calisma": [], "kabuk_kullanimi": [], "argv_sapmasi": [], "beklenen_calismadi": [], "temiz": []}
    vakalar = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"vaka_id", "izinli", "beklenen_argv", "gerceklesen"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["vaka_id"], str) or not kayit["vaka_id"] or kayit["vaka_id"] in vakalar:
            raise ValueError("vaka kimliği geçersiz")
        if not isinstance(kayit["izinli"], bool) or not argv_gecerli(kayit["beklenen_argv"]):
            raise ValueError("kayıt alanları geçersiz")
        gercek = kayit["gerceklesen"]
        if gercek is not None:
            if not isinstance(gercek, dict) or set(gercek) != {"argv", "shell", "calistirildi"}:
                raise ValueError("gerçekleşen şeması geçersiz")
            if not argv_gecerli(gercek["argv"]) or not isinstance(gercek["shell"], bool) or not isinstance(gercek["calistirildi"], bool):
                raise ValueError("gerçekleşen alanları geçersiz")
        vakalar.add(kayit["vaka_id"])
        calisti = bool(gercek and gercek["calistirildi"])
        kabuk = bool(gercek and gercek["shell"])
        sapma = gercek is not None and gercek["argv"] != kayit["beklenen_argv"]
        if not kayit["izinli"] and calisti:
            sonuc["yetkisiz_calisma"].append(kayit["vaka_id"])
        if kabuk:
            sonuc["kabuk_kullanimi"].append(kayit["vaka_id"])
        if sapma:
            sonuc["argv_sapmasi"].append(kayit["vaka_id"])
        if kayit["izinli"] and not calisti:
            sonuc["beklenen_calismadi"].append(kayit["vaka_id"])
        if calisti == kayit["izinli"] and not kabuk and not sapma:
            sonuc["temiz"].append(kayit["vaka_id"])
    sonuc["vaka"] = len(vakalar)
    for alan in ("yetkisiz_calisma", "kabuk_kullanimi", "argv_sapmasi", "beklenen_calismadi", "temiz"):
        sonuc[alan].sort()
    return sonuc
```

```hint
Her kayıt için `calisti`, `kabuk` ve `sapma` değerlerini ayrı hesapla. Temizlikte bu üç koşulu birlikte kullan; reddedilen ve hiç çağrısı olmayan vaka da temiz olabilir.
```
:::


::: anlat Argümanı gerçek alt sürecin gözünden gör
Sentetik ham dosya sunucuda `/data/ai-saldiri-20-argumanlar.txt` adresindedir; aynı Pafta sunucusunun adresine bu yolu yazarak açabilirsin. Markdown bağlantıları mevcut ekranda tıklanabilir değildir. Çalıştır ayrı kalıcı `calisma/ai-saldiri-20/argumanlar.json` kopyasının yolunu/içeriğini de gösterir. Kopyayı dış editör/Python ile değiştirip yeniden Çalıştır; düzenlemen korunur. Test ayrı veriler kullanır.

`yazdir` ve `kopyala` burada işletim sistemi komutu değil, sabit yerel Python adaptöründeki iki eğitim eylemidir. Öğrenci program allowlist'i ve argv planı gerçek `subprocess.run(..., shell=False)` önünde denetlenir. Alt süreç gerçekten başlar, aldığı `sys.argv`yi kendi PID/sürümüyle geri yazar; plan ile görülen argümanlar karşılaştırılır. Kopyalama yalnız deneyin `-kaynak rapor.txt` dosyasından `-kopya rapor.txt` dosyasınadır; SHA256 ile gerçek etki ölçülür.

`--help`, boşluk, tırnak, & ve ; gibi karakterler tek veri argümanı olarak kalmalıdır. Her programın `--` davranışı farklıdır; bu adaptörün davranışı bütün işletim sistemi araçlarına genellenemez. Keyfi model komutu veya shell=True hiç çalıştırılmaz; statik arka uç sınırı yanlış öğrenci kodunda da bunu engeller. İzin verilmeyen cmd önerisi gerçek süreç başlamadan reddedilir. Doğrudan sentetik argv kontrolleri ile iki canlı native model önerisi ayrı kaydedilir. Modelin saldırıya uyması geçme şartı değildir.
:::

::: gorev Gerçek deney · Program kapısı ve argv sınırını gerçek süreçte ölç
Önceki `komut_dogrula`, `arguman_plani`, `calistirma_regresyonu` işlevlerini birleştir. Çalıştır gerçek alt süreç çıktısı, görülen argv, kopya hashleri ve modelin ham önerilerini gösterir. Kontrol Et saf sözleşmeleri ve gerçek deney etkisini ayrı sınar.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def komut_dogrula(cagri,izinli_programlar):return {}

def arguman_plani(eylem,degerler):return {}

def calistirma_regresyonu(kayitlar):return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_20 as deney
    deney.goster(komut_dogrula,arguman_plani,calistirma_regresyonu)

```

```test
CAGRI = {"program": "git", "args": ["checkout", "--", "main; echo test"]}
IZINLI = ["git", "python"]
def sozlesme(fn):
    try:
        beklenen = {"izinli": True, "neden": "dogrulandi", "argv": ["git", "checkout", "--", "main; echo test"]}
        if fn(CAGRI, IZINLI) != beklenen:
            return False
        if fn({"program": "git", "args": ["", "a b", "$(test)"]}, IZINLI)["argv"] != ["git", "", "a b", "$(test)"]:
            return False
        for program in ["sh", "git; echo test", "/bin/git"]:
            if fn({"program": program, "args": []}, IZINLI) != {"izinli": False, "neden": "program-izinsiz", "argv": []}:
                return False
        kopya = {"program": "git", "args": ["status"]}
        sonuc = fn(kopya, IZINLI)
        sonuc["argv"].append("degisiklik")
        if kopya["args"] != ["status"]:
            return False
        for cagri, izinli in [
            (None, IZINLI), (dict(CAGRI, ek=1), IZINLI),
            (dict(CAGRI, program=""), IZINLI), (dict(CAGRI, program=3), IZINLI),
            (dict(CAGRI, args="status"), IZINLI), (dict(CAGRI, args=["x", None]), IZINLI),
            (dict(CAGRI, args=["a\x00b"]), IZINLI), (CAGRI, "git"),
            (CAGRI, []), (CAGRI, ["git", "git"]), (CAGRI, [""]),
            (CAGRI, ["bin/git"]), (CAGRI, ["bin\\git"]), (CAGRI, [3]),
        ]:
            try:
                fn(cagri, izinli)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(komut_dogrula), "program izni, ayrık argv, veri argümanları ve şema korunmalı")
def m_program(cagri, izinli_programlar):
    return komut_dogrula(cagri, list(izinli_programlar) + [cagri["program"]])
def m_birlestir(cagri, izinli_programlar):
    sonuc = komut_dogrula(cagri, izinli_programlar)
    if sonuc["izinli"]:
        sonuc["argv"] = [" ".join(sonuc["argv"])]
    return sonuc
def m_meta(cagri, izinli_programlar):
    sonuc = komut_dogrula(cagri, izinli_programlar)
    if sonuc["izinli"]:
        sonuc["argv"] = [x for x in sonuc["argv"] if ";" not in x]
    return sonuc
for ad, mutant in [("her programı izinli yapan", m_program), ("argv'yi tek metne birleştiren", m_birlestir), ("veri argümanını silen", m_meta)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

def sozlesme(fn):
    try:
        if fn("yazdir", ["--help"]) != {"argv": ["yazdir", "--", "--help"], "ayristirici": "argv", "shell": False}:
            return False
        if fn("kopyala", ["a b", "-v;echo test"]) != {"argv": ["kopyala", "--", "a b", "-v;echo test"], "ayristirici": "argv", "shell": False}:
            return False
        if fn("yazdir", [""])["argv"] != ["yazdir", "--", ""]:
            return False
        degerler = ["metin"]
        sonuc = fn("yazdir", degerler)
        sonuc["argv"].append("ek")
        if degerler != ["metin"]:
            return False
        for eylem, degerler in [
            ("sil", ["x"]), ("yazdir", []), ("yazdir", ["a", "b"]),
            ("kopyala", ["a"]), ("kopyala", ["a", "b", "c"]),
            ("yazdir", "metin"), ("yazdir", [None]), ("yazdir", ["a\x00b"]),
            (None, ["x"]),
        ]:
            try:
                fn(eylem, degerler)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(arguman_plani), "eylem, değer sayısı, seçenek sınırı ve kapalı shell korunmalı")
def m_sinir(eylem, degerler):
    sonuc = arguman_plani(eylem, degerler)
    sonuc["argv"].remove("--")
    return sonuc
def m_shell(eylem, degerler):
    sonuc = arguman_plani(eylem, degerler)
    sonuc["shell"] = True
    return sonuc
def m_metin(eylem, degerler):
    sonuc = arguman_plani(eylem, degerler)
    return {"argv": " ".join(sonuc["argv"]), "ayristirici": "shell", "shell": True}
for ad, mutant in [("seçenek sınırını kaldıran", m_sinir), ("shell'i açan", m_shell), ("argümanları metne çeviren", m_metin)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
KAYITLAR = [
    {"vaka_id": "v1", "izinli": True, "beklenen_argv": ["git", "status"], "gerceklesen": {"argv": ["git", "status"], "shell": False, "calistirildi": True}},
    {"vaka_id": "v2", "izinli": False, "beklenen_argv": [], "gerceklesen": {"argv": ["git", "clean", "-f"], "shell": False, "calistirildi": True}},
    {"vaka_id": "v3", "izinli": True, "beklenen_argv": ["git", "checkout", "--", "x; y"], "gerceklesen": {"argv": ["git", "checkout", "--", "x; y"], "shell": True, "calistirildi": True}},
    {"vaka_id": "v4", "izinli": True, "beklenen_argv": ["git", "checkout", "--", "--help"], "gerceklesen": {"argv": ["git", "checkout", "--help"], "shell": False, "calistirildi": True}},
    {"vaka_id": "v5", "izinli": True, "beklenen_argv": ["git", "status"], "gerceklesen": None},
    {"vaka_id": "v6", "izinli": False, "beklenen_argv": [], "gerceklesen": None},
    {"vaka_id": "v7", "izinli": False, "beklenen_argv": [], "gerceklesen": {"argv": [], "shell": False, "calistirildi": False}},
    {"vaka_id": "v8", "izinli": True, "beklenen_argv": ["git", "status"], "gerceklesen": {"argv": ["git", "status"], "shell": False, "calistirildi": False}},
]
BEKLENEN = {"vaka": 8, "yetkisiz_calisma": ["v2"], "kabuk_kullanimi": ["v3"], "argv_sapmasi": ["v2", "v4"], "beklenen_calismadi": ["v5", "v8"], "temiz": ["v1", "v6", "v7"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR) != BEKLENEN or KAYITLAR != once or fn(list(reversed(KAYITLAR))) != BEKLENEN:
            return False
        if fn([]) != {"vaka": 0, "yetkisiz_calisma": [], "kabuk_kullanimi": [], "argv_sapmasi": [], "beklenen_calismadi": [], "temiz": []}:
            return False
        for kayitlar in [
            None, {}, KAYITLAR + [KAYITLAR[0]], [None], [dict(KAYITLAR[0], ek=1)],
            [dict(KAYITLAR[0], vaka_id="")], [dict(KAYITLAR[0], izinli=1)],
            [dict(KAYITLAR[0], beklenen_argv="git status")],
            [dict(KAYITLAR[0], beklenen_argv=["a\x00b"])],
            [dict(KAYITLAR[0], gerceklesen={})],
            [dict(KAYITLAR[0], gerceklesen={"argv": [], "shell": 0, "calistirildi": True})],
            [dict(KAYITLAR[0], gerceklesen={"argv": [], "shell": False, "calistirildi": 1})],
            [dict(KAYITLAR[0], gerceklesen={"argv": "git", "shell": False, "calistirildi": True})],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(calistirma_regresyonu), "yetkisiz çalışma, shell, argv sapması ve temizlik ayrımı korunmalı")
def m_shell(kayitlar):
    sonuc = calistirma_regresyonu(kayitlar)
    sonuc["kabuk_kullanimi"] = []
    return sonuc
def m_argv(kayitlar):
    sonuc = calistirma_regresyonu(kayitlar)
    sonuc["argv_sapmasi"] = []
    return sonuc
def m_temiz(kayitlar):
    sonuc = calistirma_regresyonu(kayitlar)
    sonuc["temiz"] = sorted(x["vaka_id"] for x in kayitlar if bool(x["gerceklesen"] and x["gerceklesen"]["calistirildi"]) == x["izinli"])
    return sonuc
for ad, mutant in [("shell kullanımını gizleyen", m_shell), ("argv sapmasını gizleyen", m_argv), ("temizliği yalnız çalışmaya indirgeyen", m_temiz)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

from sandbox import ai_gercek_ai_saldiri_20 as deney
import tempfile,secrets,json
from pathlib import Path
if not ok(not ai_lab.kod_denetimi(src,('komut_ref','plan_ref','rapor_ref')), 'laboratuvar/gerçek ölçüm yamalanmamalı'):stop()
for i in range(3):
    text='--'+secrets.token_hex(4)+' & literal; iki kelime';c={'program':'yazdir','args':[text]}
    if not ok(komut_dogrula(c,['yazdir','kopyala'])==deney.komut_ref(c),'yeni metinde program/argv sözleşmesi'):stop()
    if not ok(arguman_plani('yazdir',[text])==deney.plan_ref(c),'yeni metinde seçenek sınırı ve shellFalse'):stop()
with tempfile.TemporaryDirectory(prefix='pafta_argv20_') as tmp:
    p=Path(tmp)/'argumanlar.json';p.write_text(deney.ORNEK.read_text(encoding='utf-8'),encoding='utf-8')
    r=deney.deney(komut_dogrula,arguman_plani,calistirma_regresyonu,p,Path(tmp)/'deney')
    for k,v in r['kontroller'].items():ok(v,'gerçek deney: '+k)
    accepted=all(r['kontroller'].values());ai_lab.kanit_yaz('saldiri-20-argv',dict(r,kabul=accepted));ok(accepted,'gerçek alt süreç argv/dosya etkisi; saldırı başarısı şart değil')

```

```solution
import ai_lab
def komut_dogrula(cagri, izinli_programlar):
    if not isinstance(izinli_programlar, list) or not izinli_programlar:
        raise ValueError("izin listesi geçersiz")
    if not all(isinstance(x, str) and bool(x) and not any(k in x for k in ("/", "\\", "\x00")) for x in izinli_programlar):
        raise ValueError("izinli program geçersiz")
    if len(izinli_programlar) != len(set(izinli_programlar)):
        raise ValueError("izin listesi benzersiz olmalı")
    if not isinstance(cagri, dict) or set(cagri) != {"program", "args"}:
        raise ValueError("çağrı şeması geçersiz")
    if not isinstance(cagri["program"], str) or not cagri["program"] or not isinstance(cagri["args"], list):
        raise ValueError("çağrı alanları geçersiz")
    if not all(isinstance(x, str) and "\x00" not in x for x in cagri["args"]):
        raise ValueError("argüman geçersiz")
    if cagri["program"] not in izinli_programlar:
        return {"izinli": False, "neden": "program-izinsiz", "argv": []}
    return {"izinli": True, "neden": "dogrulandi", "argv": [cagri["program"]] + list(cagri["args"])}

def arguman_plani(eylem, degerler):
    if eylem not in ("yazdir", "kopyala"):
        raise ValueError("eylem geçersiz")
    if not isinstance(degerler, list) or not all(isinstance(x, str) and "\x00" not in x for x in degerler):
        raise ValueError("değerler geçersiz")
    beklenen = 1 if eylem == "yazdir" else 2
    if len(degerler) != beklenen:
        raise ValueError("değer sayısı geçersiz")
    return {"argv": [eylem, "--"] + list(degerler), "ayristirici": "argv", "shell": False}

def calistirma_regresyonu(kayitlar):
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    def argv_gecerli(argv):
        return isinstance(argv, list) and all(isinstance(x, str) and "\x00" not in x for x in argv)
    sonuc = {"vaka": 0, "yetkisiz_calisma": [], "kabuk_kullanimi": [], "argv_sapmasi": [], "beklenen_calismadi": [], "temiz": []}
    vakalar = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"vaka_id", "izinli", "beklenen_argv", "gerceklesen"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["vaka_id"], str) or not kayit["vaka_id"] or kayit["vaka_id"] in vakalar:
            raise ValueError("vaka kimliği geçersiz")
        if not isinstance(kayit["izinli"], bool) or not argv_gecerli(kayit["beklenen_argv"]):
            raise ValueError("kayıt alanları geçersiz")
        gercek = kayit["gerceklesen"]
        if gercek is not None:
            if not isinstance(gercek, dict) or set(gercek) != {"argv", "shell", "calistirildi"}:
                raise ValueError("gerçekleşen şeması geçersiz")
            if not argv_gecerli(gercek["argv"]) or not isinstance(gercek["shell"], bool) or not isinstance(gercek["calistirildi"], bool):
                raise ValueError("gerçekleşen alanları geçersiz")
        vakalar.add(kayit["vaka_id"])
        calisti = bool(gercek and gercek["calistirildi"])
        kabuk = bool(gercek and gercek["shell"])
        sapma = gercek is not None and gercek["argv"] != kayit["beklenen_argv"]
        if not kayit["izinli"] and calisti:
            sonuc["yetkisiz_calisma"].append(kayit["vaka_id"])
        if kabuk:
            sonuc["kabuk_kullanimi"].append(kayit["vaka_id"])
        if sapma:
            sonuc["argv_sapmasi"].append(kayit["vaka_id"])
        if kayit["izinli"] and not calisti:
            sonuc["beklenen_calismadi"].append(kayit["vaka_id"])
        if calisti == kayit["izinli"] and not kabuk and not sapma:
            sonuc["temiz"].append(kayit["vaka_id"])
    sonuc["vaka"] = len(vakalar)
    for alan in ("yetkisiz_calisma", "kabuk_kullanimi", "argv_sapmasi", "beklenen_calismadi", "temiz"):
        sonuc[alan].sort()
    return sonuc
if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_20 as deney
    deney.goster(komut_dogrula,arguman_plani,calistirma_regresyonu)

```

```hint
Komut stringi birleştirme; liste argv ve seçenek sınırını koru. ShellFalse yalnız bir sözlük alanı olarak kalmıyor: gerçek alt sürece aynı plan gönderilir ve onun gördüğü argv ölçülür. Her şeyi reddetmek normal yazdırma/kopyalama kontrollerini geçemez.
```
:::
