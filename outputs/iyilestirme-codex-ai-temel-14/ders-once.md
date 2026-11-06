---
id: ai-temel-14
title: "Yapılandırılmış Çıktı ve Şema Doğrulama"
summary: Katı kayıt şeması, allowlist'li JSON araç çağrısı ve geçerli ilk çıktı seçimi uygula.
timeout: 45
---

::: anlat JSON olması şemaya uyması demek değildir
Model çıktısı sözdizimsel olarak geçerli JSON olsa bile eksik alan, yanlış tür veya beklenmeyen komut içerebilir. Katı doğrulama tam anahtar kümesini, değer türlerini ve izinli değer aralıklarını kontrol eder. Bilinmeyen alanları sessizce kabul etmek ileride güvenlik açığına dönüşebilir.

Bu derste Pydantic veya model çalıştırılmaz; standart `json` modülü ve açık doğrulama kuralları kullanılır. Hatalı aday reddedilir, ancak hiçbir araç gerçekten çalıştırılmaz.
:::

::: anlat Araç çağrısı veridir, yürütme ayrı karardır
Allowlist yalnız tanımlı araç adlarına izin verir. Her aracın argüman şeması ayrıdır; `oku` yalnız göreli ve `..` içermeyen bir yol, `topla` iki sayı alır. Bu fixture dosya okumaz ve hesaplama yapmaz, yalnız çağrıyı normalize eder.

Birden çok model adayı arasından ilk geçerli çıktıyı seçmek, geçersiz metni düzeltmeye çalışmaktan daha öngörülebilirdir. Seçimden sonra yetki ve kullanıcı onayı gibi ek katmanlar yine gerekir.
:::

::: tahmin Şema sonucunu tahmin et
Üç çıktı satırını yaz:

```python
import json
x = json.loads('{"arac":"topla","argumanlar":{"a":1,"b":2}}')
print(x["arac"])
print(set(x) == {"arac", "argumanlar"})
print([0, 1, 2] if -1 < 0 else [])
```

???

```cikti
topla
True
[0, 1, 2]
```

İlk satır izinli araç adını, ikinci satır tam anahtar eşleşmesini, üçüncü satır aday indekslerinin sırasını gösterir.
:::

::: gorev 1 · Katı kayıt şemasını doğrula
`kayit_dogrula(kayit)` işlevini yaz. Kayıt tam `ad`, `miktar`, `aktif` anahtarlı sözlüktür. Ad boş olmayan string, miktar bool olmayan 1–8 tamsayısı, aktif bool değerdir. Geçersiz veride `ValueError` yükselt.

Aynı alanları içeren bağımsız sözlük döndür; girdiyi değiştirme. Ek anahtarları kabul etme.

```starter
def kayit_dogrula(kayit):
    return {}
```

```test
K = {"ad": "rapor", "miktar": 2, "aktif": True}
def sozlesme(fn):
    try:
        sonuc = fn(K)
        if sonuc != K or sonuc is K or fn(dict(K, miktar=1))["miktar"] != 1 or fn(dict(K, miktar=8))["miktar"] != 8:
            return False
        for deger in [None, [], {}, dict(K, ek=1), dict(K, ad=""), dict(K, ad=1), dict(K, miktar=0), dict(K, miktar=9), dict(K, miktar=True), dict(K, miktar=1.0), dict(K, aktif=1)]:
            try:
                fn(deger)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kayit_dogrula), "tam anahtar, tür ve miktar sınırı korunmalı")
def m_ad(k):
    return kayit_dogrula(dict(k, ad="x"))
def m_miktar(k):
    return kayit_dogrula(dict(k, miktar=9))
def m_aktif(k):
    return kayit_dogrula(dict(k, aktif=False))
for ad, mutant in [("adı bozan", m_ad), ("miktarı bozan", m_miktar), ("aktifi bozan", m_aktif)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kayit_dogrula(kayit):
    if not isinstance(kayit, dict) or set(kayit) != {"ad", "miktar", "aktif"}:
        raise ValueError("kayıt şeması geçersiz")
    if not isinstance(kayit["ad"], str) or not kayit["ad"]:
        raise ValueError("ad geçersiz")
    if not isinstance(kayit["miktar"], int) or isinstance(kayit["miktar"], bool) or not 1 <= kayit["miktar"] <= 8:
        raise ValueError("miktar geçersiz")
    if not isinstance(kayit["aktif"], bool):
        raise ValueError("aktif geçersiz")
    return {"ad": kayit["ad"], "miktar": kayit["miktar"], "aktif": kayit["aktif"]}
```

```hint
Önce `set(kayit)` ile anahtarları, sonra her alanı ayrı doğrula; sonunda yeni sözlük oluştur.
```
:::

::: gorev 2 · Allowlist'li araç çağrısını ayrıştır
`cagri_ayristir(metin)` işlevini yaz. Metin en çok 512 karakterlik JSON object stringidir. Nesne tam `arac`, `argumanlar` anahtarlarını içerir. Geçersiz JSON, tür veya şemada `ValueError` yükselt.

`oku` için argumanlar tam `yol` anahtarlıdır; yol boş olmayan string, mutlak yol olmayan ve `..` yol parçası içermeyen göreli yoldur. `topla` için argumanlar tam `a`, `b` anahtarlı iki bool olmayan sayıdır. Başka araç kabul edilmez. Normalize edilmiş yeni sözlük döndür; aracı çalıştırma.

```starter
def cagri_ayristir(metin):
    return {}
```

```test
import json
def sozlesme(fn):
    try:
        if fn('{"arac":"topla","argumanlar":{"a":1,"b":2.5}}') != {"arac": "topla", "argumanlar": {"a": 1, "b": 2.5}}:
            return False
        if fn('{"arac":"oku","argumanlar":{"yol":"veri/a.txt"}}')["argumanlar"]["yol"] != "veri/a.txt":
            return False
        temel = '{"arac":"topla","argumanlar":{"a":1,"b":2}}'
        sinir = temel + " " * (512 - len(temel))
        if fn(sinir) != {"arac": "topla", "argumanlar": {"a": 1, "b": 2}}:
            return False
        for metin in [None, temel.encode(), "", "x", "[]", sinir + " ", '{"arac":"sil","argumanlar":{"a":1,"b":2}}', '{"arac":"topla","argumanlar":{"a":1}}', '{"arac":"topla","argumanlar":{"a":1,"b":2,"c":3}}', '{"arac":"topla","argumanlar":{"a":"1","b":2}}', '{"arac":"topla","argumanlar":{"a":true,"b":2}}', '{"arac":"topla","argumanlar":{"a":1,"b":2},"ek":0}', '{"arac":"oku","argumanlar":{"yol":"x","ek":1}}', '{"arac":"oku","argumanlar":{"yol":1}}', '{"arac":"oku","argumanlar":{"yol":""}}', '{"arac":"oku","argumanlar":{"yol":"/etc/passwd"}}', '{"arac":"oku","argumanlar":{"yol":"../x"}}', '{"arac":"oku","argumanlar":{"yol":"a/../x"}}']:
            try:
                fn(metin)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(cagri_ayristir), "JSON, araç allowlist'i ve argüman sınırları korunmalı")
def m_arac(m):
    return cagri_ayristir(m.replace("topla", "sil"))
def m_arg(m):
    return cagri_ayristir(m.replace('"a":1', '"a":9'))
def m_bicim(m):
    return cagri_ayristir(m + " ")
for ad, mutant in [("aracı bozan", m_arac), ("argümanı bozan", m_arg), ("biçimi bozan", m_bicim)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def cagri_ayristir(metin):
    import json
    if not isinstance(metin, str) or not metin or len(metin) > 512:
        raise ValueError("metin geçersiz")
    try:
        cagri = json.loads(metin)
    except (json.JSONDecodeError, TypeError):
        raise ValueError("JSON geçersiz")
    if not isinstance(cagri, dict) or set(cagri) != {"arac", "argumanlar"} or cagri["arac"] not in ("oku", "topla") or not isinstance(cagri["argumanlar"], dict):
        raise ValueError("çağrı geçersiz")
    arac = cagri["arac"]
    arg = cagri["argumanlar"]
    if arac == "oku":
        if set(arg) != {"yol"} or not isinstance(arg["yol"], str) or not arg["yol"] or arg["yol"].startswith(("/", "\\")) or ".." in arg["yol"].replace("\\", "/").split("/"):
            raise ValueError("yol geçersiz")
        return {"arac": arac, "argumanlar": {"yol": arg["yol"]}}
    if set(arg) != {"a", "b"} or any(not isinstance(arg[x], (int, float)) or isinstance(arg[x], bool) for x in ("a", "b")):
        raise ValueError("sayı geçersiz")
    return {"arac": arac, "argumanlar": {"a": arg["a"], "b": arg["b"]}}
```

```hint
JSON'u önce ayrıştır, sonra araç adına göre iki ayrı şema uygula. Yolu `/` ve `\\` ayraçlarıyla parçalayıp `..` ara.
```
:::

::: gorev 3 · İlk geçerli yapılandırılmış çıktıyı seç
`ilk_gecerli_cikti(adaylar)` işlevini yaz. Adaylar 0–8 öğeli string listesidir; her string en çok 512 karakterdir. Geçersiz üst düzey veride `ValueError` yükselt.

Her adayı JSON olarak ayrıştır. Tam `islem`, `deger` anahtarlı nesne, `islem` alanı `not_ekle` veya `raporla`, değer alanı boş olmayan string ise aday geçerlidir. Hatalı adayı reddet ve ilk geçerli adayın indeksini döndür; hiçbiri geçerli değilse -1 döndür.

```starter
def ilk_gecerli_cikti(adaylar):
    return -2
```

```test
A = ["x", '{"islem":"sil","deger":"a"}', '{"islem":"not_ekle","deger":"not"}', '{"islem":"raporla","deger":"rapor"}']
def sozlesme(fn):
    try:
        if fn(A) != 2 or fn(A[2:]) != 0 or fn(A[:2]) != -1 or fn([]) != -1:
            return False
        if len(A + A) != 8 or fn(A + A) != 2 or fn([A[2] + " " * (512 - len(A[2]))]) != 0:
            return False
        for deger in [None, {}, [1], ["x" * 513], A + A + A[:1]]:
            try:
                fn(deger)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(ilk_gecerli_cikti), "aday reddi, ilk geçerli indeks ve şema korunmalı")
def m_sira(a):
    return ilk_gecerli_cikti(list(reversed(a)))
def m_icerik(a):
    return ilk_gecerli_cikti([x.replace("not_ekle", "sil") for x in a])
def m_boyut(a):
    return ilk_gecerli_cikti(a + a)
for ad, mutant in [("sırayı bozan", m_sira), ("içeriği bozan", m_icerik), ("boyutu bozan", m_boyut)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def ilk_gecerli_cikti(adaylar):
    import json
    if not isinstance(adaylar, list) or not 0 <= len(adaylar) <= 8 or any(not isinstance(x, str) or len(x) > 512 for x in adaylar):
        raise ValueError("adaylar geçersiz")
    for i, metin in enumerate(adaylar):
        try:
            x = json.loads(metin)
        except json.JSONDecodeError:
            continue
        if isinstance(x, dict) and set(x) == {"islem", "deger"} and x["islem"] in ("not_ekle", "raporla") and isinstance(x["deger"], str) and x["deger"]:
            return i
    return -1
```

```hint
Her adayı try/except ile ayrıştır; geçersizse `continue`, bütün koşullar sağlanıyorsa hemen indeksi döndür.
```
:::

::: anlat Gerçek deney: şemayla ürettir, sonra yine doğrula
Önceki görevlerdeki JSON örnekleri hazır metinlerdi. Bu adımda kurulu Ollama modeli gerçekten `/api/chat` ile çağrılır ve `format` alanına JSON Schema verilir. Test gerçek modelin ham yanıtını saklar ve senin doğrulayıcını o yanıt üzerinde çalıştırır. [Resmî protokol](https://docs.ollama.com/capabilities/structured-outputs) JSON üretimi ile şemaya göre üretimi ayırır; burada tam şema gönderilir.

Şema doğruluğu içerik doğruluğu veya yetki değildir. Modelin `onay:true` demesi kullanıcı onayı sayılmaz; bu derste hiçbir dosya veya araç eylemi çalıştırılmaz. İstenen rastgele notun aynen kopyalanıp kopyalanmadığı ayrıca **bulgu** olarak kaydedilir, modelin sabit bir metin üretmesi kabul şartı değildir. Asıl kabul, gerçek şema isteğinin tamamlanması ve gerçek yanıtın katı yerel doğrulamadan geçmesidir.

Deney varsayılan olarak GPU'da çalışır: bilgisayardaki Ollama sunucusunu kullanır ve aynı anda başka bir Ollama deneyi GPU'yu tutuyorsa sırasını bekler (makine genelinde GPU kilidi). Yalnız kendi yüklediği modeli boşaltır; senin önceden yüklediğin modele dokunmaz. `PAFTA_OLLAMA_CIHAZ=cpu` ayarlanırsa deney kendi ayrı Ollama sunucusunu açar, istekte `num_gpu=0` kullanır ve iş bitince yalnız o sürecin ağacını kapatır; CPU üretimi daha yavaştır. Hangi cihazın kullanıldığı kanıta yazılır; model dosyaları korunur. Kurulu model/araç yoksa deney geçmez, indirme yapmaz.
:::

::: gorev Gerçek deney · Gerçek şemalı model çıktısını katı doğrula
`kati_model_jsonu(metin)` işlevini yaz. `metin`, en fazla 4096 karakterlik bir str olmalı; aksi hâlde `ValueError` yükselt.

Metnin **tamamı** tek bir JSON nesnesi olmalıdır. Markdown kod bloğu, JSON sonrası yazı, NaN/Infinity, yinelenen anahtar veya nesne dışı kök kabul edilmez. Nesne tam şu alanları taşır:

- `islem`: yalnız `not_ekle` veya `raporla` stringi.
- `deger`: 1–80 karakterlik str; boşluk dışında en az bir karakter içerir. Metni strip/normalize etme, aynen koru.
- `onay`: tam bool; 0/1, string veya None kabul edilmez. True da False da şema açısından geçerlidir; ikisi de araç yürütme yetkisi vermez.

Geçerli nesneyi bağımsız sözlük olarak döndür, her geçersiz girdide `ValueError` yükselt. Bilinmeyen alanları düşürerek veya tipleri otomatik dönüştürerek “düzeltme” yapma. JSON'un ön/son standart boşluğuna izin ver. Şemadaki karakter sınırı UTF-8 bayt değil Python str uzunluğudur.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def kati_model_jsonu(metin):
    return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_14 as lab14
    kayitlar, ortam = lab14.gercek_ciktilar()
    for k in kayitlar:
        print("Gerçek ham yanıt:", k["icerik"])
        print("Doğrulama:", kati_model_jsonu(k["icerik"]))
```

```test
import copy
import json
import secrets
import ai_lab
from sandbox import ai_gercek_ai_temel_14 as lab14
sonuclar=[]
def kontrol(c,mesaj):
    sonuclar.append(bool(c))
    return ok(c,mesaj)
kontrol(not ai_lab.kod_denetimi(src),"laboratuvar yamalanmamalı")
fn=need("kati_model_jsonu")

v={"islem":"raporla","deger":"PAFTA-"+secrets.token_hex(4),"onay":False}
valid=[v,dict(v,islem="not_ekle",onay=True),dict(v,deger=" çay 🧪 "),dict(v,deger="x"*80)]
base=json.dumps(v,ensure_ascii=False)
bosluk_siniri=base+" "*(4096-len(base))
invalid=[None,42,b"{}","", "{}", "[]", "true", "null", "NaN", "Infinity",
         "```json\n"+base+"\n```", base+" trailing", base+"{}", bosluk_siniri+" ",
         json.dumps(dict(v,ek="komut")), json.dumps(dict(v,onay=1)),json.dumps(dict(v,onay=0)),
         json.dumps(dict(v,onay="false")),json.dumps(dict(v,onay=None)),
         json.dumps(dict(v,islem="sil")),json.dumps(dict(v,islem=[])),
         json.dumps(dict(v,deger="")),json.dumps(dict(v,deger="  ")),json.dumps(dict(v,deger="x"*81)),
         json.dumps(dict(v,deger=42)),json.dumps(dict(v,deger=float("nan"))),
         '{"islem":"sil","islem":"raporla","deger":"not","onay":false}',
         '{"islem":"raporla","deger":"ilk","deger":"son","onay":false}']
def sozlesme(f):
    try:
        for obj in valid:
            text=" \n"+json.dumps(obj,ensure_ascii=False)+"\t"
            a=f(text)
            if type(a) is not dict or a!=obj or type(a["onay"]) is not bool:
                return False
        if f(bosluk_siniri)!=v:
            return False
        for text in invalid:
            try:
                f(text)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn),"katı JSON: tam şema, tam bool, uzunluk ve yinelenen anahtar reddi")

def onar(tur):
    def f(m):
        if not isinstance(m,str):
            raise ValueError("metin")
        if tur=="markdown" and m.startswith("```json"):
            m=m[7:-3].strip()
        if tur in ("ek","bool","duplicate"):
            x=json.loads(m)
            if isinstance(x,dict):
                if tur=="ek":x={k:v for k,v in x.items() if k in {"islem","deger","onay"}}
                if tur=="bool" and type(x.get("onay")) is int:x["onay"]=bool(x["onay"])
                m=json.dumps(x)
        return fn(m)
    return f
for ad,mutant in [("boş kod/işlev",None),("boş sözlük",lambda m:{}),
                  ("sabit gerçek şekilli nesne",lambda m:copy.deepcopy(v)),
                  ("bilinmeyen alanı düşüren",onar("ek")),
                  ("sayısal onayı bool'a çeviren",onar("bool")),
                  ("yinelenen anahtarı gizleyen",onar("duplicate")),
                  ("Markdown'u sessiz temizleyen",onar("markdown"))]:
    kontrol(not sozlesme(mutant),"hatalı çözüm reddedilmeli: "+ad)
if not all(sonuclar):
    stop()

try:
    kayitlar,ortam=lab14.gercek_ciktilar()
except Exception as e:
    kontrol(False,"GERÇEK JSON SCHEMA ÇAĞRISI YAPILAMADI: "+str(e))
    stop()
kontrol(len(kayitlar)==2,"iki gerçek şemalı model çağrısı tamamlandı")
ciktilar=[]
for k in kayitlar:
    try:
        a=fn(k["icerik"])
    except Exception as e:
        kontrol(False,"gerçek model çıktısı şemaya uymadı: "+str(e))
        continue
    kontrol(type(a) is dict and set(a)=={"islem","deger","onay"},"gerçek model JSON'u katı doğrulamadan geçti")
    kontrol(k["istek"]["format"]==lab14.SCHEMA and (k["istek"]["options"].get("num_gpu")==0)==(ai_lab.cihaz_kipi()=="cpu"),"gerçek istekte JSON Schema ve seçili cihaz ayarı kullanıldı")
    ciktilar.append({"ham":k,"dogrulanan":a,"istenen_degerlerle_ayni":a==k["beklenen"]})
kontrol(ai_lab.kaynak_temizlendi(ortam.get("temizlik")),"deney yalnız kendi kaynağını bıraktı (kendi sunucusu ya da kendi yüklediği model)")
bellek=ortam.get("bellek") or {}
kontrol(ai_lab.cihaz_dogrulandi(bellek),"gerçek /api/ps ölçümü seçili cihazla tutarlı (CPU kipinde VRAM 0)")
ai_lab.kanit_yaz("temel-14-schema",{
    "kaynak":"gercek","kabul":all(sonuclar),"ortam":ortam,
    "ayarlar":{"schema":lab14.SCHEMA,"cihaz":ai_lab.cihaz_kipi(),"num_ctx":1024,"num_predict":96},
    "ciktilar":ciktilar,"sinir":"şema/tür kabulü; semantik doğruluk ve araç yetkisi ayrı; araç yürütülmedi",
    "kaynak_belge":"https://docs.ollama.com/capabilities/structured-outputs"})
for k in ciktilar:
    print("gerçek JSON:",k["ham"]["icerik"],"istenen değerlerle aynı:",k["istenen_degerlerle_ayni"])
```

```solution
import ai_lab
import json

def kati_model_jsonu(metin):
    if not isinstance(metin,str) or len(metin)>4096:
        raise ValueError("metin geçersiz")
    def nesne(ciftler):
        out={}
        for k,v in ciftler:
            if k in out:
                raise ValueError("yinelenen anahtar")
            out[k]=v
        return out
    def sabit(_):
        raise ValueError("standart dışı JSON sayısı")
    x=json.loads(metin,object_pairs_hook=nesne,parse_constant=sabit)
    if type(x) is not dict or set(x)!={"islem","deger","onay"}:
        raise ValueError("şema geçersiz")
    if not isinstance(x["islem"],str) or x["islem"] not in ("not_ekle","raporla"):
        raise ValueError("işlem geçersiz")
    if not isinstance(x["deger"],str) or not 1<=len(x["deger"])<=80 or not x["deger"].strip():
        raise ValueError("değer geçersiz")
    if type(x["onay"]) is not bool:
        raise ValueError("onay bool olmalı")
    return dict(x)

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_temel_14 as lab14
    kayitlar,ortam=lab14.gercek_ciktilar()
    for k in kayitlar:
        print("Gerçek ham yanıt:",k["icerik"])
        print("Doğrulama:",kati_model_jsonu(k["icerik"]))
```

```hint
`object_pairs_hook`, JSON nesnesi sözlüğe dönüşmeden önce anahtar çiftlerini görür; yinelenen anahtarları burada reddet. `parse_constant` ile NaN/Infinity'yi engelle. Kod bloklarını veya bilinmeyen alanları temizlemek yerine geçersiz say.
```
:::
