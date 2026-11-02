# Purple ve AI tarafında puanı artırma planı

claude-opus, 02.11.2026. Kaynaklar: `docs/ai-gercek/ai-puanlar.json` (153 AI dersi), `docs/denetim/puanlar.json` (108 Purple maddesi), puanlayıcı `claude-devir/puan/puanla.py`.

## 1. Durum

| | AI | Purple |
|---|---|---|
| Birim | 153 ders | 108 madde |
| A (≥90) | 153 | 105 |
| Ortalama | 93.1 | 92.6 |
| Bağımsız ölçüm | hepsi (validate, mutasyon, tahmin, kopya sondası, içerik okuması) | 1 madde açıkça bağımsız; 42 madde "öz değerlendirme, bağımsız denetim bekleniyor"; 65 maddede kaynak yalnız "Claude" |

Purple ortalaması AI ortalamasıyla aynı güvenilirlikte değil. Puanı artırmadan önce Purple puanlarının gerçek olduğu doğrulanmalı.

## 2. AI tarafı: puan neden 93–95'te duruyor

| Bileşen | Tavan | Bugün | Nasıl veriliyor |
|---|---|---|---|
| test | 25 | 24–25 | ölçülüyor |
| derinlik | 25 | 25 | ölçülüyor |
| kapsam | 25 | 22, herkese sabit | ölçülmüyor |
| gerçeklik | 15 | 14 | 15. puan yalnız elle |
| yol | 10 | 7 temel, 8 savunma/güvence, 9 saldırı/ile-güvenlik | yola sabit taban, derse göre değil |

Ders yazarak puan artık artmaz. Kalan 5–8 puan, ölçülmeyen üç bileşende duruyor. Bunlar ölçülebilir hale getirilmeli. Puanı yükseltmek için ölçütü gevşetmek kabul edilmez; her yeni ölçüt dersin gerçek değerini ölçmeli ve bazı dersleri düşürebilmeli.

### 2.1 Kapsam (22 → ölçülen 0–25)
`ai_mufredat_plan_v3.json` her ders için `summary` (ne öğretir) ve `tools` (hangi araç) veriyor.
- Özetteki her öğretim hedefi anlatımda geçiyor mu, ve en az bir görevin testiyle sınanıyor mu?
- `tools` alanındaki araç gerçek deneyde gerçekten kullanılıyor mu?
- Puan: hedeflerin hepsi anlatılıp sınanıyorsa 25; anlatılıp sınanmayan her hedef −1; hiç geçmeyen her hedef −2; araç kullanılmıyorsa −2.
- Denetçi her ders için hedef–görev eşleme tablosunu yazar (otomatik değil, okuma).

### 2.2 Gerçeklik (14 → 15)
15. puan şu üçü birlikte varsa verilir:
- Kanıt dosyasında model adı ve sürümü/özeti, `seed` ve ayarlar var.
- Gerçek deney aynı makinede ikinci kez koşulduğunda aynı kararı veriyor.
- Fixture verisi gerçek araç biçiminde (gerçek Sysmon XML, gerçek Ollama JSON gövdesi gibi), uydurma basit sözlük değil.

### 2.3 Yol değeri (sabit taban → derse göre)
Tanım zaten "HTB AI Red Teamer, OWASP LLM Top 10 (2025), NIST AI RMF açısından değeri". Yolun adına göre değil, derse göre ölçülmeli:
- Ders başlığına `esleme:` alanı: OWASP LLM 2025 kimliği, MITRE ATLAS tekniği, NIST AI RMF alt kategorisi, HTB AI Red Teamer modülü.
- Denetçi her eşlemeyi yerel kanonik listeyle karşılaştırır ve dersin bir görevinin o konuyu gerçekten çalıştırdığını kontrol eder. Süs eşleme sayılmaz.
- Puan: 6 taban + doğrulanmış her çerçeve için +1 (en fazla 10).
- Sonuç: Gerçek bir red-team konusunu çalıştıran temel dersi 7'den 9–10'a çıkabilir. Hiçbir çerçeveye dokunmayan saldırı dersi 9'dan düşebilir.

## 3. Purple tarafı

### 3.1 Önce bağımsız denetim
AI tarafındaki yöntem Purple'a da uygulanmalı: validate, mutasyon, tahmin, kopya sondası ve içerik okuması.
- Öncelik, kaynağında "öz değerlendirme" yazan 42 maddede.
- Puan düşerse düşer; bu düşüş gerçeği gösterir.

### 3.2 Yol değeri (ortalama 8.4)
Tanım: seçilen HTB/THM yollarında (CJCA, CPTS, CDSA, CAPE, CDEP) ne kadar işe yaradığı.
- 7 alan 38 madde var: purple 9, csharp 5, php 5, c 4, javascript 4, asm 4, bitirme 3, regex 2, java 1, ids 1.
- Bu maddeler dil öğretiyor ama yol becerisine bağlanmıyor.
- Her birine o dilde, bir yol becerisini gerçek biçimli veriyle çalıştıran bir görev eklenmeli. Örnekler:
  - php: CPTS tarzı kaynak kod incelemesinde dosya dahil etme açığı
  - javascript: CJCA DOM XSS akışı
  - csharp: .NET deserialization ya da AD araç çıktısını ayrıştırma (CAPE)
  - c/asm: tampon taşması çökme dökümünü okuma
- Puan, eklenen görevin testiyle hak edilir; eşleme yazmak yetmez.

### 3.3 Derinlik (ortalama 22.2)
AI derslerini 25'e taşıyan kalıp Purple'a da uygulanır:
- İlk anlatımda "Gerçek araç ne gösterir | Bu ders ne kullanır | Ne söyleyemez?" tablosu.
- "Aracın altında ne olur / Saldırgan ne dener / Savunma neden kırılır / Sık tuzaklar / Çıktı nasıl okunur" bölümleri, her biri fixture'daki somut bir örneğe bağlı.
- En az 3 KUSURLU başlangıç kodu.

### 3.4 90 altındaki üç madde
| No | Madde | Puan | Ne gerekiyor |
|---|---|---|---|
| 60 | AD ACL'lerinden erişim yolu | 78 | Gerçek grafik verisini okuyan görev; AD VM gerekiyor |
| 105 | Oltalama e-postası analizi | 88 | Bağımsız denetçi; kapsam eksiğinin adı yazılmalı |
| 108 | Parola özeti biçimleri (pu17) | 87 | Bağımsız denetçi; kapsam eksiğinin adı yazılmalı |

## 4. Yeni anlatım kuralı (kullanıcı kararı, 02.11.2026)
Teknik terimler çevrilmez, yalnız anlatım Türkçe yazılır. Ayrıntı: `docs/ai-gercek/YENI-AJAN-REHBERI.md` bölüm 10. Mevcut derslerde çevrilmiş terimler var ("Şaşkın Vekil", "Açgözlü Koordinat Gradyanları", "Toplam Varyasyon Uzaklığı"); bunlar ders ele alındıkça düzeltilir.

## 5. Eksik analiziyle bağlantı
Kaynak: kullanıcının `pafta-eksik-analizi-tam.md` belgesi (31.10.2026; klasik tarafta 13, AI tarafında 18 eksik). 02.11.2026 itibarıyla bu eksiklerin hiçbiri derse dönüşmedi. Derslerde aranan kelimeler: ffuf, nuclei, format string, rug pull, spotlighting, HarmBench, AgentDojo, unlearning, C2PA ve DistilBERT için 0 eşleşme; nmap, pwntools, Ghidra, CaMeL ve cosign yalnız geçerken anılıyor.

Yol puanının gerçekten artmasının yolu bu eksikler:
- **AI:** Yol tanımındaki çerçevelere eşleme neredeyse yok. 153 dersin 5'i bir OWASP LLM ya da ATLAS kimliği anıyor; başlıkta eşleme alanı olan ders yok. Önce mevcut derslere doğrulanmış `esleme:` alanı eklenmeli. Böylece hangi OWASP/ATLAS maddesinin hiç ders almadığı ölçülür. B1/B2 eksikleri (MCP rug pull, eğitim verisi çıkarımı, guardrail eğitimi, adversarial training, HarmBench/AgentDojo) bu boşlukları kapatan yeni dersler olur.
- **Purple:** Yol puanı 7 olan dil maddelerine eklenecek yol görevleri A bölümündeki eksiklerle aynı yerde: web sömürüsü (php, javascript), pwn (c, asm), tersine mühendislik (asm, c), Windows/AD (csharp). Bu görevler eksik analizindeki lab sınırlarına uyar: yalnız `127.0.0.1` ya da internete kapalı VM/Docker, sıfırlanabilir lab, kanıtla ve savunmayla biten görev.
- **Kurulum gerektirenler** kullanıcı onayı ister: nmap, ffuf, nuclei, Ghidra, Juice Shop/DVWA, VLM, DistilBERT, cosign, Windows/AD VM.

## 6. Önerilen sıra
1. Purple'daki 42 öz değerlendirme maddesinin bağımsız denetimi. Puanların gerçek olup olmadığını gösterir.
2. AI derslerine doğrulanmış `esleme:` alanı (OWASP LLM 2025, ATLAS, NIST AI RMF, HTB AI Red Teamer). Kurulum gerekmez. Hangi çerçeve maddesinin hiç ders almadığını gösterir.
3. AI puanlayıcısında kapsam, gerçeklik ve yol ölçütlerinin tanımı; 153 dersin yeniden puanlanması.
4. Eksik analizindeki yeni dersler, kendi sırasıyla: AI'da MCP yetkilendirme, eğitim verisi çıkarımı, guardrail eğitimi; klasikte keşif, web, pwn. Kurulum gerektirenler için önce onay.
5. Purple'da yol puanı 7 olan 38 maddeye yol görevi eklenmesi (4. adımdaki lab'ları kullanır); aynı zamanda derinlik kalıbı.
6. 60, 105, 108 numaralı maddeler. 60 için AD VM gerekiyor.
