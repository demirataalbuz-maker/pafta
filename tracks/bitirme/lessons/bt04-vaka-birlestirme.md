---
id: bt04
title: Paket Kanıtı ve Uçtan Uca İnceleme
summary: Gerçek TShark filtresini aynı vaka aramalarıyla birleştir; ortak zaman çizelgesi üret, nedensellik uydurma.
---

::: anlat Ağ gözlemi neyi kanıtlar?
Vaka envanteri ws01 için 10.0.0.10 adresini verir. PCAP'te aynı URI başka istemciden, aynı istemciden farklı host'a ve benzer ama farklı dosya adına da istenmiştir. Yalnız ilgili isteği ayırmak için kaynak IP, HTTP Host ve URI birlikte gerekir. PCAP yalnız istek içerir; yanıt, gövde veya dosya özeti yoktur. Proxy kaydındaki 200 ayrı bir sensör gözlemidir; paket kaydında 200 gördüğünü söyleme. Bir isteğin görülmesi, indirilen baytların çalıştırıldığını veya veri sızdırıldığını kanıtlamaz.

`v.paketler(filtre,raw=None)` gerçek TShark görüntü filtresi yürütür. raw verilmezse vaka.pcap kullanılır. `v.paket_zamanlari(frame_ids)` kayıt başlıklarındaki zamanı okur ve vaka başlangıcına göre `(saniye,"vaka.pcap#frame=N")` verir; manifestte yazılı açıklamayı paket zamanı yerine kullanmaz. TShark yoksa açık hata alınır. Canlı arayüz açılmaz. [TShark -r, -Y ve alan çıktısı](https://www.wireshark.org/docs/man-pages/tshark.html).
:::

::: tahmin
```python
import vaka_lab as v
ids=v.paketler('http.request.uri == "/health.ps1"')
print(ids)
print(v.paket_zamanlari([1]))
```

???
`[1, 2, 4]` ve `[(130.0, 'vaka.pcap#frame=1')]`. URI tek başına cihaz ve Host bağlamını seçmez.
:::

::: gorev İlgili HTTP isteğinin filtresini yaz
`filtre()` kaynak IPv4 10.0.0.10, HTTP Host updates.lab.test ve tam URI /health.ps1 olan isteğin görüntü filtresini döndürsün. Alanlar native TShark anlamıyla karşılaştırılır. Frame numarasını koda gömme.

```starter
def filtre():
    return 'http.request'
```

```test
import vaka_lab as v
from pathlib import Path
from sandbox.capture_formats import parse_capture
from sandbox.packet_fixtures import pcap
raw=Path('vaka.pcap').read_bytes()
eq(v.paketler(filtre(),raw),[1],'üç koşul birlikte')
frames=parse_capture(raw)
eq(v.paketler(filtre(),pcap([f.data for f in reversed(frames)])),[4],'frame sırası ezberlenmez')
eq(v.paketler(filtre(),pcap([frames[0].data,frames[0].data])),[1],'aynı TCP segmenti tekrar iletim; ikinci HTTP isteği sayılmaz')
eq(v.paketler(filtre(),pcap([frames[1].data,frames[2].data,frames[3].data])),[],'komşu olumsuzlar')
```

```solution
def filtre():
    return 'ip.src == 10.0.0.10 and http.host == "updates.lab.test" and http.request.uri == "/health.ps1"'
```

```hint
Tam URI kıyası .bak dosyasını dışarıda bırakır. IP ve Host aynı kanıt alanı değildir.
```
:::

::: gorev İncelemeyi tek işlevde yeniden üret
`incele(kq,sq,sg,df,rows=None)` verilen KQL/SPL metinlerini v.sorgu ile, Sigma'yı yalnız endpoint kaynağı üzerinde, filtreyi paketlerde çalıştırsın. rows yoksa v.yukle(). KQL/SPL id kümeleri farklıysa ValueError; hata veya uyumsuzluğu boş/temiz rapora çevirme. Çıktı auth, process, frames ve timeline anahtarlarıdır: ilk ikisi sıralı tekrarsız id'ler, frames native sıra; timeline auth ve process kayıtlarının `(ts,source:id)` ve seçili frame zamanlarının birleşimi, zaman/kanıt kimliği sıralı. Bu bir sorgu sonucu birleştirmesidir; nedensellik kararı vermez.

```starter
def incele(kq,sq,sg,df,rows=None):
    return {}
```

```test
import vaka_lab as v
kq='olaylar | where source == "auth" and host == "ws01" and user == "alice" and outcome == "failure" and ts >= 0 and ts <= 120 | project id'
sq='sourcetype=olaylar | where source="auth" AND host="ws01" AND user="alice" AND outcome="failure" AND ts>=0 AND ts<=120 | table id'
sg="""title: Vaka
logsource:
    product: windows
    category: process_creation
detection:
    s:
        Image|endswith: '\\powershell.exe'
        CommandLine|contains: '\\health.ps1'
    condition: s
"""
df='ip.src == 10.0.0.10 and http.host == "updates.lab.test" and http.request.uri == "/health.ps1"'
r=incele(kq,sq,sg,df)
eq(r,{'auth':['a-edge','a-mid','a-start'],'process':['p-run'],'frames':[1],'timeline':[(0,'auth:a-start'),(60,'auth:a-mid'),(120,'auth:a-edge'),(130.0,'vaka.pcap#frame=1'),(135,'endpoint:p-run')]},'dört araç ve tek zaman çizelgesi')
rows=v.yukle()
extra=dict(next(r for r in rows if r['id']=='p-run'),id='auth-fake',source='auth')
eq(incele(kq,sq,sg,df,rows+[extra])['process'],['p-run'],'Sigma kaynak yönlendirme')
renamed=[dict(r,id='new-'+r['id']) for r in rows]
eq(incele(kq,sq,sg,df,renamed)['process'],['new-p-run'],'gerçek girdiyi kullan')
raises(ValueError,lambda:incele(kq,'sourcetype=olaylar | table id',sg,df),msg='arama uyuşmazlığı')
empty=incele('olaylar | where ts > 999 | project id','sourcetype=olaylar | where ts>999 | table id',sg,df,[])
eq(empty['auth'],[],'boş sonuç yetkisiz başarı değil')
eq(empty['process'],[],'boş endpoint')
eq(empty['frames'],[1],'paket kanıtı bağımsız kalır')
```

```solution
import vaka_lab as v

def incele(kq,sq,sg,df,rows=None):
    rows=v.yukle() if rows is None else rows
    a={r['id'] for r in v.sorgu('kql',kq,rows)}
    b={r['id'] for r in v.sorgu('spl',sq,rows)}
    if a!=b:raise ValueError('Aramalar uyuşmuyor')
    ep=[r for r in rows if r['source']=='endpoint']
    p=set(v.sigma(sg,ep))
    frames=v.paketler(df)
    timeline={(r['ts'],r['source']+':'+r['id']) for r in rows if (r['source']=='auth' and r['id'] in a) or (r['source']=='endpoint' and r['id'] in p)}
    timeline.update(v.paket_zamanlari(frames))
    return dict(auth=sorted(a),process=sorted(p),frames=frames,timeline=sorted(timeline))
```

```hint
Her aracı çağır; sonuç kümelerini karşılaştır, kaynaklarını koru. İstek ve süreç gözlemi arasında dosya hash'iyle bağ kuramadığını rapora yaz.
```
:::

::: anlat İnceleme sonucu ve müdahale devri
Şu an doğrulananlar: belirtilen pencerede üç başarısız auth gözlemi; sağlanan paket kaydında ilgili istek; uç nokta kaynağında bakım scriptine işaret eden süreç kaydı. Başarılı giriş a-ok ayrıca incelenebilir, ancak bunların aynı oturum/ProcessGuid zincirinden geldiği kanıtlanmadı. İki saniyelik hata bütçesi içindeki yakın zamanları kesin sebep-sonuç diye sıralama.

Bir sonraki karar için bakım kaydı ve kullanıcı doğrulaması, süreç parent/ProcessGuid, dosya hash'i, oturum kimliği ve daha geniş cihaz kapsamı iste. Acil sınırlama gerekiyorsa olay sorumlusu hizmet etkisini değerlendirip yetkili playbook'u uygulamalı; bu ders hesap kapatmaz veya ağ izolasyonu yapmaz. Kanıt koruma ile değişiklik kaydını birbirine bağla. Bu ayrımı rapor dersinde sürdüreceksin.
:::
