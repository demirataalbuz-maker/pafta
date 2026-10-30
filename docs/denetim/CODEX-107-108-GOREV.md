# Codex görevi: madde 107 (PU16) ve 108 (PU17) eksiklerini kapat

Kullanıcı kararı (30.10.2026). Düzelten: Codex. Bağımsız denetçi: Claude. Önce 107, sonra 108.

## 107 · PU16 (Linux yetki yükseltme)

`puanlar.json` 107 kaydındaki eksik: PU16 görev 2'de `and→or` mutantı (çözüm satırı 28) testi geçiyor.

1. `python -X utf8 docs/denetim/araclar/mutasyon.py . --en-cok 1000 pu16` ile mutantı yeniden üret.
2. Mutantı elle incele: bütün girdilerde aynı sonucu veriyorsa **eşdeğerdir**; testi değiştirme, gerekçeyi `duzeltme.ozet`e yaz. Farklı sonuç veren bir girdi varsa o vakayı teste ekle; doğru testi zayıflatma.
3. `validate.py pu16` TEMİZ, `tahmin.py . pu16` 0, mutasyonda yeni geçen yok.
4. 107 kaydında puanı değiştirme; `duzeltme` alanına sonucu yaz.

## 108 · PU17 (parola özeti biçimleri)

1. `docs/denetim/puanlar.json` içinde `no: 108` kaydının `eksikler` listesindeki kapsam maddesini oku. Bu madde Claude'un 30.10.2026 bağımsız denetim bulgusudur; kapatılacak eksik odur.
2. `tracks/purple/lessons/pu17-parola-ozeti-bicimleri.md` dersine bu eksiği kapatan anlatım ve yeni görev(ler) ekle. Mevcut 1–4. görevlerin sözleşmelerini değiştirme.
3. Dersin mevcut kuralları geçerli: yalnız sentetik veya yayımlanmış test vektörleri, parola kırma yok, gerçek kimlik bilgisi yok, ağ/indirme/paket kurulumu yok. Görevler biçim tanıma, bağlam doğrulama ve savunma bulgusu üretir.
4. Yeni görev(ler) için: kusurlu başlangıç kodu (`# KUSURLU BAŞLANGIÇ KODU:`), yanlış çözümü reddeden test, sınır vakaları.

## Teslimden önce (hepsi zorunlu)

```
python -X utf8 tools/validate.py pu17                                  # TEMİZ
python -X utf8 docs/denetim/araclar/tahmin.py . pu17                   # 0 şüpheli
python -X utf8 docs/denetim/araclar/mutasyon.py . --en-cok 1000 pu17   # yeni görevlerde 0 geçen (eşdeğer olanları raporda gerekçelendir)
python -X utf8 tools/test_laptop_quality.py                            # pu17 satırı: reference pass
```

Görev sayısını sınayan bir test varsa (`tools/` altında `pu17` ara) yeni sayıya güncelle.

## Teslim

- `puanlar.json` 108 kaydında **puanı değiştirme**. Yalnız `duzeltme` alanına yazar, tarih, özet ve dört kontrolün sonucunu yaz; `bagimsiz_denetim: "Claude yeniden denetimi bekleniyor"`.
- Ortak panoya (`Pafta-AI-GercekLab/tools/ai_pano.py yaz --kim codex --tur bitti --konu purple-107-108 ...`) teslim notu bırak.
- Commit/push yapma; Claude denetledikten sonra kullanıcıyla birlikte gönderilecek.
- `engine/` ve `web/` davranışını değiştirme; başka maddelere dokunma.
