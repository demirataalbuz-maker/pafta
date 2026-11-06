---
id: pu18
title: Nmap · Kendi Servisini Keşfet ve Değişimi Kanıtla
summary: Gerçek Nmap TCP connect taraması; görünür XML, iki yerel HTTP servisi, kapatma sonrası fark ve belirsiz port durumları. Keşif → Blue doğrulama döngüsünün ilk alt dersi.
timeout: 55
---

::: anlat Önce ham veriyi gör
Bu ders `plan-klasik-1` ve Purple M2 keşif kapsamının **Nmap alt işidir**. ffuf, nuclei, web exploitation ve GoPhish bu dersle tamamlanmaz. pu11 web kanıtına ve pu14 web triyajına geçmeden önce hangi servisin erişilebilir olduğunu ölçersin.

`kesif/ornek.xml` sentetik ve açılabilir bir öğrenci dosyasıdır; testin gizli girdisi değildir. Dosyayı `Path('kesif/ornek.xml').read_text(encoding='utf-8')` ile okuyup print et. Setup her çalıştırmada yeni geçici kopya oluşturur; değişiklik sonraki çalıştırmaya taşınmaz. Dosyayı aynı çalıştırmada değiştirerek parser'ını dene. Örnek verinin düzenlenmesi gizli test sonucunu değiştirmez.

Gerçek son görev kurulu Nmap'i PATH üzerinden bulur. İndirme yapmaz; Nmap yoksa deney hata verir, PASS olmaz. `-sT` TCP connect, `-Pn` host discovery yapmama, `-n` DNS çözmeme, `-p` yalnız kendi portları, `-oX -` XML'i stdout'a yazmadır. SYN scan, OS fingerprint ve sürüm tespiti bu ölçümün kapsamı değildir.

Resmî kaynaklar: [XML interface](https://nmap.org/book/output-formats-xml-output.html), [port states](https://nmap.org/book/man-port-scanning-basics.html). Araç sürümü gerçek kanıta yazılır; buradaki kurulu 7.80 en yeni sürüm iddiası değildir.
:::

::: gorev 1 · XML içindeki explicit TCP portlarını oku
`xml_coz(metin)` → `{int_port: state}`. Yalnız `nmaprun/host/ports/port` içindeki protocol=tcp kayıtlarını oku; UDP'yi atla. Root yanlışsa, port 1–65535 dışında veya tekrarsa, state eksik/boşsa ValueError. Bozuk XML parser hatası verebilir. `extraports` özetini tahminle portlara genişletme; bu dersin girdileri explicit port listesidir.

```starter
def xml_coz(metin):
    return {18080:'open'}
```

```test
need('xml_coz')
from pathlib import Path
eq(xml_coz(Path('kesif/ornek.xml').read_text()),{18080:'open',18081:'filtered'},'görünür XML; UDP ayrılır')
import random
for i in range(8):
    p=random.randint(1000,60000);s=random.choice(['open','closed','filtered'])
    x=f'<nmaprun><host><ports><port portid="{p}" protocol="tcp"><state state="{s}"/></port></ports></host></nmaprun>'
    eq(xml_coz(x),{p:s},'görülmemiş port/durum')
eq(xml_coz('<nmaprun/>'),{},'explicit port yok; extraports genişletilmez')
for port in (1,65535):
    x=f'<nmaprun><host><ports><port portid="{port}" protocol="tcp"><state state="closed"/></port></ports></host></nmaprun>'
    eq(xml_coz(x),{port:'closed'},'geçerli port sınırları')
for ports in ('<port portid="65536" protocol="tcp"><state state="open"/></port>',
              '<port portid="7" protocol="tcp"/>',
              '<port portid="7" protocol="tcp"><state state=""/></port>',
              '<port portid="7" protocol="tcp"><state state="open"/></port>'*2):
    raises(ValueError,xml_coz,'<nmaprun><host><ports>'+ports+'</ports></host></nmaprun>',msg='bozuk/tekrar TCP port ret')
raises(ValueError,xml_coz,'<baska/>',msg='yanlış root ret')
raises(ValueError,xml_coz,'<nmaprun><host><ports><port protocol="tcp" portid="0"><state state="open"/></port></ports></host></nmaprun>',msg='port sınırı')
```

```solution
def xml_coz(metin):
    import xml.etree.ElementTree as ET
    root=ET.fromstring(metin)
    if root.tag!='nmaprun':raise ValueError('nmaprun gerekli')
    out={}
    for p in root.findall('./host/ports/port'):
        if p.get('protocol')!='tcp':continue
        port=int(p.attrib['portid']);state=p.find('state')
        if not 1<=port<=65535 or port in out or state is None or not state.get('state'):raise ValueError('bozuk veya tekrar port')
        out[port]=state.get('state')
    return out

from pathlib import Path
print(Path("kesif/ornek.xml").read_text(encoding="utf-8"))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_nmap_lab import hazirla
hazirla()
```

```hint
Önce ham dosyayı oku; tek örneğin portunu ezberleme. Sözlük ve sıralı port birleşimini kullan.
```
:::

::: gorev 2 · İki gözlemin farkını çıkar
`degisim(once,sonra)` port sırasına göre değişen kayıtları `[{'port':p,'once':eski,'sonra':yeni}]` olarak döndürsün. Bir haritada olmayan port `yok` sayılır. Aynı durumları yazma. filtered metnini değiştirme.

```starter
def degisim(once,sonra):
    return []
```

```test
need('degisim')
eq(degisim({2:'open',1:'filtered'},{2:'closed',3:'open'}),[{'port':1,'once':'filtered','sonra':'yok'},{'port':2,'once':'open','sonra':'closed'},{'port':3,'once':'yok','sonra':'open'}],'ekleme/silme/değişim sıralı')
eq(degisim({7:'open'},{7:'open'}),[],'aynı durum değişim değil')
for p in (13,971,43123):
    eq(degisim({p:'open'},{p:'filtered'}),[{'port':p,'once':'open','sonra':'filtered'}],'filtered olduğu gibi korunur')
```

```solution
def degisim(once,sonra):
    return [{'port':p,'once':once.get(p,'yok'),'sonra':sonra.get(p,'yok')}
            for p in sorted(set(once)|set(sonra)) if once.get(p,'yok')!=sonra.get(p,'yok')]

from pathlib import Path
print(Path("kesif/ornek.xml").read_text(encoding="utf-8"))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_nmap_lab import hazirla
hazirla()
```

```hint
Önce ham dosyayı oku; tek örneğin portunu ezberleme. Sözlük ve sıralı port birleşimini kullan.
```
:::

::: gorev 3 · Bilmediğini açıkça söyle
`karar(state)`: open→acik; closed→kapali; filtered/unfiltered/open|filtered/closed|filtered→belirsiz; diğer metin→ValueError. Bu sınıflama rapor özetidir; ham state ayrıca korunur.

```starter
def karar(state):
    return 'kapali'
```

```test
need('karar')
for s,w in [('open','acik'),('closed','kapali'),('filtered','belirsiz'),('unfiltered','belirsiz'),('open|filtered','belirsiz'),('closed|filtered','belirsiz')]:eq(karar(s),w,'state: '+s)
for s in ('','OPEN','error'):raises(ValueError,karar,s,msg='bilinmeyen state ret')
```

```solution
def karar(state):
    if state=='open':return 'acik'
    if state=='closed':return 'kapali'
    if state in ('filtered','unfiltered','open|filtered','closed|filtered'):return 'belirsiz'
    raise ValueError('bilinmeyen state')

from pathlib import Path
print(Path("kesif/ornek.xml").read_text(encoding="utf-8"))
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_nmap_lab import hazirla
hazirla()
```

```hint
Önce ham dosyayı oku; tek örneğin portunu ezberleme. Sözlük ve sıralı port birleşimini kullan.
```
:::

::: anlat Hata vitrini · filtered kapalı demek değildir
Nmap state, tarayıcının gördüğü sonuçtur. `filtered/no-response` gördüğünde “servis kesin kapalı” deme. Bu Windows makinesindeki ilk gerçek sonda, dinleyicisi olmayan porta filtered yazdı; stderr ayrıca eski Npcap işlevleri için uyarı verdi. Uyarı saklanır; firewall veya Npcap kendiliğinden değiştirilmez. TCP connect ile dinleme durumunu ayrıca kontrol ederiz. Bu iki ölçüm aynı şey değildir.

Servise HTTP GET gönderip rastgele canary'yi okuruz; ardından Nmap yalnız kendi üç portumuzu tarar. İki servisten birini kapatıp yeniden tararız. Kalan servis kontrol grubudur. Nmap portu open görmüyorsa veya kapatma gözlemde fark üretmiyorsa ortam deneyi kabul edilmez; filtered sonucu closed diye düzeltilmez. Sunucu kendi bağlantı gözlemini de saklar; bu Sysmon/PCAP veya tam Blue IDS kanıtı değildir. Böyle bir entegrasyon M2'nin kalan işidir.
:::

::: gorev 4 · Gerçek Nmap ile önce/sonra ölç
Önceki üç fonksiyonu birleştir. Alttaki `calistir` satırını koru: Çalıştır gerçek Nmap'i çağırıp deneme kanıtını, Kontrol ise ayrıca kabul kanıtını yazar. İki çağrı da kendi 127.0.0.1 HTTP sunucularını açıp kapatır; kullanıcı servislerine dokunmaz. Rasgele port/canary kullanılır. Ham XML, stderr, sürüm, binary hash, ayarlar, HTTP kontrolü, TCP ground truth ve cleanup kanıt dosyasında tutulur; dosyanın yolu çıktıda görünür. Deneme çıktısı tek başına kabul değildir.

Kurulum/silme yok. Bu görev keşiftir; açık port bir vulnerability kanıtı değildir. ffuf/nuclei için ayrı araç kabulü ve kapsam gerekir.

```starter
def xml_coz(metin):return {}
def degisim(once,sonra):return []
def karar(state):return "kapali"
```

```solution
def xml_coz(metin):
    import xml.etree.ElementTree as ET
    root=ET.fromstring(metin)
    if root.tag!='nmaprun':raise ValueError('nmaprun gerekli')
    out={}
    for p in root.findall('./host/ports/port'):
        if p.get('protocol')!='tcp':continue
        port=int(p.attrib['portid']);state=p.find('state')
        if not 1<=port<=65535 or port in out or state is None or not state.get('state'):raise ValueError('bozuk veya tekrar port')
        out[port]=state.get('state')
    return out

def degisim(once,sonra):
    return [{'port':p,'once':once.get(p,'yok'),'sonra':sonra.get(p,'yok')}
            for p in sorted(set(once)|set(sonra)) if once.get(p,'yok')!=sonra.get(p,'yok')]

def karar(state):
    if state=='open':return 'acik'
    if state=='closed':return 'kapali'
    if state in ('filtered','unfiltered','open|filtered','closed|filtered'):return 'belirsiz'
    raise ValueError('bilinmeyen state')

from purple_nmap_lab import calistir
calistir(xml_coz,degisim,karar)
```

```test
need('xml_coz');need('degisim');need('karar')
from purple_nmap_lab import kod_koruma,calistir
ok(kod_koruma(src),'kaynak koruması: oracle/import/introspection kopyası yok')
if not kod_koruma(src):stop()
need('xml_coz')
from pathlib import Path
eq(xml_coz(Path('kesif/ornek.xml').read_text()),{18080:'open',18081:'filtered'},'görünür XML; UDP ayrılır')
import random
for i in range(8):
    p=random.randint(1000,60000);s=random.choice(['open','closed','filtered'])
    x=f'<nmaprun><host><ports><port portid="{p}" protocol="tcp"><state state="{s}"/></port></ports></host></nmaprun>'
    eq(xml_coz(x),{p:s},'görülmemiş port/durum')
eq(xml_coz('<nmaprun/>'),{},'explicit port yok; extraports genişletilmez')
for port in (1,65535):
    x=f'<nmaprun><host><ports><port portid="{port}" protocol="tcp"><state state="closed"/></port></ports></host></nmaprun>'
    eq(xml_coz(x),{port:'closed'},'geçerli port sınırları')
for ports in ('<port portid="65536" protocol="tcp"><state state="open"/></port>',
              '<port portid="7" protocol="tcp"/>',
              '<port portid="7" protocol="tcp"><state state=""/></port>',
              '<port portid="7" protocol="tcp"><state state="open"/></port>'*2):
    raises(ValueError,xml_coz,'<nmaprun><host><ports>'+ports+'</ports></host></nmaprun>',msg='bozuk/tekrar TCP port ret')
raises(ValueError,xml_coz,'<baska/>',msg='yanlış root ret')
raises(ValueError,xml_coz,'<nmaprun><host><ports><port protocol="tcp" portid="0"><state state="open"/></port></ports></host></nmaprun>',msg='port sınırı')

need('degisim')
eq(degisim({2:'open',1:'filtered'},{2:'closed',3:'open'}),[{'port':1,'once':'filtered','sonra':'yok'},{'port':2,'once':'open','sonra':'closed'},{'port':3,'once':'yok','sonra':'open'}],'ekleme/silme/değişim sıralı')
eq(degisim({7:'open'},{7:'open'}),[],'aynı durum değişim değil')
for p in (13,971,43123):
    eq(degisim({p:'open'},{p:'filtered'}),[{'port':p,'once':'open','sonra':'filtered'}],'filtered olduğu gibi korunur')

need('karar')
for s,w in [('open','acik'),('closed','kapali'),('filtered','belirsiz'),('unfiltered','belirsiz'),('open|filtered','belirsiz'),('closed|filtered','belirsiz')]:eq(karar(s),w,'state: '+s)
for s in ('','OPEN','error'):raises(ValueError,karar,s,msg='bilinmeyen state ret')

k=calistir(xml_coz,degisim,karar,kabul=True)
eq(k['kaynak'],'gercek','fixture değil gerçek araç')
ok(k['kabul'],'gerçek ölçüm kabulü')
ok(k['cleanup']['own_threads_stopped'],'yalnız kendi kaynakları kapandı')
```

```setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.modules["__main__"].__file__).resolve().parent))
from purple_nmap_lab import hazirla
hazirla()
```

```meta
timeout: 55
```

```hint
Üç görevin çözümünü birleştir; son çağrıyı koru. Uyarı ve filtered durumunu ham kayıtta incele.
```
:::
