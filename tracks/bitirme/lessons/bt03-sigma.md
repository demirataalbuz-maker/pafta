---
id: bt03
title: Sigma · Alarmı Etiketli Kontrol Grubuyla Ölç
summary: Uç nokta gözlemini kural metnine çevir; yanlış pozitif, kaçırma ve bilinmeyen etiketi ayır.
---

::: anlat Kural davranışı seçer, niyeti kanıtlamaz
İkinci soru: endpoint olaylarında Image alanı `\powershell.exe` ile biten ve CommandLine içinde `\health.ps1` geçen kayıtlar hangileri? Bakım betiği meşru olabilir; bu bir **inceleme seçicisi**. Logsource product windows/category process_creation, alanların gerçekten bu kaynaktan geldiğini varsayar. `v.sigma(kural,rows)` routing yapmaz; kaynağı önce doğru seçmek senin sorumluluğun. Gerçek pySigma YAML ayrıştırılır; mevcut yerel backend modifier/condition mantığını olaylarda yürütür. Gerçek SIEM pipeline/dağıtımı veya Sigma correlation yürütülmez.

Image sonundaki ters bölü işareti önemli: notpowershell.exe aynı binary adı değildir. Bu görev CommandLine ayrıştırıcısı yazmaz; belirtilen substring sözleşmesidir. Tırnak, argüman kodlama veya farklı script yolu için kapsam boşluğu raporlanmalı. Varsayılan Sigma metin eşleşmesi harf duyarsızdır; cased eklemek davranışı değiştirir. [Sigma kural biçimi](https://sigmahq.io/docs/basics/rules.html), [modifier'lar](https://sigmahq.io/docs/basics/modifiers.html).
:::

::: tahmin
```python
import vaka_lab as v
rows=[r for r in v.yukle() if r['source']=='endpoint']
print([r['id'] for r in rows])
print(len(rows))
```

???
`['p-run', 'p-maint', 'p-otherimage']` ve `3`. Kaynak seçmek, kuralın eşleşme seçimi değildir.
:::

::: gorev İnceleme seçicisini Sigma olarak yaz
`kural()` YAML metni döndürsün. Image endswith `\powershell.exe` ve CommandLine contains `\health.ps1`; iki koşul birlikte. logsource product windows, category process_creation. Native kural varsayılan harf davranışını koru. Sabit id listesi yazma.

```starter
def kural():
    return 'title: Eksik'
```

```test
import vaka_lab as v
from sandbox.sigma_engine import SigmaProgram
p=SigmaProgram(kural()).rules[0].rule
eq(p.logsource.product,'windows','kaynak ürün')
eq(p.logsource.category,'process_creation','kaynak kategori')
rows=[r for r in v.yukle() if r['source']=='endpoint']
eq(v.sigma(kural(),rows),['p-run'],'binary ve script koşulu')
base=dict(rows[0],id='renamed')
eq(v.sigma(kural(),[dict(base,Image=base['Image'].upper(),CommandLine=base['CommandLine'].upper())]),['renamed'],'Sigma harf duyarsızlığı')
eq(v.sigma(kural(),[dict(base,Image=r'C:\Lab\notpowershell.exe')]),[],'son binary bileşeni')
eq(v.sigma(kural(),[dict(base,CommandLine='powershell.exe updates.ps1')]),[],'script koşulu zorunlu')
eq(v.sigma(kural(),[dict(base,Image=None),{k:x for k,x in base.items() if k!='CommandLine'}]),[],'eksik alan eşleşme değil')
eq(v.sigma(kural(),[dict(base,Image=base['Image']+'.bak')]),[],'binary uzantısı tam uç')
eq(v.sigma(kural(),[dict(base,CommandLine=base['CommandLine']+' -Mode Check')]),['renamed'],'script substring, sonda olmak zorunda değil')
eq(v.sigma(kural(),[]),[],'boş kaynak')
```

```solution
def kural():
    return r'''title: Pafta Bakim Betigi Incelemesi
logsource:
    product: windows
    category: process_creation
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains: '\health.ps1'
    condition: selection
'''
```

```hint
Tek seçim sözlüğündeki farklı alanlar AND'dir. YAML'da tek tırnak ters bölüyü korur.
```
:::

::: anlat Etiketi ve ölçüm kapsamını kaydet
Etiketli doğrulama setinde positive/negative seçicinin hedef davranışına göre tanımlanır; “zararlı” anlamına otomatik gelmez. unknown, analistin henüz sınıflamadığı kayıttır. Unknown'u negative saymak precision'ı yanlış düşürür; tamamen saklamak da kapsamı olduğundan iyi gösterir. Bu yüzden unknown eşleşmeler ayrıca sayılır. Precision=TP/(TP+FP), recall=TP/(TP+FN). Payda sıfırsa yüzde yüz uydurmak yerine None üret.

Bu oranlar yalnız bu küçük etiketli korpusa aittir; üretim başarısı veya alarm hacmi tahmini değildir. Üretim kabulünde temsilî pozitif/negatif kayıt, sensör eksikliği, performans ve analist incelemesi de gerekir.
:::

::: gorev Bilinmeyeni başarı saymadan ölç
`olc(hits,labels)` tekrarlı hit'leri tek saysın. labels id→positive/negative/unknown. Tanınmayan hit veya etiket ValueError. Çıktı tp/fp/fn/unknown_hits/precision/recall. Unknown ne FP ne FN olsun. Precision/recall float veya payda sıfırsa None.

```starter
def olc(hits, labels):
    return {}
```

```test
eq(olc(['a','a','b','u'],{'a':'positive','b':'negative','c':'positive','u':'unknown'}),{'tp':1,'fp':1,'fn':1,'unknown_hits':1,'precision':0.5,'recall':0.5},'tekrar, kaçırma ve bilinmeyen')
eq(olc([],{}),{'tp':0,'fp':0,'fn':0,'unknown_hits':0,'precision':None,'recall':None},'boş ölçüm başarı değil')
eq(olc(['a'],{'a':'positive'})['recall'],1.0,'tam yakalama')
eq(olc([],{'a':'positive'})['recall'],0.0,'tam kaçırma')
raises(ValueError,lambda:olc(['x'],{}),msg='bilinmeyen kanıt id')
raises(ValueError,lambda:olc([],{'a':'maybe'}),msg='etiket sözleşmesi')
```

```solution
def olc(hits,labels):
    h=set(hits)
    if h-set(labels) or set(labels.values())-{'positive','negative','unknown'}:raise ValueError('Etiket uyuşmazlığı')
    p={k for k,v in labels.items() if v=='positive'}
    n={k for k,v in labels.items() if v=='negative'}
    tp=len(h&p);fp=len(h&n);fn=len(p-h)
    return dict(tp=tp,fp=fp,fn=fn,unknown_hits=len(h-p-n),precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None)
```

```hint
Kümeler tekrarları kaldırır. Unknown için ayrı sayaç tut; sıfır payda ölçüm olmadığını gösterir.
```
:::
