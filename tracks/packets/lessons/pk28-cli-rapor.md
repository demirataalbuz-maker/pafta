---
id: pk28
title: TShark CLI · Alan, İstatistik ve Kayıt Raporu
summary: -T fields/-e, protokol hiyerarşisi ve filtrelenmiş PCAPNG çıktısı üret.
---

::: anlat Komutun girdisi, filtresi ve çıktısı
`-r secili` eğitim kaydını okur. `-Y` görüntü filtresidir; canlı yakalama filtresi `-f` ile aynı dil değildir. `-T fields` ve tekrarlanan `-e` alan sütunlarını seçer; varsayılan ayırıcı sekmedir. Alan yokluğu boş hücre üretebilir. `-E header=y`, `-E separator=,` gibi seçenekler biçimi değiştirir; aşağıdaki görevler başlıksız, sekmeli çıktı ister.

`-q -z io,phs` protokol hiyerarşisini sayar. Bu bir uygulama olay sayacı değildir: katmanlar iç içe olduğundan satırları toplayıp paket sayısı üretme. `-w sonuc.pcapng -F pcapng`, seçilen frame'leri yeni kayıt olarak yazar; HTTP nesnesi çıkarmakla aynı işlem değildir. Yeni kayıttaki frame numaraları baştan başlar. Kaydı yalnız sonuca göre kesersen yeniden birleştirme ve akış bağlamını kaybedebilirsin.

Kaynak: [TShark CLI](https://www.wireshark.org/docs/man-pages/tshark.html).
```tshark
tshark -r secili -q -z io,phs
```
```meta
dil: tshark
```
```stdin
{"dil": "tshark", "kayit": "olay"}
```
:::

::: tahmin
401 yanıtlarını frame ve kod alanlarıyla raporlayan komut ne yazar?
```tshark
tshark -r secili -Y "http.response.code == 401" -T fields -e frame.number -e http.response.code
```
```meta
dil: tshark
```
```stdin
{"dil": "tshark", "kayit": "olay"}
```
???
7	401
13	401
24	401
Sütunlar sekmeyle ayrılır; farklı istemci ve sunucuların yanıtları da bu kayıtta 401 olabilir.
:::

::: gorev 401 yanıtlarını iki sütunla raporla
Yalnız HTTP yanıt kodu 401 olan frame'lerin numarasını ve yanıt kodunu bu sırayla, başlıksız ve sekmeyle ayrılmış yazdır.
```starter
tshark -r secili -q
```
```meta
dil: tshark
```
```stdin
{"dil": "tshark", "kayit": "olay"}
```
```test
eq(calistir()["stdout"].splitlines(),["7	401","13	401","24	401"],"olay kaydı")
eq(calistir("sinirlar")["stdout"].splitlines(),["43	401"],"400/401/402 durum komşuları")
eq(calistir("temel")["stdout"].splitlines(),["20	401"],"başka frame numarası")
```
```solution
tshark -r secili -Y "http.response.code == 401" -T fields -e frame.number -e http.response.code
```
```hint
Komutu açıklanan gerçek seçeneklerle kur; sonuç alanları native araç çıktısından gelir.
```
:::

::: gorev Protokol hiyerarşisi özeti
Paket özetlerini sustur ve bütün seçili kayıt için gerçek protocol hierarchy istatistiği üret.
```starter
tshark -r secili -q
```
```meta
dil: tshark
```
```stdin
{"dil": "tshark", "kayit": "olay"}
```
```test
import re
for name,count in (("olay",25),("temel",24),("sinirlar",50)):
    out=calistir(name)["stdout"]
    ok(out.strip().splitlines()[0].startswith("==="),"paket özet satırları susturuldu")
    ok("Protocol Hierarchy Statistics" in out,"gerçek hiyerarşi başlığı")
    ok(re.search(r"(?m)^frame\s+frames:"+str(count)+r"\b",out) is not None,"native frame sayısı")
```
```solution
tshark -r secili -q -z io,phs
```
```hint
Komutu açıklanan gerçek seçeneklerle kur; sonuç alanları native araç çıktısından gelir.
```
:::

::: gorev Yalnız 4xx yanıtlarını yeni kayda yaz
400–499 dahil HTTP yanıtlarını sonuc.pcapng dosyasına PCAPNG biçiminde yaz. 500 ve 501 dahil olmasın.
```starter
tshark -r secili -q
```
```meta
dil: tshark
```
```stdin
{"dil": "tshark", "kayit": "sinirlar"}
```
```test
import base64
import packet_engine as pe
for name,count in (("sinirlar",4),("olay",4),("temel",3)):
    r=calistir(name)
    eq(len(r["exports"]),1,"tek çıktı kaydı")
    if r["exports"]:
        raw=base64.b64decode(r["exports"][0]["base64"])
        eq(raw[:4],b"\x0a\x0d\x0d\x0a","gerçek PCAPNG magic")
        eq(len(pe.pcap_lengths(raw)),count,"seçili 4xx sayısı")
        eq(pe.evaluate("http.response.code >= 400 and http.response.code <= 499",raw),list(range(1,count+1)),"bütün çıktı frame'leri doğru aralıkta")
import packet_fixtures as pf
frames=[]
for i,status in enumerate((399,400,401,498,499,500)):
    data=f"HTTP/1.1 {status} Training\r\nContent-Length: 0\r\n\r\n".encode()
    tcp=pf.tcp(80,55000+i,data,src=pf.SERVER,dst=pf.CLIENT,flags=0x18)
    packet=pf.ethernet(pf.ipv4(tcp,pf.SERVER,pf.CLIENT,6))
    frames.append((packet,len(packet)))
r=calistir(pf.pcap_bytes(frames))
eq(len(r["exports"]),1,"bağımsız eşik kaydı")
if r["exports"]:
    raw=base64.b64decode(r["exports"][0]["base64"])
    eq(len(pe.pcap_lengths(raw)),4,"399/400/401 ve 498/499/500 komşuları")
    eq(pe.evaluate("http.response.code >= 400 and http.response.code <= 499",raw),[1,2,3,4],"tam 4xx sınırları")
```
```solution
tshark -r secili -Y "http.response.code >= 400 and http.response.code <= 499" -w sonuc.pcapng -F pcapng
```
```hint
Komutu açıklanan gerçek seçeneklerle kur; sonuç alanları native araç çıktısından gelir.
```
:::
