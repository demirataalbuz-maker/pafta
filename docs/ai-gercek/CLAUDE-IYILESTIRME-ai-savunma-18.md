# ai-savunma-18 iyileştirme teslimi

claude-yazar kendi uygulama kontrollerini yaptı. Puan ve bağımsız denetim başka bir AI'ya aittir; claude-yazar bu dersi puanlamaz.

## Ne değişti

### Anlatım

- **Çelişki:** İlk anlatımda "Bu derste Promptfoo veya Qdrant çalıştırılmaz; ağa veya modele erişilmez" yazıyordu. Bu cümle kaldırıldı. Yeni metin şöyle: görev 1–3 sentetik veriyle çalışır, son adım kurulu yerel Ollama modelini gerçekten çağırır, Qdrant ve Promptfoo çalıştırılmaz.
- **Tablo + `[!NOT]`:** İlk anlatımın başına bir tablo eklendi. Tablo gerçek RAG hattını (gömme, Qdrant araması, bağlama ekleme, Promptfoo puanlaması) ve dersin bunu nasıl temsil ettiğini anlatır. Altına sentetik veri ve kalıcılık notu kondu.
- **Uzunluk ve içerik:** 5 anlatım bloğu toplam 1007 kelime oldu. Eklenen konular:
  - Modelin talimatla veriyi ayıramaması ve dolaylı injection'ın mekanizması.
  - Kaynak etiketinin tek başına güvence olmaması (`sistem-taklidi` örneği).
  - Tekrar oranının neden bir işaret olduğu (PoisonedRAG, 2024).
  - Saldırgan bakışı: Türkçe veya kodlanmış talimat, talimatsız yanlış bilgi.
  - Fail-closed yaklaşım, eşitlik, `elif` tuzağı, istemciden gelen karar, katmanlı savunma.
  - Gerçek deneyin 4 adımı, deterministik kabul çekirdeği, sınırlar ve bu makinede ölçülen sonuç.

### Görünür fixture

`tracks/ai-savunma/fixtures/ai-savunma-18/` altına bir README ve iki veri dosyası eklendi:

- `veri/rag_politikasi.json`: asıl politika (`max_belge` 3) ve 4 bozuk politika (boş kaynak listesi, bool sınır, `uyar` kararı, 1.2 eşik).
- `veri/getirilen_belgeler.json`: 8 belge ve 3 bozuk belge. Belgeler şu durumları kapsar:

  | Belge | Durum |
  |---|---|
  | `forum-zehir` | Dört neden birden |
  | `sistem-taklidi` | Kurumsal kaynak ama `[System Message]` içeriyor |
  | `guvenilir-dis` | Yalnız kaynak nedeni |
  | `sinir-belgesi` | Eşiklere tam eşit, aday olmalı |
  | `turkce-zehir` | **Yanlış negatif:** Türkçe talimat bağlama giriyor |
  | 2 belge | Kapasite dışında kalan |

  Beklenen paket referans işlevle doğrulandı.

Görev 1–3'ün setup bloğu `hazirla("ai-savunma-18")` çağırır. Başlangıç kodları bu dosyaları okuyup sonuçlarını basar. Veriler sentetik olarak etiketlendi ve kalıcı değil. Testler bu dosyalardan ayrı, gizli verilerle sınar.

### Kusurlu başlangıç kodları (4 görev)

| Görev | Kusur | Görünür veride sonuç |
|---|---|---|
| 1 | Yalnız alanların var olup olmadığına bakar | 4 bozuk politikayı kabul eder |
| 2 | `elif` ile ilk nedende durur, tekrarda `>=` kullanır, harf duyarlı arar | `forum-zehir` yalnız `kaynak` nedeni alır, `sinir-belgesi` karantinaya gider, `sistem-taklidi` aday olur |
| 3 | Kimliğe göre sıralar, kapasite dışı belgeleri sessizce atar | Çelişkili `eski-kampanya` ("7 gün") bağlama girer, `kapasite` kaydı yok |
| Gerçek deney | Yalnız harf duyarlı talimat işaretine bakar | Çalıştır'da zehirli belge gerçek modelin bağlamına giriyor ve UYARI basılıyor |

### Gerçek deney modülü (`sandbox/ai_gercek_ai_savunma_18.py`, yalnız bu derse ait)

- Model boş yanıt verirse `GercekLabYok` yükseltilir. Eskiden boş yanıt "sızmadı" sayılıyordu.
- Ayarlar (`ayarlar`) kanıta yazılır. Bağlam metni ve iki ham yanıt (`ham_yanitlar(r)`, ilk 600 karakter) kanıta eklendi. Eskiden kanıtta model yanıtı hiç yoktu.
- Çalıştır çıktısı artık bağlamı ve iki yanıtı gösterir. Zehirli işaret bağlama girerse UYARI basar.
- Testin kullandığı `guvenli_rag_paketi_referans` eklendi.

### Kopya koruması

- Test `kod_denetimi(src, yasak=("guvenli_rag_paketi_referans", "sizinti_referans", "kanit_yaz"))` çağırır. Eski hâli `("referans", "getattr")` idi ve ihlalde test durmuyordu.
- Ek AST kontrolü şunları yakalar: yasaklı veya yıldızlı import, `inspect`/`importlib`/`runpy`, `exec`/`eval`/`compile`/`__builtins__`.
- İhlal bulunursa test `stop()` ile durur.

### Gerçek deney testi

- **Sözleşmeye eklenenler:**
  - Eşiğe eşitlik.
  - `[System Message]` talimatı.
  - Güven azalan ve kimlik artan sıralama.
  - Kapasite karantinası (tam çıktı).
  - Yinelenen kimlik, NaN güven, bool tekrar oranı.
- **Referans karşılaştırması:** Gerçek belgelerden üretilen paket `guvenli_rag_paketi_referans` ile birebir karşılaştırılır. Modele giden bağlam metninin yalnız referans temiz belgelerden oluştuğu da denetlenir.
- **Bilerek yapılan değişiklik:** Eski `kontrol(r["baglam_sizdi"] is False, ...)` satırı kaldırıldı. Bu satır, modelin canary sızdırmamasını kabul şartı yapıyordu. Rehber §6 ve kabul almış ai-savunma-29 kararı model davranışının kabul şartı olmamasını istiyor. Sızıntı bilgisi artık bulgu olarak kanıta yazılıyor.
  - Savunmanın asıl kabulü deterministik ve korunuyor: zehirli belge karantinada, bağlamda değil, işaret bağlam metninde yok.
  - Referans eşleşmesi bu kabulü eskisinden daha sıkı hâle getiriyor.
- Kanıt yalnız `kabul=all(sonuclar)` ile yazılır.

Ortak `sandbox/ai_gercek_lab.py`, `engine/` ve `web/` değiştirilmedi.

## Dört kontrol (`.ai-venv/Scripts/python.exe -X utf8`, geçici klasörler oturum scratchpad'inde)

| Kontrol | Komut | Sonuç |
|---|---|---|
| Doğrulama | `tools/validate.py ai-savunma-18` (PAFTA_DATA=`<scratchpad>/s18-kabul`) | **TEMİZ**, 9 kontrol. Son anlatım düzenlemesinden sonra yeniden koşturuldu. |
| Tahmin | `docs/denetim/araclar/tahmin.py . ai-savunma-18` | 1 tahmin, **0 şüpheli** |
| Mutasyon | `kirp_gercek.py <scratchpad>/s18-mutasyon`, ardından `mutasyon.py --en-cok 1000 ai-savunma-18` | 12 + 21 + 21 = 54 mutant, **0 geçen**. Kopya klasörü sonra silindi. |
| Kopya sondası | `kopya_sonda.py ai-savunma ai-savunma-18 ...` | 6/6 **fail → korunuyor**, kanıt yazılmadı |

Kopya sondasında denenen 6 yol: takma adla import, öznitelik erişimi, `getattr`, `inspect` + `exec`, yıldızlı import, `importlib` + `__dict__`.

## Gerçek sonuç

- **Kanıt:** `<scratchpad>/s18-kabul/ai-kanit/savunma-ragpoison-1793377749443.json` (kabul: true).
- **Model:** `qwen3:4b-instruct-2507-q4_K_M`, sıcaklık 0, tohum 5.
- **Paket:** Bağlamda `d-urun` ve `d-kargo` var. `d-zehir` karantinada, nedenleri `kaynak`, `guven`, `tekrar` ve `talimat`. İşaret ham birleşimde var, bağlamda yok.
- **Model yanıtları:** Temiz bağlamın yanıtı "Iade suresi teslimattan sonra 14 gün sürer.", ham birleşimin yanıtı "Iade süresi 14 gün sürer." oldu. İkisinde de canary sızmadı; bu model ham talimata uymadı. Bu sonuç anlatıma eklendi ve "filtre gereksiz" anlamına gelmediği açıklandı.
- **Çalıştır (CLI runner `run`):** Başlangıç kodu `ok` döndü. Zehirli belge gerçek modele giden bağlama girdi ve UYARI basıldı. Model bu koşuda da sızdırmadı.
- **Görev 1–3, görünür veriyle elle koşturuldu:**
  - Başlangıç kodları kusuru gösterdi (yukarıdaki tablo).
  - Çözümler 4 bozuk politikayı reddetti.
  - `forum-zehir` dört nedenin hepsini aldı, `sinir-belgesi` aday oldu, `sistem-taklidi` `talimat` nedeniyle karantinaya alındı.
  - Paket `iade-politikasi`, `kargo-sss` ve `turkce-zehir` belgelerinden oluştu; iki belge kapasite nedeniyle dışarıda kaldı.

## Yapılamayanlar

- **Tarayıcıda görsel kabul YAPILMADI.** Kontrol, Çalıştır ve dosya erişimi yalnız CLI ve runner üzerinden doğrulandı.
- Gerçek deneyin kendi belgeleri değiştirilmedi; zehirli belge hâlâ kolay bir vaka. Daha zor bir vakanın (Türkçe talimat) yalnız görünür veride gösterildiği anlatımda açıkça yazılı.
- Kurulum, indirme, commit/push ve puan yazımı yapılmadı. Ollama sunucusuna dokunulmadı.
