---
id: pk29
title: Gerçek tcpdump · Loopback, Snaplen ve Dosya Döndürme
summary: Yalnız laboratuvarın kendi UDP çiftinde gerçek yakalama yap; kesme ve dosya boyutunu ölç.
---

::: anlat Yakalama filtresi kayıt oluşmadan uygulanır
Bu ders kurulu Kali WSL'de gerçek `tcpdump` çalıştırır. Dağıtım `PAFTA_WSL_DISTRO` ayarından okunur; varsayılan kali-linux. Yakalama için WSL'nin root kullanıcısı seçilir. Çalışma klasörü Linux `/tmp` altındadır ve işlem sonunda temizlenir. Fiziksel arayüz seçilmez: yalnız lo üzerinde laboratuvarın açtığı iki rastgele localhost UDP portu toplanır. Öğrencinin BPF ifadesine bu uç çifti zorunlu `and` koşulu olarak eklenir; başka uygulamaların loopback trafiği kapsam dışıdır.

`-s 64` her paketin en fazla 64 baytını kaydeder; hat uzunluğu değişmez. Kısa profil 21/22/23 bayt UDP yükleri gönderir; Ethernet/IP/UDP başlıklarıyla özgün boylar 63/64/65'tir. `-c 3` seçilen üç paketten sonra biter. Yanlış filtre bu paketleri dışlarsa süre sınırında açık hata verir. `-nn` ad/servis çözümlemeyi kapatır; `-w` kayıt yazar. Kalıcı dosya yolu veya başka arayüz verilmez.

Döndürme profilinde yalnız 20 adet 60000 baytlık eğitim datagramı vardır. `-C 1 -W 2` ondalık 1 milyon bayt eşiğinde en fazla iki dosya kullanır. Kontrol paket yazılmadan önce yapıldığından ilk dosya eşiği bir frame kadar aşabilir; 1 MB'ı katı üst sınır sanma. `-s 0` bu kontrollü büyük datagramların tamamını alır. Root yetkisi ve tcpdump yalnız bu laboratuvar için gereklidir; önceki offline dersler bunları istemez.

Kaynak: [tcpdump resmî kılavuz kaynağı](https://github.com/the-tcpdump-group/tcpdump/blob/master/tcpdump.1.in).
```meta
dil: tcpdump-lab
```
```stdin
{"dil": "tcpdump-lab", "laboratuvar": "kisa"}
```
:::

::: tahmin
Aşağıdaki komutun gerçekten topladığı kayıtta hangi uzunluklar görülür?
```tcpdump-lab
tcpdump -i lo -nn -s 64 -c 3 -w sonuc.pcap udp
```
```meta
dil: tcpdump-lab
```
```stdin
{"dil": "tcpdump-lab", "laboratuvar": "kisa"}
```
???
Paketler: 3
Dosyalar: 1
Yakalanan: 63, 64, 64
Hat: 63, 64, 65
Son datagramın yalnız 64 baytı kaydedilir; özgün 65 bayt olduğu bilgisi korunur.
:::

::: gorev Gerçek yakalamada 64 bayt snaplen
lo arayüzünde laboratuvarın üç UDP datagramını, -nn, snaplen 64 ve -c 3 ile sonuc.pcap dosyasına kaydet.
```starter
tcpdump -i lo -nn -s 63 -c 3 -w sonuc.pcap udp
```
```meta
dil: tcpdump-lab
```
```stdin
{"dil": "tcpdump-lab", "laboratuvar": "kisa"}
```
```test
r=calistir()
eq(len(r["exports"]),1,"tek kayıt")
if r["exports"]:
    f=r["exports"][0]
    eq(f["count"],3,"üç gerçek datagram")
    eq(f["caplens"],[63,64,64],"63/64/65 sınırında snaplen 64")
    eq(f["wirelens"],[63,64,65],"hat boyu korunur")
ok(r["runtime"]["reaped"],"tcpdump süreci kapandı")
ok(r["runtime"]["linux_directory"].startswith("/tmp/"),"Linux dosya sistemi")
```
```solution
tcpdump -i lo -nn -s 64 -c 3 -w sonuc.pcap udp
```
```hint
Komutu açıklanan gerçek seçeneklerle kur; sonuç alanları native araç çıktısından gelir.
```
:::

::: gorev Boyut eşiğinde iki dosyaya döndür
Döndürme profilindeki 20 UDP datagramını tam boyuyla al: snaplen 0, -c 20, ondalık 1 MB dosya eşiği ve en fazla 2 dosya. -nn ve lo kullan.
```starter
tcpdump -i lo -nn -s 96 -c 20 -C 1 -W 2 -w sonuc.pcap udp
```
```meta
dil: tcpdump-lab
```
```stdin
{"dil": "tcpdump-lab", "laboratuvar": "donusum"}
```
```test
r=calistir()
eq(len(r["exports"]),2,"gerçek döndürme iki dosya oluşturdu")
eq([x["count"] for x in r["exports"]],[17,3],"20 tam datagram eşiği aşarak 17+3 ayrıldı")
for f in r["exports"]:
    ok(all(n==60042 for n in f["caplens"]),"datagram tam kaydedildi")
    eq(f["caplens"],f["wirelens"],"snaplen kesimi yok")
    ok(f["size"]<=1_000_000+60042+16+24,"en çok bir kayıt kadar eşik aşımı")
ok(r["runtime"]["reaped"],"süreç toplandı")
```
```solution
tcpdump -i lo -nn -s 0 -c 20 -C 1 -W 2 -w sonuc.pcap udp
```
```hint
Komutu açıklanan gerçek seçeneklerle kur; sonuç alanları native araç çıktısından gelir.
```
:::
