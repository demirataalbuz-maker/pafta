# Yeni ders pu25 (plan-purple-1, İstihbarattan plana: CTID APT29): yazar kontrolleri tamam, denetime hazır

- **Yazar:** claude-yazar.
- **Atama:** ortak pano 04.11.2026 18:13.
- **Kararlar:**
  - Purple yapısı seçenek A.
  - CTID APT29 planının indirilmesi kullanıcı onaylı ("Hepsini onayla", 04.11).
- **Puan** verilmedi; bağımsız denetim claude-opus'tadır.
- **Görsel sınama** yapılmadı; kabul CLI üzerinden `tools/validate.py` ile yapıldı.

## Eklenen / değişen dosyalar

- `tracks/purple/lessons/pu25-istihbarattan-test-planina.md` (sha256 14248115ffe1c479…)
- `sandbox/purple_istihbarat_lab.py` (97201936a1f257c7…): gerçek planı okur.
  - Kaynak: `.deps/ctid-apt29-4467a6ee/APT29.yaml`; sha256 `644f2818…1615` sabit değerle karşılaştırılır.
  - Okuma: `.deps` altındaki PyYAML 6.0.3 `safe_load`.
  - Referanslar, `kod_koruma` ve `calistir`.
  - **Hiçbir komut çalıştırılmaz.** Komut metinlerinin öğrenci çıktısına girmediği ayrıca sayılır (`komut_sizintisi`).
- `tracks/purple/fixtures/pu25_istihbarat/` (`ornekler.json`, `telemetri.json`, `README.md`):
  - `ornekler.json`: CTID biçiminde sentetik bir plan; komutlar çıkarılmış.
  - `telemetri.json`: Varsayımsal izole Windows VM telemetrisi ve ortam sınırları; **elle yazılmış bir varsayımdır**, ölçüm değildir.
- `outputs/yeni-pu25/pu25-1793828140833678600.json`: son kabul kanıtı.
- `tracks/purple/track.json`: mevcut "İstihbarattan Avcılığa" modülüne yalnız `pu25` eklendi; panoda `uyari` yazıldı.
- `engine/` ve `web/` değişmedi. Commit/push yok.

## İçerik

### Görevler

1. **`plan_adimlari`:**
   - Plan ayrıntısını anahtara bakarak atlar.
   - Adım ve teknik kimliklerinin biçimini doğrular.
   - Yürütücü ve girdi anahtarlarını sıralı listeler; komut metinlerine dokunmaz.
   - Yinelenen adımı reddeder.
   - **Doğal sıra** uygular: `2.B` < `2.B.1` < `10.A`.
2. **`attack_denetle`:** ATT&CK 19.2 özetine karşı denetler.
   - Durumlar: geçerli, yeniden adlandırılmış, emekli, kullanım dışı, bilinmiyor.
   - Kullanım dışı, emekliden önce gelir.
   - Alt teknik adı ilk `": "`'dan sonra karşılaştırılır.
3. **`test_plani`:**
   - Emekli teknik için güncel kimliği kullanır.
   - Telemetri önce tam kimlikle aranır, yoksa üst teknikle. Açık boş liste kör noktadır.
   - Durum önceliği: kapsam dışı > ertele > planla.
   - Taktik özeti üretir.
4. **Gerçek deney:** Gerçek plan → denetim → test planı.

### KUSURLU başlangıç kodları

- **K1:** Plan ayrıntısının konumuna güveniyor, metin sırası kullanıyor, yürütücüleri tekilleştirmiyor.
- **K2:** Alt teknik adını kırpmıyor; emekli ve kullanım dışı kimlikleri tanımıyor; her tekrarı ayrı kayıt yapıyor.
- **K3:** Telemetriyi yalnız tam kimlikle arıyor, "ertele" yok, özet sırasız.

## Gerçek final (son kabul koşusu)

- **Plan:** 101.876 bayt, `attack_version: 8.1`, 79 adım (`1.A` … `20.B`).
- **Denetim:** 42 tekniğin 39'u geçerli, 3'ü yeniden adlandırılmış:
  - `T1003` "Credential Dumping" → "OS Credential Dumping"
  - `T1036.005` → "Match Legitimate Resource Name or Location"
  - `T1041` → "Exfiltration Over C2 Channel"

  Emekli, kullanım dışı ya da bilinmeyen kimlik yok.
- **Test planı:** 69 adım planlandı, 9 ertelendi (çok makine gerekiyor), 1 kapsam dışı (OneDrive'a sızdırma).
- **Kör noktalar:** 11 teknik. Toplama taktiğinin 7 adımının 7'si kör noktada.
- **Diğer:** `komut_sizintisi: 0`, `calistirilan_komut: 0`, `kabul: true`. Koşu yaklaşık 0,3 sn sürdü.

## Kendi kontrollerim (`.ai-venv/Scripts/python.exe -X utf8`)

- **`tools/validate.py pu25`:** TEMİZ, 9 kontrol.
- **`tahmin.py`:** 1 tahmin, 0 şüpheli.
- **Mekanik mutasyon:** 14 mutant, 0 geçen.
  - İlk turda sıralama anahtarındaki `1→2` sabiti eşdeğer bir mutant olarak geçti. Anahtar sabitsiz biçime çevrildi: `(not p.isdigit(), int(p) if p.isdigit() else p)`.
- Mekanik sayı az olduğu için **elle anlamsal mutant** da denendi: 23 mutant, 0 geçen.
  - İlk turda `"technique" in x` → `x.get("technique")` mutantı geçti. `technique: None` ve `{}` için testler eklendi.
  - Aynı sınamada alt teknik adının son `": "`'dan bölünmesi de yakalanıyor.
- **Kopya sondası:** 7/7 reddedildi.

## Denetçiye not

- "Gerçek deney" burada bir saldırı çalıştırmak değildir. Gerçek, hash'i doğrulanmış bir CTI dosyasının işlenmesidir. Bu, purple-1 maddesinin (istihbarattan plana) doğası gereğidir. Uçtan uca öykünme Dalga C'deki purple-10'a bırakıldı.
- Denetim, üst teknik adı değişikliklerini (ör. "Signed Binary Proxy Execution" → "System Binary Proxy Execution") bilerek kapsamıyor. Ders bunu hata vitrininde açıkça gösterip yansıtma sorusu yapıyor.
- `.deps` kökündeki mevcut PyYAML kullanıldı; yeni paket kurulmadı.
