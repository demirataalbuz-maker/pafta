# Devir raporu: Gemini için Pafta AI ders iyileştirme

Yazan: claude-opus, 01.11.2026. Kendisi bu işte denetçi. Bu rapor, önceki çalışmadan haberi olmayan Gemini için yazıldı. Rapordaki sayılar yazıldığı güne ait; işe başlamadan durumu kendin yeniden say.

## 0. En önemli 10 kural (önce bunları oku)

1. Kuyrukta kendi adın **`gemini`**. Her komutta `--kim gemini` yaz. `codex`, `claude-yazar` ve `claude-opus` adlarını kullanma.
2. **Kendi işini puanlama.** `denetle` komutunu çalıştırma. `docs/ai-gercek/ai-puanlar.json` dosyasına dokunma.
3. **Aynı anda tek ders.** Bir dersi al, bitir, teslim et, sonra yenisini al. Bırakman gerekirse `birak` komutunu çalıştır.
4. **Başkasının dersine dokunma.** Durumu `alindi` olan ve sahibi Codex ya da başka bir ajan olan derse dokunma.
5. **Testi zayıflatma.** Bir test başarısız oluyorsa çözümü düzelt. Testi gevşetmek, silmek veya `ok(True)` yazmak doğrudan iade sebebi.
6. **Yalan kanıt yazma.** Sentetik veriyi gerçek kayıt gibi sunma. Koşturmadığın bir kontrolü "geçti" diye raporlama.
7. **Commit ve push yok.** İndirme, kurulum ve `pip install` de yok. Gerekirse panoya `soru` yaz ve kullanıcıyı bekle.
8. **`engine/` ve `web/` klasörlerinin davranışını değiştirme.** Paylaşılan `sandbox/ai_gercek_lab.py` dosyasına dokunacaksan önce panoya `uyari` yaz.
9. **Süreçleri kapatma.** Kullanıcının Ollama'sını, yüklü modellerini, WSL ve Docker'ı kapatma. Yalnız kendi başlattığın süreçleri kapat.
10. **Gerçek deneyi aynı anda tek ajan koştursun.** Bellek dar. Validate'i başlatmadan önce `ollama ps` çıktısına ve panonun son 5 kaydına bak. Başka biri o an gerçek deney koşturuyorsa bekle.
11. **Terimleri çevirme (02.11.2026).** Anlatım Türkçe, teknik terimler orijinal kalır: `confused deputy`, `gradient masking`, `prompt injection`. "Şaşkın Vekil", "Açgözlü Koordinat Gradyanları" gibi Türkçe karşılık uydurma. Gerekirse cümle içinde ne olduğunu Türkçe açıkla.
12. **Teknik iddiayı doğrulamadan yazma.** Şimdiye kadarki derslerinde düzeltilen hataların hepsi bu türdendi: yanlış makale atfı, ters anlatılmış metrik, uydurma sayı, sandbox'ın sabit seçimini genel gerçek gibi sunma. Bir sayı, atıf, sürüm veya "X, Y'yi aşar" cümlesi yazıyorsan sandbox koduyla ya da birincil kaynakla karşılaştır; emin değilsen cümleyi daha dar kur.

## 1. Proje ve senin rolün

Proje klasörü `C:\Users\demo12\Documents\Pafta-AI-GercekLab`. Bu klasör git deposu değil.

Pafta, siber güvenlik eğitim platformu. Bu klasörde AI güvenliği müfredatı var: 153 ders, yollar `ai-temel`, `ai-saldiri`, `ai-savunma`, `ai-guvence` ve `ai-ile-guvenlik`. Kullanıcının hedefi her dersin A notuna (≥ 90) çıkması.

Şu an 94/153 ders A notunda. İyileştirme kuyruğunda 57 açık ders var.

Yazarlar ve denetçi:

| Ad | Rol |
|---|---|
| `codex` | Yazar / düzelten. Kuyruğun üstünden ders alıyor. |
| `gemini` (sen) | Yazar / düzelten. Kuyruğun **altından** ders al. |
| `claude-opus` | Bağımsız denetçi. Teslimini ölçer, puanlar, `kabul` ya da `iade` verir. |

Bu oturumda Codex 17 ders teslim etti ve iade almadı. Senden de aynı kalite bekleniyor.

## 2. İşe başlamadan oku

Okuma sırası:

1. `AGENTS.md`
2. `docs/ai-gercek/YENI-AJAN-REHBERI.md`: ders biçimi, veri kökeni ve gerçeklik etiketleri.
3. `docs/ai-gercek/IYILESTIRME.md`: kuyruk akışı ve dalgalar.
4. `docs/ai-gercek/CODEX-IYILESTIRME-GOREV.md`: düzeltenin ayrıntılı görevi. Bu senin görevinle aynı; yalnız `codex` yerine `gemini` yaz.
5. Örnek ders: `tracks/ai-guvence/lessons/ai-guvence-14-*.md`. Hedef standardın tam uygulanmış hali.
6. Yakın zamanda kabul almış bir ders (ör. `tracks/ai-savunma/lessons/ai-savunma-06-*.md`) ve onun `sandbox/ai_gercek_ai_savunma_06.py` dosyası.

Dosyaları baştan sona oku. Özet çıkarıp geçme.

## 3. Ders biçimi (kısa)

- Ders dosyası `tracks/<yol>/lessons/<ders>-*.md` yolunda.
- Blok türleri:
  - `::: anlat`: anlatım.
  - `::: tahmin`: öğrencinin tahmin sorusu.
  - `::: gorev N · Başlık`: içinde `starter`, `solution`, `test` ve `hint` kod blokları var.
- Son adım `::: gorev Gerçek deney · …` başlıklı ve `motor: ai-gercek` ile çalışıyor. Gerçek yerel modeli çağırıyor; bu makinede Ollama ve kurulu Transformers kullanılıyor.
- Gerçek deneyin sandbox modülü `sandbox/ai_gercek_<ders_alt_çizgili>.py`.
  - İçinde `referans…` ya da `…_ref` adlı **referans** fonksiyonlar bulunur. Test bunları çözüm doğrulamak için kullanır; öğrenci bunları **kullanamamalı**.
  - Modül içinde `import ai_lab` yazar. `ai_lab`, çalışma anında `sandbox/ai_gercek_lab.py` dosyasına bağlanır.
- Görünür veri dosyaları `tracks/<yol>/fixtures/<ders>/` klasöründe durur: bir `README.md` ve `veri/…json` ya da metin dosyaları. Kurulum bloğu bunları `from ai_<yol>_veri import hazirla; hazirla("<ders>")` ile yükler.

## 4. Bir dersi yapma adımları

Bütün komutları proje kökünden çalıştır. `PY=./.ai-venv/Scripts/python.exe` kullan.

```
python -X utf8 tools/ai_iyilestirme.py liste --durum acik        # alttan, alindi olmayan bir ders seç
python -X utf8 tools/ai_iyilestirme.py al <ders> --kim gemini
python -X utf8 tools/ai_pano.py yaz --kim gemini --tur basladi --konu <ders> --mesaj "aldım"
python -X utf8 tools/ai_iyilestirme.py goster <ders>              # 'yapilacaklar' listesinin HEPSİNİ yap
```

Dersi düzelttikten sonra dört kontrolün dördü de temiz olmalı:

```
# 1) validate: sonunda TEMİZ yazmalı (gerçek deney dahil). PAFTA_DATA'yı izole bir klasöre ver.
PAFTA_DATA=C:/Users/demo12/AppData/Local/Temp/gemini-iz/<ders> $PY -X utf8 tools/validate.py <ders>

# 2) tahmin: "0 şüpheli" yazmalı
$PY -X utf8 docs/denetim/araclar/tahmin.py . <ders>

# 3) mutasyon: "0 geçen" yazmalı. Önce kırpılmış kopya oluştur, MUTLAK yol ver.
rm -rf C:/Users/demo12/AppData/Local/Temp/gemini-k2
$PY -X utf8 docs/denetim/araclar/kirp_gercek.py C:/Users/demo12/AppData/Local/Temp/gemini-k2
$PY -X utf8 C:/Users/demo12/AppData/Local/Temp/gemini-k2/docs/denetim/araclar/mutasyon.py C:/Users/demo12/AppData/Local/Temp/gemini-k2 --en-cok 1000 <ders>

# 4) kopya sondası: üç denemenin üçü de "fail → korunuyor" demeli
PAFTA_DATA=<izole> $PY -X utf8 docs/denetim/araclar/kopya_sonda.py <yol> <ders> "from sandbox.ai_gercek_<d> import <referans> as <need_adı>"
PAFTA_DATA=<izole> $PY -X utf8 docs/denetim/araclar/kopya_sonda.py <yol> <ders> "import sandbox.ai_gercek_<d> as m; <need_adı> = getattr(m, 'ref' + 'erans…')"
PAFTA_DATA=<izole> $PY -X utf8 docs/denetim/araclar/kopya_sonda.py <yol> <ders> "import inspect, sandbox.ai_gercek_<d> as m; exec(inspect.getsource(m)); <need_adı> = <referans>"
```

Teslim:

```
python -X utf8 tools/ai_iyilestirme.py teslim <ders> --kim gemini --not "validate TEMİZ · tahmin 0 · mutasyon 0/N · kopya 3/3 korunuyor · yapılanlar: ..."
python -X utf8 tools/ai_pano.py yaz --kim gemini --tur bitti --konu <ders> --mesaj "teslim: <aynı özet>"
```

Teslimden sonra kısa bir rapor yaz: `docs/ai-gercek/GEMINI-IYILESTIRME-<ders>.md`. Raporda ne değiştiği, dört kontrolün çıktısı ve yapamadığın şeyler olsun.

## 5. Denetçinin baktığı şeyler (iade yememek için)

Teslimlerini claude-opus şu sırayla ölçer:

1. **Validate TEMİZ olmalı.** Başlangıç kodu testi GEÇMEMELİ, çözüm GEÇMELİ, gerçek deney gerçekten koşmalı.
2. **Tahmin: 0 şüpheli.**
3. **Mutasyon: 0 geçen.** Bir mutant geçiyorsa test vakası ekle. Sınırlar için `<` ve `<=` ayrımını, `and` ve `or` ayrımını, sabit ±1 değişimlerini ve kenar değerleri ayrı ayrı sına. Rastgele, görülmemiş bir girdiyle de sına; ezber çözüm geçmesin.
4. **Kopya koruması.** Gerçek deney testinde şu kalıp bulunmalı:

   ```python
   import ast
   yasak=("referans","referans_xxx","<diğer ref/yardımcı adlar>","getattr","kanit_yaz")
   ihlal=ai_lab.kod_denetimi(src,yasak=yasak)
   try:
       for node in ast.walk(ast.parse(src)):
           if isinstance(node,ast.ImportFrom) and any(a.name in yasak or a.name=="*" for a in node.names):
               ihlal.append("referans ithali")
   except SyntaxError: ihlal.append("sözdizimi")
   ok(not ihlal,"Kendi çözümünü yaz; referans ithali yasak")
   if ihlal: stop()
   ```

   - **AST kontrolü şart.** `kod_denetimi` tek başına `from modül import referans` satırını yakalamaz.
   - Modüldeki **her** referans fonksiyonu ve cevap veren yardımcı `yasak` listesinde olmalı.
   - Kanıt yalnız `ai_lab.kanit_yaz(..., kabul=all(checks))` ile yazılmalı.
5. **Çelişki olmamalı.** "Bu derste model çalıştırılmaz" deyip son adımda gerçek model koşturma. Doğru cümle: "İlk üç görev sentetik veriyle; son adım gerçek <model/araç> çalıştırır." Kullanılmayan bir aracı (FAISS, PEFT, LLM Guard…) dürüstçe "çalıştırılmaz" diye yazmak serbest, iyi bir şey.
6. **Purple standardı:**
   - İlk anlatımın başında şu tablo olmalı: `| Gerçek araç/model ne gösterir | Bu ders ne kullanır | Ne söyleyemez? |`. Altında `> [!NOT]` bloğu olmalı ve verinin sentetik olduğunu, kalıcılığın olmadığını söylemeli.
   - Görünür fixture olmalı: `README.md` ve `veri/*.json`. Kurulum bloğunda `hazirla("<ders>")` çağrılmalı. Görevler bu dosyaları okumalı.
   - En az 3 görevin başlangıç kodu `# KUSURLU BAŞLANGIÇ KODU: <hata>` yorumuyla başlamalı. Bu kod gerçekçi ama hatalı olmalı, boş `return` olmamalı. Başlangıç kodu testi geçmemeli.
   - Anlatım toplamda ~450 kelimeden uzun ve derin olmalı. Saldırgan ve savunucu bakışı tek cümleyle geçilmemeli. Sayılı mekanizma, örnek ve sınır konmalı. Kabul alan derslerde toplam 800–1000 kelime var.
7. **Gerçeklik.** Gerçek deneyin kanıtında model adı, digest, sürüm, ayarlar ve gerçek çıktı olmalı. Sentetik veri "sentetik" diye etiketlenmeli.
8. **Kapsam.** Ders planının konusu gerçekten işlenmeli. Konu adını anıp geçmek yetmez.

## 6. Bilinen tuzaklar

- **Geçici Ollama hataları.** Bellek darken validate `HTTP 500` ya da `/api/embed HTTP 400 … tokenize … bağlantı kurulamadı` verebilir. Bu dersin hatası değil. Bir süre bekle ve validate'i yeniden koştur. **Testi değiştirme.**
- **Sandbox modülünü elle denerken** `sys.modules['ai_lab']` takma adını ver ve `sandbox/` klasöründen çalıştır:

  ```
  cd sandbox && ../.ai-venv/Scripts/python.exe -X utf8 -c "import sys, ai_gercek_lab; sys.modules['ai_lab']=ai_gercek_lab; import ai_gercek_<d> as m; ..."
  ```

- **Mutasyon kopyası** için kirp_gercek'e mutlak yol ver. Göreli yol verirsen yanlış yere yazar.
- **Model yükleme.** Bir model önceden yüklü değilse deney sonunda `keep_alive=0` ile boşalt. Kullanıcı yüklemişse dokunma.
- **Uzun dosya düzenleme.** Dersin tamamını bir kerede yeniden yazma. Bölüm bölüm düzenle ve her adımdan sonra validate et. Kaybolan bir test bloğu, iadenin en sık sebebi.

## 7. İlk dersler için öneri

Listenin altındaki dersler 89 puanda. Çoğunun eksiği yalnız `anlatim`, bazılarının `kusurlu` da var. Bunlar senin için iyi bir başlangıç. Önerilen sıra: `ai-ile-guvenlik-18`, `-16`, `-15`, `-08`, sonra `ai-guvence-13`, `-12`, `-11` …

İlk **iki** dersi teslim et ve denetim sonucunu bekle. Panoda `claude-opus karar` kaydını görürsün; kuyrukta da `kabul` ya da `iade` olarak görünür. İade gelirse notu oku, aynı hatayı tekrarlama.

## 8. Durum komutları

```
python -X utf8 tools/ai_iyilestirme.py liste | tail -1            # özet sayılar
python -X utf8 tools/ai_iyilestirme.py liste | grep -E "teslim|alindi"
python -X utf8 tools/ai_pano.py oku -n 20
```
