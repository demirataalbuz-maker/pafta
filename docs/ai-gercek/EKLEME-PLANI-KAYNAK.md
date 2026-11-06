# Pafta — Nereye Ne Eklenecek (AI + Purple)

**Tarih:** 2026-11-02 · **Yazan:** claude-opus · **Kaynaklar:** `ai-puanlar.json` (153 AI dersi), `docs/denetim/puanlar.json` (108 Purple maddesi), `pafta-eksik-analizi-tam.md`, Purple + AD ders listeleri.

**Kurallar:** Her şey ücretsiz ve yerel. Mevcut dersler atılmaz; eklemeler onların üstüne gelir. Teknik terimler çevrilmez. Kurulum gerektirenler kullanıcı onayı ile.

---

## DURUM
- **AI:** 153/153 ders A (ort 93.1), hepsi bağımsız ölçüldü.
- **Purple:** 105/108 madde A (ort 92.6) ama yalnız 1 madde bağımsız denetlendi; 42'si öz değerlendirme.
- **Purple'ın sorunu:** 17 dersin 14'ü mavi takım (SOC). Saldırı anlatılıyor, uygulanmıyor. Yani bugün Blue, Purple değil.

---

# A) AI TARAFI

## A1 — Puanlama (kurulum yok, hemen)
| Nereye | Ne eklenecek |
|---|---|
| Puanlayıcı `puanla.py` | Kapsam ölçütü: müfredat hedefi anlatımda + testte var mı (bugün herkese sabit 22) |
| Puanlayıcı | Gerçeklik 15. puanı: model sürümü + seed + ikinci koşuda aynı karar + gerçek biçimli fixture |
| Puanlayıcı | Yol değeri derse göre: 6 taban + doğrulanmış her çerçeve (+1), süs eşleme ssaymaz |
| 153 dersin başlığı | `esleme:` alanı: OWASP LLM 2025, MITRE ATLAS, NIST AI RMF, HTB AI Red Teamer |

## A2 — Yeni AI saldırı dersleri
| # | Ders | Yığın | Öncelik |
|---|---|---|---|
| 1 | MCP yetkilendirme ve rug pull | yerel sahte MCP sunucusu | Yüksek |
| 2 | Eğitim verisi çıkarımı (ezber + PII) | GPT-2, küçük Qwen | Yüksek |
| 3 | Zararlı fine-tuning | küçük Qwen + LoRA | Orta |
| 4 | Kendini kopyalayan istem (ajanlar arası) | yerel 2–3 ajan | Orta |
| 5 | ML altyapısı ve gerçek CVE (MLflow/Jupyter/Gradio) | izole Docker, eski sürüm | Orta |
| 6 | Unicode tag kaçakçılığı (saldırı tarafı) | saf Python | Orta |
| 7 | VLM adversarial pertürbasyon | küçük VLM (8GB sınırda) | Sonra |
| 8 | Güvenlik ML dedektörünü atlatma | scikit-learn, küçük phishing | Sonra |
| 9 | Deepfake / ses klonlama tespiti | yerel TTS | Sonra |

## A3 — Yeni AI savunma dersleri
| # | Ders | Yığın | Öncelik |
|---|---|---|---|
| 1 | Kendi guardrail'ini eğitme | DistilBERT + açık dataset | Yüksek |
| 2 | Adversarial training ve circuit breaker | PyTorch, küçük model | Yüksek |
| 3 | Injection mimari desenleri (CaMeL, dual-LLM, spotlighting) | yerel model | Orta |
| 4 | Standart benchmark (HarmBench, AgentDojo, StrongREJECT) | açık setler | Orta |
| 5 | Gerçek model imzalama | cosign | Orta |
| 6 | Watermark / C2PA | yerel | Sonra |
| 7 | Multimodal savunma (görsel + ses) | Pillow, Tesseract | Sonra |
| 8 | Unlearning doğrulaması | küçük model | Sonra |

## A4 — AI ↔ Purple köprüsü
SOC'deki LLM asistanına saldırı ve savunma (log enjeksiyonu, triyaj modelini kandırma, deterministik alarm kilidi). `ai-ile-guvenlik-12` gibi dersler Purple döngüsünün mavi yarısı olur.

---

# B) PURPLE TARAFI

## B1 — Önce bağımsız denetim (kurulum yok)
- 42 öz değerlendirme maddesi + 65 "Claude" kaynaklı madde → AI yöntemiyle denetle (validate, mutasyon, tahmin, kopya, içerik).
- 105 (oltalama), 108 (parola özeti) → kapsam eksiğinin adı yazılsın.
- 60 (AD ACL erişim yolu, 78 puan) → BloodHound CE + GOAD gelince.

## B2 — 10 modül: mevcut ders (mavi, kalır) + eklenecek kırmızı
| Modül | Mevcut mavi ders | Eklenecek kırmızı yarı |
|---|---|---|
| M1 İstihbarattan plana | pu01, pu13, pu04 | CTID planından gerçek öykünme |
| M2 Keşif ve ilk erişim | pu11, pu14 | nmap/ffuf keşif, Juice Shop sömürü, GoPhish |
| M3 Çalıştırma ve kalıcılık | pu15, pu03 | LOLBins, zamanlanmış görev, Run anahtarı |
| M4 Yetki yükseltme | pu12, pu16, ad01–ad07 | Windows + Linux privesc'i koşturma |
| M5 Kimlik bilgisi | pu17, ad08–ad10 | Kerberoast, AS-REP roast, LSASS dökümü |
| M6 Yatay hareket + C2 | **yok (tamamen yeni)** | Sliver izole C2, PsExec/WMI; Zeek beaconing |
| M7 Tespiti doğrulama | pu05, pu06, pu07 | Atomic Red Team ile tekrar koşup kural sınama |
| M8 Atlatma + dayanıklılık | **yok (tamamen yeni)** | teknik varyantları; davranış tespiti |
| M9 Tatbikat yönetimi | pu02 | rules of engagement, VECTR, pentest raporu |
| M10 Bitirme | pu10 | APT29 planının GOAD-Light'ta uçtan uca öykünmesi |

**Ayrı modüle:** pu08, pu09 (cloud log) → "Cloud tespiti". **Derinlik için:** ad11–ad25 → M4/M5'in mavi derinliği.

## B3 — Puan artırma (kurulum yok)
- Yol puanı 7 olan 38 dil maddesine yol görevi: php→dosya dahil etme, javascript→DOM XSS, csharp→AD araç çıktısı, c/asm→çökme dökümü.
- Derinlik kalıbı (gerçek araç tablosu, 5 bölüm, 3 kusurlu başlangıç kodu) tüm Purple'a.

## B4 — Purple araçları (ücretsiz)
Atomic Red Team + Caldera · CTID emülasyon planları · Sysmon + auditd · Sigma + CI · ATT&CK Navigator + DeTT&CT · VECTR · BloodHound CE · Sliver + RITA + Zeek · Canarytokens · GoPhish + MailHog · GOAD-Light (3 VM, ~10–12 GB) · SIEM: Splunk Free (SPL) + Elastic (alarm) + Wazuh.
**Sonra:** Falco/Tetragon, SilkETW, CAPE Sandbox (Linux ana makinede, izole; gerçek zararlı riski derste belirtilir).

---

# C) KLASİK EKSİKLER (Purple modüllerine bağlanır)
| Konu | Nereye | Öncelik |
|---|---|---|
| Keşif (nmap, ffuf, nuclei) | M2 | Yüksek |
| Web sömürüsü (XSS, SQLi, SSTI, XXE) | M2 | Yüksek |
| Pwn (overflow, ROP, format string) | ayrı modül + mavi: çökme tespiti | Yüksek |
| Tersine mühendislik (Ghidra, capa, FLOSS) | ayrı modül | Orta |
| Windows/AD saldırı | M4, M5 | Orta |
| DevSecOps (Semgrep, Trivy, gitleaks) | M7 ile ortak CI | Orta |
| Pentest raporu | M9 | Düşük |
| Cloud/container | ayrı modül (moto, kind, Trivy) | Sonra |
| Mobil, kripto, gerçek imajla DFIR | sonraya | Sonra |

**Eklenmeyecek:** ayrı Rust yolu (gerekirse AI dersine), wireless, ICS/OT, IoT.

---

# D) PAFTA OS
| Ne | Nasıl |
|---|---|
| Taban | Ubuntu LTS (yeni GPU sürücüsü için) |
| AI | doğrudan OS'ta, GPU tam hız (CUDA/ROCm) |
| Linux lab | Docker/Podman konteyner (neredeyse yerel hız) |
| Windows/GOAD/CAPE | KVM (GPU kullanmaz, %2–10 kayıp önemsiz) |
| Lab profilleri | AI / AD / Malware / Web — tek komut, önce bellek kontrolü |
| Üretim | önce kurulum betikleri, sonra ISO + live USB aynı betikten |
| Lisans | Windows, Splunk, Llama/Gemma pakete konmaz, betikle indirilir |

**Donanım sınırı:** 32 GB takılı ama Windows 23 GB görüyor (~8 GB iGPU'ya ayrılmış, BIOS'tan düşürülebilir). Model + GOAD + CAPE aynı anda çalışmaz → lab profilleri bu yüzden şart.

---

# E) ÖNERİLEN SIRA
1. Purple'daki 42 öz değerlendirme maddesinin bağımsız denetimi *(kurulum yok)*
2. AI derslerine `esleme:` alanı *(kurulum yok)*
3. Puanlayıcıya kapsam/gerçeklik/yol ölçütü; 153 dersi yeniden puanla *(kurulum yok)*
4. Purple modül yapısı: hangi mevcut ders hangi modülün mavi yarısı *(kurulum yok)*
5. Purple kırmızı yarısı + klasik eksikler *(kurulum var — onay)*
6. Yeni AI dersleri *(kısmen kurulum)*
7. Dil maddelerine yol görevleri + Purple derinlik kalıbı + 60/105/108
