---
id: pk24
title: Follow Stream ve HTTP Nesnesini Çıkarmak
summary: İki geçişli gerçek TShark komutuyla sırasız veriyi birleştir ve tam gövdeyi doğrula.
---

::: anlat Filtre editöründen gerçek CLI komutuna
Bu derste editöre bir TShark komutu yazılır; girdi `dil:tshark`tır. `-r secili`, JSON'da seçilen eğitim kaydının geçici kopyasıdır. `-2` iki geçişli analiz, `-q -z follow,tcp,ascii,0` akış 0'ın iki yönünü gösterir. Akış kimliği yalnız bu kayıt için anlamlıdır; iki yön Follow Stream çıktısında farklı girintilerle ayrılır.

```packets
tshark -r secili -2 -q -z follow,tcp,ascii,0
```

`tcp.reassemble_out_of_order:TRUE` sırasız segmentlerin uygulama ayrıştırıcısına verilmesini sağlar. Bu tercih eksik baytları yaratmaz. `--export-objects http,sonuc` HTTP nesnelerini geçici klasöre çıkarır; tezgâh dosya adı, boyut, SHA256, base64 ve metin önizlemesini `exports` alanında döndürür. Kalıcı disk yolu seçilmez. Komutlar kabuktan geçmez; destek dışı seçenekler açık hata verir. Dışarıdan keylog yolu, program çalıştırma veya canlı arayüz bu komut editöründen açılmaz.

Kaynak: [TShark -2, -z ve --export-objects](https://www.wireshark.org/docs/man-pages/tshark.html), [TCP yeniden birleştirme](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvReassemblySection.html).
```meta
dil: tshark
```
```stdin
{"dil":"tshark","kayit":"tcp-sirasiz"}
```
:::

::: tahmin
Sırasız kayıt doğru tercihle yeniden birleştirilince HTTP yanıtı hangi frame'de tamamlanır?
```packets
tshark -r secili -2 -o tcp.reassemble_out_of_order:TRUE -Y http.response -T fields -e frame.number
```
```meta
dil: tshark
```
```stdin
{"dil":"tshark","kayit":"tcp-sirasiz"}
```
???
8
Sonradan gelen orta segmentle mesaj tamamlanır. Bu sayının diğer kayıtlar için sabit olduğunu varsayma.
:::

::: gorev Yanıtın tamamlandığı frame'i raporla
Gerçek TShark komutuyla sırasız yeniden birleştirmeyi aç, iki geçişli analiz yap, yalnız HTTP yanıtlarını seç ve yalnız `frame.number` alanını yazdır.
```starter
tshark -r secili -Y frame.number==0 -T fields -e frame.number
```
```meta
dil: tshark
```
```stdin
{"dil":"tshark","kayit":"tcp-sirasiz"}
```
```test
eq(calistir()["stdout"].splitlines(),["8"],"sırasız orta segment")
eq(calistir("tcp-tam")["stdout"].splitlines(),["7"],"normal sıra")
eq(calistir("tcp-tekrar")["stdout"].splitlines(),["7"],"tekrar ikinci HTTP yanıtı üretmez")
eq(calistir("tcp-kayip")["stdout"].splitlines(),[],"eksik gövde tamamlanmaz")
```
```solution
tshark -r secili -2 -o tcp.reassemble_out_of_order:TRUE -Y http.response -T fields -e frame.number
```
```hint
-Y görüntü filtresi, -T fields çıktı biçimi, -e alan seçimidir. Sırasız yeniden birleştirme tercihini ekle.
```
:::

::: gorev Gövdenin tam baytlarını çıkar
İki geçişli analiz ve sırasız yeniden birleştirme ile HTTP nesnesini `sonuc` klasörüne çıkar; paket özetini sustur. Tam ve tekrarlı kayıtta da tek, doğru nesne; eksik kayıtta hiç nesne çıkmalı.
```starter
tshark -r secili -q
```
```meta
dil: tshark
```
```stdin
{"dil":"tshark","kayit":"tcp-sirasiz"}
```
```test
import base64,hashlib
for name in ("tcp-sirasiz","tcp-tam","tcp-tekrar"):
    result=calistir(name)
    eq(result["stdout"],"","özet susturuldu: "+name)
    eq(len(result["exports"]),1,"tek nesne: "+name)
    if result["exports"]:
        obj=result["exports"][0]
        eq(base64.b64decode(obj["base64"]),b"PAFTA-TCP-LAB","13 gerçek bayt")
        eq(obj["sha256"],hashlib.sha256(b"PAFTA-TCP-LAB").hexdigest(),"bağımsız özet")
eq(calistir("tcp-kayip")["exports"],[],"eksik gövde dosya değildir")
```
```solution
tshark -r secili -2 -o tcp.reassemble_out_of_order:TRUE -q --export-objects http,sonuc
```
```hint
--export-objects http,sonuc kullan; -w paket kaydı yazar, HTTP gövdesi çıkarmaz.
```
:::
