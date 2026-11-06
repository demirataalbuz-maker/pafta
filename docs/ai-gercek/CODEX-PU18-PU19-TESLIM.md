# pu18 / pu19 — yerel keşif ve SQLi alt dersleri

2026-11-03 · Codex yazdı, kendi kontrollerini yaptı. Opus denetimi bekliyor, puan verilmedi. Bunlar AI değil Purple yolundaki klasik plan alt dersleridir. AI tracker'ına Purple ID eklenmedi; sahiplik ortak panoda, alt iş durumu CODEX-PLAN-ALT-ISLER.json içindedir.

## Kapsam
pu18, plan-klasik-1 ve Purple M2'nin Nmap alt işi; pu19, plan-klasik-2 ve M2'nin SQLi alt işidir. Bu iki teslim ffuf/nuclei, XSS/SSTI/XXE, Juice Shop, GoPhish, SIEM/PCAP veya M2 modülünün tamamlandığı anlamına gelmez. Mevcut17Purple dersinin göreli sırası ve dosyaları korundu; yeni iki ders Keşif ve İlk Erişim modülüne eklendi. engine/web değiştirilmedi. Yeni indirme/kurulum yapılmadı.

## Gerçek davranış
Nmap PATH'ten bulunur; laptopta7.80. İki kendi HTTP servisi + bir bağlı ama dinlemeyen socket; yalnız127.0.0.1 ve bu üç port TCP connect ile taranır. Servislerden biri kapatılır; kalan kontrol servisidir. HTTP canary, doğrudan TCP ground truth, raw XML, stderr, komut, sürüm, executableSHA256, cihaz ve cleanup kalıcı kanıttadır. İlk sonda closed beklediği için başarısız oldu; gerçek Nmap filtered/no-response verdi. Son ders ham filtered sonucunu korur; kapalı diye yeniden etiketlemez. EskiNpcap uyarısı kayıtta korunur; güncelleme/firewall değişikliği yapılmadı. HTTP kontrolü ortam proxy'sinden bağımsız http.client kullanır.

SQLi stdlib HTTPServer ve her koşuda ayrı gerçek SQLite dosyasıdır. Accounts + audit tabloları, rastgele sentetik hesap/parola/canary vardır. Beş gerçek HTTP deneyi: normal vulnerable200, normal secure200, injection vulnerable200+canary, injection secure401, bozukSQL500. Yanıtlar DB audit kayıtlarıyla bağımsız karşılaştırılır; uydurulmuş yanıt kabul edilmez. Öğrencinin parameter binding fonksiyonu aynı gerçek DB üzerinde de sınanır; SQL karakterleri içeren meşru hesap çalışır. Bunlar sentetik parolalardır; production'da parola loglamak öğütlenmez. Yalnız kendi lab DB/server kaynakları temizlenir.

## Görünür veri ve arayüz
pu18: kesif/ornek.xml + README. pu19: yerel_sqli/istekler.json,istek.http,sorgular.sql,README. Hepsi açıkça sentetik fixture'dır. Setup geçici çalışma kopyası yapar; aynı çağrıda düzenlenebilir, sonraki çağrıya kalıcı olacağı söylenmez. UI'da Path.read_text üzerinden XML/HTTP dosyası erişimi ayrıca sınandı. Gerçek deney fixture'dan sonuç okumaz.

Her iki dersin finali ders ekranından Check ve Run ile gerçek çalıştı. Nmap ekranı ilk30/30 geçti; son XML sınır testleriyle sayı36'ya yükseldi (son ekran görüntüsü ve gerçek kabul receipt'i doğrulandı). SQLi12/12. Run receipt kabul=false, Check receipt kabul=true; dosya yolu stdout'ta. Ekran görüntüleri Desktop/pafta-pu18-ui-kabul-20261103.png ve pafta-pu19-ui-kabul-20261103.png.

## Kontroller
- python -X utf8 tools/validate.py pu18 pu19 → 2ders12kontrol TEMİZ,6çözüm geçti6starter reddedildi.
- docs/denetim/araclar/tahmin.py . pu18 pu19 →0tahmin0şüpheli. Tahmin bulunmadığından bu ayrı bir tahmin kabulü değildir.
- Resmî mutasyon.py KURALLAR/mutantlar üreteci, değiştirilmeden yalnız saf görevlerde seri uygulandı:11üretilen,0geçen. SQLi saf sorgu kodundan bu kurallar mutant üretmedi; o dersin test gücü ayrıca üç anlamlı yanlışla sınandı. Gerçek ağ deneyleri bu mekanik11mutasyonda tekrarlanmadı.
- Her finalde boş,sabit,3anlamlıyanlış,oracle-import ve inspect kopyası reddedildi. SQLi yanıt-uydur mutantının ilk çalışması transport timeout oldu; bu test gücü sayılmadı. Tek başına tekrarında doğru AssertionError: gerçek beş HTTP/DB audit kaydıyla eşleşmeli. Son dosya bunu içeriyor.
- Purple regresyon: varsayılan8paralel işte6mevcutadım timeout oldu. Testler/süre sınırları değiştirilmeden seri zamanlama ile19ders125kontrol TEMİZ:17tahmin54solution54starter. Paralel yükte performans riski gizlenmedi.
- Sınav testi ilk koşu12testte sq12:4 nedeniyle1hata verdi; SQL sorusu tek başına PASS. Diğer testler bittikten sonraki tekrar:12test,10.719s,OK. İlk başarısız koşu gizlenmedi; SQL sorusu veya sınav testi değiştirilmedi.

## Kanıt ve tekrar üretim
outputs/pu18-pu19-kabul/teslim-kanit.json dosyaSHA256,UIreceiptlistesi ve teslim özetidir. Aynı klasörde tüm referans/yanlış/kopya JSON sonuçları,11mutasyon,pure-mutations.json,summary.json,Run kayıtları bulunur. UI receiptleri Desktop/pafta-pu18-pu19-ui-20261103/purple-kanit altında. Önceki başarısız Nmap sondası outputs/yeni-kesif-nmap/native-probe-1793723812773772100.json içinde kabul=false korunmuştur.

Desktop/probe_pu18_pu19.py referans ve yanlış çözümleri,Desktop/recheck_pu19_fake.py doğru audit reddini,Desktop/pu18_edges_mutation.py saf görev mutasyonlarını yeniden üretir. Son helper mevcut test sınırlarını idempotent ekler; proje engine/web davranışını değiştirmez. Seri regresyon komutu: python -X utf8 -c "import sys;from tools import validate as v;v.run_jobs=lambda jobs:[v.run_job(j) for j in jobs];sys.argv=['validate.py','--yol','purple'];raise SystemExit(v.main())". Bu yalnız zamanlama seçer, hiçbir testi/süre sınırını değiştirmez.

## Sınırlar
Yalnız bu Windows laptopta kabul yapıldı. İkinci masaüstü/Linux/macOS Nmap kabulü yok. Sürüm7.80 eskidir; otomatik güncellenmedi. Npcap uyarısıyla TCP connect yolu ölçüldü; raw packet/SYN/OS/version taraması kanıtlanmadı. Sunucu audit'i tam Blue monitoring değildir. Üst planların kalan işleri açık, Codex'in26planı bitmiş değildir. Commit/push yok.
