---
id: p78
title: Impacket · SID Baytlarını Okumak
summary: Kurulu Impacket ortamını bulmak; LDAP_SID nesnesi ile ham SID verisini dönüştürmek; sürüme bağlı yardımcı sınırlarını ve alan genişliklerini ölçmek.
backend: wsl
timeout: 60
---

::: anlat Hazır protokol betiğinde önce ortam
Impacket, Windows/AD ortamlarında kullanılan protokoller için Python sınıfları sağlar. Hazır bir betikte importları, komut satırı seçeneklerini ve en son bağlantıyı başlatan satırı ayrı ayrı oku. `--help` seçeneğinin adı bile her betikte aynı sözleşme anlamına gelmez; önce argparse bölümü ve ana akış incelenir.

Bu iki derste mevcut Kali sistem Python'undaki **0.14.0.dev0** kullanılıyor. Bu bir geliştirme sürümüdür; aşağıdaki çıktı sürümü ve gerçek import yolunu gösterir. Windows'a veya yeni bir venv'e otomatik kopyalanmaz.

```python
import importlib.metadata
import impacket
import sys
print(sys.executable)
print(importlib.metadata.version("impacket"))
print(list(impacket.__path__))
```

`ModuleNotFoundError` alırsan önce betiğin hangi yorumlayıcıyla açıldığına ve bu envantere bak. Farklı sürümün internetteki örneğini aynen çalıştırmak da API uyuşmazlığı yaratabilir. Bu tezgah paket kurmaz; gerçek kütüphaneyi Linux geçici klasöründe kullanır. Ağ bağlantısı, DC, oturum açma veya bir hesap parolası gerekmez.

Kaynak: [Fortra Impacket](https://github.com/fortra/impacket).
:::

::: anlat SID bir alanlar dizisidir
SID, Windows güvenlik kimliğidir. Burada yalnız **LDAP_SID'nin kullandığı ikili temsil** üzerinde çalışıyoruz; RPC'nin NDR taşıma biçimi veya bir erişim kararı bu görevlerin konusu değildir.

| Alan | Uzunluk ve temsil |
|---|---|
| Revision | 1 bayt; bu derste 1 |
| SubAuthorityCount | 1 bayt; en fazla 15 öğe |
| IdentifierAuthority | 6 bayt; burada big-endian olarak sayıya açılır |
| SubAuthority | Her öğe 4 bayt unsigned little-endian |

Örnek `S-1-5-21-42`: revision 1, authority 5, iki alt authority 21 ve 42. Alanları okumak, kimliğin bir dizinde gerçekten var olduğunu veya neye erişebileceğini kanıtlamaz.

```python
from impacket.ldap.ldaptypes import LDAP_SID
sid = LDAP_SID()
sid.fromCanonical("S-1-5-21-42")
ham = sid.getData()
print(ham.hex())
print(LDAP_SID(data=ham).formatCanonical())
```

Kaynak: [Microsoft SID ikili temsil](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/f992ad60-0fe4-4b87-9fed-beb478836861), [Fortra LDAP yapıları](https://github.com/fortra/impacket/blob/master/impacket/ldap/ldaptypes.py). SID dizesinin sözdizimi ile ikili alan sözleşmesini karıştırma; aşağıdaki görevler sayısal alan ve bytes alır, genel bir SID dizesi ayrıştırıcısı değildir.
:::

::: anlat Kütüphane yardımcısının sınırı
Kurulu sürümde `fromCanonical` authority'yi tek bayta paketliyor; `formatCanonical` yalnız altıncı baytını okuyor. Bu yardımcılar **genel 48 bit authority için yeterli değil**. Gerçek sınıfın altı baytlık `IdentifierAuthority["Value"]` alanı ise bütün alanı saklıyor.

Bu yüzden görevlerde authority'yi altı bayt olarak doldurup o alanın tamamından okuyacağız; metin yardımcısının sınırını gizleyen bir taklit kullanmayacağız. `getData` serileştirir; `LDAP_SID(data=...)` ham kaydı nesneye açar. Bunların başarıyla çalışması tek başına bütün protokol kurallarının doğrulandığı anlamına gelmez. Uzunluk ve aralık denetimleri ayrıca gerekir.

Bu bulgu kurulu kaynak üzerinde ölçüldü; kaynak karşılaştırması: [fromCanonical ve formatCanonical](https://github.com/fortra/impacket/blob/master/impacket/ldap/ldaptypes.py).
:::

::: tahmin Yardımcıyla ham alan neden ayrılıyor?
```python
from impacket.ldap.ldaptypes import LDAP_SID

sid = LDAP_SID()
sid.fromCanonical("S-1-5-21-42")
sid["IdentifierAuthority"]["Value"] = (256).to_bytes(6, "big")
okunan = LDAP_SID(data=sid.getData())
print(len(sid.getData()), okunan["SubAuthorityCount"])
print(int.from_bytes(okunan["IdentifierAuthority"]["Value"], "big"))
print(okunan.formatCanonical())
```

???

```text
16 2
256
S-1-0-21-42
```

Altı authority baytı `00 00 00 00 01 00` olarak saklanır. Alanın tamamı 256'dır; bu sürümün metin yardımcısı yalnız son baytı okuyup 0 gösterir. Son satır **doğru SID metni diye kullanılmamalıdır**; tahmin, gerçek kütüphane sınırını görünür kılar.
:::

::: gorev Sayısal alanlardan SID kaydı üret
`sid_yaz(otorite, altlar)` yaz; Impacket `LDAP_SID` nesnesinden `bytes` üret.

- `otorite` bool olmayan int, 0 ile `2**48 - 1` dahil aralığında.
- `altlar` liste veya tuple; 0–15 dahil öğe. Her öğe bool olmayan int, 0 ile `2**32 - 1` dahil aralığında.
- Revision 1; authority altı bayt big-endian, alt alanlar dörder bayt little-endian.
- Uygunsuz girişte `ValueError`. Boş liste, bu ikili alan alıştırmasında sıfır öğeli kayıt üretir; bir hesap SID'si veya standart SID dizesi üretildiği iddia edilmez.

```starter
from impacket.ldap.ldaptypes import LDAP_SID

def sid_yaz(otorite, altlar):
    sid = LDAP_SID()
    sid.fromCanonical("S-1-" + str(otorite) + "".join("-" + str(x) for x in altlar))
    return sid.getData()
```
```test
f = need("sid_yaz")
for otorite in (0, 5, 255, 256, 2**32, 2**48 - 1):
    for altlar in ([], [0], [2**32 - 1], [0x12345678, 42], list(range(14)), list(range(15))):
        ham = bytes([1, len(altlar)]) + otorite.to_bytes(6, "big")
        ham += b"".join(x.to_bytes(4, "little") for x in altlar)
        eq(f(otorite, altlar), ham, f"authority={otorite}, adet={len(altlar)}")
eq(f(5, (21, 42)), bytes.fromhex("0102000000000005150000002a000000"), "Tuple ve sabit bağımsız tanık")
for a in (-1, 2**48, True, "5", 5.0, None):
    raises(ValueError, f, a, [1], msg="Authority tür/sınırı")
for alt in ([1] * 16, [-1], [2**32], [True], ["1"], [1.5], None, b"", {1}):
    raises(ValueError, f, 5, alt, msg="Alt alan tür/sayısı/sınırı")
```
```solution
from impacket.ldap.ldaptypes import LDAP_SID, LDAP_SID_IDENTIFIER_AUTHORITY

def sid_yaz(otorite, altlar):
    if type(otorite) is not int or not 0 <= otorite <= 2**48 - 1:
        raise ValueError("48 bit authority gerekli")
    if not isinstance(altlar, (list, tuple)) or len(altlar) > 15:
        raise ValueError("En fazla 15 alt alan")
    if any(type(x) is not int or not 0 <= x <= 2**32 - 1 for x in altlar):
        raise ValueError("32 bit unsigned alt alan gerekli")
    sid = LDAP_SID()
    sid["Revision"] = 1
    sid["SubAuthorityCount"] = len(altlar)
    sid["IdentifierAuthority"] = LDAP_SID_IDENTIFIER_AUTHORITY()
    sid["IdentifierAuthority"]["Value"] = otorite.to_bytes(6, "big")
    sid["SubAuthority"] = b"".join(x.to_bytes(4, "little") for x in altlar)
    return sid.getData()
```
```hint
fromCanonical yardımcısının tek bayt sınırına takılma. Altı baytlık Value alanını doğrudan doldur; ardından gerçek nesnenin getData metodunu çağır.
```
:::

::: gorev Ham SID'yi kayıpsız oku
`sid_oku(ham)` yaz; `(otorite, alt_alanlar_tuple)` döndür. `ham` bytes olmalı, en az 8 bayt olmalı, revision 1 ve alt alan sayısı en fazla 15 olmalı. Toplam uzunluk **tam `8 + 4 * adet`** olmalı. Fazla veya eksik bayt dahil her geçersiz durumda `ValueError` yükselt. Sayıları gerçek `LDAP_SID` nesnesinin alanlarından çıkar; formatCanonical kullanma.

```starter
from impacket.ldap.ldaptypes import LDAP_SID

def sid_oku(ham):
    sid = LDAP_SID(data=ham)
    return sid.formatCanonical()
```
```test
f = need("sid_oku")
for a in (0, 5, 255, 256, 2**32, 2**48 - 1):
    for alt in ((), (0,), (2**32 - 1,), (0x12345678, 42), tuple(range(14)), tuple(range(15))):
        ham = bytes([1, len(alt)]) + a.to_bytes(6, "big") + b"".join(x.to_bytes(4, "little") for x in alt)
        eq(f(ham), (a, alt), f"authority={a}, adet={len(alt)}")
base = bytes.fromhex("01010000000000052a000000")
for ham in (b"", b"\1" + b"\0" * 6, base[:-1], base + b"\0",
            b"\0" + base[1:], b"\2" + base[1:],
            b"\1\x10" + b"\0" * 6 + b"\0" * 64,
            b"\1\xff" + b"\0" * 6, "", bytearray(base), None):
    raises(ValueError, f, ham, msg="Başlık, öğe sayısı ve tam uzunluk doğrulanır")
```
```solution
from impacket.ldap.ldaptypes import LDAP_SID

def sid_oku(ham):
    if not isinstance(ham, bytes) or len(ham) < 8:
        raise ValueError("Eksik SID başlığı")
    adet = ham[1]
    if ham[0] != 1 or adet > 15 or len(ham) != 8 + 4 * adet:
        raise ValueError("SID alanları veya uzunluk hatalı")
    sid = LDAP_SID(data=ham)
    otorite = int.from_bytes(sid["IdentifierAuthority"]["Value"], "big")
    veri = sid["SubAuthority"]
    altlar = tuple(int.from_bytes(veri[i:i+4], "little") for i in range(0, len(veri), 4))
    return otorite, altlar
```
```hint
Kütüphane nesnesini oluşturmadan önce sabit başlığı ve tam boyu denetle. Byte 1 alt alan sayısıdır; authority'nin bütün altı baytını oku.
```
:::


::: anlat Seçeneği ve import hatasını bağlantı kurmadan oku
Kurulu `/usr/share/doc/python3-impacket/examples/smbclient.py` kaynağını okuyacağız. Bu Kali paketinin dosya konumudur; başka dağıtımda aynı yol garanti edilmez. Betiği `main()` ile çalıştırmıyoruz: kaynakta bağlantı ve parola isteme akışı da var. AST ile yalnız `add_argument` bildirimlerini envantere almak, bağlantı seçeneğiyle kimlik doğrulama seçeneğini ayırmayı sağlar. Bu envanter argparse'ın çalışma zamanı doğrulamasının yerine geçmez; örneğin `choices` bildirimini kaydeder, komut çalıştırmaz.

`ModuleNotFoundError.name`, istenen modülün mü yoksa onun import ettiği başka bir bağımlılığın mı eksik olduğunu ayırır. Dağıtım metadata'sının bulunmaması, modül dosyasının import edilememesiyle aynı şey değildir. Bir simgenin yokluğu da sürüm/API uyuşmazlığına işarettir; parola veya sunucu hatası değildir. Otomatik `pip install` ile sistem Python'unu değiştirmek yerine yorumlayıcı, modül yolu ve dağıtım sürümünü kaydet; P75'teki ayrı ortam düzenine dön.

Kaynak: [kurulu örneğin upstream karşılığı](https://github.com/fortra/impacket/blob/master/examples/smbclient.py), [Python metadata ve PackageNotFoundError](https://docs.python.org/3/library/importlib.metadata.html), [ModuleNotFoundError](https://docs.python.org/3/library/exceptions.html#ModuleNotFoundError). Burada sürüm karşılaştırma motoru yazılmıyor; mevcut API'nin kullanılabilirliği yoklanıyor.
:::

::: gorev Gerçek örnek betiğin seçenek bildirimlerini çıkar
`secenek_kayitlari(kaynak)` AST'deki `.add_argument(...)` çağrılarını kaynak sırasıyla okusun. Her kayıt `(adlar, action, default, choices)`; adlar positional dahil tuple, action bildirilmemişse `'store'`, default/choices bildirilmemişse None. Bu üç keyword ve bütün adlar yalnız literal ise kabul edilir; dinamik ifadede ValueError. Diğer keyword'ler bu envanterin kapsamı dışında ve değerlendirilmez. Kaynağı exec/eval ile çalıştırma; dosya/ağ işlemi yapılmaz. Tek bir keyword bildirimi iki kez yazılmış kaynaklar kapsam dışıdır.

```starter
def secenek_kayitlari(kaynak):
    return []
```

```test
from pathlib import Path
f=need('secenek_kayitlari')
source=Path('/usr/share/doc/python3-impacket/examples/smbclient.py').read_text()
rows=f(source)
by_name={name:row for row in rows for name in row[0]}
eq(by_name['target'],(('target',),'store',None,None),'positional hedef de envanterde')
eq(by_name['-port'],(('-port',),'store','445',['139','445']),'gerçek port default ve choices')
eq(by_name['-k'],(('-k',),'store_true',None,None),'kimlik doğrulama bayrağı')
for name in ('-target-ip','-dc-ip','-hashes','-aesKey','-no-pass','-inputfile','-outputfile','-debug','-ts'):
    ok(name in by_name,'kurulu kaynak seçeneği: '+name)
eq(f('p.add_argument("-x", "--extra", default=0, choices=[0,1])\np.add_argument("file")'),[(('-x','--extra'),'store',0,[0,1]),(('file',),'store',None,None)],'çoklu ad, sıralama, sıfır default')
eq(f('raise RuntimeError("kaynak çalıştırılmamalı")'),[],'kaynak çalıştırılmaz')
eq(f('p.add_argument("x", help=bilinmeyen())'),[(('x',),'store',None,None)],'kapsam dışı keyword çalıştırılmaz')
for text in ('p.add_argument(ad)','p.add_argument("x", default=hesapla())','p.add_argument("x", choices=liste)','p.add_argument("x", action=eylem)'):
    raises(ValueError,lambda text=text:f(text),msg='dinamik bildirim açık hata')
```

```solution
import ast

def secenek_kayitlari(kaynak):
    calls=[node for node in ast.walk(ast.parse(kaynak)) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='add_argument']
    calls.sort(key=lambda node:(node.lineno,node.col_offset))
    result=[]
    for call in calls:
        try:
            names=tuple(ast.literal_eval(arg) for arg in call.args)
            if not names or any(not isinstance(name,str) for name in names):raise ValueError('Literal seçenek adı gerekli')
            values={kw.arg:ast.literal_eval(kw.value) for kw in call.keywords if kw.arg in ('action','default','choices')}
        except (ValueError,TypeError,SyntaxError) as error:
            raise ValueError('Dinamik seçenek bildirimi desteklenmiyor') from error
        result.append((names,values.get('action','store'),values.get('default'),values.get('choices')))
    return result
```
:::

::: gorev Eksik paket ile eksik API'yi ayır
`ortam_yokla(modul,dagitim,simge)` gerçek importlib ile modülü import etsin, metadata sürümünü ve simgenin varlığını denetlesin. Sonuç iki elemanlı tuple: başarılıysa `('ok',(version,module.__file__))`; hata durumlarında `('modul-eksik',eksik_ad)`, `('alt-bagimlilik-eksik',eksik_ad)`, `('metadata-eksik',dagitim)` veya `('api-uyusmaz',simge)`. Öncelik import, metadata, simge. ModuleNotFoundError.name istenen ad veya onun nokta ile ayrılmış üst paketiyse modul-eksik; başka adsa alt-bagimlilik-eksik. Diğer import hatalarını gizleme. Sadece simgenin varlığı ölçülür, çağrılabilir olması gerekmez. Paket kurma, sunucuya bağlanma.

```starter
def ortam_yokla(modul,dagitim,simge):
    return ('ok',('', ''))
```

```test
import importlib,importlib.metadata,sys,tempfile
from pathlib import Path
f=need('ortam_yokla')
import impacket.ldap.ldaptypes as real
version=importlib.metadata.version('impacket')
eq(f('impacket.ldap.ldaptypes','impacket','LDAP_SID'),('ok',(version,real.__file__)),'gerçek modül ve dağıtım kimliği')
eq(f('impacket.ldap.ldaptypes','impacket','PAFTA_OLMAYAN_API'),('api-uyusmaz','PAFTA_OLMAYAN_API'),'yanlış API adı')
eq(f('impacket.ldap.ldaptypes','pafta_metadata_yok_726','LDAP_SID'),('metadata-eksik','pafta_metadata_yok_726'),'import var, metadata yok')
eq(f('pafta_modul_yok_726.child','impacket','x'),('modul-eksik','pafta_modul_yok_726'),'üst paket eksik')
eq(f('impacket.pafta_olmayan_alt_modul','impacket','x'),('modul-eksik','impacket.pafta_olmayan_alt_modul'),'alt modül eksik')
with tempfile.TemporaryDirectory() as folder:
    root=Path(folder)
    (root/'pafta_broken_import_726.py').write_text('import pafta_alt_bagimlilik_yok_726\n')
    (root/'pafta_import_error_726.py').write_text('raise ImportError("gerçek başka hata")\n')
    (root/'pafta_none_api_726.py').write_text('api=None\n')
    sys.path.insert(0,folder);importlib.invalidate_caches()
    try:
        eq(f('pafta_broken_import_726','impacket','x'),('alt-bagimlilik-eksik','pafta_alt_bagimlilik_yok_726'),'var olan modülün bağımlılığı eksik')
        raises(ImportError,lambda:f('pafta_import_error_726','impacket','x'),msg='diğer ImportError gizlenmez')
        ok(f('pafta_none_api_726','impacket','api')[0]=='ok','None değerli simge vardır')
    finally:
        sys.path.remove(folder)
        for name in ('pafta_broken_import_726','pafta_import_error_726','pafta_none_api_726'):sys.modules.pop(name,None)
```

```solution
import importlib
import importlib.metadata

def ortam_yokla(modul,dagitim,simge):
    try:
        loaded=importlib.import_module(modul)
    except ModuleNotFoundError as error:
        missing=error.name
        own=missing==modul or (missing is not None and modul.startswith(missing+'.'))
        return ('modul-eksik' if own else 'alt-bagimlilik-eksik',missing)
    try:
        version=importlib.metadata.version(dagitim)
    except importlib.metadata.PackageNotFoundError:
        return ('metadata-eksik',dagitim)
    if not hasattr(loaded,simge):return ('api-uyusmaz',simge)
    return ('ok',(version,loaded.__file__))
```
:::
