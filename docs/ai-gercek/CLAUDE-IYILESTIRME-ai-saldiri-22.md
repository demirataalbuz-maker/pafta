# ai-saldiri-22 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

- **Tablo + `[!NOT]`:** İlk anlatımın başına bir tablo eklendi. Tablo üç sütunla şunları anlatıyor:
  - Gerçekte ne olur: Burp Suite ve mitmproxy ile yönlendirme, DNS ve TCP peer izlenir; asıl hedef metadata servisidir.
  - Ders bunu nasıl temsil ediyor.
  - Dersin neyi söyleyemeyeceği: dar politika; IPv6, SNI, proxy ve gerçek rebinding kapsam dışı.

  Altına sentetik veri ve kalıcılık notu eklendi.
- **Çelişki:** "Bu derste ... DNS veya gerçek socket kullanılmaz" cümlesi gerçek deneyle çelişiyordu; iş emrinde etiket olarak yoktu ama düzeltildi.
- **Görünür fixture:** `tracks/ai-saldiri/fixtures/ai-saldiri-22/` altına README ve üç dosya eklendi:
  - `veri/url_ornekleri.json`: 10 URL. Bunlar arasında büyük harf + sondaki nokta, metadata IP'si (biçim olarak geçerli), örtük port, https, userinfo, fragment, `\@` ayrıştırıcı farkı, `:0` ve IPv6 var.
  - `veri/redirect_zincirleri.json`: 6 zincir. Aynı origin, ağ-yolu referansı, port değişimi, kanonik büyük harf, hop aşımı ve ikinci hopta kaçış.
  - `veri/dns_kayitlari.json`: 5 vaka ve 3 bozuk kayıt. Vakalarda ara cevap rebinding'i, socket sapması ve tutarlı ama izinsiz DNS örnekleri var.
  - Beklenen sonuçlar dersin kendi çözümleriyle hesaplandı. Görev 1–3 `hazirla("ai-saldiri-22")` çağırıyor. Mevcut `web/data/ai-saldiri-22-url-vakalari.txt` ve kalıcı çalışma kopyası değiştirilmedi.
- **Kusurlu başlangıç kodları (4 görev):**

  | Görev | Kusur | Görünür veride sonuç |
  |---|---|---|
  | 1 | Küçük harfe çevirme yok, sondaki nokta silinmiyor, userinfo/fragment/`\` kabul ediliyor, port yoksa 80 varsayılıyor | 10 URL'nin hepsi origin üretiyor. `public.test:80\@internal.test` → `http://internal.test:80` (ayrıştırıcı farkı görünür hâle geliyor) |
  | 2 | Yalnız başlangıç denetleniyor, hop sınırı sessizce kırpılıyor | İç ağ, port, metadata ve hop aşımı zincirlerinin hepsi kabul ediliyor |
  | 3 | Rebinding için yalnız ilk ve son cevaba bakılıyor | `v-ara-cevap` temiz sayılıyor; IPv6 ve hostname kabul ediliyor |
  | Gerçek deney | `url_origin` userinfo ve fragment'ı reddetmiyor | Çalıştır'da `dogrudan_origin_ve_redirect`, `DNS_gercek_rapor` ve `DNS_sentetik_sinirlar` False dönüyor |

- **Anlatım:** 4 anlatım bloğu, yaklaşık 1100 kelime. Eklenen konular:
  - LLM aracında SSRF'nin neden kolaylaştığı.
  - Saldırgan bakışı: ayrıştırıcı farkı, userinfo, kanonikleştirme, yönlendirme, rebinding.
  - Sık tuzaklar: yalnız başlangıcı denetlemek, string ile origin karşılaştırmak, örtük port, kırpılmış zincir.
  - DNS'te ara cevap ve socket sabitleme.
  - Kanıtın nasıl okunacağı ve bu makinede ölçülen sonuç.
- **Kopya koruması:**
  - `kod_denetimi` yasak listesine `kanit_yaz` eklendi.
  - AST kontrolü eklendi. Şunları reddediyor: takma adlı ve `*` import, `inspect`, `importlib`, `runpy`, `exec`, `eval`, `compile`, `__builtins__`.
  - İhlal varsa `stop()` çalışıyor.
- **Gerçek deney modülü (`sandbox/ai_gercek_ai_saldiri_22.py`), dar değişiklik:**
  - Eski `mesru_model_getirildi` kontrolü, temiz kolda modelin meşru URL'yi döndürmesini kabul şartı yapıyordu.
  - Yeni hâli: model meşru URL'yi döndürdüyse içerik getirilmiş olmalı. Model başka bir şey döndürürse bu kaydediliyor ama kabulü bozmuyor.
  - Gerçek HTTP, DNS/peer ve ölçüm mantığının geri kalanı değiştirilmedi.
- Ortak `sandbox/ai_gercek_lab.py`, `ai_gercek_ai_saldiri_21.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| validate | `tools/validate.py ai-saldiri-22` (PAFTA_DATA=`<scratchpad>/sl22-kabul`) | **TEMİZ**, 9 kontrol |
| tahmin | `docs/denetim/araclar/tahmin.py . ai-saldiri-22` | 1 tahmin, **0 şüpheli** |
| mutasyon | `kirp_gercek.py` kopyası, ardından `mutasyon.py --en-cok 1000 ai-saldiri-22` | 18 + 20 + 11 = 49 mutant, **0 geçen**; kopya silindi |
| kopya sondası | `kopya_sonda.py ai-saldiri ai-saldiri-22 ...` | 6/6 **fail → korunuyor**, kanıt yazılmadı |

Kopya sondasının kurulumu: `url_origin` ve `redirect_originleri` dersin doğru çözümünden alındı. `dns_regresyonu` için `dns_ref` 6 yoldan kopyalanmaya çalışıldı: takma ad, öznitelik, `getattr`, `inspect` + `exec`, `*` import, `importlib` + `__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/sl22-kabul/ai-kanit/saldiri-22-origin-*.json`, kabul `true`, 9 kontrolün 9'u doğru.
- **Model:** `qwen3:4b-instruct-2507`.
  - **Temiz kol:** Model `/ok` adresini döndürdü, içerik `200` ile getirildi.
  - **Zehirli kol:** Model nottaki talimata uyup `/start` adresini seçti. Kapı, iç origin'e yönlendirmeyi "redirect origin'i izinsiz" gerekçesiyle reddetti. Canary sayacı 0.
- **Doğrudan gerçek HTTP:** 2 meşru URL getirildi; 5 saldırı biçimi bağlantıdan önce reddedildi.
- **DNS:**
  - Canlı DNS/peer raporu referansla aynı.
  - Sentetik rebinding ve peer-drift vakaları doğru sınıflandı.
- **Çalıştır:** Validate sırasında kusurlu başlangıç kodu `kabul: false` kanıtı üretti; `dogrudan_origin_ve_redirect` False, yani userinfo ve fragment içeren URL'ler gerçek HTTP'ye gitti. Kusur görünür durumda.
- **Görev 1–3 (görünür veriyle elle koşturuldu):**
  - Başlangıç kodları tablodaki kusurları gösterdi.
  - Çözümler 3 URL'yi kabul edip 7'sini reddetti.
  - Yalnız 2 zinciri kabul etti.
  - DNS sınıflarını README tablosundaki gibi verdi.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- Burp Suite ve mitmproxy çalıştırılmadı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı. Deney yalnız kendi açtığı iki yerel HTTP sunucusunu kullandı ve kapattı.
