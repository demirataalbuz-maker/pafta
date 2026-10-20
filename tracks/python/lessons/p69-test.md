---
id: p69
title: Test Yazmak
summary: unittest, assert yöntemleri, subTest, mock ile yalıtım ve testlerini test etmek: mutasyon testi.
---

::: anlat Neden test?
64 paftadır testlerimin senin kodunu denetlediğini gördün. Şimdi rolleri değiştiriyoruz: **sen** test yazacaksın. Testler üç şey sağlar:

1. **Doğruluk**: kodun bugün çalıştığının kanıtı
2. **Cesaret**: kodu değiştirdiğinde neyin bozulduğunu hemen görmek (regresyon)
3. **Tasarım**: test edilmesi zor kod genelde kötü tasarlanmış koddur

### unittest
Standart kütüphanedeki test çatısı:

```python
import unittest, io

def ip_gecerli_mi(ip):
    p = ip.split(".")
    return len(p) == 4 and all(x.isdigit() and int(x) <= 255 and (x == "0" or x[0] != "0") for x in p)

class IpTestleri(unittest.TestCase):              #! TestCase'ten türet
    def test_gecerli(self):                       #! test_ ile başlayan her metot bir test
        self.assertTrue(ip_gecerli_mi("10.0.0.1"))

    def test_aralik_disi(self):
        self.assertFalse(ip_gecerli_mi("256.0.0.1"))

    def test_eksik_parca(self):
        self.assertFalse(ip_gecerli_mi("10.0.1"))

    def test_hata_turu(self):
        with self.assertRaises(AttributeError):   #! bu bloğun hata vermesini bekle
            ip_gecerli_mi(None)

paket = unittest.defaultTestLoader.loadTestsFromTestCase(IpTestleri)
sonuc = unittest.TextTestRunner(stream=io.StringIO(), verbosity=2).run(paket)
print(sonuc.testsRun, "test,", len(sonuc.failures), "başarısız,", len(sonuc.errors), "hata")
```

| Yöntem | Kontrol |
|---|---|
| `assertEqual(a, b)` / `assertNotEqual` | a == b |
| `assertTrue(x)` / `assertFalse(x)` | doğruluk değeri |
| `assertIs(a, b)` / `assertIsNone(x)` | kimlik |
| `assertIn(a, b)` | a in b |
| `assertRaises(Hata)` | blok bu hatayı yükseltmeli |
| `assertAlmostEqual(a, b)` | float karşılaştırma |

Gerçek projelerde testleri `python -m unittest` ya da **pytest** (`pip install pytest`, düz `assert` ile yazılan test fonksiyonları, `pytest` komutu) çalıştırır. Tezgahta ise yukarıdaki gibi programatik çalıştırıyoruz.

### subTest: tablo tabanlı testler
```python
import unittest, io

def port_sinifi(p):
    return "sistem" if 0 <= p <= 1023 else "kayitli" if p <= 49151 else "dinamik"

class PortTest(unittest.TestCase):
    def test_tablo(self):
        for port, beklenen in [(0, "sistem"), (1023, "sistem"), (1024, "kayitli"), (49152, "dinamik")]:
            with self.subTest(port=port):        #! biri başarısız olsa da diğerleri koşar
                self.assertEqual(port_sinifi(port), beklenen)

r = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(PortTest))
print(r.wasSuccessful())
```

> [!NOT]
> İyi test **sınırları** dener: 0, 1023, 1024, boş liste, tek eleman, en büyük değer, geçersiz tür. Hataların çoğu "bir eksik/bir fazla" (off-by-one) sınırlarda yaşar.
:::

::: tahmin
Çıktı tek satır:

```python
import unittest, io

class T(unittest.TestCase):
    def test_a(self):
        self.assertEqual(1 + 1, 2)
    def test_b(self):
        self.assertEqual("a".upper(), "B")
    def yardimci(self):
        self.fail("bu çalışmaz")

r = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(T))
print(r.testsRun, len(r.failures), r.wasSuccessful())
```

???

`2 1 False`. Sadece `test_` ile başlayan metotlar test sayılır, bu yüzden `yardimci` hiç çalışmaz. `test_b` başarısız olur ("A" ≠ "B").
:::

::: anlat Mock ile yalıtım ve mutasyon testi
Test edilen kod ağa, veritabanına ya da bir e-posta sunucusuna gidiyorsa testler yavaş, kırılgan ve **tehlikeli** olur (testte gerçek alarm e-postası göndermek istemezsin). **Mock** nesneleri gerçek bağımlılığın yerine geçer ve nasıl kullanıldıklarını kaydeder:

```python
from unittest.mock import Mock, patch

def kritikleri_bildir(bildirici, olaylar):
    for o in olaylar:
        if o["seviye"] == "kritik":
            bildirici.gonder(f"KRİTİK: {o['mesaj']}")

sahte = Mock()                                     #! her niteliği ve çağrıyı kabul eder
kritikleri_bildir(sahte, [{"seviye": "kritik", "mesaj": "disk dolu"},
                          {"seviye": "bilgi", "mesaj": "yedek tamam"}])
print(sahte.gonder.call_count)                     #! kaç kez çağrıldı
sahte.gonder.assert_called_once_with("KRİTİK: disk dolu")   #! tam bu argümanla mı
print("doğrulandı")

import time
with patch("time.time", return_value=1_700_000_000):        #! modül fonksiyonunu geçici değiştir
    print(time.time())
print(time.time() > 1_700_000_000)                 #! blok bitince orijinal geri gelir
```

### Testleri kim test eder? Mutasyon testi
Bir test paketinin kalitesini nasıl ölçersin? **Mutasyon testi** kasıtlı olarak bozulmuş kod sürümleri (**mutantlar**) üretir: `<=` yerine `<`, `255` yerine `256`... İyi bir test paketi her mutantı **öldürmelidir** (en az bir testi başarısız olmalıdır). Hayatta kalan bir mutant, testlerinde bir kör nokta olduğunu söyler. `mutmut` ve `cosmic-ray` bunu otomatik yapar.

Bu paftanın görevlerinde testlerin tam olarak böyle değerlendirilecek: önce **doğru** koda karşı hepsi geçmeli, sonra her **mutanta** karşı en az biri başarısız olmalı.

> [!GÜVENLİK]
> Güvenlik kontrolleri (yetki, girdi doğrulama, imza doğrulama) için yazılan testler **olumsuz durumları** da denemeli: yanlış imza reddediliyor mu, yetkisiz rol gerçekten engelleniyor mu? "Her şeyi kabul eden" bir doğrulayıcı sadece olumlu testlerle asla yakalanmaz; o da bir mutanttır.
:::

::: tahmin
İki satır:

```python
from unittest.mock import Mock

m = Mock(return_value=42)
print(m(1, x=2), m.call_count)
m.assert_called_with(1, x=2)
print(type(m.yeni_nitelik).__name__, m.yeni_nitelik is m.yeni_nitelik)
```

???

`42 1`, sonra `Mock True`. Mock'a verilen `return_value` her çağrıda döner. Olmayan bir niteliğe eriştiğinde Mock yeni bir alt-Mock üretir ve onu hatırlar, bu yüzden aynı nitelik her seferinde aynı nesnedir.
:::

::: gorev IP doğrulayıcısını test et
`ip_gecerli_mi` fonksiyonu hazır ve **doğru**. Senin işin `IpTestleri` adında bir `unittest.TestCase` yazmak. Değerlendirme şöyle yapılacak:

1. Testlerin doğru koda karşı **hepsi geçmeli**
2. Sonra fonksiyon sırayla dört **mutantla** değiştirilecek (ör. 256'ya izin veren, başında sıfır kabul eden...). Her mutantta testlerinden **en az biri başarısız** olmalı

Fonksiyonu değiştirme; testlerinin içinde onu `ip_gecerli_mi(...)` adıyla çağır.

```starter
import unittest

def ip_gecerli_mi(ip):
    p = ip.split(".")
    if len(p) != 4:
        return False
    for x in p:
        if not x.isdigit() or int(x) > 255 or (len(x) > 1 and x[0] == "0"):
            return False
    return True

class IpTestleri(unittest.TestCase):
    def test_ornek(self):
        self.assertTrue(ip_gecerli_mi("10.0.0.1"))
```

```test
import unittest, io
T = need("IpTestleri", "sınıf")
def kos():
    paket = unittest.defaultTestLoader.loadTestsFromTestCase(T)
    return unittest.TextTestRunner(stream=io.StringIO()).run(paket)
dogru = kullanici["ip_gecerli_mi"]
r = kos()
ok(r.testsRun >= 4, "en az 4 test metodu yaz", got=r.testsRun)
ok(r.wasSuccessful(), "doğru koda karşı bütün testler geçmeli", got=f"{len(r.failures)} başarısız, {len(r.errors)} hata")
def m_256(ip):
    p = ip.split(".")
    return len(p) == 4 and all(x.isdigit() and int(x) <= 256 and (len(x) == 1 or x[0] != "0") for x in p)
def m_sifir(ip):
    p = ip.split(".")
    return len(p) == 4 and all(x.isdigit() and int(x) <= 255 for x in p)
def m_parca(ip):
    p = ip.split(".")
    return 3 <= len(p) <= 4 and all(x.isdigit() and int(x) <= 255 and (len(x) == 1 or x[0] != "0") for x in p)
def m_harf(ip):
    p = ip.split(".")
    return len(p) == 4 and all(x and (not x.isdigit() or (int(x) <= 255 and (len(x) == 1 or x[0] != "0"))) for x in p)
for ad, mutant in [("256'ya izin veren", m_256), ("baştaki sıfırı kabul eden", m_sifir), ("3 parçayı kabul eden", m_parca), ("harfleri kabul eden", m_harf)]:
    kullanici["ip_gecerli_mi"] = mutant
    ok(not kos().wasSuccessful(), f"mutant öldürülmeli: {ad}")
kullanici["ip_gecerli_mi"] = dogru
```

```solution
import unittest

def ip_gecerli_mi(ip):
    p = ip.split(".")
    if len(p) != 4:
        return False
    for x in p:
        if not x.isdigit() or int(x) > 255 or (len(x) > 1 and x[0] == "0"):
            return False
    return True

class IpTestleri(unittest.TestCase):
    def test_gecerli(self):
        for ip in ["10.0.0.1", "0.0.0.0", "255.255.255.255"]:
            with self.subTest(ip=ip):
                self.assertTrue(ip_gecerli_mi(ip))

    def test_sinir_256(self):
        self.assertFalse(ip_gecerli_mi("256.0.0.1"))

    def test_bastaki_sifir(self):
        self.assertFalse(ip_gecerli_mi("01.2.3.4"))

    def test_parca_sayisi(self):
        self.assertFalse(ip_gecerli_mi("1.2.3"))
        self.assertFalse(ip_gecerli_mi("1.2.3.4.5"))

    def test_harf(self):
        self.assertFalse(ip_gecerli_mi("1.2.3.a"))
```

```hint
Her mutant tek bir kuralı gevşetir. Her kural için o kuralı **tam sınırından** ihlal eden bir girdi dene: 256, "01", üç parça, harf.
```
:::

::: gorev Mock ile bildirim testi
`kritikleri_bildir(bildirici, olaylar)` fonksiyonu hazır ve doğru: sadece `seviye == "kritik"` olan olaylar için `bildirici.gonder("KRİTİK: <mesaj>")` çağırıyor. Bunun için `BildirimTestleri` adında bir `TestCase` yaz; gerçek bildirici yerine `unittest.mock.Mock` kullan.

Değerlendirme: testlerin doğru koda karşı geçmeli; şu üç mutanttan her birini yakalamalı: **her olayı** bildiren, **hiçbir şey** bildirmeyen ve mesajı **"KRİTİK:" öneki olmadan** gönderen.

```starter
import unittest
from unittest.mock import Mock

def kritikleri_bildir(bildirici, olaylar):
    for o in olaylar:
        if o["seviye"] == "kritik":
            bildirici.gonder(f"KRİTİK: {o['mesaj']}")

class BildirimTestleri(unittest.TestCase):
    pass
```

```test
import unittest, io
T = need("BildirimTestleri", "sınıf")
def kos():
    return unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(T))
dogru = kullanici["kritikleri_bildir"]
r = kos()
ok(r.testsRun >= 1, "en az bir test yaz", got=r.testsRun)
ok(r.wasSuccessful(), "doğru koda karşı testler geçmeli", got=f"{len(r.failures)} başarısız, {len(r.errors)} hata")
def m_hepsi(b, olaylar):
    for o in olaylar:
        b.gonder(f"KRİTİK: {o['mesaj']}")
def m_hic(b, olaylar):
    pass
def m_onek(b, olaylar):
    for o in olaylar:
        if o["seviye"] == "kritik":
            b.gonder(o["mesaj"])
for ad, mutant in [("her olayı bildiren", m_hepsi), ("hiç bildirmeyen", m_hic), ("öneksiz mesaj", m_onek)]:
    kullanici["kritikleri_bildir"] = mutant
    ok(not kos().wasSuccessful(), f"mutant öldürülmeli: {ad}")
kullanici["kritikleri_bildir"] = dogru
ok("Mock" in src, "unittest.mock.Mock kullan")
```

```solution
import unittest
from unittest.mock import Mock

def kritikleri_bildir(bildirici, olaylar):
    for o in olaylar:
        if o["seviye"] == "kritik":
            bildirici.gonder(f"KRİTİK: {o['mesaj']}")

class BildirimTestleri(unittest.TestCase):
    def test_sadece_kritikler(self):
        b = Mock()
        kritikleri_bildir(b, [
            {"seviye": "kritik", "mesaj": "disk dolu"},
            {"seviye": "bilgi", "mesaj": "yedek tamam"},
            {"seviye": "kritik", "mesaj": "servis düştü"},
        ])
        self.assertEqual(b.gonder.call_count, 2)
        b.gonder.assert_any_call("KRİTİK: disk dolu")
        b.gonder.assert_any_call("KRİTİK: servis düştü")

    def test_kritik_yoksa_sessiz(self):
        b = Mock()
        kritikleri_bildir(b, [{"seviye": "bilgi", "mesaj": "x"}])
        b.gonder.assert_not_called()
```

```hint
`b = Mock()` ver, fonksiyonu çağır, sonra `b.gonder.call_count`, `b.gonder.assert_any_call("KRİTİK: ...")` ve `b.gonder.assert_not_called()` ile doğrula.
```
:::

::: gorev Sınır değer tablosu
`port_sinifi(p)` hazır ve doğru (0–1023 `sistem`, 1024–49151 `kayitli`, 49152–65535 `dinamik`, diğerleri `ValueError`). `PortTestleri` adında, **`subTest`** ile tablo tabanlı bir `TestCase` yaz. Testlerin şu mutantları yakalamalı: 1023'ü `kayitli` sayan (sınır kaymış), 49152'yi `kayitli` sayan ve aralık dışı değerlerde hata yerine `"dinamik"` döndüren.

```starter
import unittest

def port_sinifi(p):
    if not 0 <= p <= 65535:
        raise ValueError(p)
    if p <= 1023:
        return "sistem"
    if p <= 49151:
        return "kayitli"
    return "dinamik"

class PortTestleri(unittest.TestCase):
    pass
```

```test
import unittest, io
T = need("PortTestleri", "sınıf")
def kos():
    return unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(T))
dogru = kullanici["port_sinifi"]
r = kos()
ok(r.testsRun >= 1 and r.wasSuccessful(), "doğru koda karşı testler geçmeli", got=f"{r.testsRun} test, {len(r.failures)} başarısız, {len(r.errors)} hata")
def m_1023(p):
    if not 0 <= p <= 65535: raise ValueError(p)
    return "sistem" if p < 1023 else "kayitli" if p <= 49151 else "dinamik"
def m_49152(p):
    if not 0 <= p <= 65535: raise ValueError(p)
    return "sistem" if p <= 1023 else "kayitli" if p <= 49152 else "dinamik"
def m_aralik(p):
    return "sistem" if 0 <= p <= 1023 else "kayitli" if 1024 <= p <= 49151 else "dinamik"
for ad, mutant in [("1023 sınırı kaymış", m_1023), ("49152 sınırı kaymış", m_49152), ("aralık dışında hata vermeyen", m_aralik)]:
    kullanici["port_sinifi"] = mutant
    ok(not kos().wasSuccessful(), f"mutant öldürülmeli: {ad}")
kullanici["port_sinifi"] = dogru
ok("subTest" in src, "subTest kullan")
```

```solution
import unittest

def port_sinifi(p):
    if not 0 <= p <= 65535:
        raise ValueError(p)
    if p <= 1023:
        return "sistem"
    if p <= 49151:
        return "kayitli"
    return "dinamik"

class PortTestleri(unittest.TestCase):
    def test_tablo(self):
        tablo = [(0, "sistem"), (1023, "sistem"), (1024, "kayitli"),
                 (49151, "kayitli"), (49152, "dinamik"), (65535, "dinamik")]
        for port, beklenen in tablo:
            with self.subTest(port=port):
                self.assertEqual(port_sinifi(port), beklenen)

    def test_aralik_disi(self):
        for port in (-1, 65536):
            with self.subTest(port=port):
                with self.assertRaises(ValueError):
                    port_sinifi(port)
```

```hint
Her sınırın **iki yanını** da test et: 1023 ve 1024, 49151 ve 49152, 65535 ve 65536.
```
:::
