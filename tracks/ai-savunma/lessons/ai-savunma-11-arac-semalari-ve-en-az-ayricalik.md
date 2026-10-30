---
id: ai-savunma-11
title: Araç Şemaları ve En Az Ayrıcalık
summary: Dar araç şemalarını doğrula, çağrı argümanlarını izin listesiyle sınırla ve oturum yetkisinden bağımsız en az ayrıcalık kararı üret.
timeout: 45
---

::: anlat Modelin araç çağırabilmesi yetki vermek değildir
Araç çağrısı modelden gelen yapılandırılmış bir istektir; uygulama bu isteği ayrı bir şema, argüman ve yetki denetiminden geçirmeden çalıştırmamalıdır. Genel bir `dosya_yonet` aracı yerine `dosya_oku` ve `rapor_yaz` gibi dar araçlar, hangi parametrelerin ve yetkilerin gerekli olduğunu açıkça ayırır.

FastAPI ve Pydantic gerçek uygulamada istek şemalarını uygulamaya, Ollama ise araç çağrısı üretmeye yardımcı olabilir. Bu derste model, ağ ve dosya sistemi kullanılmaz. Üç fixture aracının kayıtları ve çağrıları standart Python ile doğrulanır; hiçbir araç gerçekten yürütülmez.
:::

::: tahmin Oturumda yetki olması isteği en az kapsamlı yapmaz
Üç çıktı satırını yaz:

```python
gerekli = {"dosya:oku"}
istenen = {"dosya:oku", "dosya:yaz"}
print(istenen - gerekli)
print(gerekli.issubset(istenen))
print(istenen == gerekli)
```

???

```cikti
{'dosya:yaz'}
True
False
```

İstenen kümü gerekli yetkiyi kapsasa bile fazladan yazma yetkisi taşır; en az ayrıcalık için iki kümenin tam eşitliği aranır.
:::

::: gorev 1 · Dar araç kayıt şemasını doğrula
`arac_semasi_dogrula(sema)` işlevini yaz. Şema tam olarak `ad`, `parametreler`, `yetkiler`, `yan_etkili`, `zaman_asimi_ms` alanlarını taşısın. Yalnız şu üç kayıt kabul edilir:

```text
dosya_oku : parametreler {"yol":"string"}             yetki dosya:oku  yan_etkili false
web_getir : parametreler {"url":"string"}             yetki ag:get     yan_etkili false
rapor_yaz : parametreler {"baslik":"string",          yetki dosya:yaz  yan_etkili true
                         "icerik":"string"}
```

`yetkiler`, araca ait tek yetkiyi taşıyan bir liste olmalıdır. Zaman aşımı bool olmayan 1–10000 aralığında int olmalıdır. Bilinmeyen araç, parametre, yetki veya alan `ValueError` yükseltir.

Şemayı yeni bir sözlük, parametre sözlüğü ve yetki listesiyle kopyalayarak döndür; girdiyi değiştirme.

```starter
def arac_semasi_dogrula(sema):
    return {}
```

```test
import copy
S = {"ad": "dosya_oku", "parametreler": {"yol": "string"}, "yetkiler": ["dosya:oku"], "yan_etkili": False, "zaman_asimi_ms": 1000}
DIGER = [
    {"ad": "web_getir", "parametreler": {"url": "string"}, "yetkiler": ["ag:get"], "yan_etkili": False, "zaman_asimi_ms": 1},
    {"ad": "rapor_yaz", "parametreler": {"baslik": "string", "icerik": "string"}, "yetkiler": ["dosya:yaz"], "yan_etkili": True, "zaman_asimi_ms": 10000},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(S)
        sonuc = fn(S)
        if sonuc != S or S != once or sonuc is S or sonuc["parametreler"] is S["parametreler"] or sonuc["yetkiler"] is S["yetkiler"]:
            return False
        if any(fn(x) != x for x in DIGER):
            return False
        for sema in [
            None, [], dict(S, ek=1), dict(S, ad="dosya_yonet"),
            dict(S, parametreler={}), dict(S, parametreler={"yol": "string", "mod": "string"}),
            dict(S, parametreler={"yol": "serbest"}), dict(S, yetkiler=[]),
            dict(S, yetkiler=["dosya:oku", "dosya:yaz"]), dict(S, yetkiler=["dosya:yaz"]),
            dict(S, yetkiler="dosya:oku"), dict(S, yan_etkili=True), dict(S, yan_etkili=0),
            dict(S, zaman_asimi_ms=True), dict(S, zaman_asimi_ms=0),
            dict(S, zaman_asimi_ms=10001), dict(S, zaman_asimi_ms=1.5),
        ]:
            try:
                fn(sema)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(arac_semasi_dogrula), "araç bazlı parametre, tek yetki, yan etki ve süre korunmalı")
def m_yetki(sema):
    sonuc = arac_semasi_dogrula(sema)
    sonuc["yetkiler"].append("dosya:yaz")
    return sonuc
def m_parametre(sema):
    sonuc = arac_semasi_dogrula(sema)
    sonuc["parametreler"]["mod"] = "serbest"
    return sonuc
def m_yan_etki(sema):
    sonuc = arac_semasi_dogrula(sema)
    sonuc["yan_etkili"] = not sonuc["yan_etkili"]
    return sonuc
for ad, mutant in [("yetki ekleyen", m_yetki), ("serbest parametre ekleyen", m_parametre), ("yan etkiyi değiştiren", m_yan_etki)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def arac_semasi_dogrula(sema):
    if not isinstance(sema, dict) or set(sema) != {"ad", "parametreler", "yetkiler", "yan_etkili", "zaman_asimi_ms"}:
        raise ValueError("araç şeması geçersiz")
    kayitlar = {
        "dosya_oku": ({"yol": "string"}, "dosya:oku", False),
        "web_getir": ({"url": "string"}, "ag:get", False),
        "rapor_yaz": ({"baslik": "string", "icerik": "string"}, "dosya:yaz", True),
    }
    if sema["ad"] not in kayitlar:
        raise ValueError("bilinmeyen araç")
    parametreler, yetki, yan_etkili = kayitlar[sema["ad"]]
    if sema["parametreler"] != parametreler:
        raise ValueError("araç parametreleri geçersiz")
    if not isinstance(sema["yetkiler"], list) or sema["yetkiler"] != [yetki]:
        raise ValueError("araç yetkisi geçersiz")
    if type(sema["yan_etkili"]) is not bool or sema["yan_etkili"] is not yan_etkili:
        raise ValueError("yan etki bilgisi geçersiz")
    sure = sema["zaman_asimi_ms"]
    if type(sure) is not int:
        raise ValueError("zaman aşımı int olmalı")
    if sure < 1 or sure > 10000:
        raise ValueError("zaman aşımı aralığı geçersiz")
    return {"ad": sema["ad"], "parametreler": dict(sema["parametreler"]), "yetkiler": list(sema["yetkiler"]), "yan_etkili": sema["yan_etkili"], "zaman_asimi_ms": sure}
```

```hint
Araç adını sabit kayıt tablosunda ara. Parametre sözlüğünü ve tek yetkili listeyi aynen karşılaştır; sonuçta iç içe yapıları ayrı kopyala.
```
:::

::: anlat Şema adı yetmez, argüman değeri de sınırlandırılır
`dosya_oku` aracının `yol` parametresi göreli ve güvenli parçalardan oluşur. Mutlak yol, `..`, boş parça, ters eğik çizgi ve sürücü iki noktası kabul edilmez. `web_getir` yalnız HTTPS ve iki dokümantasyon alan adına gidebilir; kullanıcı bilgisi ve açık port içeren URL reddedilir.

Bu kontroller gerçek dosya veya ağ erişimi yapmaz. Yalnız modelden gelen çağrının uygulama sınırına ulaşmadan önce hangi sözleşmeyi sağlaması gerektiğini sınar.
:::

::: gorev 2 · Araç çağrısını şema ve güvenli argümanlarla doğrula
`arac_cagrisi_dogrula(cagri, sema)` işlevini yaz. Şema ilk görevdeki kuralları sağlasın. Çağrı tam olarak `id`, `arac`, `argumanlar` alanlarını taşısın; araç adı şemayla eşleşmelidir. Kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren stringdir.

Argümanlar şemadaki tam parametre kümesini taşısın ve bütün değerler string olsun. Ek kurallar:

- `yol`: en fazla 200 karakter; `/` ile ayrılmış, boş olmayan parçalar; parçalar `.` veya `..` olamaz ve yalnız ASCII harf, rakam, nokta, alt çizgi veya tire içerebilir. Mutlak yol, `\` ve `:` yasak.
- `url`: yalnız `https`, alan adı `example.test` veya `docs.example.test`; kullanıcı bilgisi ve açık port yok. Boşluk içeremez.
- `baslik`: baş/son boşluğu olmayan 1–100 karakter.
- `icerik`: baş/son boşluğu olmayan 1–5000 karakter.

Geçersiz veride `ValueError` yükselt. Çağrıyı yeni argüman sözlüğüyle kopyalayıp döndür; aracı çalıştırma ve girdileri değiştirme.

```starter
def arac_cagrisi_dogrula(cagri, sema):
    return {}
```

```test
import copy
S = {"ad": "dosya_oku", "parametreler": {"yol": "string"}, "yetkiler": ["dosya:oku"], "yan_etkili": False, "zaman_asimi_ms": 1000}
C = {"id": "cagri-1", "arac": "dosya_oku", "argumanlar": {"yol": "belgeler/ozet.txt"}}
def sozlesme(fn):
    try:
        conce = copy.deepcopy(C)
        sonce = copy.deepcopy(S)
        sonuc = fn(C, S)
        if sonuc != C or C != conce or S != sonce or sonuc["argumanlar"] is C["argumanlar"]:
            return False
        web_sema = {"ad": "web_getir", "parametreler": {"url": "string"}, "yetkiler": ["ag:get"], "yan_etkili": False, "zaman_asimi_ms": 1}
        for url in ("https://example.test/veri", "https://docs.example.test/a?q=1"):
            if fn({"id": "w1", "arac": "web_getir", "argumanlar": {"url": url}}, web_sema)["argumanlar"]["url"] != url:
                return False
        rapor_sema = {"ad": "rapor_yaz", "parametreler": {"baslik": "string", "icerik": "string"}, "yetkiler": ["dosya:yaz"], "yan_etkili": True, "zaman_asimi_ms": 10000}
        rapor = {"id": "r1", "arac": "rapor_yaz", "argumanlar": {"baslik": "a" * 100, "icerik": "b" * 5000}}
        if fn(rapor, rapor_sema) != rapor or fn(dict(C, id="a" * 64, argumanlar={"yol": "a" * 200}), S)["id"] != "a" * 64:
            return False
        for cagri, sema in [
            (None, S), (C, None), (dict(C, ek=1), S), (dict(S, ek=1) and C, dict(S, ek=1)),
            (dict(C, id=""), S), (dict(C, id="a" * 65), S), (dict(C, id="a b"), S),
            (dict(C, arac="web_getir"), S), (dict(C, argumanlar={}), S),
            (dict(C, argumanlar={"yol": "a", "ek": "b"}), S),
            (dict(C, argumanlar={"yol": None}), S), (dict(C, argumanlar={"yol": "a" * 201}), S),
            (dict(C, argumanlar={"yol": "/etc/passwd"}), S),
            (dict(C, argumanlar={"yol": "../a"}), S), (dict(C, argumanlar={"yol": "a/../b"}), S),
            (dict(C, argumanlar={"yol": "a//b"}), S), (dict(C, argumanlar={"yol": "a\\b"}), S),
            (dict(C, argumanlar={"yol": "C:/a"}), S), (dict(C, argumanlar={"yol": "a b"}), S),
            ({"id": "w", "arac": "web_getir", "argumanlar": {"url": "http://example.test/a"}}, web_sema),
            ({"id": "w", "arac": "web_getir", "argumanlar": {"url": "https://evil.test/a"}}, web_sema),
            ({"id": "w", "arac": "web_getir", "argumanlar": {"url": "https://u:p@example.test/a"}}, web_sema),
            ({"id": "w", "arac": "web_getir", "argumanlar": {"url": "https://example.test:443/a"}}, web_sema),
            (dict(rapor, argumanlar={"baslik": "a" * 101, "icerik": "x"}), rapor_sema),
            (dict(rapor, argumanlar={"baslik": "x", "icerik": "a" * 5001}), rapor_sema),
            (dict(rapor, argumanlar={"baslik": " x", "icerik": "x"}), rapor_sema),
        ]:
            try:
                fn(cagri, sema)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(arac_cagrisi_dogrula), "çağrı şeması, güvenli yol, HTTPS izin listesi ve uzunluklar korunmalı")
def m_yol(cagri, sema):
    sonuc = arac_cagrisi_dogrula(cagri, sema)
    sonuc["argumanlar"]["yol"] = "../gizli"
    return sonuc
def m_arac(cagri, sema):
    sonuc = arac_cagrisi_dogrula(cagri, sema)
    sonuc["arac"] = "web_getir"
    return sonuc
def m_kopya(cagri, sema):
    return cagri
for ad, mutant in [("yolu değiştiren", m_yol), ("aracı değiştiren", m_arac), ("kopyalamayan", m_kopya)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def arac_cagrisi_dogrula(cagri, sema):
    import re
    import urllib.parse
    kayitlar = {
        "dosya_oku": ({"yol": "string"}, "dosya:oku", False),
        "web_getir": ({"url": "string"}, "ag:get", False),
        "rapor_yaz": ({"baslik": "string", "icerik": "string"}, "dosya:yaz", True),
    }
    if not isinstance(sema, dict) or set(sema) != {"ad", "parametreler", "yetkiler", "yan_etkili", "zaman_asimi_ms"}:
        raise ValueError("araç şeması geçersiz")
    if sema["ad"] not in kayitlar:
        raise ValueError("bilinmeyen araç")
    parametreler, yetki, yan_etkili = kayitlar[sema["ad"]]
    if sema["parametreler"] != parametreler:
        raise ValueError("araç parametreleri geçersiz")
    if sema["yetkiler"] != [yetki]:
        raise ValueError("araç yetkisi geçersiz")
    if sema["yan_etkili"] is not yan_etkili:
        raise ValueError("yan etki bilgisi geçersiz")
    if type(sema["zaman_asimi_ms"]) is not int:
        raise ValueError("zaman aşımı int olmalı")
    if sema["zaman_asimi_ms"] < 1:
        raise ValueError("zaman aşımı pozitif olmalı")
    if sema["zaman_asimi_ms"] > 10000:
        raise ValueError("zaman aşımı üst sınırı aştı")
    if not isinstance(cagri, dict) or set(cagri) != {"id", "arac", "argumanlar"}:
        raise ValueError("çağrı şeması geçersiz")
    if not isinstance(cagri["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", cagri["id"]):
        raise ValueError("çağrı kimliği geçersiz")
    if cagri["arac"] != sema["ad"]:
        raise ValueError("araç ve şema eşleşmiyor")
    args = cagri["argumanlar"]
    if not isinstance(args, dict) or set(args) != set(parametreler):
        raise ValueError("argüman şeması geçersiz")
    if any(not isinstance(deger, str) for deger in args.values()):
        raise ValueError("argümanlar string olmalı")
    if "yol" in args:
        yol = args["yol"]
        if not yol:
            raise ValueError("dosya yolu boş olamaz")
        if len(yol) > 200:
            raise ValueError("dosya yolu çok uzun")
        if yol.startswith("/"):
            raise ValueError("mutlak yol geçersiz")
        if "\\" in yol:
            raise ValueError("ters eğik çizgi geçersiz")
        if ":" in yol:
            raise ValueError("sürücü yolu geçersiz")
        for parca in yol.split("/"):
            if parca in ("", ".", ".."):
                raise ValueError("dosya parçası geçersiz")
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", parca):
                raise ValueError("dosya parçası geçersiz")
    if "url" in args:
        url = args["url"]
        if any(c.isspace() for c in url):
            raise ValueError("URL boşluk içeremez")
        parca = urllib.parse.urlsplit(url)
        if parca.scheme != "https":
            raise ValueError("yalnız HTTPS kabul edilir")
        if parca.hostname not in ("example.test", "docs.example.test"):
            raise ValueError("alan adı izin listesinde değil")
        if parca.username is not None:
            raise ValueError("URL kullanıcı adı içeremez")
        if parca.password is not None:
            raise ValueError("URL parola içeremez")
        if parca.port is not None:
            raise ValueError("URL açık port içeremez")
    if "baslik" in args:
        baslik = args["baslik"]
        if not baslik:
            raise ValueError("başlık boş olamaz")
        if baslik != baslik.strip():
            raise ValueError("başlık boşluklu olamaz")
        if len(baslik) > 100:
            raise ValueError("başlık çok uzun")
    if "icerik" in args:
        icerik = args["icerik"]
        if not icerik:
            raise ValueError("içerik boş olamaz")
        if icerik != icerik.strip():
            raise ValueError("içerik boşluklu olamaz")
        if len(icerik) > 5000:
            raise ValueError("içerik çok uzun")
    return {"id": cagri["id"], "arac": cagri["arac"], "argumanlar": dict(args)}
```

```hint
Önce şemayı, sonra çağrının araç ve argüman kümesini eşle. URL için `urlsplit` metadata'sını denetle; yol parçalarını ayrı doğrula ve sonucu yeni sözlükle döndür.
```
:::

::: anlat En az ayrıcalık iki yönde denetlenir
Oturumun geniş yetkisi olması, araç çağrısının bütün yetkileri istemesi gerektiği anlamına gelmez. Gerekli yetki istekte yoksa çağrı çalışamaz; fazla yetki varsa en az ayrıcalık bozulur; gerekli yetki oturumda yoksa çağrı yetkilendirilemez. Üç durum da raporda ayrı nedenlerdir.

Bu ders karar için istenen kümenin araç gereksinimine tam eşit olmasını ister. `calistir` kararı yalnız eşitlik ve oturum kapsamı birlikte sağlandığında verilir; yine de bu fixture aracı gerçekten çalıştırmaz.
:::

::: gorev 3 · İstenen ve oturum yetkilerini en az ayrıcalıkla karşılaştır
`yetki_karar_raporu(istekler)` işlevini yaz. Her istek tam olarak `id`, `arac`, `istenen_yetkiler`, `oturum_yetkileri` alanlarını taşısın. Kimlik ikinci görevdeki kurallara uysun ve benzersiz olsun. Araç yalnız üç bilinen araçtır. Yetki listeleri `dosya:oku`, `dosya:yaz`, `ag:get` değerlerinden oluşan yinelenmeyen listelerdir. Geçersiz veride `ValueError` yükselt.

Aracın gerekli yetkisi ilk görevdeki tekil yetkidir. Nedenleri sabit sırayla üret:

- Gerekli yetki istenenlerde yoksa `eksik_istek`.
- İstenen kümede gereksiz yetki varsa `fazla_yetki`.
- Gerekli yetki oturumda yoksa `oturum_yetkisi_yok`.

Hiç neden yoksa `calistir`, aksi hâlde `reddet` kararı ver. Her kayıt için `{"id":ID,"karar":KARAR,"gerekli_yetkiler":[YETKI],"nedenler":[...]}` döndür. Kimliğe göre sırala, boş girdide boş liste döndür ve girdiyi değiştirme.

```starter
def yetki_karar_raporu(istekler):
    return []
```

```test
import copy
I = [
    {"id": "izin-1", "arac": "dosya_oku", "istenen_yetkiler": ["dosya:oku"], "oturum_yetkileri": ["dosya:oku", "dosya:yaz"]},
    {"id": "fazla-1", "arac": "dosya_oku", "istenen_yetkiler": ["dosya:oku", "dosya:yaz"], "oturum_yetkileri": ["dosya:oku", "dosya:yaz"]},
    {"id": "eksik-1", "arac": "web_getir", "istenen_yetkiler": ["dosya:oku"], "oturum_yetkileri": ["dosya:oku"]},
    {"id": "yaz-1", "arac": "rapor_yaz", "istenen_yetkiler": [], "oturum_yetkileri": []},
]
BEKLENEN = [
    {"id": "eksik-1", "karar": "reddet", "gerekli_yetkiler": ["ag:get"], "nedenler": ["eksik_istek", "fazla_yetki", "oturum_yetkisi_yok"]},
    {"id": "fazla-1", "karar": "reddet", "gerekli_yetkiler": ["dosya:oku"], "nedenler": ["fazla_yetki"]},
    {"id": "izin-1", "karar": "calistir", "gerekli_yetkiler": ["dosya:oku"], "nedenler": []},
    {"id": "yaz-1", "karar": "reddet", "gerekli_yetkiler": ["dosya:yaz"], "nedenler": ["eksik_istek", "oturum_yetkisi_yok"]},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(I)
        if fn(I) != BEKLENEN or I != once or fn(list(reversed(I))) != BEKLENEN or fn([]) != []:
            return False
        if fn([dict(I[0], id="a" * 64)])[0]["id"] != "a" * 64:
            return False
        for istekler in [
            None, {}, [None], [dict(I[0], ek=1)], [dict(I[0], id="")],
            [dict(I[0], id="a" * 65)], [dict(I[0], id="a b")], [dict(I[0], arac="diger")],
            [dict(I[0], istenen_yetkiler=None)], [dict(I[0], oturum_yetkileri=None)],
            [dict(I[0], istenen_yetkiler="dosya:oku")],
            [dict(I[0], istenen_yetkiler=["admin"])], [dict(I[0], oturum_yetkileri=["admin"])],
            [dict(I[0], istenen_yetkiler=["dosya:oku", "dosya:oku"])],
            [dict(I[0], oturum_yetkileri=["dosya:oku", "dosya:oku"])], [I[0], I[0]],
        ]:
            try:
                fn(istekler)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(yetki_karar_raporu), "eksik, fazla ve oturum yetkisi nedenleri birlikte korunmalı")
def m_fazla(istekler):
    degisen = [dict(x, istenen_yetkiler=[y for y in x["istenen_yetkiler"] if y != "dosya:yaz"]) for x in istekler]
    return yetki_karar_raporu(degisen)
def m_oturum(istekler):
    degisen = [dict(x, oturum_yetkileri=["dosya:oku", "dosya:yaz", "ag:get"]) for x in istekler]
    return yetki_karar_raporu(degisen)
def m_eksik(istekler):
    degisen = [dict(x, istenen_yetkiler=["dosya:oku"]) for x in istekler]
    return yetki_karar_raporu(degisen)
for ad, mutant in [("fazla yetkiyi silen", m_fazla), ("oturumu genişleten", m_oturum), ("eksik isteği değiştiren", m_eksik)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def yetki_karar_raporu(istekler):
    import re
    if not isinstance(istekler, list):
        raise ValueError("istek listesi geçersiz")
    gerekli = {"dosya_oku": "dosya:oku", "web_getir": "ag:get", "rapor_yaz": "dosya:yaz"}
    izinli = {"dosya:oku", "dosya:yaz", "ag:get"}
    kimlikler = set()
    rapor = []
    for istek in istekler:
        if not isinstance(istek, dict) or set(istek) != {"id", "arac", "istenen_yetkiler", "oturum_yetkileri"}:
            raise ValueError("istek şeması geçersiz")
        kimlik = istek["id"]
        if not isinstance(kimlik, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kimlik geçersiz")
        if kimlik in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kimlik)
        if istek["arac"] not in gerekli:
            raise ValueError("bilinmeyen araç")
        for alan in ("istenen_yetkiler", "oturum_yetkileri"):
            yetkiler = istek[alan]
            if not isinstance(yetkiler, list):
                raise ValueError("yetkiler liste olmalı")
            if len(set(yetkiler)) != len(yetkiler):
                raise ValueError("yetkiler yinelenemez")
            if any(y not in izinli for y in yetkiler):
                raise ValueError("bilinmeyen yetki")
        gereken = gerekli[istek["arac"]]
        istenen = set(istek["istenen_yetkiler"])
        oturum = set(istek["oturum_yetkileri"])
        nedenler = []
        if gereken not in istenen:
            nedenler.append("eksik_istek")
        if istenen - {gereken}:
            nedenler.append("fazla_yetki")
        if gereken not in oturum:
            nedenler.append("oturum_yetkisi_yok")
        rapor.append({"id": kimlik, "karar": "reddet" if nedenler else "calistir", "gerekli_yetkiler": [gereken], "nedenler": nedenler})
    return sorted(rapor, key=lambda x: x["id"])
```

```hint
Her aracın tek gerekli yetkisini sabit eşlemeden al. Üç nedeni bağımsız koşullarla ve sabit sırayla ekle; kararı yalnız nedenler tamamlandıktan sonra ver.
```
:::

::: anlat Doğrulama, modelin çağrısı uygulamaya ulaşmadan çalışır
Araç çağrısı doğrulaması ancak modelin **gerçekten ürettiği** bir çağrı üzerinde çalıştığında anlam kazanır. Son görevde senin `arac_cagrisi_dogrula` işlevin, gerçek yerel modelin dar şemalı bir `dosya_oku` aracıyla ürettiği çağrıları doğrular. Deney iki senaryoda koşar: güvenli göreli bir yol ve modelin bir yol-gezinti dizesini araç argümanına taşıdığı senaryo.

Doğrulama uygulama sınırından **önce** çalışır; araç hiçbir zaman gerçekten dosya okumaz. Güvenli çağrı geçer; gezinti dizesi içeren çağrı reddedilir ve uygulamaya ulaşmaz. Model dizeyi bir belgeden ya da kullanıcıdan almış olsa ve oturumun geniş yetkisi bulunsa bile, en az ayrıcalık argüman düzeyinde uygulanır.
:::

::: gorev Gerçek deney · Gerçek araç çağrısını en az ayrıcalıkla doğrula
`arac_cagrisi_dogrula(cagri, sema)` işlevini yaz — kuralları ve çıktısı 2. görevdekiyle **aynıdır**. Deney gerçek modele `dosya_oku` aracını verir, modelin ürettiği gerçek çağrıları toplar ve senin doğrulayıcın her çağrıyı şema + güvenli-yol kurallarıyla sınar; gezinti dizesi içeren çağrı reddedilir.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def arac_cagrisi_dogrula(cagri, sema):
    return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_11 as deney
    deney.goster(arac_cagrisi_dogrula)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("arac_cagrisi_dogrula")
from sandbox import ai_gercek_ai_savunma_11 as D
S = {"ad": "dosya_oku", "parametreler": {"yol": "string"}, "yetkiler": ["dosya:oku"], "yan_etkili": False, "zaman_asimi_ms": 1000}
C = {"id": "cagri-1", "arac": "dosya_oku", "argumanlar": {"yol": "belgeler/ozet.txt"}}
def sozlesme(f):
    try:
        if f(C, S) != C:
            return False
        for kotu in ({"yol": "../gizli.txt"}, {"yol": "/etc/passwd"}, {"yol": "a\\b"}, {"yol": "c:/x"}):
            try:
                f(dict(C, argumanlar=kotu), S)
                return False
            except ValueError:
                pass
        for bozuk in (None, [], dict(C, ek=1), dict(C, arac="web_getir")):
            try:
                f(bozuk, S)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "şema, araç eşleşmesi ve güvenli yol kuralları korunmalı")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    guvenli = next((a for a in r["akislar"] if a["id"] == "guvenli-1"), {})
    gezinti = next((a for a in r["akislar"] if a["id"] == "gezinti-1"), {})
    kontrol(guvenli.get("cagirdi") and guvenli.get("gecerli") is True, "güvenli gerçek çağrı doğrulandı")
    kontrol(gezinti.get("cagirdi") and gezinti.get("gecerli") is False, "gezinti dizeli gerçek çağrı reddedildi")
    oz = D.ozet(r)
yol = ai_lab.kanit_yaz("savunma-arac", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-11",
                                        "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({r['ortam']['model']['ad']}): modelin gerçek araç çağrıları doğrulandı — "
             f"güvenli yol '{oz['guvenli_yol']}' geçerli; gezinti yolu '{oz['gezinti_yol']}' reddedildi. "
             f"Doğrulama uygulama sınırından önce çalıştı; model dizeyi taşısa bile araç tetiklenmedi (en az ayrıcalık).")
```

```solution
import ai_lab

def arac_cagrisi_dogrula(cagri, sema):
    import re
    import urllib.parse
    kayitlar = {
        "dosya_oku": ({"yol": "string"}, "dosya:oku", False),
        "web_getir": ({"url": "string"}, "ag:get", False),
        "rapor_yaz": ({"baslik": "string", "icerik": "string"}, "dosya:yaz", True),
    }
    if not isinstance(sema, dict) or set(sema) != {"ad", "parametreler", "yetkiler", "yan_etkili", "zaman_asimi_ms"}:
        raise ValueError("araç şeması geçersiz")
    if sema["ad"] not in kayitlar:
        raise ValueError("bilinmeyen araç")
    parametreler, yetki, yan_etkili = kayitlar[sema["ad"]]
    if sema["parametreler"] != parametreler:
        raise ValueError("araç parametreleri geçersiz")
    if sema["yetkiler"] != [yetki]:
        raise ValueError("araç yetkisi geçersiz")
    if sema["yan_etkili"] is not yan_etkili:
        raise ValueError("yan etki bilgisi geçersiz")
    if type(sema["zaman_asimi_ms"]) is not int:
        raise ValueError("zaman aşımı int olmalı")
    if sema["zaman_asimi_ms"] < 1:
        raise ValueError("zaman aşımı pozitif olmalı")
    if sema["zaman_asimi_ms"] > 10000:
        raise ValueError("zaman aşımı üst sınırı aştı")
    if not isinstance(cagri, dict) or set(cagri) != {"id", "arac", "argumanlar"}:
        raise ValueError("çağrı şeması geçersiz")
    if not isinstance(cagri["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", cagri["id"]):
        raise ValueError("çağrı kimliği geçersiz")
    if cagri["arac"] != sema["ad"]:
        raise ValueError("araç ve şema eşleşmiyor")
    args = cagri["argumanlar"]
    if not isinstance(args, dict) or set(args) != set(parametreler):
        raise ValueError("argüman şeması geçersiz")
    if any(not isinstance(deger, str) for deger in args.values()):
        raise ValueError("argümanlar string olmalı")
    if "yol" in args:
        yol = args["yol"]
        if not yol:
            raise ValueError("dosya yolu boş olamaz")
        if len(yol) > 200:
            raise ValueError("dosya yolu çok uzun")
        if yol.startswith("/"):
            raise ValueError("mutlak yol geçersiz")
        if "\\" in yol:
            raise ValueError("ters eğik çizgi geçersiz")
        if ":" in yol:
            raise ValueError("sürücü yolu geçersiz")
        for parca in yol.split("/"):
            if parca in ("", ".", ".."):
                raise ValueError("dosya parçası geçersiz")
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", parca):
                raise ValueError("dosya parçası geçersiz")
    if "url" in args:
        url = args["url"]
        if any(c.isspace() for c in url):
            raise ValueError("URL boşluk içeremez")
        parca = urllib.parse.urlsplit(url)
        if parca.scheme != "https":
            raise ValueError("yalnız HTTPS kabul edilir")
        if parca.hostname not in ("example.test", "docs.example.test"):
            raise ValueError("alan adı izin listesinde değil")
        if parca.username is not None:
            raise ValueError("URL kullanıcı adı içeremez")
        if parca.password is not None:
            raise ValueError("URL parola içeremez")
        if parca.port is not None:
            raise ValueError("URL açık port içeremez")
    if "baslik" in args:
        baslik = args["baslik"]
        if not baslik:
            raise ValueError("başlık boş olamaz")
        if baslik != baslik.strip():
            raise ValueError("başlık boşluklu olamaz")
        if len(baslik) > 100:
            raise ValueError("başlık çok uzun")
    if "icerik" in args:
        icerik = args["icerik"]
        if not icerik:
            raise ValueError("içerik boş olamaz")
        if icerik != icerik.strip():
            raise ValueError("içerik boşluklu olamaz")
        if len(icerik) > 5000:
            raise ValueError("içerik çok uzun")
    return {"id": cagri["id"], "arac": cagri["arac"], "argumanlar": dict(args)}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_11 as deney
    deney.goster(arac_cagrisi_dogrula)
```

```hint
Bu işlev 2. görevdeki `arac_cagrisi_dogrula` ile birebir aynıdır; tek fark, çağrının gerçek model koşusundan gelmesidir. Önce şemayı, sonra çağrı şemasını ve araç eşleşmesini doğrula; yol parçalarını ayrı denetle.
```
:::
