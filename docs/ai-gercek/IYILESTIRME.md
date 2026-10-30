# AI dersleri iyileştirme: hedef her ders A (≥ 90)

Kullanıcı kararı (30.10.2026): 153 AI dersinin hepsi A notuna çıkacak. Puanlar `docs/ai-gercek/ai-puanlar.json`,
görünüm `docs/ai-gercek/AI_DENETIM.html`. A altındaki 127 ders `docs/ai-gercek/iyilestirme.json` kuyruğunda.
Kuyruk aracı: `tools/ai_iyilestirme.py`.

## Akış

```
acik → al (düzelten) → teslim (düzelten kendi kontrolüyle) → denetle kabul | iade (başka AI)
```

1. `liste --durum acik --dalga N` ile boştaki emri seç, `al <ders> --kim <ad>` ile sahiplen. Başkasının emrine dokunma.
2. `goster <ders>` → `yapilacaklar` listesinin **hepsini** yap. Liste denetçinin bulgusudur; atlarsan iade edilir.
3. Kendi kontrolün (teslimden önce, hepsi zorunlu):
   - `./.ai-venv/Scripts/python.exe -X utf8 tools/validate.py <ders>` → TEMİZ (gerçek deney dahil)
   - `docs/denetim/araclar/tahmin.py . <ders>` → 0 şüpheli
   - mutasyon: gerçek deney adımı çıkarılmış kopyada `docs/denetim/araclar/mutasyon.py <kopya> --en-cok 1000 <ders>` → 0 geçen
   - kopya sondası: gerçek deney adımına "kendi kodu yerine modüldeki referansı import eden" çözüm ver → GEÇMEMELİ
4. `teslim <ders> --kim <ad> --not "<4 kontrolün sonucu>"`.
5. Denetçi (düzelten değil) aynı 4 kontrolü kendisi koşar, dersi okur, puanlar. ≥ 90 ve yüksek öncelikli eksik yoksa
   `denetle <ders> kabul --puan N`, değilse `denetle <ders> iade --not "<neden>"`. İade edilen emri eski sahibi yeniden alır.

## Dalgalar

| Dalga | Ne | Ders |
|---|---|---|
| 1 | Test güvenliği: kopya açığı (`kod_denetimi` yok, referans import edilince geçiyor) ve geçen mutantlar | 23 |
| 2 | Giriş anlatımındaki "bu derste model çalıştırılmaz" çelişkisi (son adım gerçek deney koşuyor) | 27 |
| 3 | Purple standardı: ilk tablo + `[!NOT]`, görünür fixture + `hazirla()`, kusurlu başlangıç kodu, ~450+ kelime anlatım | 77 |

Dalga 1 ve 2'deki derslerin çoğunda Dalga 3 işleri de vardır; emir A'ya ulaşmadan kapanmaz.

## Değişmeyen kurallar

- Commit/push yok. Yeni indirme/kurulum yalnız kullanıcı onayıyla (kaynak, sürüm, boyut önce sunulur).
- Yalnız kendi başlattığın süreçleri kapat; kullanıcının Ollama sunucusu, yüklü modelleri, WSL ve Docker Desktop'a dokunma.
- `engine/` ve `web/` davranışını değiştirmeden önce kullanıcıya sor. Ortak dosyada önce pano `uyari`, dar değişiklik.
- Gerçek deney davranışını değiştirme: kanıt yalnız `kabul=all(checks)` ile yazılır; deneyler izole `PAFTA_DATA` ile sınanır.
- Var olan doğru bir testi zayıflatma; puanı yükseltmek için test/ölçüt kırpmak iade sebebidir.
- Örnek ders: `tracks/ai-guvence/lessons/ai-guvence-14-*.md` (purple standardının tam uygulanmış hâli).

## Elle karar gerektiren 3 ders (Dalga 3 içinde, kullanıcı onayı gerekebilir)

- `ai-temel-08`: plan vLLM/llama.cpp sunucusu diyor; Windows'ta vLLM yok. Ya llama.cpp server (indirme onayı) ya da planı Ollama'ya göre güncelleme.
- `ai-savunma-27`: garak 0.17.1 `.ai-araclar` ortamında kurulu; gerçek deney garak'ı yerel Ollama hedefine karşı koşturmalı.
- `ai-guvence-23`: gerçek GGUF nicemleme karşılaştırması için aynı modelin iki nicemleme seviyesi gerekir (indirme onayı).
