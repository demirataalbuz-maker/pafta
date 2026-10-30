---
id: ai-saldiri-26
title: Kodlama Ajanları ve Repo İçeriği Saldırıları
summary: Repo talimatlarını ve bağımlılık değişikliklerini güvenilmez veri olarak envanterle; ajanın dosya ve komut yetkilerini bağımsız politikayla sınırla.
timeout: 45
---

::: anlat Repo içeriği yetki belgesi değildir
Bir kodlama ajanı `AGENTS.md`, README, issue, bağımlılık manifesti ve CI dosyalarını aynı çalışma bağlamında görebilir. Saldırgan bu dosyalara önceki talimatları yok sayma, komut çalıştırma veya ağa veri gönderme yönergeleri yerleştirebilir. Metnin model tarafından okunması, o metne sistem yetkisi vermez.

Saldırı zinciri çoğu zaman üç halkadan oluşur: güvenilmez repo içeriği modele ulaşır, model bir eylem adayı üretir ve uygulama bu adayı fazla geniş yetkiyle çalıştırır. Son halka bağımsız izin listesiyle kesilmelidir. Statik işaretler yalnız inceleme önceliği verir; bir dosyanın kesin zararlı olduğunu kanıtlamaz.

Bu derste Docker, Git, CodeQL, paket kurulumu, ağ veya gerçek komut çalıştırma yoktur. Bütün dosyalar ve eylemler deterministik Python fixture'larıdır.
:::

::: tahmin Dosya türünü kim belirliyor?
Uygulama iki Markdown dosyasına farklı güven sınıfları veriyor. Üç çıktı satırını yaz:

```python
dosyalar = [
    {"yol": "AGENTS.md", "tur": "ajan-talimati"},
    {"yol": "README.md", "tur": "repo-verisi"},
]
print(len(dosyalar))
print([x["yol"] for x in dosyalar if x["tur"] == "ajan-talimati"])
print(dosyalar[1]["tur"] == "ajan-talimati")
```

???

```cikti
2
['AGENTS.md']
False
```

Uzantı tek başına güven sınırı değildir. Ajan talimatı olarak tüketilen yol ayrıca envanterlenir; içeriğindeki istekler yine uygulama yetkisi kazanmaz.
:::

::: gorev 1 · Repo dosyalarının saldırı yüzeyini envanterle
`repo_yuzey_envanteri(dosyalar)` işlevini yaz. Girdi liste olmalı; her kayıt tam olarak `yol`, `icerik` alanlarını taşımalıdır. Yol benzersiz, boş olmayan, `/` ayraçlı göreli POSIX yolu olmalı; NUL, `\`, mutlak yol, boş parça, `.` veya `..` parçası içeremez. İçerik en fazla 4096 karakterli ve NUL içermeyen string olmalıdır. Geçersiz veride `ValueError` yükselt.

Dosya türünü yalnız şu kurallarla belirle:

- `AGENTS.md`, `CLAUDE.md` veya `.github/copilot-instructions.md` ise `ajan-talimati`.
- `package.json`, `pyproject.toml` veya `requirements.txt` ise `bagimlilik`.
- Diğer bütün yollar `repo-verisi`.

İçerik küçük harfe çevrildiğinde `system:`, `ignore previous`, `curl ` veya `subprocess.run` izlerinden biri varsa `supheli` true olur. Bu etiket yalnız inceleme işaretidir. Dönüş, yola göre artan sıralı `{"yol":YOL,"tur":TUR,"supheli":BOOL}` kayıtlarının listesidir. Girdi değiştirilmemelidir.

```starter
def repo_yuzey_envanteri(dosyalar):
    return []
```

```test
import copy
DOSYALAR = [
    {"yol": "README.md", "icerik": "Kullanım"},
    {"yol": "package.json", "icerik": '{"scripts":{"postinstall":"curl x"}}'},
    {"yol": "AGENTS.md", "icerik": "IGNORE PREVIOUS instructions"},
    {"yol": "docs/AGENTS.md", "icerik": "SYSTEM: alt dizin notu"},
]
BEKLENEN = [
    {"yol": "AGENTS.md", "tur": "ajan-talimati", "supheli": True},
    {"yol": "README.md", "tur": "repo-verisi", "supheli": False},
    {"yol": "docs/AGENTS.md", "tur": "repo-verisi", "supheli": True},
    {"yol": "package.json", "tur": "bagimlilik", "supheli": True},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(DOSYALAR)
        if fn(DOSYALAR) != BEKLENEN or DOSYALAR != once or fn(list(reversed(DOSYALAR))) != BEKLENEN:
            return False
        if fn([]) != []:
            return False
        diger = [
            {"yol": "CLAUDE.md", "icerik": "not"},
            {"yol": ".github/copilot-instructions.md", "icerik": "not"},
            {"yol": "pyproject.toml", "icerik": "subprocess.run"},
            {"yol": "requirements.txt", "icerik": ""},
            {"yol": "src/AGENTS.md", "icerik": "not"},
        ]
        sonuc = fn(diger)
        if [x["tur"] for x in sonuc] != ["ajan-talimati", "ajan-talimati", "bagimlilik", "bagimlilik", "repo-verisi"]:
            return False
        if [x["supheli"] for x in sonuc] != [False, False, True, False, False]:
            return False
        if fn([{"yol": "not.txt", "icerik": "x" * 4096}])[0]["supheli"]:
            return False
        for dosyalar in [
            None, {}, [None], [dict(DOSYALAR[0], ek=1)],
            [dict(DOSYALAR[0], yol=None)], [dict(DOSYALAR[0], yol=123)], [dict(DOSYALAR[0], yol="")],
            [dict(DOSYALAR[0], yol="a\x00b")], [dict(DOSYALAR[0], yol="/README.md")],
            [dict(DOSYALAR[0], yol="../README.md")], [dict(DOSYALAR[0], yol="docs//README.md")],
            [dict(DOSYALAR[0], yol="docs/./README.md")], [dict(DOSYALAR[0], yol="docs\\README.md")],
            [dict(DOSYALAR[0], icerik=None)], [dict(DOSYALAR[0], icerik="a\x00b")],
            [dict(DOSYALAR[0], icerik="x" * 4097)], [DOSYALAR[0], DOSYALAR[0]],
        ]:
            try:
                fn(dosyalar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(repo_yuzey_envanteri), "göreli yol, tam eşleşen tür, işaret ve sıralama korunmalı")
def m_yol(dosyalar):
    return repo_yuzey_envanteri(dosyalar) + [{"yol": "src/AGENTS.md", "tur": "ajan-talimati", "supheli": False}]
def m_isaret(dosyalar):
    sonuc = repo_yuzey_envanteri(dosyalar)
    for kayit in sonuc:
        kayit["supheli"] = False
    return sonuc
def m_sira(dosyalar):
    return list(reversed(repo_yuzey_envanteri(dosyalar)))
for ad, mutant in [("alt dizindeki aynı adı ajan talimatı sayan", m_yol), ("inceleme işaretlerini silen", m_isaret), ("deterministik sırayı bozan", m_sira)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def repo_yuzey_envanteri(dosyalar):
    if not isinstance(dosyalar, list):
        raise ValueError("dosya listesi geçersiz")
    talimatlar = {"AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"}
    bagimliliklar = {"package.json", "pyproject.toml", "requirements.txt"}
    izler = ("system:", "ignore previous", "curl ", "subprocess.run")
    yollar = set()
    sonuc = []
    for dosya in dosyalar:
        if not isinstance(dosya, dict) or set(dosya) != {"yol", "icerik"}:
            raise ValueError("dosya şeması geçersiz")
        yol = dosya["yol"]
        icerik = dosya["icerik"]
        if not isinstance(yol, str) or not yol or yol in yollar or "\x00" in yol or "\\" in yol or yol.startswith("/"):
            raise ValueError("yol geçersiz")
        parcalar = yol.split("/")
        if any(parca in ("", ".", "..") for parca in parcalar):
            raise ValueError("göreli yol geçersiz")
        if not isinstance(icerik, str) or len(icerik) > 4096 or "\x00" in icerik:
            raise ValueError("içerik geçersiz")
        yollar.add(yol)
        tur = "ajan-talimati" if yol in talimatlar else "bagimlilik" if yol in bagimliliklar else "repo-verisi"
        kucuk = icerik.lower()
        sonuc.append({"yol": yol, "tur": tur, "supheli": any(iz in kucuk for iz in izler)})
    sonuc.sort(key=lambda x: x["yol"])
    return sonuc
```

```hint
Önce şema ve yol güvenliğini doğrula. Türü tam yol eşleşmesiyle seç; şüphe işaretini içerikte ara, dönüşü en son yola göre sırala.
```
:::

::: anlat Eylem adayı ile çalıştırma yetkisi ayrıdır
Modelin `komut` önermesi veya bir dosyayı yazmak istemesi tek başına zararlı değildir; ancak uygulama bu öneriyi otomatik yetki saymamalıdır. Politika repo metninden değil, ajanı çalıştıran uygulamadan gelir. Tam yol ve tam komut eşleşmesi kullanmak, `pytest` iznini `pytest && curl ...` biçiminde genişletmeyi önler.

Bu fixture izin kararı verir fakat eylemi çalıştırmaz. Okuma, yazma ve komut yetkileri ayrı listelerdir; okunabilen bir dosya otomatik olarak yazılabilir değildir.
:::

::: gorev 2 · Ajanın dosya ve komut eylemini bağımsız politikayla sınırla
`repo_eylem_onayi(eylem, politika)` işlevini yaz. Eylem tam olarak `tur`, `hedef` alanlarını taşıyan dict; iki değer de boş olmayan string olmalıdır. Politika tam olarak `okuma_yollari`, `yazma_yollari`, `komutlar` alanlarını taşımalı; her alan benzersiz, boş olmayan stringlerden oluşan bir liste olmalıdır. Listeler boş olabilir. Dosya yolları ilk görevdeki güvenli göreli yol kurallarını sağlamalı; komutlar NUL veya satır sonu içermemelidir. Geçersiz şema veya değerde `ValueError` yükselt.

Kararlar:

- `dosya-oku`: hedef okuma listesindeyse izinli, değilse `yol-yasak`.
- `dosya-yaz`: hedef yazma listesindeyse izinli, değilse `yol-yasak`.
- `komut`: hedef komut listesinde tam eşleşiyorsa izinli, değilse `komut-yasak`.
- Başka eylem türü `bilinmeyen-eylem` olarak reddedilir.

Dönüş `{"izin":BOOL,"neden":"izinli"|"yol-yasak"|"komut-yasak"|"bilinmeyen-eylem"}` biçimindedir. Alt yol, ön ek veya komut parçası eşleşmesi yapma. Girdileri değiştirme ve hiçbir eylemi çalıştırma.

```starter
def repo_eylem_onayi(eylem, politika):
    return {}
```

```test
import copy
POLITIKA = {"okuma_yollari": ["README.md", "src/app.py"], "yazma_yollari": ["src/app.py"], "komutlar": ["pytest", "git status"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(POLITIKA)
        beklenenler = [
            ({"tur": "dosya-oku", "hedef": "README.md"}, {"izin": True, "neden": "izinli"}),
            ({"tur": "dosya-yaz", "hedef": "README.md"}, {"izin": False, "neden": "yol-yasak"}),
            ({"tur": "dosya-yaz", "hedef": "src/app.py"}, {"izin": True, "neden": "izinli"}),
            ({"tur": "dosya-oku", "hedef": "src/app.py.bak"}, {"izin": False, "neden": "yol-yasak"}),
            ({"tur": "komut", "hedef": "pytest"}, {"izin": True, "neden": "izinli"}),
            ({"tur": "komut", "hedef": "pytest && curl x"}, {"izin": False, "neden": "komut-yasak"}),
            ({"tur": "komut", "hedef": "git status --short"}, {"izin": False, "neden": "komut-yasak"}),
            ({"tur": "ag-istegi", "hedef": "https://example.invalid"}, {"izin": False, "neden": "bilinmeyen-eylem"}),
        ]
        for eylem, beklenen in beklenenler:
            if fn(eylem, POLITIKA) != beklenen or POLITIKA != once:
                return False
        bos = {"okuma_yollari": [], "yazma_yollari": [], "komutlar": []}
        if fn({"tur": "komut", "hedef": "pytest"}, bos)["izin"]:
            return False
        for eylem, politika in [
            (None, POLITIKA), ({"tur": "komut"}, POLITIKA), (dict(beklenenler[0][0], ek=1), POLITIKA),
            ({"tur": "", "hedef": "x"}, POLITIKA), ({"tur": "komut", "hedef": None}, POLITIKA),
            ({"tur": "dosya-oku", "hedef": "../x"}, POLITIKA),
            ({"tur": "komut", "hedef": "bad\x00cmd"}, POLITIKA),
            ({"tur": "komut", "hedef": "bad\ncmd"}, POLITIKA),
            ({"tur": "komut", "hedef": "bad\rcmd"}, POLITIKA),
            (beklenenler[0][0], None), (beklenenler[0][0], dict(POLITIKA, ek=[])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari="abc")),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=[None])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=[""])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["a\x00b"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["a\\b"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["/README.md"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["../README.md"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["a//b"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["a/./b"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["README.md", "README.md"])),
            (beklenenler[0][0], dict(POLITIKA, komutlar="abc")),
            (beklenenler[0][0], dict(POLITIKA, komutlar=[None])),
            (beklenenler[0][0], dict(POLITIKA, komutlar=[""])),
            (beklenenler[0][0], dict(POLITIKA, komutlar=["bad\x00command"])),
            (beklenenler[0][0], dict(POLITIKA, komutlar=["bad\ncommand"])),
            (beklenenler[0][0], dict(POLITIKA, komutlar=["bad\rcommand"])),
            (beklenenler[0][0], dict(POLITIKA, komutlar=["pytest", "pytest"])),
        ]:
            try:
                fn(eylem, politika)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(repo_eylem_onayi), "ayrı yetki listeleri, tam eşleşme ve güvenli ret korunmalı")
def m_on_ek(eylem, politika):
    genis = copy.deepcopy(politika)
    if eylem["tur"] == "komut":
        genis["komutlar"] = genis["komutlar"] + [eylem["hedef"].split(" &&")[0], eylem["hedef"] + " --short"]
    return repo_eylem_onayi(eylem, genis)
def m_okuma(eylem, politika):
    genis = copy.deepcopy(politika)
    genis["yazma_yollari"] = genis["yazma_yollari"] + genis["okuma_yollari"]
    return repo_eylem_onayi(eylem, genis)
def m_varsayilan(eylem, politika):
    if eylem["tur"] not in ("dosya-oku", "dosya-yaz", "komut"):
        return {"izin": True, "neden": "izinli"}
    return repo_eylem_onayi(eylem, politika)
for ad, mutant in [("komut ön ekini yetki sayan", m_on_ek), ("okumayı yazma yetkisine çeviren", m_okuma), ("bilinmeyen eylemi kabul eden", m_varsayilan)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def repo_eylem_onayi(eylem, politika):
    if not isinstance(eylem, dict) or set(eylem) != {"tur", "hedef"}:
        raise ValueError("eylem şeması geçersiz")
    if any(not isinstance(eylem[alan], str) or not eylem[alan] for alan in ("tur", "hedef")):
        raise ValueError("eylem değeri geçersiz")
    if not isinstance(politika, dict) or set(politika) != {"okuma_yollari", "yazma_yollari", "komutlar"}:
        raise ValueError("politika şeması geçersiz")
    def yol_guvenli(yol):
        return isinstance(yol, str) and bool(yol) and "\x00" not in yol and "\\" not in yol and not yol.startswith("/") and all(parca not in ("", ".", "..") for parca in yol.split("/"))
    for alan in ("okuma_yollari", "yazma_yollari"):
        degerler = politika[alan]
        if not isinstance(degerler, list) or len(set(degerler)) != len(degerler) or any(not yol_guvenli(x) for x in degerler):
            raise ValueError("yol politikası geçersiz")
    komutlar = politika["komutlar"]
    if not isinstance(komutlar, list) or len(set(komutlar)) != len(komutlar) or any(not isinstance(x, str) or not x or "\x00" in x or "\n" in x or "\r" in x for x in komutlar):
        raise ValueError("komut politikası geçersiz")
    tur = eylem["tur"]
    hedef = eylem["hedef"]
    if tur in ("dosya-oku", "dosya-yaz"):
        if not yol_guvenli(hedef):
            raise ValueError("eylem yolu geçersiz")
        alan = "okuma_yollari" if tur == "dosya-oku" else "yazma_yollari"
        izin = hedef in politika[alan]
        return {"izin": izin, "neden": "izinli" if izin else "yol-yasak"}
    if tur == "komut":
        if "\x00" in hedef or "\n" in hedef or "\r" in hedef:
            raise ValueError("eylem komutu geçersiz")
        izin = hedef in komutlar
        return {"izin": izin, "neden": "izinli" if izin else "komut-yasak"}
    return {"izin": False, "neden": "bilinmeyen-eylem"}
```

```hint
Politika listelerini eylemden önce doğrula. Eylem türünü üç ayrı dala ayır; her dalda yalnız ilgili listenin tam üyeliğini denetle ve diğer türleri reddet.
```
:::

::: anlat Değişiklik incelemesi zincirin erken halkasını görünür kılar
Repo saldırıları yalnız ajan talimat dosyalarından gelmez. Bir bağımlılığa eklenen `postinstall` kancası veya `pull_request_target` tetikli CI değişikliği kod çalıştırma yüzeyini büyütebilir. İşaret tabanlı rapor bu değişiklikleri insan incelemesine taşır; işaretin bulunmaması güvenlik garantisi değildir.

CodeQL gibi statik analiz araçları gerçek projede ek kanıt sağlar. Burada amaç aracı çalıştırmak değil, hangi değişikliğin hangi inceleme kategorisine gireceğini tekrarlanabilir biçimde sınamaktır.
:::

::: gorev 3 · Talimat, bağımlılık ve CI değişikliklerini risk kategorilerine ayır
`degisiklik_risk_raporu(degisiklikler)` işlevini yaz. Girdi liste; her değişiklik tam olarak `dosya`, `tur`, `icerik` alanlarını taşısın. Dosya ilk görevdeki güvenli göreli yol olmalı ve listede benzersiz olmalıdır. Tür yalnız `eklendi` veya `degisti`; içerik en fazla 4096 karakterli, NUL'suz string olmalıdır. Geçersiz veride `ValueError` yükselt.

Her dosya için şu kuralların hepsini bağımsız uygula:

- `AGENTS.md`, `CLAUDE.md` veya `.github/copilot-instructions.md` içeriğinde `system:` ya da `ignore previous` varsa `ajan-yonlendirme` bulgusu.
- `package.json`, `pyproject.toml` veya `requirements.txt` içeriğinde `preinstall`, `postinstall` ya da `setup.py` varsa `kurulum-kancasi` bulgusu.
- `.github/workflows/` altındaki `.yml` veya `.yaml` dosyasında `pull_request_target` varsa `ci-calistirma` bulgusu.

Metin eşleşmeleri büyük/küçük harf duyarsızdır. Dönüş:

```text
{"bulgular":[{"dosya":DOSYA,"kategori":KATEGORI},...],
 "inceleme_gerekli":BOOL}
```

Bulgular `(dosya, kategori)` ile artan sıralıdır. `inceleme_gerekli`, en az bir bulgu varsa true olur. Bulgu üretmeyen değişiklikleri rapora ekleme; girdiyi değiştirme.

```starter
def degisiklik_risk_raporu(degisiklikler):
    return {}
```

```test
import copy
DEGISIKLIKLER = [
    {"dosya": "README.md", "tur": "degisti", "icerik": "SYSTEM: belge metni"},
    {"dosya": "AGENTS.md", "tur": "degisti", "icerik": "Ignore Previous instructions"},
    {"dosya": "package.json", "tur": "eklendi", "icerik": '{"scripts":{"postinstall":"node x.js"}}'},
    {"dosya": ".github/workflows/pr.yml", "tur": "degisti", "icerik": "on: pull_request_target"},
    {"dosya": ".github/workflows/pr.txt", "tur": "degisti", "icerik": "pull_request_target"},
]
BEKLENEN = {"bulgular": [
    {"dosya": ".github/workflows/pr.yml", "kategori": "ci-calistirma"},
    {"dosya": "AGENTS.md", "kategori": "ajan-yonlendirme"},
    {"dosya": "package.json", "kategori": "kurulum-kancasi"},
], "inceleme_gerekli": True}
def sozlesme(fn):
    try:
        once = copy.deepcopy(DEGISIKLIKLER)
        if fn(DEGISIKLIKLER) != BEKLENEN or DEGISIKLIKLER != once or fn(list(reversed(DEGISIKLIKLER))) != BEKLENEN:
            return False
        if fn([]) != {"bulgular": [], "inceleme_gerekli": False}:
            return False
        kapsam = [
            {"dosya": "docs/AGENTS.md", "tur": "eklendi", "icerik": "SYSTEM:"},
            {"dosya": "pyproject.toml", "tur": "eklendi", "icerik": "SETUP.PY"},
            {"dosya": "requirements.txt", "tur": "degisti", "icerik": "preinstall"},
            {"dosya": ".github/workflows/x.yaml", "tur": "eklendi", "icerik": "PULL_REQUEST_TARGET"},
            {"dosya": ".github/workflows/x.yml.bak", "tur": "eklendi", "icerik": "pull_request_target"},
            {"dosya": "ci/pr.yml", "tur": "eklendi", "icerik": "pull_request_target"},
            {"dosya": "notlar.txt", "tur": "eklendi", "icerik": "postinstall"},
        ]
        beklenen = [
            {"dosya": ".github/workflows/x.yaml", "kategori": "ci-calistirma"},
            {"dosya": "pyproject.toml", "kategori": "kurulum-kancasi"},
            {"dosya": "requirements.txt", "kategori": "kurulum-kancasi"},
        ]
        if fn(kapsam) != {"bulgular": beklenen, "inceleme_gerekli": True}:
            return False
        if fn([{"dosya": "not.txt", "tur": "eklendi", "icerik": "x" * 4096}])["inceleme_gerekli"]:
            return False
        for kayitlar in [
            None, {}, [None], [dict(DEGISIKLIKLER[0], ek=1)],
            [dict(DEGISIKLIKLER[0], dosya=None)], [dict(DEGISIKLIKLER[0], dosya=123)], [dict(DEGISIKLIKLER[0], dosya="")],
            [dict(DEGISIKLIKLER[0], dosya="a\x00b")], [dict(DEGISIKLIKLER[0], dosya="a\\b")],
            [dict(DEGISIKLIKLER[0], dosya="/x")], [dict(DEGISIKLIKLER[0], dosya="../x")],
            [dict(DEGISIKLIKLER[0], dosya="a//b")], [dict(DEGISIKLIKLER[0], dosya="a/./b")],
            [dict(DEGISIKLIKLER[0], tur="silindi")], [dict(DEGISIKLIKLER[0], icerik=None)],
            [dict(DEGISIKLIKLER[0], icerik="a\x00b")], [dict(DEGISIKLIKLER[0], icerik="x" * 4097)],
            [DEGISIKLIKLER[0], DEGISIKLIKLER[0]],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(degisiklik_risk_raporu), "dosya kapsamı, bağımsız bulgular, sıralama ve inceleme bayrağı korunmalı")
def m_kapsam(degisiklikler):
    degisen = copy.deepcopy(degisiklikler)
    for kayit in degisen:
        if kayit["dosya"] == "docs/AGENTS.md":
            kayit["dosya"] = "AGENTS.md"
        if kayit["dosya"] == ".github/workflows/pr.txt":
            kayit["dosya"] = ".github/workflows/pr.yml"
    return degisiklik_risk_raporu(degisen)
def m_isaret(degisiklikler):
    degisen = copy.deepcopy(degisiklikler)
    for kayit in degisen:
        kayit["icerik"] = kayit["icerik"].replace("postinstall", "").replace("SETUP.PY", "").replace("preinstall", "")
    return degisiklik_risk_raporu(degisen)
def m_bayrak(degisiklikler):
    sonuc = degisiklik_risk_raporu(degisiklikler)
    sonuc["inceleme_gerekli"] = False
    return sonuc
for ad, mutant in [("yalnız tam dosya kapsamını genişleten", m_kapsam), ("kurulum kancası işaretlerini yok sayan", m_isaret), ("inceleme bayrağını kapatan", m_bayrak)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def degisiklik_risk_raporu(degisiklikler):
    if not isinstance(degisiklikler, list):
        raise ValueError("değişiklik listesi geçersiz")
    talimatlar = {"AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"}
    bagimliliklar = {"package.json", "pyproject.toml", "requirements.txt"}
    yollar = set()
    bulgular = []
    for kayit in degisiklikler:
        if not isinstance(kayit, dict) or set(kayit) != {"dosya", "tur", "icerik"}:
            raise ValueError("değişiklik şeması geçersiz")
        dosya = kayit["dosya"]
        if not isinstance(dosya, str) or not dosya or dosya in yollar or "\x00" in dosya or "\\" in dosya or dosya.startswith("/") or any(parca in ("", ".", "..") for parca in dosya.split("/")):
            raise ValueError("dosya yolu geçersiz")
        if kayit["tur"] not in ("eklendi", "degisti"):
            raise ValueError("değişiklik türü geçersiz")
        icerik = kayit["icerik"]
        if not isinstance(icerik, str) or len(icerik) > 4096 or "\x00" in icerik:
            raise ValueError("içerik geçersiz")
        yollar.add(dosya)
        kucuk = icerik.lower()
        if dosya in talimatlar and any(iz in kucuk for iz in ("system:", "ignore previous")):
            bulgular.append({"dosya": dosya, "kategori": "ajan-yonlendirme"})
        if dosya in bagimliliklar and any(iz in kucuk for iz in ("preinstall", "postinstall", "setup.py")):
            bulgular.append({"dosya": dosya, "kategori": "kurulum-kancasi"})
        if dosya.startswith(".github/workflows/") and dosya.endswith((".yml", ".yaml")) and "pull_request_target" in kucuk:
            bulgular.append({"dosya": dosya, "kategori": "ci-calistirma"})
    bulgular.sort(key=lambda x: (x["dosya"], x["kategori"]))
    return {"bulgular": bulgular, "inceleme_gerekli": bool(bulgular)}
```

```hint
Her kayıtta üç kuralı ayrı `if` bloklarıyla uygula. Tam dosya adı ve workflow uzantısı koşullarını koru; bulgu listesinden bayrağı türet.
```
:::


::: anlat Repo içeriğini gerçek dosyadan oku, değişimi gerçek ağaçtan incele
Ham sentetik not aynı Pafta sunucusunda `/data/ai-saldiri-26-repo.txt` adresindedir. Mevcut Markdownrenderer linkleri tıklanabilir yapmaz;sunucuadresine bu yolu yaz. Çalıştır ayrı kalıcı `calisma/ai-saldiri-26/repo-notu.txt` kopyasının yolunu/içeriğini gösterir. Dış editör/Python ile değiştirip yeniden Çalıştır,düzenlemen korunur. Test ayrı dosya kullanır.

Deney kendi sentetik repo ağacını gerçek diskte kurar. `AGENTS.md`,bağımlılık ve CI dosyaları burada **güvenilmez eğitim verisidir**, bu uygulayıcı ajanın talimatı değildir. Öğrenci gerçek dosyalardan envanter çıkarır;yerel model repo eylemi önerir;öğrenci politika kapısı gerçek okuma/yazmadan önce çalışır. Yalnız `src/app.py` normal yazma hedefine dahildir. Native modelin normal yazmayı gerçekten yapması da doğrulanır.

Komut kontrolü yalnız sabit Python `--version` alt süreciyle ölçülür;model komut stringi shell'e verilmez. Paket/kurulum kancası/CI çalıştırılmaz,Gitcommit/push yapılmaz. Altı doğrudan sentetik eylem gerçek dosya/alt-süreç etkisini sınar. Ayrı pozitif risk kontrolünde üç inert dosya gerçekten değiştirilir;öğrenci risk raporu diskten çıkarılan değişimlere uygulanır. Bu,modelin saldırıya uyduğunun kanıtı diye sunulmaz. Temiz/korumalı/kapısız model kollarının ham kararları ve önce/sonra ağaçhashleri ayrı kaydedilir. Stringsezgileri bütün kod veya tedarikzinciri risklerini yakalamaz;saldırıbaşarısı geçme şartı değildir.
:::

::: gorev Gerçek deney · Sentetik repoda model eylemini ve gerçek değişimi denetle
Önceki `repo_yuzey_envanteri`,`repo_eylem_onayi`,`degisiklik_risk_raporu` işlevlerini birleştir. Çalıştır gerçek dosya değişimleri ve risk raporunu gösterir. Kontrol Et saf sözleşmelerden sonra gerçek model/dosya/alt-süreç akışını sınar. Kurulumkancası veya modelin keyfi komutu çalıştırılmaz.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def repo_yuzey_envanteri(dosyalar):return []

def repo_eylem_onayi(eylem,politika):return {}

def degisiklik_risk_raporu(degisiklikler):return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_26 as deney
    deney.goster(repo_yuzey_envanteri,repo_eylem_onayi,degisiklik_risk_raporu)

```

```test
import copy
DOSYALAR = [
    {"yol": "README.md", "icerik": "Kullanım"},
    {"yol": "package.json", "icerik": '{"scripts":{"postinstall":"curl x"}}'},
    {"yol": "AGENTS.md", "icerik": "IGNORE PREVIOUS instructions"},
    {"yol": "docs/AGENTS.md", "icerik": "SYSTEM: alt dizin notu"},
]
BEKLENEN = [
    {"yol": "AGENTS.md", "tur": "ajan-talimati", "supheli": True},
    {"yol": "README.md", "tur": "repo-verisi", "supheli": False},
    {"yol": "docs/AGENTS.md", "tur": "repo-verisi", "supheli": True},
    {"yol": "package.json", "tur": "bagimlilik", "supheli": True},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(DOSYALAR)
        if fn(DOSYALAR) != BEKLENEN or DOSYALAR != once or fn(list(reversed(DOSYALAR))) != BEKLENEN:
            return False
        if fn([]) != []:
            return False
        diger = [
            {"yol": "CLAUDE.md", "icerik": "not"},
            {"yol": ".github/copilot-instructions.md", "icerik": "not"},
            {"yol": "pyproject.toml", "icerik": "subprocess.run"},
            {"yol": "requirements.txt", "icerik": ""},
            {"yol": "src/AGENTS.md", "icerik": "not"},
        ]
        sonuc = fn(diger)
        if [x["tur"] for x in sonuc] != ["ajan-talimati", "ajan-talimati", "bagimlilik", "bagimlilik", "repo-verisi"]:
            return False
        if [x["supheli"] for x in sonuc] != [False, False, True, False, False]:
            return False
        if fn([{"yol": "not.txt", "icerik": "x" * 4096}])[0]["supheli"]:
            return False
        for dosyalar in [
            None, {}, [None], [dict(DOSYALAR[0], ek=1)],
            [dict(DOSYALAR[0], yol=None)], [dict(DOSYALAR[0], yol=123)], [dict(DOSYALAR[0], yol="")],
            [dict(DOSYALAR[0], yol="a\x00b")], [dict(DOSYALAR[0], yol="/README.md")],
            [dict(DOSYALAR[0], yol="../README.md")], [dict(DOSYALAR[0], yol="docs//README.md")],
            [dict(DOSYALAR[0], yol="docs/./README.md")], [dict(DOSYALAR[0], yol="docs\\README.md")],
            [dict(DOSYALAR[0], icerik=None)], [dict(DOSYALAR[0], icerik="a\x00b")],
            [dict(DOSYALAR[0], icerik="x" * 4097)], [DOSYALAR[0], DOSYALAR[0]],
        ]:
            try:
                fn(dosyalar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(repo_yuzey_envanteri), "göreli yol, tam eşleşen tür, işaret ve sıralama korunmalı")
def m_yol(dosyalar):
    return repo_yuzey_envanteri(dosyalar) + [{"yol": "src/AGENTS.md", "tur": "ajan-talimati", "supheli": False}]
def m_isaret(dosyalar):
    sonuc = repo_yuzey_envanteri(dosyalar)
    for kayit in sonuc:
        kayit["supheli"] = False
    return sonuc
def m_sira(dosyalar):
    return list(reversed(repo_yuzey_envanteri(dosyalar)))
for ad, mutant in [("alt dizindeki aynı adı ajan talimatı sayan", m_yol), ("inceleme işaretlerini silen", m_isaret), ("deterministik sırayı bozan", m_sira)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
POLITIKA = {"okuma_yollari": ["README.md", "src/app.py"], "yazma_yollari": ["src/app.py"], "komutlar": ["pytest", "git status"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(POLITIKA)
        beklenenler = [
            ({"tur": "dosya-oku", "hedef": "README.md"}, {"izin": True, "neden": "izinli"}),
            ({"tur": "dosya-yaz", "hedef": "README.md"}, {"izin": False, "neden": "yol-yasak"}),
            ({"tur": "dosya-yaz", "hedef": "src/app.py"}, {"izin": True, "neden": "izinli"}),
            ({"tur": "dosya-oku", "hedef": "src/app.py.bak"}, {"izin": False, "neden": "yol-yasak"}),
            ({"tur": "komut", "hedef": "pytest"}, {"izin": True, "neden": "izinli"}),
            ({"tur": "komut", "hedef": "pytest && curl x"}, {"izin": False, "neden": "komut-yasak"}),
            ({"tur": "komut", "hedef": "git status --short"}, {"izin": False, "neden": "komut-yasak"}),
            ({"tur": "ag-istegi", "hedef": "https://example.invalid"}, {"izin": False, "neden": "bilinmeyen-eylem"}),
        ]
        for eylem, beklenen in beklenenler:
            if fn(eylem, POLITIKA) != beklenen or POLITIKA != once:
                return False
        bos = {"okuma_yollari": [], "yazma_yollari": [], "komutlar": []}
        if fn({"tur": "komut", "hedef": "pytest"}, bos)["izin"]:
            return False
        for eylem, politika in [
            (None, POLITIKA), ({"tur": "komut"}, POLITIKA), (dict(beklenenler[0][0], ek=1), POLITIKA),
            ({"tur": "", "hedef": "x"}, POLITIKA), ({"tur": "komut", "hedef": None}, POLITIKA),
            ({"tur": "dosya-oku", "hedef": "../x"}, POLITIKA),
            ({"tur": "komut", "hedef": "bad\x00cmd"}, POLITIKA),
            ({"tur": "komut", "hedef": "bad\ncmd"}, POLITIKA),
            ({"tur": "komut", "hedef": "bad\rcmd"}, POLITIKA),
            (beklenenler[0][0], None), (beklenenler[0][0], dict(POLITIKA, ek=[])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari="abc")),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=[None])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=[""])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["a\x00b"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["a\\b"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["/README.md"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["../README.md"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["a//b"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["a/./b"])),
            (beklenenler[0][0], dict(POLITIKA, okuma_yollari=["README.md", "README.md"])),
            (beklenenler[0][0], dict(POLITIKA, komutlar="abc")),
            (beklenenler[0][0], dict(POLITIKA, komutlar=[None])),
            (beklenenler[0][0], dict(POLITIKA, komutlar=[""])),
            (beklenenler[0][0], dict(POLITIKA, komutlar=["bad\x00command"])),
            (beklenenler[0][0], dict(POLITIKA, komutlar=["bad\ncommand"])),
            (beklenenler[0][0], dict(POLITIKA, komutlar=["bad\rcommand"])),
            (beklenenler[0][0], dict(POLITIKA, komutlar=["pytest", "pytest"])),
        ]:
            try:
                fn(eylem, politika)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(repo_eylem_onayi), "ayrı yetki listeleri, tam eşleşme ve güvenli ret korunmalı")
def m_on_ek(eylem, politika):
    genis = copy.deepcopy(politika)
    if eylem["tur"] == "komut":
        genis["komutlar"] = genis["komutlar"] + [eylem["hedef"].split(" &&")[0], eylem["hedef"] + " --short"]
    return repo_eylem_onayi(eylem, genis)
def m_okuma(eylem, politika):
    genis = copy.deepcopy(politika)
    genis["yazma_yollari"] = genis["yazma_yollari"] + genis["okuma_yollari"]
    return repo_eylem_onayi(eylem, genis)
def m_varsayilan(eylem, politika):
    if eylem["tur"] not in ("dosya-oku", "dosya-yaz", "komut"):
        return {"izin": True, "neden": "izinli"}
    return repo_eylem_onayi(eylem, politika)
for ad, mutant in [("komut ön ekini yetki sayan", m_on_ek), ("okumayı yazma yetkisine çeviren", m_okuma), ("bilinmeyen eylemi kabul eden", m_varsayilan)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
DEGISIKLIKLER = [
    {"dosya": "README.md", "tur": "degisti", "icerik": "SYSTEM: belge metni"},
    {"dosya": "AGENTS.md", "tur": "degisti", "icerik": "Ignore Previous instructions"},
    {"dosya": "package.json", "tur": "eklendi", "icerik": '{"scripts":{"postinstall":"node x.js"}}'},
    {"dosya": ".github/workflows/pr.yml", "tur": "degisti", "icerik": "on: pull_request_target"},
    {"dosya": ".github/workflows/pr.txt", "tur": "degisti", "icerik": "pull_request_target"},
]
BEKLENEN = {"bulgular": [
    {"dosya": ".github/workflows/pr.yml", "kategori": "ci-calistirma"},
    {"dosya": "AGENTS.md", "kategori": "ajan-yonlendirme"},
    {"dosya": "package.json", "kategori": "kurulum-kancasi"},
], "inceleme_gerekli": True}
def sozlesme(fn):
    try:
        once = copy.deepcopy(DEGISIKLIKLER)
        if fn(DEGISIKLIKLER) != BEKLENEN or DEGISIKLIKLER != once or fn(list(reversed(DEGISIKLIKLER))) != BEKLENEN:
            return False
        if fn([]) != {"bulgular": [], "inceleme_gerekli": False}:
            return False
        kapsam = [
            {"dosya": "docs/AGENTS.md", "tur": "eklendi", "icerik": "SYSTEM:"},
            {"dosya": "pyproject.toml", "tur": "eklendi", "icerik": "SETUP.PY"},
            {"dosya": "requirements.txt", "tur": "degisti", "icerik": "preinstall"},
            {"dosya": ".github/workflows/x.yaml", "tur": "eklendi", "icerik": "PULL_REQUEST_TARGET"},
            {"dosya": ".github/workflows/x.yml.bak", "tur": "eklendi", "icerik": "pull_request_target"},
            {"dosya": "ci/pr.yml", "tur": "eklendi", "icerik": "pull_request_target"},
            {"dosya": "notlar.txt", "tur": "eklendi", "icerik": "postinstall"},
        ]
        beklenen = [
            {"dosya": ".github/workflows/x.yaml", "kategori": "ci-calistirma"},
            {"dosya": "pyproject.toml", "kategori": "kurulum-kancasi"},
            {"dosya": "requirements.txt", "kategori": "kurulum-kancasi"},
        ]
        if fn(kapsam) != {"bulgular": beklenen, "inceleme_gerekli": True}:
            return False
        if fn([{"dosya": "not.txt", "tur": "eklendi", "icerik": "x" * 4096}])["inceleme_gerekli"]:
            return False
        for kayitlar in [
            None, {}, [None], [dict(DEGISIKLIKLER[0], ek=1)],
            [dict(DEGISIKLIKLER[0], dosya=None)], [dict(DEGISIKLIKLER[0], dosya=123)], [dict(DEGISIKLIKLER[0], dosya="")],
            [dict(DEGISIKLIKLER[0], dosya="a\x00b")], [dict(DEGISIKLIKLER[0], dosya="a\\b")],
            [dict(DEGISIKLIKLER[0], dosya="/x")], [dict(DEGISIKLIKLER[0], dosya="../x")],
            [dict(DEGISIKLIKLER[0], dosya="a//b")], [dict(DEGISIKLIKLER[0], dosya="a/./b")],
            [dict(DEGISIKLIKLER[0], tur="silindi")], [dict(DEGISIKLIKLER[0], icerik=None)],
            [dict(DEGISIKLIKLER[0], icerik="a\x00b")], [dict(DEGISIKLIKLER[0], icerik="x" * 4097)],
            [DEGISIKLIKLER[0], DEGISIKLIKLER[0]],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(degisiklik_risk_raporu), "dosya kapsamı, bağımsız bulgular, sıralama ve inceleme bayrağı korunmalı")
def m_kapsam(degisiklikler):
    degisen = copy.deepcopy(degisiklikler)
    for kayit in degisen:
        if kayit["dosya"] == "docs/AGENTS.md":
            kayit["dosya"] = "AGENTS.md"
        if kayit["dosya"] == ".github/workflows/pr.txt":
            kayit["dosya"] = ".github/workflows/pr.yml"
    return degisiklik_risk_raporu(degisen)
def m_isaret(degisiklikler):
    degisen = copy.deepcopy(degisiklikler)
    for kayit in degisen:
        kayit["icerik"] = kayit["icerik"].replace("postinstall", "").replace("SETUP.PY", "").replace("preinstall", "")
    return degisiklik_risk_raporu(degisen)
def m_bayrak(degisiklikler):
    sonuc = degisiklik_risk_raporu(degisiklikler)
    sonuc["inceleme_gerekli"] = False
    return sonuc
for ad, mutant in [("yalnız tam dosya kapsamını genişleten", m_kapsam), ("kurulum kancası işaretlerini yok sayan", m_isaret), ("inceleme bayrağını kapatan", m_bayrak)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

from sandbox import ai_gercek_ai_saldiri_26 as deney
import tempfile
from pathlib import Path
if not ok(not ai_lab.kod_denetimi(src,('envanter_ref','risk_ref','karar_ref')), 'laboratuvar/gerçek ölçüm yamalanmamalı'):stop()
with tempfile.TemporaryDirectory(prefix='pafta_repo26_') as tmp:
    p=Path(tmp)/'not.txt';p.write_text(deney.ORNEK.read_text(encoding='utf-8'),encoding='utf-8')
    r=deney.deney(repo_yuzey_envanteri,repo_eylem_onayi,degisiklik_risk_raporu,p,Path(tmp)/'deney')
    for k,v in r['kontroller'].items():ok(v,'gerçek deney: '+k)
    accepted=all(r['kontroller'].values());ai_lab.kanit_yaz('saldiri-26-repo',dict(r,kabul=accepted));ok(accepted,'gerçek repo dosyası/komut kapısı/gerçek değişiklik riski; saldırıbaşarısı şart değil')

```

```solution
import ai_lab
def repo_yuzey_envanteri(dosyalar):
    if not isinstance(dosyalar, list):
        raise ValueError("dosya listesi geçersiz")
    talimatlar = {"AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"}
    bagimliliklar = {"package.json", "pyproject.toml", "requirements.txt"}
    izler = ("system:", "ignore previous", "curl ", "subprocess.run")
    yollar = set()
    sonuc = []
    for dosya in dosyalar:
        if not isinstance(dosya, dict) or set(dosya) != {"yol", "icerik"}:
            raise ValueError("dosya şeması geçersiz")
        yol = dosya["yol"]
        icerik = dosya["icerik"]
        if not isinstance(yol, str) or not yol or yol in yollar or "\x00" in yol or "\\" in yol or yol.startswith("/"):
            raise ValueError("yol geçersiz")
        parcalar = yol.split("/")
        if any(parca in ("", ".", "..") for parca in parcalar):
            raise ValueError("göreli yol geçersiz")
        if not isinstance(icerik, str) or len(icerik) > 4096 or "\x00" in icerik:
            raise ValueError("içerik geçersiz")
        yollar.add(yol)
        tur = "ajan-talimati" if yol in talimatlar else "bagimlilik" if yol in bagimliliklar else "repo-verisi"
        kucuk = icerik.lower()
        sonuc.append({"yol": yol, "tur": tur, "supheli": any(iz in kucuk for iz in izler)})
    sonuc.sort(key=lambda x: x["yol"])
    return sonuc

def repo_eylem_onayi(eylem, politika):
    if not isinstance(eylem, dict) or set(eylem) != {"tur", "hedef"}:
        raise ValueError("eylem şeması geçersiz")
    if any(not isinstance(eylem[alan], str) or not eylem[alan] for alan in ("tur", "hedef")):
        raise ValueError("eylem değeri geçersiz")
    if not isinstance(politika, dict) or set(politika) != {"okuma_yollari", "yazma_yollari", "komutlar"}:
        raise ValueError("politika şeması geçersiz")
    def yol_guvenli(yol):
        return isinstance(yol, str) and bool(yol) and "\x00" not in yol and "\\" not in yol and not yol.startswith("/") and all(parca not in ("", ".", "..") for parca in yol.split("/"))
    for alan in ("okuma_yollari", "yazma_yollari"):
        degerler = politika[alan]
        if not isinstance(degerler, list) or len(set(degerler)) != len(degerler) or any(not yol_guvenli(x) for x in degerler):
            raise ValueError("yol politikası geçersiz")
    komutlar = politika["komutlar"]
    if not isinstance(komutlar, list) or len(set(komutlar)) != len(komutlar) or any(not isinstance(x, str) or not x or "\x00" in x or "\n" in x or "\r" in x for x in komutlar):
        raise ValueError("komut politikası geçersiz")
    tur = eylem["tur"]
    hedef = eylem["hedef"]
    if tur in ("dosya-oku", "dosya-yaz"):
        if not yol_guvenli(hedef):
            raise ValueError("eylem yolu geçersiz")
        alan = "okuma_yollari" if tur == "dosya-oku" else "yazma_yollari"
        izin = hedef in politika[alan]
        return {"izin": izin, "neden": "izinli" if izin else "yol-yasak"}
    if tur == "komut":
        if "\x00" in hedef or "\n" in hedef or "\r" in hedef:
            raise ValueError("eylem komutu geçersiz")
        izin = hedef in komutlar
        return {"izin": izin, "neden": "izinli" if izin else "komut-yasak"}
    return {"izin": False, "neden": "bilinmeyen-eylem"}

def degisiklik_risk_raporu(degisiklikler):
    if not isinstance(degisiklikler, list):
        raise ValueError("değişiklik listesi geçersiz")
    talimatlar = {"AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"}
    bagimliliklar = {"package.json", "pyproject.toml", "requirements.txt"}
    yollar = set()
    bulgular = []
    for kayit in degisiklikler:
        if not isinstance(kayit, dict) or set(kayit) != {"dosya", "tur", "icerik"}:
            raise ValueError("değişiklik şeması geçersiz")
        dosya = kayit["dosya"]
        if not isinstance(dosya, str) or not dosya or dosya in yollar or "\x00" in dosya or "\\" in dosya or dosya.startswith("/") or any(parca in ("", ".", "..") for parca in dosya.split("/")):
            raise ValueError("dosya yolu geçersiz")
        if kayit["tur"] not in ("eklendi", "degisti"):
            raise ValueError("değişiklik türü geçersiz")
        icerik = kayit["icerik"]
        if not isinstance(icerik, str) or len(icerik) > 4096 or "\x00" in icerik:
            raise ValueError("içerik geçersiz")
        yollar.add(dosya)
        kucuk = icerik.lower()
        if dosya in talimatlar and any(iz in kucuk for iz in ("system:", "ignore previous")):
            bulgular.append({"dosya": dosya, "kategori": "ajan-yonlendirme"})
        if dosya in bagimliliklar and any(iz in kucuk for iz in ("preinstall", "postinstall", "setup.py")):
            bulgular.append({"dosya": dosya, "kategori": "kurulum-kancasi"})
        if dosya.startswith(".github/workflows/") and dosya.endswith((".yml", ".yaml")) and "pull_request_target" in kucuk:
            bulgular.append({"dosya": dosya, "kategori": "ci-calistirma"})
    bulgular.sort(key=lambda x: (x["dosya"], x["kategori"]))
    return {"bulgular": bulgular, "inceleme_gerekli": bool(bulgular)}
if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_26 as deney
    deney.goster(repo_yuzey_envanteri,repo_eylem_onayi,degisiklik_risk_raporu)

```

```hint
Repo talimatı gerçek politika kaynağı değildir. Kapı kararını gerçekten dosya/komut yürütücüsünden önce uygula. Risk raporu gerçek değişmiş dosyalara bakmalı;her yazmayı reddetmek normal src/app.py kontrolünü geçemez.
```
:::
