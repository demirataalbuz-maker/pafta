# Devir raporu: Pafta AI derslerini yazma / A'ya çıkarma

Yazan: claude-opus (şimdiye kadar denetçi), 30.10.2026. Bu rapor, AI derslerini yazmak için gelen ve önceki sohbetten haberi olmayan Claude içindir. Sayılar bu tarihe aittir; işe başlamadan kendin yeniden say.

## 1. Senin işin

Pafta AI müfredatı `C:\Users\demo12\Documents\Pafta-AI-GercekLab` klasöründe. Bu klasör git deposu değil. Müfredatta 153 ders var ve kullanıcının hedefi hepsinin A notuna (≥ 90) çıkması.

Sen **ders yazan / düzelten** tarafsın. Aynı işi Codex de yapıyor. İkiniz aynı kuyruktan ders alıyorsunuz.

Akış şöyle:
1. Kuyruktan bir ders al.
2. Yapılacaklar listesinin hepsini yap.
3. Dört kontrolü (validate, tahmin, mutasyon, kopya sondası) kendin koştur.
4. `teslim` et.
5. Dersi başka bir yapay zekâ bağımsız olarak denetler ve puanlar.

Kendi yazdığın dersi asla kendin puanlama. `denetle` komutunu ve `ai-puanlar.json` dosyasını puan için kullanma.

Kuyrukta kendini ayırt etmek için `--kim claude-yazar` adını kullan. `claude-opus` denetçinin adı, onu kullanma.

İşe başlamadan önce şu dosyaları oku:
- `AGENTS.md`
- `docs/ai-gercek/YENI-AJAN-REHBERI.md`: ders yazım standardı, veri kökeni ve gerçeklik etiketleri.
- `docs/ai-gercek/IYILESTIRME.md`: kuyruk akışı ve değişmeyen kurallar.
- `docs/ai-gercek/CODEX-IYILESTIRME-GOREV.md`: düzelten için ayrıntılı görev ve komutlar. Senin görevin de birebir bu; `codex` yerine kendi adını yaz.
- Örnek ders: `tracks/ai-guvence/lessons/ai-guvence-14-*.md`. Hedef standardın tam uygulanmış hali.
- Son örnekler: kabul almış derslerin raporları, `docs/ai-gercek/CODEX-IYILESTIRME-<ders>.md` dosyaları (ör. ai-saldiri-05, ai-savunma-27). Denetçinin neye baktığını gösterirler.

## 2. Güncel durum (30.10.2026)

- 153 dersin 51'i A notunda; 102'si 90'ın altında.
- İyileştirme kuyruğunda (`docs/ai-gercek/iyilestirme.json`) 127 kayıt var:
  - kabul 25
  - teslim 1 (`ai-temel-03`, denetim bekliyor)
  - alındı 1 (`ai-temel-06`, Codex'te)
  - açık 100
- Durumu görmek için:

  ```
  python -X utf8 tools/ai_iyilestirme.py liste --durum acik
  python -X utf8 tools/ai_pano.py oku -n 30
  ```

Dalgalar ve ders sayıları:

| Dalga | Ne | Ders |
|---|---|---|
| 1 | Kopya açığı ve geçen mutantlar | 23 |
| 2 | "Bu derste model çalıştırılmaz" çelişkisi | 27 |
| 3 | Purple standardı (tablo + `[!NOT]`, görünür fixture + `hazirla()`, kusurlu başlangıç, ~450+ kelime anlatım) | 77 |

Ayrıntılar `IYILESTIRME.md` dosyasında. Dalga 1'in büyük kısmı kabul aldı. Sıradaki işin çoğu Dalga 2 ve 3'te.

## 3. Bir dersi yapma adımları (tek tek)

Kullanıcı açıkça **tek tek** istiyor:
- Aynı anda yalnız 1 ders üzerinde ol.
- Bitir, teslim et, sonra yenisini al. Yarım iş bırakma.
- Hakkın biterse elindeki dersi ya `teslim` et ya da `birak`.

```
python -X utf8 tools/ai_iyilestirme.py al <ders> --kim claude-yazar
python -X utf8 tools/ai_iyilestirme.py goster <ders>        # yapilacaklar: hepsini yap, atlarsan iade
# ... dersi düzelt: tracks/<yol>/lessons/<ders>-*.md, gerekirse tracks/<yol>/fixtures/<ders>/ ve sandbox/ai_<yol>_veri.py
./.ai-venv/Scripts/python.exe -X utf8 tools/validate.py <ders>                       # TEMİZ (gerçek deney dahil, izole PAFTA_DATA)
./.ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/tahmin.py . <ders>       # 0 şüpheli
./.ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/kirp_gercek.py <geçici>  # mutasyon kopyası (mutlak yol ver)
./.ai-venv/Scripts/python.exe -X utf8 <geçici>/docs/denetim/araclar/mutasyon.py <geçici> --en-cok 1000 <ders>   # 0 geçen
PAFTA_DATA=<izole> ./.ai-venv/Scripts/python.exe -X utf8 docs/denetim/araclar/kopya_sonda.py <yol> <ders> "<referansı import eden kod>" [başlık-parçası]
python -X utf8 tools/ai_iyilestirme.py teslim <ders> --kim claude-yazar --not "validate TEMİZ · tahmin 0 · mutasyon 0/N · kopya korunuyor · yapılanlar: ..."
```

Teslimden sonra `docs/ai-gercek/CODEX-IYILESTIRME-<ders>.md` biçiminde kısa bir rapor yaz. Ad için `CLAUDE-IYILESTIRME-<ders>.md` kullan. Raporda şunlar olsun:
- ne değişti,
- dört kontrolün çıktısı,
- yapılamayanlar (ör. tarayıcıda görsel kabul).

## 4. Denetçinin baktığı şeyler (iade yememek için)

- **Kopya koruması:** Gerçek deney testinde `ai_lab.kod_denetimi(src, yasak=(<modüldeki her *_ref / ref* / *_referans adı>, "kanit_yaz"))` çağrısı bulunmalı; ihlalde `stop()` edilmeli. Kanıt yalnız `kanit_yaz(..., kabul=all(checks))` ile yazılmalı.
  - Denetçi üç yolu dener: doğrudan import, `getattr(m, "re"+"f…")` ve `inspect.getsource`. Üçü de engellenmeli.
  - `kod_denetimi` bunları artık yakalıyor (getattr, vars, globals, __dict__, getmembers, ...), yeter ki çağrılsın.
- **Mutasyon:** 0 mutant geçmeli. Sınır (`<` / `<=`), `and` / `or` ve sabit+1 mutantlarını yakalayan test vakası ekle. Doğru bir testi zayıflatmak iade sebebidir.
- **Çelişki:** Anlatımda "bu derste model çalıştırılmaz" deyip son adımda gerçek deney koşturma.
- **Purple standardı:**
  - İlk anlatımda tablo ve `[!NOT]` olmalı.
  - Görünür sentetik fixture olmalı, `hazirla()` ile hazırlanmalı.
  - En az 3 görevde kusurlu başlangıç kodu olmalı.
  - Anlatım ~450 kelimeden uzun ve derin olmalı; saldırgan ve savunucu bakışı tek cümleyle geçilmemeli.
- **Gerçeklik:** Sentetik veriyi gerçek kayıt gibi sunma. Gerçek deneyde sürüm, model, ayar ve gerçek sonuç kanıta yazılmalı.
- **Kapsam:** Plandaki konu gerçekten işlenmeli. Ör. temel-08, vLLM/llama.cpp karşılaştırması olmadığı için kapsamdan puan kaybetti.

## 5. Kurallar (kullanıcının koyduğu, hepsi geçerli)

- **Commit/push yok.** Yalnız kullanıcı isterse.
- **Yeni indirme veya kurulum** yalnız kullanıcı onayıyla. Önce kaynağı, sürümü ve boyutu göster, sonra panoya `soru` yaz ve bekle.
- **Süreçler:** Yalnız kendi başlattığın süreçleri kapat. Kullanıcının Ollama'sına, yüklü modellerine, WSL'e ve Docker Desktop'a dokunma. İş bitince kendi başlattığın araçları kapat.
- **`engine/` ve `web/`:** Davranışını değiştirmeden önce kullanıcıya sor.
- **Paylaşılan dosyalar** (`sandbox/ai_gercek_lab.py` gibi): Önce `tools/ai_pano.py yaz` ile `uyari` yaz, değişikliği dar tut, düzenlemeden önce dosyayı yeniden oku.
- **Başkasının işi:** Başkasının `alindi` emrine dokunma. Codex aynı anda çalışıyor.
- **Dürüstlük:** Test edilmemiş işi bitmiş gösterme. Yapılamayanı raporda açıkça yaz.
- **Bellek:** Makine bellek darlığı yaşıyor. Uzun süre arka planda çalışan izleyici ya da sunucu bırakma.
- **Engellenen içerik:** Güvenlik sınıflandırıcısı daha önce Purple PU17 için "hash biçimleri / araç modları" görev içeriğini durdurdu. Bu içeriği yeniden üretmeye çalışma.

## 6. Denetim kimde

Senin teslimlerini claude-opus (bu raporu yazan) ya da kullanıcının belirlediği başka bir yapay zekâ denetler. Codex'in teslimlerini denetleme görevi kullanıcı sana ayrıca verirse, yöntemin ve araçlarım şurada:

- Ölçüm klasörüm: `C:\Users\demo12\Documents\claude-devir\puan`. İçinde şunlar var:
  - `puanla.py` ve `yapi.py`,
  - `elle.json` (elle notlar),
  - eski validate ve mutasyon logları,
  - `d1/yeniden.py`: tek dersi puanlayıp `ai-puanlar.json` dosyasına birleştirir. Kullanım: `python -X utf8 d1/yeniden.py <proje> <puan klasörü> <ders>`.
  - `d1/elle-d1.json`: elle notlar.
- Purple çalışma kopyalarım: `C:\Users\demo12\Documents\claude-devir\purple`.
- Bir dersi yazdıysan onu denetleyemezsin.

## 7. Purple tarafı (`C:\Users\demo12\Documents\Pafta`, bilgi için)

Purple'da bütün maddeler A aralığında. Açık konular `Pafta\docs\denetim\INCELEME_NOTU.md` dosyasında.

- **105 (PU14):** Claude'un eklediği 5. görev bağımsız denetim bekliyor. Bu görevi sen yazmadın, istersen denetleyebilirsin; ama Codex de denetleyebilir, ikiniz birden yapmayın.
- **37, 60 ve 63:** Canlı ortam gerekiyor.
- **pu02:** Validate sırasında süre sınırını aşıyor.
- **AD22 ve AD23:** AD laboratuvar VM'i gerekiyor.

Kullanıcının asıl hedefi şu an AI dersleri.
