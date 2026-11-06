# Yeni ders pu23 (plan-klasik-6, DevSecOps: Semgrep, gitleaks, Trivy): yazar kontrolleri tamam, denetime hazır

- **Yazar:** claude-yazar.
- **Atama:** ortak pano 04.11.2026 18:13.
- **Kararlar:**
  - Purple yapısı seçenek A (kullanıcı, 04.11).
  - Araç indirmeleri kullanıcı onaylı: "Hepsini onayla", 04.11. Ayrıntı: `docs/ai-gercek/DALGA-A-KURULUM-ONAYI.md`.
- **Puan** verilmedi; bağımsız denetim claude-opus'tadır.
- **Görsel sınama** yapılmadı; kabul CLI üzerinden `tools/validate.py` ile yapıldı.

## Eklenen / değişen dosyalar

- `tracks/purple/lessons/pu23-devsecops-sast-sir-yapilandirma.md` (sha256 26b8957441f8882d…)
- `sandbox/purple_devsecops_lab.py` (28cd61b799ee3c5d…):
  - Geçici, iki commit'lik, kasıtlı açıklı bir git deposu kurar. Sırlar her koşuda rastgele ve sahtedir.
  - `.deps` altındaki sabit sürümlerle üç aracı paralel koşturur.
  - Her isteği kaydedip 403 dönen yerel bir vekil kullanır.
  - Etiketli gerçek liste: 10 sorun ve 4 tuzak.
  - İstisna listesi, referanslar, `kod_koruma` ve `calistir`.
- `tracks/purple/fixtures/pu23_devsecops/ornekler.json` (83ce7c0c…) ve `README.md`; sentetik, sırlar `REDACTED`.
- `outputs/yeni-pu23/pu23-1793828124158713800.json`: son kabul kanıtı.
- `tracks/purple/track.json`: yeni modül "DevSecOps ve Kod Güvenliği" (rank `buyuk-orta`), içinde yalnız `pu23`. Eski dersler taşınmadı; panoda `uyari` yazıldı.
- `engine/`, `web/` ve diğer lab modülleri değişmedi. Commit/push yok.

## Araçlar (indirildi, doğrulandı)

- **Sürümler:** Semgrep 1.183.0 (`.deps/semgrep-venv`, `--require-hashes`), gitleaks 8.30.1, Trivy 0.76.1.
- **Doğrulama:** Boyut ve sha256 onay listesiyle birebir aynı (`.deps/dalga-a-indirme-kaydi.json`).
- **Çevrimdışı sınama** (`.deps/dalga-a-sinama.json`):
  - Kayıt vekiline 0 istek geldi.
  - Trivy `misconfig` denetimleri ikili dosyaya gömülü; zafiyet veritabanı yok, gerekmedi.
- **Semgrep kipi:** Lab Semgrep'i `scan --experimental` (yerel osemgrep motoru) ile çağırır.
  - Standart Python sarmalayıcısı bu makinede her koşuda 18–28 sn sürdü ve bir validate koşusu 60 sn sınırını aştı.
  - Aynı depoda iki kipin bulguları birebir aynıydı.
  - Son validate'te Semgrep 1–6 sn sürdü.
  - **Not:** `--experimental` Semgrep'in resmî ama "deneysel" etiketli kipidir.

## İçerik

### Görevler

1. **`normalize`:** Üç aracın JSON'unu tek biçime çevirir.
   - Yol ayırıcısını düzeltir, `./` öneklerini atar.
   - Trivy'de PASS denetimleri atlanır; `CauseMetadata` satırı yoksa, `None` ya da 0 ise satır 0 olur.
   - Sıralı döner; bozuk çıktıda `ValueError` verir.
2. **`olc`:** Kapsama göre doğru / yanlış / kaçan sayar; kesinlik ve duyarlılığı hesaplar; "hat" (bütün araçların birleşimi) ekler.
   - Eşleşme kural adına değil konuma göredir: `(dosya, satır, tür)`.
3. **`ci_kapisi`:** Gerekçeli ve bitiş tarihli istisnalar uygular.
   - Bitiş günü dahildir; satır kapsamı vardır.
   - `suresi_dolan` ve `kullanilmayan` istisnaları raporlar.
4. **Gerçek deney:** Üç araç gerçek depoda koşar; sonuçlar referansla karşılaştırılır.

### KUSURLU başlangıç kodları

Kusurlar kodda yorumla söylenmez.

- **K1:** Yol düzeltilmiyor, PASS bulgu sayılıyor, `None` alanlar çöküyor, sıralama yok.
- **K2:** Tuzakla eşleşen bulgu doğru sayılıyor, tekrar iki kez sayılıyor, kapsam yok sayılıyor, sıfıra bölme oluyor.
- **K3:** Süresi dolan istisna bastırıyor, satır ve gerekçe yok sayılıyor.

### Anlatım öğeleri

- Tablo ve NOT; "Saldırgan ne dener" ve "Savunma neden kırılır".
- Blue karşılığı: sızan sır için rotate.
- Tahmin bloğu, hata vitrini ve Sınır cümlesi.

## Gerçek final (son kabul koşusu)

| Araç | Doğru | Yanlış | Kaçan | Kesinlik | Duyarlılık |
|---|---|---|---|---|---|
| Semgrep | 3 | 1 (önbellek MD5'i) | `S4` (`os.system`; kural yazılmamış) | 0,75 | 0,75 |
| gitleaks | 3 | 0 | yok; `.env` token'ını **geçmişten** buldu | 1,0 | 1,0 |
| Trivy | 5 | 1 (`DS-0026`) | `G3`: çalışma ağacında olmayan dosya | 0,833 | 0,833 |
| Hat | 9 | 2 | `S4` | 0,818 | 0,9 |

- **CI kapısı kapandı:**
  - 11 bulgu engelledi, 2 bulgu bastırıldı (`I1`, `I2`).
  - `I3`'ün süresi doldu.
  - `I4` hiçbir şeyi bastırmadı.
- **Diğer:** Dış istek 0, kanıtta sır sızıntısı 0, `cleanup: true`, `kabul: true`.

## Kendi kontrollerim (`.ai-venv/Scripts/python.exe -X utf8`)

- **`tools/validate.py pu23`:** TEMİZ, 9 kontrol (1 tahmin, 4 solution, 4 starter).
  - Erken bir koşuda gerçek deney 60 sn'de zaman aşımına uğradı (standart Semgrep sarmalayıcısı, makine yüklü). `--experimental` kipine geçilip sorun giderildi.
  - Bir deneme koşusunda gitleaks'in genel kuralı, `/` ve `+` içeren rastgele bir sahte anahtarı kaçırdı. Lab artık yalnız harf ve rakam üretir; ders bunu hata vitrininde anlatıyor. Araç davranışı beklentisi artık birebir denetleniyor: kaçanlar `(["S4"], [], ["G3"])`.
- **`tahmin.py`:** 1 tahmin, 0 şüpheli.
- **Mekanik mutasyon:** 41 mutant, 0 geçen.
  - İlk turda 2 mutant geçti:
    - (a) Eşdeğer `or→and`: gereksiz `isinstance(ham, dict)` kontrolü kaldırıldı.
    - (b) Gerçek boşluk: gerçek listede sözlük olmayan öğe, sayı kimlik ve `None` dosya için testler eklendi.
- **Elle anlamsal mutant** (`elle_mutant.py pu23_uret.py`): 14 mutant, 0 geçen.
  - İlk turda `.get("StartLine") or 0` → `.get("StartLine", 0)` mutantı geçti. `StartLine: None` için test eklendi.
- **Kopya sondası:** 7/7 reddedildi.

## Denetçiye not

- Ders gerçek araç ikilileri çalıştırır; `.deps` eksikse hata verir, PASS olmaz. İndirme yapmaz.
- Oranlar yalnız bu küçük sentetik depo ve bu kurallar içindir; ders bunu açıkça söylüyor.
- Purple dersleri `ai_ders_takip`'te değil; durum pano ve bu raporla izleniyor.
