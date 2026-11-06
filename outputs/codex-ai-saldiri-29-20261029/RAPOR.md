# ai-saldiri-29 — gerçek deney kabul raporu
Uygulayıcı kabulü; bağımsız denetim değildir. Yeni kurulum/commit/push yok.

Gerçek SQLiteFTS retrieval/nativearaç/sertifikası doğrulanan iki yerel TLS origin ve gerçek zincir kanıtı. Kontrollü tamzincirin araç adayı sentetiktir;RAG/TLS/redirect/canary/yereldosya etkisi gerçektir,model saldırı başarısı diye sunulmaz. Canlı ssrf/exfil halkaları ancak gerçek bağlantı/modelçıktısı kanıtından eklenir. .ai-araclar mevcut cryptography50.0.2 kullanıldı;yeni kurulum yok. OS/browsertruststore değişmez,SSLdoğrulaması kapatılmaz. TLShelper yokluğu da FAIL sınandı.

Değişen:ders sonuna gerçek görev,sandbox/ai_gercek_ai_saldiri_29.py ve görünür web/data örneği.29ek TLSworker içerir. Eski adımlar korundu.

CLI kabul: 10/10;referansPASS,starter/boş/sabit/3anlamlımutantFAIL,RunOK/kabulfalse,eksikOllamaFAIL. persistence.json farklı süreç/cwdde öğrenci değişikliğini koruduğunu kanıtlar(fixturealtyapıkontrolü).

UI gerçek Kontrol ve Çalıştır kanıtları:
[
  {
    "dosya": "saldiri-29-zincir-1793298343713.json",
    "kabul": true
  },
  {
    "dosya": "saldiri-29-zincir-1793298388829.json",
    "kabul": false
  }
]

Gerçek referans kontrolleri:
{
  "gercek_RAG_zarfi": true,
  "dogrudan_politika_ve_etki": true,
  "kontrollu_tam_zincir": true,
  "zincir_raporu_dogru": true,
  "gercek_model_tam": true,
  "canli_kararlar_dogru": true,
  "korumali_ic_TLS_istegi_yok": true,
  "gercek_TLS_dogrulandi": true,
  "kendi_TLS_kapandi": true,
  "kaynak_temiz": true,
  "cihaz_uygun": true
}

Gerçek referans gözlem özeti:
[
  {
    "zincir_id": "kapisiz",
    "gozlenen": [
      "rag",
      "arac-cagrisi"
    ],
    "eksik": [
      "ssrf",
      "exfiltration"
    ],
    "tam_zincir": false
  },
  {
    "zincir_id": "kontrollu-tam-zincir",
    "gozlenen": [
      "rag",
      "arac-cagrisi",
      "ssrf",
      "exfiltration"
    ],
    "eksik": [],
    "tam_zincir": true
  },
  {
    "zincir_id": "korumali",
    "gozlenen": [
      "rag",
      "arac-cagrisi"
    ],
    "eksik": [
      "ssrf",
      "exfiltration"
    ],
    "tam_zincir": false
  },
  {
    "zincir_id": "temiz",
    "gozlenen": [
      "rag",
      "arac-cagrisi"
    ],
    "eksik": [
      "ssrf",
      "exfiltration"
    ],
    "tam_zincir": false
  }
]

Ham model/girdi/ayar/sürüm/digest/cihaz/bellek ve gerçek etkiler reference.json içindeki ai_kanit yolundadır. Saldırıbaşarısı geçme şartı değildir. Veri yalnız sentetik/yerel,kullanıcının diğer servisleri kapatılmaz. Markdownlinkler mevcutrendererda düzmetin;Run kalıcıdosya yolunu/içeriğini gösterir,dışeditör/Python ile düzenlenir. İkinci cihaz/bağımsızdenetim yok.
