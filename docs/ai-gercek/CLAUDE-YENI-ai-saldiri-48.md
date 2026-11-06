# Yeni ders ai-saldiri-48 — yazar kontrolleri tamam, denetime hazır

Yazar: claude-yazar. Görev kaynağı `docs/ai-gercek/GOREV-YENI-AI-DERSLERI.md`. Bu rapor yazarın kendi kontrolleridir; puan verilmedi, bağımsız denetim claude-opus'tadır. Ders ekranı (web arayüzü) tarayıcıda açılıp sınanmadı; kabul CLI `tools/validate.py` ile yapıldı.

## Eklenen / değişen dosyalar
- `tracks/ai-saldiri/lessons/ai-saldiri-48-egitim-verisi-cikarimi.md` (sha256 35947e11b7a90f25…)
- `sandbox/ai_gercek_ai_saldiri_48.py` (41eca78252566a08…)
- `tracks/ai-saldiri/fixtures/ai-saldiri-48/README.md`, `veri/uyelik.json` (bcf0e46ac7cc95f2…)
- `outputs/yeni-ai-saldiri-48/gorunur-run-1.json` (hata vitrini kaynağı), `saldiri48-kabul-1793657183284.json` (son gerçek kabul kanıtının kopyası)
- `tracks/ai-saldiri/track.json`: yalnız "Model Bilgisi…" modülünün listesine `ai-saldiri-48` eklendi (HEAD'e göre 2 satır; Codex'in commit edilmemiş 49/51 kayıtları korundu). Panoya önce `uyari` yazıldı.
- engine/, web/, `sandbox/ai_gercek_lab.py`, puan dosyaları değişmedi. Kurulum/indirme yok; commit/push yok.

## İçerik
- Konu: membership inference (loss-threshold, Yeom vd. 2018; shadow model, Shokri vd. 2017), referansla kalibre skor, ROC AUC ve TPR @ düşük FPR (Carlini vd. 2022 "Membership Inference Attacks From First Principles"), Secret Sharer canary (Carlini vd. 2019) ve training data extraction (Carlini vd. 2021). Kaynaklar arXiv numarasıyla verildi.
- Metrik yönü: `ham_skor = -kayip_hedef` (düşük loss → daha olası üye), `kalibre_skor = kayip_ref - kayip_hedef`. AUC'de eşitlik 0.5; FPR sınırı dahil.
- 3 görev + gerçek deney. Her görevde KUSURLU başlangıç kodu (toplam 3), kusur yorumda söylenmez: K1 ters skor yönü/ters kalibrasyon, K2 eşitliği kazanç sayma + yanlış FPR paydası + katı sınır, K3 ilk 4 karakteri "tam" sayma, kısmi/çapraz yok.
- Teknikler: tahmin→çalıştır→fark; `esleme: ai-temel-12, ai-temel-16, ai-saldiri-49`; hata vitrini (kusurlu kodun görünür veride gerçekten verdiği AUC 0.111 / 0.000, kaydı `gorunur-run-1.json`); kanıt dosyasını okutma (ikinci koşuda PIN ve tam çıkarım sayısı değişir mi); Sınır cümlesi.
- Ders metni koşuya özgü bir başarı oranı iddia etmez; final her koşuda yeni rastgele PIN üretir.

## Gerçek final (son kabul koşusu)
Model Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775 offline; cuda (RTX 5050 Laptop); torch 2.14.1+cu130, transformers 5.21.0, peft 0.21.2. LoRA r8/alpha16 q_proj,v_proj, 540672 eğitilen parametre, 12 tur × 6 üye = 72 gerçek adım (loss 4.712 → 0.719, grad_norm > 0). Base hash aynı, adapter hash değişti.
- Kayıp: üyeler hedef 0.125–0.309, üye-olmayanlar 1.505–3.360 (ref hepsi 4.13–5.09).
- AUC: ham 1.0, kalibre 1.0; TPR @ FPR≤0.25 = 1.0 ikisinde de.
- Çıkarım: üye tam 2 / kısmi 2 / yok 2; üye-olmayan 0/0/6; bu koşuda çapraz 0. (Prototip koşusunda tam 1/6 ve 1 çapraz görülmüştü — sayılar koşudan koşuya değişiyor; derste sabit sayı yok.)
- Kanıt: `outputs/yeni-ai-saldiri-48/saldiri48-kabul-1793657183284.json`.

## Kendi kontrollerim (`.ai-venv/Scripts/python.exe -X utf8`)
- `tools/validate.py ai-saldiri-48` (PAFTA_DATA scratchpad): TEMİZ, 9 kontrol (1 tahmin, 4 solution, 4 starter). İlk koşu T2'de yanlış yazılmış bir test beklentisi yüzünden çözümü reddetti; test düzeltildi (çözüm değişmedi).
- `docs/denetim/araclar/tahmin.py . ai-saldiri-48`: 1 tahmin, 0 şüpheli.
- `kirp_gercek.py` + `mutasyon.py --en-cok 1000`: 7 + 18 + 18 = 43 mutant, 0 geçen. İlk turda 1 mutant geçti (önek döngüsünde `n+=1`→`n+=2`); tek karakter atlamayı yakalayan sınır testi eklendi, doğru beklentiler korundu.
- Kopya sondası 5/5 reddedildi (kanıt dosyası yazılmadan): doğrudan alias import, modül attribute, importlib+getattr/vars/__dict__, inspect.getsource+exec, `*` import. `kod_denetimi(..., izin=())`.
- Gerçek adımda üç mutasyon (ters skor, eşitlik tam kazanç, çapraz yok) ve sinama1/2/3 başarısızsa deney koşmaz.

## Bilinen sınırlar / denetçiye not
- Tek model, tek LoRA koşusu, 12 kurgusal kayıt; genel saldırı başarı oranı değildir.
- Web arayüzünde görsel sınama yapılmadı.
