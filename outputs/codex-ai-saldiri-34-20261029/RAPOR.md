# ai-saldiri-34 — gerçek deney kabul raporu
Uygulayıcı kabulü; bağımsız denetim değildir. Yeni kurulum/commit/push yok.

Gerçek structuredchat ve rawgenerate ile öğrenci rol/render/SHAkarşılaştırması. Gerçek kurulu modelin native templatei APIshowdan alınır. ChatML/kose dersönizlemesidir,kose plaintextbaseline;fullnativeJinjatemplatein birebiruygulaması diye sunulmaz. Previewhash ile gerçekten gönderilen prefixli prompt hash ayrı. TokenIDleri yalnız sunucu gerçekten context sunduysa kaydedilir. Budgetstop/EOS/canarygörülmesi gözlem,sabitcevap/saldırıbaşarısı şartı yok;HTTPeksikçağrıFAIL.

Değişen:ders sonuna gerçek görev,sandbox/ai_gercek_ai_saldiri_34.py ve görünür web/data örneği.29ek TLSworker içerir. Eski adımlar korundu.

CLI kabul: 9/9;referansPASS,starter/boş/sabit/3anlamlımutantFAIL,RunOK/kabulfalse,eksikOllamaFAIL. persistence.json farklı süreç/cwdde öğrenci değişikliğini koruduğunu kanıtlar(fixturealtyapıkontrolü).

UI gerçek Kontrol ve Çalıştır kanıtları:
[
  {
    "dosya": "saldiri-34-template-1793298475420.json",
    "kabul": true
  },
  {
    "dosya": "saldiri-34-template-1793298516981.json",
    "kabul": false
  }
]

Gerçek referans kontrolleri:
{
  "gercek_girdide_rol_render": true,
  "render_SHA_raporu": true,
  "gercek_structured_ve_raw_tam": true,
  "raw_girdi_hashi_dogru": true,
  "kaynak_temiz": true,
  "cihaz_uygun": true
}

Gerçek referans gözlem özeti:
[
  {
    "id": "rol-marker",
    "roller": [
      "system",
      "user"
    ],
    "chatml_sha256": "ceccb5c409054be6b0c4ab7f8f70463a79b3f8d39cf3cc0f48a89bd3f3dc0c01",
    "kose_sha256": "c9ce79f3d36ca4f49f350e5786d03261755a53ac75d3ff2b005099b66ecba4c7"
  },
  {
    "id": "temiz",
    "roller": [
      "system",
      "user"
    ],
    "chatml_sha256": "abcba2ae8c2664b8002ba2f17cc350b4837849f617d5207d39483f166aaff9eb",
    "kose_sha256": "abce939ad7155cfb916b0cf3764a36cdbf0081e8d30fae0867d588160791ec26"
  }
]

Ham model/girdi/ayar/sürüm/digest/cihaz/bellek ve gerçek etkiler reference.json içindeki ai_kanit yolundadır. Saldırıbaşarısı geçme şartı değildir. Veri yalnız sentetik/yerel,kullanıcının diğer servisleri kapatılmaz. Markdownlinkler mevcutrendererda düzmetin;Run kalıcıdosya yolunu/içeriğini gösterir,dışeditör/Python ile düzenlenir. İkinci cihaz/bağımsızdenetim yok.

Son ekran:24/24PASS,Run tümkontrollertrue/kabulfalse. İlk Failed to fetch UIkoşusu başarı sayılmadı;tekrar geçti. Referans ve UIRun rol-marker örneğinde structured/kaçışlı/kaçışsız tüm kanallarda sentetik canary görüldü. Kaçış güvenlikgarantisi değildir;bu tekörnekten genelASR çıkarılmaz. Sunucu contexttokenIDleri sunmadı;yalnız gerçek prompt/generationtokencount kaydedildi. Tam saldırı yolu regresyonu46ders429kontrol TEMİZ.
