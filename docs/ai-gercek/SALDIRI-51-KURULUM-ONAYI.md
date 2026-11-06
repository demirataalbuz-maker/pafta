# Saldırı 51 — onaylandı ve kuruldu

2026-11-03: Kullanıcı “evet onay verdim” diyerek önceden sunulan resmi Python taban imajı, MLflow 2.1.1/2.2.1 ve uyumlu PyPI bağımlılıklarına onay verdi. Kurulum tamamlandı, gerçek CLI ve UI kabulü ayrı deneylerle geçti. Ayrıntı: CODEX-YENI-ai-saldiri-51.md.

Resmi kaynaklar: Docker Official Image `python:3.10-slim-bookworm`, https://pypi.org/project/mlflow/2.1.1/ ve https://pypi.org/project/mlflow/2.2.1/ . MLflow Apache-2.0. Bağımlılıkların sürüm/URL/hash kayıtları `outputs/s51-kurulum/20261103T091940Z/pip-*.json` içinde. Ücretli hesap/abonelik yok.

Taban: `python:3.10-slim-bookworm@sha256:db6ee5170ebce0f4d165af242e8e77addc08bd9ffc37e8b1815752cf027aa4f8`

| İmaj | ID | Mantıksal boyut (bayt) |
|---|---|---|
| `pafta-ai-s51:mlflow-2.1.1` | `sha256:e70da0b4dd92ebe0fbc6c838a1d1df15da6a86f1c249caeaf698c5f47aad1590` | 1351630645 |
| `pafta-ai-s51:mlflow-2.2.1` | `sha256:977a660407b57f86316f3665306b15ec77267a06fbe48e39271f1be709b15024` | 1355951699 |

Toplam mantıksal boyut 2.707.582.344 bayt. Ortak katmanlar nedeniyle benzersiz disk tüketimi ölçülmüş değildir. Önceden sunulan yaklaşık 300–600 MB indirme ve 1–2 GB disk planlama tahminiydi; toplam ağ indirmesi ölçülmedi, mantıksal imaj toplamı disk tahmininden yüksek çıktı.

Kurulum aracı: `python -X utf8 tools/ai_s51_kur.py --kur`; rapor `outputs/s51-kurulum/20261103T091940Z/kurulum.json`. Mevcut Docker29.9.2 ve venv yeniden kurulmadı. Build ağ kullanır; deney runtime ağsızdır ve otomatik kurulum yapmaz. Kullanıcının container/WSL/DockerDesktop süreçleri kapatılmaz. Yalnız labın tam container ID'leri temizlenir; imajlar kalır.

CVE kaynağı: https://github.com/mlflow/mlflow/security/advisories/GHSA-xg73-94fp-g449 . 2.2.1 yalnız bu CVE karşılaştırmasıdır, güncel/genel güvenli sürüm iddiası değildir. Gradio/Jupyter kurulumu bu onay kapsamında gerçekleştirilmedi.
