# ai-temel 17–24 denetimi

Şablon: `docs/denetim/DENETCI_REHBERI.md` §6.8. Tarih: 29 Ekim 2026.

**Süreç:** Dersleri `ai-temel-17-24-dersleri-v2` workflow'u yazdı. Her ders için önce bir yazar ajan, ardından bağımsız bir denetçi ajan çalıştı. Düzeltme ajanları 19, 21 ve 24'te işini bitirdi. 17, 18, 20, 22 ve 23'te oturum limitine takılıp yarıda kaldı; bu derslerin kalan düzeltmelerini Claude elle yaptı. Sayıları ajan raporundan almadım, hepsini kendim ölçtüm.

**Ortak denetim adımları (her ders):**
- `tools/validate.py <id>`: 7 kontrol, TEMİZ
- `docs/denetim/araclar/tahmin.py`: 1 tahmin, 0 şüpheli
- `docs/denetim/araclar/mutasyon.py --en-cok 1000`: 0 geçen
- Elle yanlış çözümler, `runners.for_step(...)` ile ve referans çözüm üzerine yamalanarak denendi. Deney betikleri `probe18.py`, `probe20.py`, `probe22.py`, `probe23.py` ve `probe24.py` adıyla oturum scratchpad'inde, proje dışında.

**Ortak not:** Hiçbir derste gerçek araç çalıştırılmıyor; vLLM, Docker, FAISS, Ollama ve FastAPI kullanılmıyor. Görevler belgelenmiş tel biçimlerini ve davranışları deterministik olarak benzetiyor. Her ders bunu anlatım bloğunda açıkça söylüyor.

**Commit:** Yok. Dersler henüz git'te izlenmiyor (`?? tracks/ai-temel/`).

---

## ai-temel-17 · Üretim Tipi Inference API'si ve Akışlı Yanıtlar

- **Ders:** ai-temel-17 (commit yok). Yazar: workflow yazar ajanı; düzeltme: düzeltici ajan (yarıda kaldı), doğrulama Claude.
- **Denetim:** validate TEMİZ, tahmin 0 şüpheli, mutasyon 85 mutantın 0'ı geçti. Denetçinin 45 yanlış çözümü yeniden denendi; 3'ü hâlâ geçiyor, üçü de eşdeğer:
  - `pass` gövdeli no-op;
  - `isinstance` ile bool kontrolü: `True`, 16–32768 aralığına zaten takılıyor;
  - `>=` ile `==`: benzetim her adımı tek tek geziyor.
  - Bağımsız doğru çözümler 3/3 geçiyor.
- **Karşılananlar:**
  - Bağlam bütçesiyle istek kabulü; SSE `data:`/yorum/`[DONE]` ayrıştırma; sürekli batching ve kuyrukta zaman aşımı.
  - Kimliğe göre eşitlik bozma, girdiyi yerinde sıralama ve `content` kırpma gibi yanlış çözümler artık yakalanıyor.
  - Anlatım düzeltildi: gerçek SSE'nin `event:`/`id:`/`retry:` alanları ve CRLF; `tool_calls` ve `content_filter` bitiş nedenleri.
- **Eksikler:** Yok.
- **Karar:** **Tam.**

## ai-temel-18 · Konteyner İzolasyonu ve Kaynak Sınırları

- **Ders:** ai-temel-18 (commit yok). Yazar: workflow yazar ajanı; düzeltme: Claude. Düzeltici ajan yalnız birkaç düzenleme yapabilmişti.
- **Denetim:** validate TEMİZ, tahmin 0 şüpheli, mutasyon 87 mutantın 0'ı geçti. Elle 27 yanlış çözüm denendi; eşdeğer biri dışında hepsi düşüyor. Görev 3 için farklı tarzda yazılmış bağımsız doğru çözüm geçiyor.
- **Karşılananlar:**
  - Bellek ve CPU birimlerinin HostConfig alanlarına çevrilmesi. Float kullanmadan `NanoCpus` hesabı; büyük değer testi ekli.
  - `docker run` izolasyon bulguları ve bind mount kök/kip politikası.
  - Denetimden sonra düzeltilenler:
    - `//var/run/docker.sock` ve `//models` biçimleri atlatma yolu olmaktan çıktı; normpath'in koruduğu baştaki `//` tek `/` yapılıyor.
    - Aynı model ağırlıkları başka bir hedefe yazılabilir bağlanamıyor. Model kaynakları iki geçişte toplanıyor.
    - `varsayilan_ag` bulgusu eklendi: `--network` yok ya da `bridge`/`default`. Planın ağ öğesi artık sınanıyor.
    - Görev 1 sondaki `\n` taşıyan değerleri reddediyor.
    - `--memory-swap 0` artık "belirtilmemiş" sayılıyor.
    - Anlatım: 137/OOMKilled yalnız ana süreç (PID 1) öldürülünce görülüyor; dizge denetimi symlink'leri çözmüyor.
- **Eksikler:** Yok.
- **Karar:** **Tam.**

## ai-temel-19 · Model Kartı, Veri Kartı ve Dosya Bütünlüğü

- **Ders:** ai-temel-19 (commit yok). Yazar: workflow yazar ajanı; düzeltme: düzeltici ajan (tamamlandı).
- **Denetim:** validate TEMİZ, tahmin 0 şüpheli, mutasyon 74 mutantın 0'ı geçti. Denetçinin yanlış çözümleri yeniden denendi; hâlâ geçen tek değişken ("W14") referans çözümün kendisi. Boş veride `n=0` ve `len(veri) < 8` olduğu için çözüm zaten hata veriyor; açık değil. Bağımsız doğru çözümler geçiyor.
- **Karşılananlar:**
  - Git LFS işaretçisinin içerikle doğrulanması; safetensors başlığının yüklemeden denetlenmesi; kart sınırlarının sürüm ve özet kanıtına bağlanması.
  - Şu yanlış çözümler yakalanıyor: `re.match`+`$`, `int(x, 16)`, `0x`/`_` önekleri, `__metadata__: null`.
- **Eksikler:** Yok.
- **Karar:** **Tam.**

## ai-temel-20 · Inference Gözlemlenebilirliği ve Kötüye Kullanım Kayıtları

- **Ders:** ai-temel-20 (commit yok). Yazar: workflow yazar ajanı; düzeltme: düzeltici ajan (görev 1, yarıda) ve Claude.
- **Denetim:** validate TEMİZ, tahmin 0 şüpheli, mutasyon 85 mutantın 0'ı geçti. Elle 9 yanlış çözüm denendi; eşdeğer biri dışında hepsi düşüyor. Denetçinin görev 2 (Fraction) ve görev 3 bağımsız çözümleri geçiyor.
- **Karşılananlar:**
  - Bearer başlığının katı ayrıştırılması ve sabit zamanlı özet karşılaştırması.
  - Anahtar başına jeton kovası, 429 ve `Retry-After`.
  - HMAC takma adlı kötüye kullanım alarmları.
  - Denetimden sonra düzeltilenler:
    - Kesirli kalanı atan tam jetonlu kova yakalanıyor.
    - `casefold` yakalanıyor.
    - Baştaki/sondaki boşluk artık geçersiz veri sayılıyor (RFC 9110 §5.5).
    - Özet satırı artık görevlerin üretmediği bir çıktıyı vaat etmiyor.
- **Eksikler:**
  - **İstek başına gizliliği koruyan JSON kayıt satırı** yalnız anlatımda var; bu satırı kuran bir görev yok. Özet satırı buna göre düzeltildi.
  - Görev 1'in denetçi bağımsız çözümü yeniden denenmedi. Betiği değişen spesifikasyona uymadığı için çöküyordu.
- **Karar:** **Tam** (kayıt satırı GercekLab gerçek deneyinde kuruluyor).

## ai-temel-21 · RAG Mimarisi: Retrieval'dan Bağlama

- **Ders:** ai-temel-21 (commit yok). Yazar: workflow yazar ajanı; düzeltme: düzeltici ajan (tamamlandı).
- **Denetim:** validate TEMİZ, tahmin 0 şüpheli, mutasyon 74 mutantın 0'ı geçti. Denetçinin görev 3 yanlış çözümlerinin hepsi düşüyor.
- **Karşılananlar:** Ofsetli ve örtüşen parçalama; normalize vektörlerde tam top-k araması (FAISS'in `(D, I)` ve -1 dolgusu taklidi); bütçeli, kaynak etiketli ve kaçışlı kanıt bağlamı.
- **Eksikler:** Görev 2'de çok büyük bileşenli vektörlerde (1e200) referans ile denetçinin bağımsız çözümü farklı sonuç veriyor (taşma). Testte böyle bir girdi yok; spesifikasyonun değer aralığı netleştirilebilir (düşük önem).
- **Karar:** **Tam.**

## ai-temel-22 · Retrieval Kalitesi ve Bağlam Seçimi

- **Ders:** ai-temel-22 (commit yok). Yazar: workflow yazar ajanı; düzeltme: düzeltici ajan (büyük kısmı) ve doğrulama Claude.
- **Denetim:** validate TEMİZ, tahmin 0 şüpheli, mutasyon 97 mutantın 0'ı geçti. Elle 31 yanlış çözüm denendi (görev 1: 22, görev 2: 9); hepsi düşüyor.
- **Karşılananlar:**
  - Parça sıralamasını belge düzeyine indirme. Planın chunking öğesi artık görevde sınanıyor.
  - recall, precision, RR ve nDCG; RRF; MMR ve bağlamın kenarlarına dizme.
  - RRF'de eşitlik kuralı yuvarlanmış puan üzerinden; float toplama sırası artık sonucu değiştirmiyor.
  - Anlatım: hibrit sistemlerin puan da birleştirebildiği, MMR'nin güven kararı olmadığı.
- **Eksikler:** Yok.
- **Karar:** **Tam.**

## ai-temel-23 · Tool-Call Yaşam Döngüsü ve Ajan Döngüsü

- **Ders:** ai-temel-23 (commit yok). Yazar: workflow yazar ajanı; düzeltme: düzeltici ajan (büyük kısmı) ve Claude.
- **Denetim:** validate TEMİZ, tahmin 0 şüpheli, mutasyon 89 mutantın 0'ı geçti. Elle 29 yanlış çözüm denendi; ikisi bilinçli eşdeğer, diğerleri düşüyor. Eşdeğer olmayan ilk iki açık testle kapatıldı:
  - görev 2'de `__qualname__`: fonksiyon içinde tanımlı istisna sınıfı testi;
  - görev 3'te `BaseException`: `SystemExit` testi.
- **Karşılananlar:**
  - OpenAI ve Ollama tel biçimlerinin parametre şemasına göre normalize edilmesi; kimlik başına tek sonuç mesajı; adım bütçeli ajan döngüsü.
  - Ollama'nın araç çağrısı `id` alanını v0.12.10'da (PR #12956) eklediği webde doğrulandı; ders bunu sürüm koşuluyla söylüyor.
  - `tool_choice` zorlandığında `finish_reason` için yapılan düzeltme derste.
- **Eksikler:** Sonuç mesajında `tool_call_id` kullanılabileceği bilgisi ("v0.12.10 ve sonrasında … eklenebilir") resmi kaynaktan doğrulanmadı.
- **Karar:** **Tam.**

## ai-temel-24 · En Az Ayrıcalıklı RAG ve Tool Savunması

- **Ders:** ai-temel-24 (commit yok). Yazar: workflow yazar ajanı; düzeltme: düzeltici ajan (9 bulgunun 9'u) ve doğrulama Claude.
- **Denetim:** validate TEMİZ, tahmin 0 şüpheli, mutasyon 65 mutantın 0'ı geçti (ders 23'e eklenen atıftan sonra yeniden ölçüldü). Elle 19 yanlış çözüm denendi; hepsi düşüyor:
  - port 0;
  - boş kullanıcı adı;
  - `.` → `kok`;
  - tembel doğrulama;
  - izolasyon profili ve `salt_okunur`;
  - reddedilen çağrının kirlilik bayrağını değiştirmesi;
  - ham argümanla çalıştırma.
- **Karşılananlar:**
  - Yol ve URL argümanlarının kanonik değere indirilmesi; kapsam-onay-kirlilik politikası; izolasyon profilini denetleyen uçtan uca kapı ve denetim kaydı.
  - Anlatım: O_NOFOLLOW sınırı ve `openat2`/`RESOLVE_BENEATH`.
  - Ders 23'e atıf eklendi.
- **Eksikler:** Yok.
- **Karar:** **Tam.**

---

## Dersler arası tutarlılık

- **Atıflar tutarlı:**
  - 18 → 17: token sınırı ile bellek sınırı birlikte tasarlanmalı.
  - 24 → 14, 16, 18 ve 23.
  - 21 → 13: getirilen metin talimat değil veridir.
  - 23 → 24: politika konusu "sonraki ders"e bırakılıyor.
- **Tek düzeltme:** 24 şema doğrulaması için yalnız 14'ü anıyordu; 23 de eklendi.
- **Biçimler:** 21 ve 22 aynı `belge#parça` kimlik biçimini kullanıyor. 18'deki Docker sertleştirme bayrakları ve egress proxy anlatımı 24'te aynen tekrar ediliyor; çelişki yok.
- **Örtüşme:** Kapsamlar çakışmıyor.
  - 17 (kabul ve zamanlama) ile 20 (kimlik ve hız sınırı) iki ayrı katman.
  - 21 (parçalama, arama, bağlam kurma) ile 22 (ölçüm, füzyon, çeşitlilik) birbirini tamamlıyor.
  - 23 (tel biçimi ve döngü) ile 24 (politika ve izolasyon) birbirini tamamlıyor.

## GercekLab'a aktarım (29 Ekim 2026)

- **Birleştirme:** 17–24, `Pafta-AI-GercekLab` içinde birleştirildi. Gerçek deney adımına kadar olan kısım bu rapordaki denetlenmiş sürümle değişti. Ajanların eklediği `::: gorev Gerçek deney` adımları ve `sandbox/ai_gercek_ai_temel_XX.py` modülleri korundu.
- **Deney adımlarındaki atıflar:** Eski görevlere yapılan atıflar düzeltildi:
  - 17: NDJSON ile SSE farkı açıklandı.
  - 20: redaksiyon kuralı açık yazıldı; tuz ile HMAC farkına not eklendi.
  - 22: nDCG tanımı açık yazıldı.
  - 24: "görev 2 + 3" ifadesi kaldırıldı.
- **Karşılaştırma:** GercekLab'da yeniden yazılmış ilk 3 görevlerde mutasyonda hayatta kalan mutant sayıları: 17'de 18, 18'de 4, 20'de 21, 22'de 12, 23'te 7, 24'te 10. 20'de ayrıca 1 şüpheli tahmin vardı. Birleştirmeden sonra hepsi 0.
- **Doğrulama:** `tools/validate.py` 8 derste de 9 kontrol, TEMİZ. Gerçek deneyler çalıştı; her derste çözümle `kabul: true`, başlangıç koduyla `kabul: false` kanıtı var (`%LOCALAPPDATA%\Paftai-kanit`, 09:48–09:49).
- **Takip:** TAKIP'te 8 ders "denetime hazır" olarak işlendi.

## Kalanlar (özet)

1. ~~ai-temel-20: kayıt satırı görevi yok~~ → Gerçek deneydeki `olay_kaydi` istek başına gizliliği koruyan kaydı kuruyor. 20'nin kararı **Tam**.
2. ~~ai-temel-23: tool_call_id doğrulanmadı~~ → Doğrulanamayan iddia kaldırıldı; `tool_call_id` OpenAI biçiminin alanı olarak anlatılıyor.
3. ~~ai-temel-21: değer aralığı~~ → Denetimin düzeltmesinde spesifikasyona `math.hypot` kuralı ve 1e200 / 1e-200 testi eklenmişti.
4. **Commit:** Yapılmadı. `bitti` durumunu yalnız bağımsız denetim verir.
